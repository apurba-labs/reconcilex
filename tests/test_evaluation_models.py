import pytest
from pydantic import ValidationError

from reconcilex.evaluation.models import (
    CaseEvaluation,
    ProviderEvaluation,
)


def test_case_evaluation_model_accepts_valid_result():
    result = CaseEvaluation(
        case_id="PAY-008",
        root_cause_correct=True,
        first_divergence_correct=True,
        abstention_correct=True,
        safe_action_compliant=True,
        evidence_coverage=1.0,
        unsupported_claims=0,
        tool_calls=4,
        reasoning_steps=14,
        passed=True,
    )

    assert result.case_id == "PAY-008"
    assert result.evidence_coverage == 1.0
    assert result.passed is True


def test_case_evaluation_rejects_invalid_coverage():
    with pytest.raises(ValidationError):
        CaseEvaluation(
            case_id="PAY-008",
            root_cause_correct=True,
            first_divergence_correct=True,
            abstention_correct=True,
            safe_action_compliant=True,
            evidence_coverage=1.5,
            unsupported_claims=0,
            tool_calls=4,
            reasoning_steps=14,
            passed=True,
        )


def test_provider_evaluation_model():
    case = CaseEvaluation(
        case_id="PAY-012",
        root_cause_correct=True,
        first_divergence_correct=True,
        abstention_correct=True,
        safe_action_compliant=True,
        evidence_coverage=0.75,
        unsupported_claims=0,
        tool_calls=8,
        reasoning_steps=25,
        passed=True,
    )

    result = ProviderEvaluation(
        provider="openai",
        cases=[case],
        total_cases=1,
        passed_cases=1,
        root_cause_accuracy=1.0,
        first_divergence_accuracy=1.0,
        abstention_accuracy=1.0,
        safe_action_compliance=1.0,
        average_evidence_coverage=0.75,
        unsupported_claim_rate=0.0,
        average_tool_calls=8.0,
        average_reasoning_steps=25.0,
    )

    assert result.provider == "openai"
    assert result.total_cases == 1
    assert result.passed_cases == 1