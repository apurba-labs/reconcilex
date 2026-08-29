from reconcilex.domain.case_input_loader import load_case_input
from reconcilex.domain.record_loader import PaymentRecordStore
from reconcilex.investigator.investigator import Investigator
from reconcilex.investigator.models import HypothesisStatus
from reconcilex.investigator.verifier import EvidenceVerifier
from reconcilex.tools.payment_tools import PaymentTools


def build_investigator() -> Investigator:
    store = PaymentRecordStore("data/records")

    return Investigator(
        tools=PaymentTools(store),
        verifier=EvidenceVerifier(store),
    )


def test_pay_008_rejects_webhook_failure_hypothesis():
    investigator = build_investigator()

    case_input = load_case_input(
        "data/inputs/cases.json",
        "PAY-008",
    )

    result = investigator.investigate(case_input)

    webhook_hypothesis = next(
        hypothesis
        for hypothesis in result.hypotheses
        if hypothesis.hypothesis_id == "H-001"
    )

    assert webhook_hypothesis.status == HypothesisStatus.REJECTED
    assert len(webhook_hypothesis.contradicting_evidence) == 1


def test_pay_008_supports_currency_mismatch_hypothesis():
    investigator = build_investigator()

    case_input = load_case_input(
        "data/inputs/cases.json",
        "PAY-008",
    )

    result = investigator.investigate(case_input)

    currency_hypothesis = next(
        hypothesis
        for hypothesis in result.hypotheses
        if hypothesis.hypothesis_id == "H-002"
    )

    assert currency_hypothesis.status == HypothesisStatus.SUPPORTED
    assert len(currency_hypothesis.supporting_evidence) == 3


def test_pay_008_identifies_first_divergence():
    investigator = build_investigator()

    case_input = load_case_input(
        "data/inputs/cases.json",
        "PAY-008",
    )

    result = investigator.investigate(case_input)

    assert result.root_cause == "currency_mismatch"
    assert result.first_divergence == "payment_recorded"
    assert result.abstained is False


def test_pay_008_requires_human_control_for_action():
    investigator = build_investigator()

    case_input = load_case_input(
        "data/inputs/cases.json",
        "PAY-008",
    )

    result = investigator.investigate(case_input)

    assert result.requires_human_approval is True
    assert "currency" in result.recommended_action.lower()


def test_pay_008_final_evidence_is_verifiable():
    store = PaymentRecordStore("data/records")
    verifier = EvidenceVerifier(store)

    investigator = Investigator(
        tools=PaymentTools(store),
        verifier=verifier,
    )

    case_input = load_case_input(
        "data/inputs/cases.json",
        "PAY-008",
    )

    result = investigator.investigate(case_input)

    assert result.evidence

    for evidence in result.evidence:
        verification = verifier.verify(evidence)
        assert verification.verified is True