from reconcilex.domain.case_input_loader import load_case_input
from reconcilex.investigator.model_planner import (
    ModelPlanner,
    SYSTEM_PROMPT,
)
from reconcilex.investigator.planner import (
    PlannerAction,
    PlannerActionType,
)
from reconcilex.investigator.trajectory import InvestigationTrajectory


class RecordingProvider:
    def __init__(self) -> None:
        self.system_prompt: str | None = None
        self.user_prompt: str | None = None
        self.response_model = None

    def generate_structured(
        self,
        *,
        system_prompt,
        user_prompt,
        response_model,
    ):
        self.system_prompt = system_prompt
        self.user_prompt = user_prompt
        self.response_model = response_model

        return PlannerAction(
            action_type=PlannerActionType.CALL_TOOL,
            hypothesis_id="H-001",
            hypothesis="Webhook processing may have failed.",
            tool_call={
                "tool_name": "get_webhook_events",
                "arguments": {
                    "payment_id": "PI-1008",
                },
            },
        )


def test_model_planner_requests_structured_action():
    provider = RecordingProvider()
    planner = ModelPlanner(provider)

    case_input = load_case_input(
        "data/inputs/cases.json",
        "PAY-008",
    )

    trajectory = InvestigationTrajectory(
        case_id="PAY-008",
    )

    result = planner.next_action(
        case_input,
        trajectory,
    )

    assert result.action_type == PlannerActionType.CALL_TOOL
    assert provider.response_model is PlannerAction


def test_model_planner_prompt_contains_case_not_ground_truth():
    provider = RecordingProvider()
    planner = ModelPlanner(provider)

    case_input = load_case_input(
        "data/inputs/cases.json",
        "PAY-008",
    )

    planner.next_action(
        case_input,
        InvestigationTrajectory(case_id="PAY-008"),
    )

    assert provider.user_prompt is not None

    assert "INV-1008" in provider.user_prompt
    assert "PI-1008" in provider.user_prompt

    forbidden = [
        "expected_root_cause",
        "required_evidence",
        "misleading_evidence",
        "prohibited_actions",
        "expected_outcome",
    ]

    for field in forbidden:
        assert field not in provider.user_prompt


def test_system_prompt_forbids_uncontrolled_access():
    assert "files" in SYSTEM_PROMPT.lower()
    assert "sql" in SYSTEM_PROMPT.lower()
    assert "shell" in SYSTEM_PROMPT.lower()
    assert "evaluator" in SYSTEM_PROMPT.lower()