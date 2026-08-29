from reconcilex.domain.record_loader import PaymentRecordStore
from reconcilex.investigator.models import EvidenceRef
from reconcilex.investigator.verifier import EvidenceVerifier


def build_verifier() -> EvidenceVerifier:
    store = PaymentRecordStore("data/records")
    return EvidenceVerifier(store)


def test_verifies_real_failed_webhook_evidence():
    verifier = build_verifier()

    evidence = EvidenceRef(
        source="webhook_event",
        record_id="WH-1001",
        claim="Webhook processing failed with HTTP 500.",
    )

    result = verifier.verify(evidence)

    assert result.verified is True


def test_rejects_missing_record():
    verifier = build_verifier()

    evidence = EvidenceRef(
        source="webhook_event",
        record_id="WH-NOT-REAL",
        claim="Webhook processing failed.",
    )

    result = verifier.verify(evidence)

    assert result.verified is False
    assert "not found" in result.reason.lower()


def test_pay_008_rejects_false_webhook_failure_claim():
    verifier = build_verifier()

    evidence = EvidenceRef(
        source="webhook_event",
        record_id="WH-8001",
        claim="Webhook processing failed.",
    )

    result = verifier.verify(evidence)

    assert result.verified is False
    assert "200" in result.reason
    assert "processed" in result.reason.lower()


def test_pay_008_verifies_successful_webhook_claim():
    verifier = build_verifier()

    evidence = EvidenceRef(
        source="webhook_event",
        record_id="WH-8001",
        claim="Webhook processing succeeded successfully.",
    )

    result = verifier.verify(evidence)

    assert result.verified is True


def test_verifies_unpaid_invoice():
    verifier = build_verifier()

    evidence = EvidenceRef(
        source="invoice",
        record_id="INV-1008",
        claim="Invoice remains unpaid.",
    )

    result = verifier.verify(evidence)

    assert result.verified is True


def test_rejects_false_paid_invoice_claim():
    verifier = build_verifier()

    evidence = EvidenceRef(
        source="invoice",
        record_id="INV-1008",
        claim="Invoice is paid.",
    )

    result = verifier.verify(evidence)

    assert result.verified is False


def test_verifies_gateway_capture():
    verifier = build_verifier()

    evidence = EvidenceRef(
        source="gateway_event",
        record_id="GE-8001",
        claim="Payment was captured successfully.",
    )

    result = verifier.verify(evidence)

    assert result.verified is True


def test_verifies_audit_reason():
    verifier = build_verifier()

    evidence = EvidenceRef(
        source="audit_event",
        record_id="AUD-8002",
        claim=(
            "Payment application failed because "
            "currency_mismatch_invoice_EUR_payment_USD."
        ),
    )

    result = verifier.verify(evidence)

    assert result.verified is True