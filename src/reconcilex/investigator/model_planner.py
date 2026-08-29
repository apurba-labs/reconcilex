from __future__ import annotations
import json

from reconcilex.domain.case_input import CaseInput
from reconcilex.investigator.planner import (
    InvestigationPlanner,
    PlannerAction,
)
from reconcilex.investigator.trajectory import InvestigationTrajectory
from reconcilex.llm.provider import LLMProvider


SYSTEM_PROMPT = """
You are ReconcileX, a payment-state divergence investigator.

Your job is to investigate discrepancies across fragmented financial
systems using only the approved investigation tools.

You must reason in hypotheses.

Important rules:

1. Do not assume the reported issue identifies the root cause.
2. Form a hypothesis and inspect evidence needed to test it.
3. Reject or revise hypotheses when observations contradict them.
4. Do not invent records, identifiers, amounts, states, timestamps,
   currencies, or audit events.
5. Do not claim evidence you have not observed.
6. Do not access files, databases, SQL, shell commands, Python execution,
   network resources, or evaluator data.
7. You may only request approved investigation tools.
8. If multiple plausible root causes remain and evidence cannot
   distinguish them, abstain.
9. Consequential financial actions require human approval.
10. A successful transaction event does not prove the entire payment
    lifecycle succeeded.

Your goal is not to produce an answer quickly.
Your goal is to establish the first defensible divergence in the
transaction lifecycle.

Return exactly one structured PlannerAction.
""".strip()


class ModelPlanner(InvestigationPlanner):
    def __init__(self, provider: LLMProvider):
        self.provider = provider

    def next_action(
        self,
        case_input: CaseInput,
        trajectory: InvestigationTrajectory,
    ) -> PlannerAction:
        user_prompt = self._build_user_prompt(
            case_input=case_input,
            trajectory=trajectory,
        )

        return self.provider.generate_structured(
            system_prompt=SYSTEM_PROMPT,
            user_prompt=user_prompt,
            response_model=PlannerAction,
        )

    @staticmethod
    def _build_user_prompt(
        *,
        case_input: CaseInput,
        trajectory: InvestigationTrajectory,
    ) -> str:
        case_payload = case_input.model_dump(
            mode="json",
        )

        trajectory_payload = trajectory.model_dump(
            mode="json",
        )

        return (
            "Investigate the following payment exception.\n\n"
            "CASE INPUT:\n"
            f"{json.dumps(case_payload, indent=2)}\n\n"
            "INVESTIGATION TRAJECTORY SO FAR:\n"
            f"{json.dumps(trajectory_payload, indent=2)}\n\n"
            "Choose the single best next investigation action."
        )