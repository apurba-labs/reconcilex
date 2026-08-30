from reconcilex.evaluation.metrics import (
    build_provider_evaluation,
)
from reconcilex.evaluation.models import CaseEvaluation


def make_case(
    *,
    case_id: str,
    passed: bool,
    root_cause_correct: bool = True,
    first_divergence_correct: bool = True,
    abstention_correct: bool = True,
    safe_action_compliant: bool = True,
    evidence_coverage: float = 1.0,
    unsupported_claims: int = 0,
    tool_calls: int = 4,
    reasoning_steps: int = 10,
) -> CaseEvaluation:
    return CaseEvaluation(
        case_id=case_id,
        root_cause_correct=root_cause_correct,
        first_divergence_correct=first_divergence_correct,
        abstention_correct=abstention_correct,
        safe_action_compliant=safe_action_compliant,
        evidence_coverage=evidence_coverage,
        unsupported_claims=unsupported_claims,
        tool_calls=tool_calls,
        reasoning_steps=reasoning_steps,
        passed=passed,
    )


def test_build_provider_evaluation():
    cases = [
        make_case(
            case_id="PAY-001",
            passed=True,
        ),
        make_case(
            case_id="PAY-002",
            passed=False,
            root_cause_correct=False,
            safe_action_compliant=False,
            evidence_coverage=0.5,
            unsupported_claims=1,
            tool_calls=6,
            reasoning_steps=14,
        ),
    ]

    result = build_provider_evaluation(
        provider="openai",
        cases=cases,
    )

    assert result.total_cases == 2
    assert result.passed_cases == 1

    assert result.root_cause_accuracy == 0.5
    assert result.first_divergence_accuracy == 1.0
    assert result.abstention_accuracy == 1.0
    assert result.safe_action_compliance == 0.5

    assert result.average_evidence_coverage == 0.75
    assert result.unsupported_claim_rate == 0.5

    assert result.average_tool_calls == 5.0
    assert result.average_reasoning_steps == 12.0


def test_empty_provider_evaluation():
    result = build_provider_evaluation(
        provider="gemini",
        cases=[],
    )

    assert result.total_cases == 0
    assert result.passed_cases == 0
    assert result.root_cause_accuracy == 0.0