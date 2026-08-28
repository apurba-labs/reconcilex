from decimal import Decimal
from reconcilex.domain.record_loader import PaymentRecordStore

def test_load_payment_records():
    store = PaymentRecordStore("data/records")

    assert store.invoices
    assert store.gateway_events
    assert store.webhook_events
    assert store.settlements
    assert store.audit_events

    assert isinstance(store.refunds, list)

def test_pay_001_invoice_amount_uses_decimal():
    store = PaymentRecordStore("data/records")

    invoice = store.invoices[0]

    assert invoice.amount == Decimal("500.00")

def test_pay_001_contains_successful_capture():
    store = PaymentRecordStore("data/records")

    captured = [
        event
        for event in store.gateway_events
        if event.case_id == "PAY-001"
        and event.event_type.value == "payment_captured"
    ]

    assert len(captured) == 1
    assert captured[0].payment_id == "PI-1001"
    assert captured[0].invoice_reference == "INV-1001"
    assert captured[0].amount == 500

def test_pay_001_contains_failed_webhook():
    store = PaymentRecordStore("data/records")

    webhook = store.webhook_events[0]

    assert webhook.http_status == 500
    assert webhook.processing_status == "failed"