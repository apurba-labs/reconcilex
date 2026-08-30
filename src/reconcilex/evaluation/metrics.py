from __future__ import annotations

from reconcilex.evaluation.models import (
    CaseEvaluation,
    ProviderEvaluation,
)


def build_provider_evaluation(
    *,
    provider: str,
    cases: list[CaseEvaluation],
) -> ProviderEvaluation:
    total_cases = len(cases)

    if total_cases == 0:
        return ProviderEvaluation(
            provider=provider,
            cases=[],
            total_cases=0,
            passed_cases=0,
            root_cause_accuracy=0.0,
            first_divergence_accuracy=0.0,
            abstention_accuracy=0.0,
            safe_action_compliance=0.0,
            average_evidence_coverage=0.0,
            unsupported_claim_rate=0.0,
            average_tool_calls=0.0,
            average_reasoning_steps=0.0,
        )

    passed_cases = sum(
        case.passed
        for case in cases
    )

    root_cause_accuracy = _ratio(
        sum(case.root_cause_correct for case in cases),
        total_cases,
    )

    first_divergence_accuracy = _ratio(
        sum(case.first_divergence_correct for case in cases),
        total_cases,
    )

    abstention_accuracy = _ratio(
        sum(case.abstention_correct for case in cases),
        total_cases,
    )

    safe_action_compliance = _ratio(
        sum(case.safe_action_compliant for case in cases),
        total_cases,
    )

    average_evidence_coverage = (sum(case.evidence_coverage for case in cases) / total_cases)

    total_unsupported_claims = sum(
        case.unsupported_claims
        for case in cases
    )

    unsupported_claim_rate = (total_unsupported_claims / total_cases)

    average_tool_calls = (sum(case.tool_calls for case in cases) / total_cases)

    average_reasoning_steps = (sum(case.reasoning_steps for case in cases) / total_cases)

    return ProviderEvaluation(
        provider=provider,
        cases=cases,
        total_cases=total_cases,
        passed_cases=passed_cases,
        root_cause_accuracy=root_cause_accuracy,
        first_divergence_accuracy=first_divergence_accuracy,
        abstention_accuracy=abstention_accuracy,
        safe_action_compliance=safe_action_compliance,
        average_evidence_coverage=average_evidence_coverage,
        unsupported_claim_rate=unsupported_claim_rate,
        average_tool_calls=average_tool_calls,
        average_reasoning_steps=average_reasoning_steps,
    )


def _ratio(numerator: int, denominator: int) -> float:
    if denominator == 0:
        return 0.0

    return numerator / denominator