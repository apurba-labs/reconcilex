from datetime import datetime, timezone

from reconcilex.domain.record_loader import PaymentRecordStore
from reconcilex.investigator.models import (
    EvidenceRef, 
    EvidenceAssertion, 
    EvidenceSource 
)
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
    
def test_structured_gateway_evidence_is_verified():
    verifier = build_verifier()

    evidence = EvidenceRef(
        source="gateway_event",
        record_id="GE-8001",
        claim="Gateway payment was recorded in USD.",
        assertions=[
            EvidenceAssertion(
                field="currency",
                operator="eq",
                value="USD",
            )
        ],
    )

    result = verifier.verify(evidence)

    assert result.verified is True


def test_structured_audit_evidence_is_verified():
    verifier = build_verifier()

    evidence = EvidenceRef(
        source="audit_event",
        record_id="AUD-8002",
        claim="Payment application failed because of currency mismatch.",
        assertions=[
            EvidenceAssertion(
                field="result",
                operator="eq",
                value="failed",
            ),
            EvidenceAssertion(
                field="reason",
                operator="eq",
                value="currency_mismatch_invoice_EUR_payment_USD",
            ),
        ],
    )

    result = verifier.verify(evidence)

    assert result.verified is True


def test_structured_assertion_rejects_false_value():
    verifier = build_verifier()

    evidence = EvidenceRef(
        source="gateway_event",
        record_id="GE-8001",
        claim="Gateway payment was recorded in EUR.",
        assertions=[
            EvidenceAssertion(
                field="currency",
                operator="eq",
                value="EUR",
            )
        ],
    )

    result = verifier.verify(evidence)

    assert result.verified is False
    assert "actual value was 'USD'" in result.reason
    
    
def test_verifies_structured_gateway_assertion():
    verifier = build_verifier()
    evidence = EvidenceRef(
        source=EvidenceSource.GATEWAY_EVENT,
        record_id="GE-8001",
        claim="Gateway payment was captured in USD.",
        assertions=[
            EvidenceAssertion(
                field="currency",
                operator="eq",
                value="USD",
            ),
            EvidenceAssertion(
                field="event_type",
                operator="eq",
                value="payment_captured",
            ),
        ],
    )

    result = verifier.verify(evidence)

    assert result.verified is True
    
    
def test_verifies_structured_audit_assertion():
    verifier = build_verifier()
    evidence = EvidenceRef(
        source=EvidenceSource.AUDIT_EVENT,
        record_id="AUD-8002",
        claim="Payment application failed because of currency mismatch.",
        assertions=[
            EvidenceAssertion(
                field="result",
                operator="eq",
                value="failed",
            ),
            EvidenceAssertion(
                field="reason",
                operator="eq",
                value="currency_mismatch_invoice_EUR_payment_USD",
            ),
        ],
    )

    result = verifier.verify(evidence)

    assert result.verified is True

def test_normalize_datetime_and_iso_z_are_equivalent():
    actual = datetime(
        2026,
        8,
        11,
        9,
        0,
        0,
        tzinfo=timezone.utc,
    )

    expected = "2026-08-11T09:00:00Z"

    assert EvidenceVerifier._normalize_value(
        actual
    ) == EvidenceVerifier._normalize_value(
        expected
    )


def test_normalize_non_datetime_string_is_unchanged():
    assert (
        EvidenceVerifier._normalize_value("payment_captured")
        == "payment_captured"
    )
    
def test_normalize_null_string_matches_none():
    assert (
        EvidenceVerifier._normalize_value("null")
        == EvidenceVerifier._normalize_value(None)
    )


def test_normalize_none_string_matches_none():
    assert (
        EvidenceVerifier._normalize_value("None")
        == EvidenceVerifier._normalize_value(None)
    )