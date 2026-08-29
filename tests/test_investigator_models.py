import pytest
from pydantic import ValidationError

from reconcilex.investigator.models import (
    EvidenceRef,
    Hypothesis,
    HypothesisStatus,
    InvestigationResult,
)


def test_evidence_ref_identifies_source_record():
    evidence = EvidenceRef(
        source="webhook_event",
        record_id="WH-1001",
        claim="Webhook processing failed with HTTP 500.",
    )

    assert evidence.source == "webhook_event"
    assert evidence.record_id == "WH-1001"


def test_hypothesis_can_be_rejected_by_contradictory_evidence():
    evidence = EvidenceRef(
        source="webhook_event",
        record_id="WH-8001",
        claim="Webhook processing succeeded.",
    )

    hypothesis = Hypothesis(
        hypothesis_id="H-001",
        description="Webhook processing failure caused the unpaid invoice.",
        status=HypothesisStatus.REJECTED,
        contradicting_evidence=[evidence],
    )

    assert hypothesis.status == HypothesisStatus.REJECTED
    assert len(hypothesis.contradicting_evidence) == 1


def test_investigation_result_supports_abstention():
    result = InvestigationResult(
        case_id="PAY-012",
        reported_issue="Systems disagree about payment processing.",
        finding=None,
        root_cause=None,
        first_divergence=None,
        confidence=0.35,
        recommended_action="Request additional evidence and escalate for human review.",
        requires_human_approval=True,
        abstained=True,
        abstention_reason="Evidence supports multiple plausible root causes.",
    )

    assert result.abstained is True
    assert result.root_cause is None
    assert result.requires_human_approval is True


def test_confidence_must_be_between_zero_and_one():
    with pytest.raises(ValidationError):
        InvestigationResult(
            case_id="PAY-001",
            reported_issue="Invoice remains unpaid.",
            confidence=1.5,
            recommended_action="Review payment.",
            requires_human_approval=True,
        )


def test_investigation_result_does_not_contain_evaluator_truth_fields():
    result = InvestigationResult(
        case_id="PAY-001",
        reported_issue="Invoice remains unpaid.",
        confidence=0.9,
        recommended_action="Review failed webhook processing.",
        requires_human_approval=True,
    )

    exposed = result.model_dump()

    forbidden_fields = {
        "expected_root_cause",
        "required_evidence",
        "misleading_evidence",
        "expected_outcome",
        "allowed_actions",
        "prohibited_actions",
    }

    assert forbidden_fields.isdisjoint(exposed.keys())