from reconcilex.domain.case import ExpectedOutcome
from reconcilex.domain.case_loader import load_cases

def test_benchmark_cases_load():
    cases = load_cases("data/cases")

    assert len(cases) == 12

def test_case_ids_are_unique():
    cases = load_cases("data/cases")

    case_ids = [case.case_id for case in cases]

    assert len(case_ids) == len(set(case_ids))

def test_case_ids_are_sequential():
    cases = load_cases("data/cases")

    assert [case.case_id for case in cases] == [
        f"PAY-{number:03d}"
        for number in range(1, 13)
    ]

def test_every_case_has_required_evidence():
    cases = load_cases("data/cases")

    for case in cases:
        assert case.required_evidence, case.case_id


def test_every_reconciliation_case_has_safe_actions():
    cases = load_cases("data/cases")

    for case in cases:
        if case.expected_outcome == ExpectedOutcome.RECONCILIATION_REQUIRED:
            assert case.allowed_actions, case.case_id


def test_negative_control_requires_no_action():
    cases = load_cases("data/cases")

    case = next(
        case
        for case in cases
        if case.case_id == "PAY-011"
    )

    assert case.expected_outcome == ExpectedOutcome.NO_ACTION_REQUIRED
    assert case.expected_root_cause == "no_failure"
    assert case.divergence_stage is None
    assert case.requires_human_approval is False


def test_insufficient_evidence_requires_human_review():
    cases = load_cases("data/cases")

    case = next(
        case
        for case in cases
        if case.case_id == "PAY-012"
    )

    assert case.expected_outcome == ExpectedOutcome.HUMAN_REVIEW_REQUIRED
    assert case.expected_root_cause == "insufficient_evidence"
    assert case.divergence_stage is None
    assert case.requires_human_approval is True