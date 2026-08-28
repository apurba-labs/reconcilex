from reconcilex.domain.case_loader import load_case

def test_load_benchmark_case():
    case = load_case("data/cases/PAY-001.yaml")

    assert case.case_id == "PAY-001"
    assert case.expected_root_cause == "webhook_processing_failure"
    assert "gateway_payment_captured" in case.required_evidence
    assert case.requires_human_approval is True