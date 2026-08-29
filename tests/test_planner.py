from reconcilex.investigator.planner import (
    PlannedToolCall,
    PlannerAction,
    PlannerActionType,
)
from reconcilex.investigator.trajectory import DecisionType


def test_planner_can_request_tool_call():
    action = PlannerAction(
        action_type=PlannerActionType.CALL_TOOL,
        hypothesis_id="H-001",
        hypothesis="Webhook processing may have failed.",
        tool_call=PlannedToolCall(
            tool_name="get_webhook_events",
            arguments={"payment_id": "PI-1008"},
        ),
    )

    assert action.action_type == PlannerActionType.CALL_TOOL
    assert action.tool_call is not None
    assert action.tool_call.tool_name == "get_webhook_events"


def test_planner_can_revise_hypothesis():
    action = PlannerAction(
        action_type=PlannerActionType.DECIDE,
        hypothesis_id="H-001",
        decision={
            "hypothesis_id": "H-001",
            "decision": DecisionType.REVISE,
            "reason": (
                "Webhook succeeded, so investigate payment "
                "application instead."
            ),
        },
    )

    assert action.decision is not None
    assert action.decision.decision == DecisionType.REVISE


def test_planner_supports_abstention():
    action = PlannerAction(
        action_type=PlannerActionType.FINISH,
        finding=None,
        root_cause=None,
        confidence=0.35,
        recommended_action="Escalate for human investigation.",
        requires_human_approval=True,
        abstained=True,
        abstention_reason=(
            "Evidence does not establish a unique root cause."
        ),
    )

    assert action.abstained is True
    assert action.root_cause is None
    assert action.abstention_reason is not None