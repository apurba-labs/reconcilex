from reconcilex.domain.case_input_loader import (
    load_case_input,
    load_case_inputs,
)

def test_load_all_case_inputs():
    cases = load_case_inputs("data/inputs/cases.json")

    assert len(cases) == 12


def test_case_inputs_are_sequential():
    cases = load_case_inputs("data/inputs/cases.json")

    assert [case.case_id for case in cases] == [
        f"PAY-{number:03d}"
        for number in range(1, 13)
    ]


def test_case_input_does_not_expose_ground_truth():
    case = load_case_input(
        "data/inputs/cases.json",
        "PAY-001",
    )

    dumped = case.model_dump()

    forbidden = {
        "expected_root_cause",
        "divergence_stage",
        "required_evidence",
        "allowed_actions",
        "prohibited_actions",
    }

    assert forbidden.isdisjoint(dumped.keys())