from __future__ import annotations
import json
from typing import Any

from reconcilex.domain.case_input import CaseInput
from reconcilex.investigator.models import InvestigationResult
from reconcilex.investigator.planner import (
    InvestigationPlanner,
    PlannerAction,
    PlannerActionType,
)
from reconcilex.investigator.tool_executor import ToolExecutor
from reconcilex.investigator.trajectory import (
    DecisionType,
    InvestigationStep,
    InvestigationTrajectory,
    StepType,
    ToolCall,
)
from reconcilex.investigator.verifier import EvidenceVerifier


class AgentInvestigationError(Exception):
    pass


class AgentInvestigator:
    def __init__(
        self,
        *,
        planner: InvestigationPlanner,
        executor: ToolExecutor,
        verifier: EvidenceVerifier,
        max_steps: int = 12,
    ):
        self.planner = planner
        self.executor = executor
        self.verifier = verifier
        self.max_steps = max_steps

    def investigate(
        self,
        case_input: CaseInput,
    ) -> tuple[InvestigationResult, InvestigationTrajectory]:
        trajectory = InvestigationTrajectory(
            case_id=case_input.case_id,
        )

        for _ in range(self.max_steps):
            action = self.planner.next_action(
                case_input,
                trajectory,
            )

            result = self._apply_action(
                case_input=case_input,
                trajectory=trajectory,
                action=action,
            )

            if result is not None:
                return result, trajectory

        return (
            self._max_steps_abstention(
                case_input=case_input,
            ),
            trajectory,
        )

    def _apply_action(
        self,
        *,
        case_input: CaseInput,
        trajectory: InvestigationTrajectory,
        action: PlannerAction,
    ) -> InvestigationResult | None:
        if action.action_type == PlannerActionType.CALL_TOOL:
            self._handle_tool_call(trajectory=trajectory, action=action)
            return None

        if action.action_type == PlannerActionType.DECIDE:
            self._handle_decision(
                trajectory=trajectory,
                action=action,
            )
            return None

        if action.action_type == PlannerActionType.FINISH:
            return self._handle_finish(
                case_input=case_input,
                trajectory=trajectory,
                action=action,
            )

        raise AgentInvestigationError(f"Unsupported planner action: {action.action_type}")

    def _handle_tool_call(
        self,
        *,
        trajectory: InvestigationTrajectory,
        action: PlannerAction,
    ) -> None:
        if action.tool_call is None:
            raise AgentInvestigationError("CALL_TOOL action did not include a tool call.")

        if action.hypothesis:
            trajectory.add_step(
                step_type=StepType.HYPOTHESIS,
                hypothesis_id=action.hypothesis_id,
                content=action.hypothesis,
            )

        trajectory.add_step(
            step_type=StepType.TOOL_CALL,
            hypothesis_id=action.hypothesis_id,
            content=f"Call {action.tool_call.tool_name}.",
            tool_call=ToolCall(
                tool_name=action.tool_call.tool_name,
                arguments=action.tool_call.arguments,
            ),
        )

        observation = self.executor.execute(action.tool_call)

        record_ids = self._extract_record_ids(observation)

        trajectory.add_step(
            step_type=StepType.OBSERVATION,
            hypothesis_id=action.hypothesis_id,
            content=json.dumps(
                observation,
                default=str,
                sort_keys=True,
            ),
            observation_record_ids=record_ids,
        )

    @staticmethod
    def _handle_decision(
        *,
        trajectory: InvestigationTrajectory,
        action: PlannerAction,
    ) -> None:
        if action.decision is None:
            raise AgentInvestigationError(
                "DECIDE action did not include a decision."
            )

        trajectory.add_step(
            step_type=StepType.DECISION,
            hypothesis_id=action.decision.hypothesis_id,
            content=action.decision.reason,
            decision=action.decision.decision,
        )

    def _handle_finish(
        self,
        *,
        case_input: CaseInput,
        trajectory: InvestigationTrajectory,
        action: PlannerAction,
    ) -> InvestigationResult:
        verified_evidence = []
        rejected_evidence = []

        for evidence in action.evidence:
            verification = self.verifier.verify(evidence)

            if verification.verified:
                verified_evidence.append(evidence)
            else:
                rejected_evidence.append(evidence)

        if rejected_evidence and not action.abstained:
            trajectory.add_step(
                step_type=StepType.FINAL,
                content=(
                    "Final conclusion contained evidence that could "
                    "not be deterministically verified."
                ),
                decision=DecisionType.ABSTAIN,
            )

            return InvestigationResult(
                case_id=case_input.case_id,
                reported_issue=case_input.reported_issue,
                hypotheses=[],
                finding=None,
                root_cause=None,
                first_divergence=None,
                evidence=verified_evidence,
                contradictory_evidence=rejected_evidence,
                confidence=0.0,
                recommended_action=(
                    "Escalate for human review and collect "
                    "additional evidence."
                ),
                requires_human_approval=True,
                abstained=True,
                abstention_reason=(
                    "The proposed conclusion relied on evidence "
                    "that could not be verified."
                ),
            )

        if action.abstained:
            trajectory.add_step(
                step_type=StepType.FINAL,
                content=(
                    action.abstention_reason
                    or "Investigation abstained."
                ),
                decision=DecisionType.ABSTAIN,
            )
        else:
            trajectory.add_step(
                step_type=StepType.FINAL,
                hypothesis_id=action.hypothesis_id,
                content=(
                    action.finding
                    or "Investigation complete."
                ),
                decision=DecisionType.COMPLETE,
            )

        return InvestigationResult(
            case_id=case_input.case_id,
            reported_issue=case_input.reported_issue,
            hypotheses=[],
            finding=action.finding,
            root_cause=action.root_cause,
            first_divergence=action.first_divergence,
            evidence=verified_evidence,
            contradictory_evidence=[],
            confidence=action.confidence or 0.0,
            recommended_action=(
                action.recommended_action
                or "Escalate for human review."
            ),
            requires_human_approval=(
                True
                if action.requires_human_approval is None
                else action.requires_human_approval
            ),
            abstained=action.abstained,
            abstention_reason=action.abstention_reason,
        )

    def _max_steps_abstention(
        self,
        *,
        case_input: CaseInput,
    ) -> InvestigationResult:
        return InvestigationResult(
            case_id=case_input.case_id,
            reported_issue=case_input.reported_issue,
            hypotheses=[],
            finding=None,
            root_cause=None,
            first_divergence=None,
            evidence=[],
            contradictory_evidence=[],
            confidence=0.0,
            recommended_action=(
                "Escalate for human review."
            ),
            requires_human_approval=True,
            abstained=True,
            abstention_reason=(
                "Investigation reached the maximum number "
                "of agent steps without a defensible conclusion."
            ),
        )

    @classmethod
    def _extract_record_ids(
        cls,
        observation: Any,
    ) -> list[str]:
        identifiers = {
            "invoice_id",
            "event_id",
            "webhook_id",
            "settlement_id",
            "refund_id",
            "audit_id",
        }

        found: list[str] = []

        def visit(value: Any) -> None:
            if isinstance(value, dict):
                for key, item in value.items():
                    if (
                        key in identifiers
                        and isinstance(item, str)
                    ):
                        found.append(item)

                    visit(item)

            elif isinstance(value, list):
                for item in value:
                    visit(item)

        visit(observation)

        return list(dict.fromkeys(found))