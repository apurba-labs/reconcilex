from __future__ import annotations

from collections.abc import Iterable


ATOMIC_EVIDENCE_ALIASES: dict[str, tuple[str, ...]] = {
    "gateway_payment_captured": (
        "payment_captured",
        "payment captured",
        "gateway captured",
    ),
    "original_payment_captured": (
        "payment_captured",
        "payment captured",
        "original payment captured",
    ),
    "payment_captured": (
        "payment_captured",
        "payment captured",
    ),
    "payment_authorized": (
        "payment_authorized",
        "payment authorized",
    ),
    "authorization_expired": (
        "authorization_expired",
        "authorization expired",
    ),
    "invoice_still_unpaid": (
        "status unpaid",
        "invoice remains unpaid",
        "invoice still unpaid",
    ),
    "invoice_unpaid": (
        "status unpaid",
        "invoice unpaid",
        "invoice remains unpaid",
    ),
    "invoice_still_paid": (
        "status paid",
        "invoice remains paid",
        "invoice still paid",
    ),
    "invoice_marked_paid": (
        "status paid",
        "invoice paid",
        "invoice marked paid",
    ),
    "webhook_http_500": (
        "http_status 500",
        "http 500",
        "webhook failed",
    ),
    "webhook_delivered_successfully": (
        "http_status 200",
        "http 200",
        "delivered successfully",
        "processing_status processed",
    ),
    "payment_received_event": (
        "payment_received",
        "payment received",
    ),
    "payment_application_rejected": (
        "payment_application",
        "payment application failed",
        "currency_mismatch",
    ),
    "full_refund_confirmed": (
        "refund succeeded",
        "refund confirmed",
        "full refund",
    ),
    "gateway_partial_refund": (
        "partial refund",
        "gateway refund",
    ),
    "internal_refund_record": (
        "internal_refund_recorded",
        "internal refund",
    ),
    "settlement_completed": (
        "status settled",
        "settlement completed",
    ),
    "settlement_pending": (
        "status pending",
        "settlement pending",
    ),
    "chargeback_recorded": (
        "chargeback_created",
        "chargeback recorded",
    ),
    "payment_reference": (
        "invoice_reference",
        "payment reference",
        "gateway reference",
    ),
    "intended_invoice_unpaid": (
        "invoice remains unpaid",
        "invoice still unpaid",
        "status eq unpaid",
        "status unpaid",
    ),
}

RELATIONAL_REQUIREMENTS = {
    "two_gateway_captures_same_invoice",
    "identical_capture_amounts",
    "invoice_requires_single_payment",
    "refund_amount_equals_capture_amount",
    "refund_amount_mismatch",
    "invoice_currency_differs_from_payment_currency",
    "payment_attached_to_wrong_invoice",
    "same_webhook_event_id_received_twice",
    "duplicate_internal_processing",
    "duplicated_internal_effect",
    "single_gateway_capture",
    "conflicting_transaction_records",
}

NEGATIVE_REQUIREMENTS = {
    "no_refund",
    "no_refund_for_duplicate_capture",
    "no_capture_event",
    "payment_absent_from_settlement",
    "missing_required_audit_evidence",
}

TEMPORAL_REQUIREMENTS = {
    "settlement_window_elapsed",
    "settlement_window_not_elapsed",
}

def atomic_requirement_satisfied(requirement: str, evidence_text: str) -> bool | None:
    aliases = ATOMIC_EVIDENCE_ALIASES.get(requirement)

    if aliases is None:
        return None

    text = evidence_text.lower()

    return any(
        alias.lower() in text
        for alias in aliases
    )