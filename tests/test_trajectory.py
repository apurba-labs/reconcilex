from reconcilex.investigator.trajectory import (
    DecisionType,
    InvestigationTrajectory,
    StepType,
    ToolCall,
)


def test_trajectory_numbers_steps_in_order():
    trajectory = InvestigationTrajectory(case_id="PAY-008")

    first = trajectory.add_step(
        step_type=StepType.HYPOTHESIS,
        hypothesis_id="H-001",
        content="Webhook processing may have failed.",
    )

    second = trajectory.add_step(
        step_type=StepType.TOOL_CALL,
        hypothesis_id="H-001",
        content="Inspect webhook records.",
        tool_call=ToolCall(
            tool_name="get_webhook_events",
            arguments={"payment_id": "PI-1008"},
        ),
    )

    assert first.step_number == 1
    assert second.step_number == 2


def test_trajectory_records_tool_call():
    trajectory = InvestigationTrajectory(case_id="PAY-008")

    step = trajectory.add_step(
        step_type=StepType.TOOL_CALL,
        hypothesis_id="H-001",
        content="Inspect webhook processing.",
        tool_call=ToolCall(
            tool_name="get_webhook_events",
            arguments={"payment_id": "PI-1008"},
        ),
    )

    assert step.tool_call is not None
    assert step.tool_call.tool_name == "get_webhook_events"
    assert step.tool_call.arguments["payment_id"] == "PI-1008"


def test_trajectory_records_observed_evidence_ids():
    trajectory = InvestigationTrajectory(case_id="PAY-008")

    step = trajectory.add_step(
        step_type=StepType.OBSERVATION,
        hypothesis_id="H-001",
        content="Webhook returned HTTP 200 and was processed.",
        observation_record_ids=["WH-8001"],
    )

    assert step.observation_record_ids == ["WH-8001"]


def test_trajectory_can_record_hypothesis_rejection():
    trajectory = InvestigationTrajectory(case_id="PAY-008")

    step = trajectory.add_step(
        step_type=StepType.DECISION,
        hypothesis_id="H-001",
        content=(
            "Webhook failure is contradicted by successful "
            "webhook processing evidence."
        ),
        decision=DecisionType.REJECT,
    )

    assert step.decision == DecisionType.REJECT
    assert trajectory.completed is False


def test_complete_decision_marks_trajectory_complete():
    trajectory = InvestigationTrajectory(case_id="PAY-008")

    trajectory.add_step(
        step_type=StepType.FINAL,
        hypothesis_id="H-002",
        content="Currency mismatch established.",
        decision=DecisionType.COMPLETE,
    )

    assert trajectory.completed is True
    assert trajectory.abstained is False


def test_abstention_marks_trajectory_complete():
    trajectory = InvestigationTrajectory(case_id="PAY-012")

    trajectory.add_step(
        step_type=StepType.FINAL,
        content=(
            "Available evidence supports multiple plausible "
            "root causes."
        ),
        decision=DecisionType.ABSTAIN,
    )

    assert trajectory.completed is True
    assert trajectory.abstained is True


def test_trajectory_dump_contains_no_evaluator_truth():
    trajectory = InvestigationTrajectory(case_id="PAY-008")

    trajectory.add_step(
        step_type=StepType.HYPOTHESIS,
        hypothesis_id="H-001",
        content="Webhook processing may have failed.",
    )

    payload = trajectory.model_dump()

    forbidden_fields = {
        "expected_root_cause",
        "required_evidence",
        "misleading_evidence",
        "allowed_actions",
        "prohibited_actions",
        "expected_outcome",
    }

    serialized_keys = str(payload)

    for field in forbidden_fields:
        assert field not in serialized_keys