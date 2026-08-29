from reconcilex.domain.case_input_loader import load_case_input
from reconcilex.domain.record_loader import PaymentRecordStore
from reconcilex.investigator.agent import AgentInvestigator
from reconcilex.investigator.model_planner import ModelPlanner
from reconcilex.investigator.planner import (
    PlannerAction,
    PlannerActionType,
)
from reconcilex.investigator.tool_executor import ToolExecutor
from reconcilex.investigator.trajectory import DecisionType
from reconcilex.investigator.verifier import EvidenceVerifier
from reconcilex.tools.payment_tools import PaymentTools


class ScriptedProvider:
    def __init__(self, actions):
        self.actions = iter(actions)

    def generate_structured(
        self,
        *,
        system_prompt,
        user_prompt,
        response_model,
    ):
        return next(self.actions)


def build_agent(actions):
    store = PaymentRecordStore("data/records")

    provider = ScriptedProvider(actions)

    return AgentInvestigator(
        planner=ModelPlanner(provider),
        executor=ToolExecutor(
            PaymentTools(store),
        ),
        verifier=EvidenceVerifier(store),
        max_steps=10,
    )


def test_agent_can_reject_then_replan_pay_008():
    actions = [
        PlannerAction(
            action_type=PlannerActionType.CALL_TOOL,
            hypothesis_id="H-001",
            hypothesis="Webhook processing may have failed.",
            tool_call={
                "tool_name": "get_webhook_events",
                "arguments": {
                    "payment_id": "PI-1008",
                },
            },
        ),
        PlannerAction(
            action_type=PlannerActionType.DECIDE,
            hypothesis_id="H-001",
            decision={
                "hypothesis_id": "H-001",
                "decision": DecisionType.REJECT,
                "reason": (
                    "Webhook evidence shows successful processing."
                ),
            },
        ),
        PlannerAction(
            action_type=PlannerActionType.CALL_TOOL,
            hypothesis_id="H-002",
            hypothesis=(
                "Payment application may have failed because "
                "invoice and payment currencies differ."
            ),
            tool_call={
                "tool_name": "get_invoice",
                "arguments": {
                    "invoice_id": "INV-1008",
                },
            },
        ),
        PlannerAction(
            action_type=PlannerActionType.CALL_TOOL,
            hypothesis_id="H-002",
            tool_call={
                "tool_name": "get_gateway_events",
                "arguments": {
                    "payment_id": "PI-1008",
                },
            },
        ),
        PlannerAction(
            action_type=PlannerActionType.CALL_TOOL,
            hypothesis_id="H-002",
            tool_call={
                "tool_name": "get_audit_events",
                "arguments": {
                    "entity_id": "INV-1008",
                },
            },
        ),
        PlannerAction(
            action_type=PlannerActionType.FINISH,
            hypothesis_id="H-002",
            finding=(
                "Payment application failed because "
                "invoice and payment currencies differ."
            ),
            root_cause="currency_mismatch",
            first_divergence="payment_recorded",
            evidence=[
                {
                    "source": "invoice",
                    "record_id": "INV-1008",
                    "claim": "Invoice currency is EUR.",
                },
                {
                    "source": "gateway_event",
                    "record_id": "GE-8001",
                    "claim": "Gateway event currency is USD.",
                },
                {
                    "source": "audit_event",
                    "record_id": "AUD-8002",
                    "claim": (
                        "Payment application failed because "
                        "currency_mismatch_invoice_EUR_payment_USD."
                    ),
                },
            ],
            confidence=0.98,
            recommended_action="Perform manual currency review.",
            requires_human_approval=True,
        ),
    ]

    agent = build_agent(actions)

    case_input = load_case_input(
        "data/inputs/cases.json",
        "PAY-008",
    )

    result, trajectory = agent.investigate(
        case_input,
    )

    assert result.root_cause == "currency_mismatch"
    assert result.abstained is False
    assert result.evidence
    assert trajectory.completed is True

    decisions = [
        step
        for step in trajectory.steps
        if step.decision is not None
    ]

    assert any(
        step.decision == DecisionType.REJECT
        for step in decisions
    )

    assert any(
        step.decision == DecisionType.COMPLETE
        for step in decisions
    )


def test_agent_forces_abstention_on_unverified_evidence():
    actions = [
        PlannerAction(
            action_type=PlannerActionType.FINISH,
            finding="Webhook definitely failed.",
            root_cause="webhook_processing_failure",
            evidence=[
                {
                    "source": "webhook_event",
                    "record_id": "WH-8001",
                    "claim": "Webhook processing failed.",
                },
            ],
            confidence=0.99,
            recommended_action="Replay webhook.",
            requires_human_approval=True,
        ),
    ]

    agent = build_agent(actions)

    case_input = load_case_input(
        "data/inputs/cases.json",
        "PAY-008",
    )

    result, trajectory = agent.investigate(
        case_input,
    )

    assert result.abstained is True
    assert result.root_cause is None
    assert result.confidence == 0.0
    assert trajectory.abstained is True
    
    
def test_agent_recovers_from_disallowed_tool():
    actions = [
        PlannerAction(
            action_type=PlannerActionType.CALL_TOOL,
            hypothesis_id="H-001",
            hypothesis="Inspect invoice state.",
            tool_call={
                "tool_name": "get_invoice_details",
                "arguments": {
                    "invoice_id": "INV-1008",
                },
            },
        ),
        PlannerAction(
            action_type=PlannerActionType.CALL_TOOL,
            hypothesis_id="H-001",
            tool_call={
                "tool_name": "get_invoice",
                "arguments": {
                    "invoice_id": "INV-1008",
                },
            },
        ),
        PlannerAction(
            action_type=PlannerActionType.FINISH,
            abstained=True,
            abstention_reason=(
                "More evidence is required before establishing "
                "a unique root cause."
            ),
            confidence=0.3,
            recommended_action="Continue investigation.",
            requires_human_approval=True,
        ),
    ]

    agent = build_agent(actions)

    case_input = load_case_input(
        "data/inputs/cases.json",
        "PAY-008",
    )

    result, trajectory = agent.investigate(
        case_input,
    )

    assert result.abstained is True

    rejected_tool_steps = [
        step
        for step in trajectory.steps
        if "get_invoice_details" in step.content
    ]

    assert rejected_tool_steps

    assert any(
        step.decision == DecisionType.REVISE
        for step in trajectory.steps
    )

    assert any(
        "INV-1008" in step.observation_record_ids
        for step in trajectory.steps
    )