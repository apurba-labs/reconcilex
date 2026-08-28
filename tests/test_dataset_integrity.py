from reconcilex.domain.case_input_loader import load_case_input, load_case_inputs
from reconcilex.domain.record_loader import PaymentRecordStore

def test_every_observable_record_has_known_case_id():
    store = PaymentRecordStore("data/records")

    all_records = [
        *store.invoices,
        *store.gateway_events,
        *store.webhook_events,
        *store.settlements,
        *store.refunds,
        *store.audit_events,
    ]

    for record in all_records:
        assert record.case_id.startswith("PAY-")


def test_pay_001_has_observable_evidence():
    store = PaymentRecordStore("data/records")

    assert any(
        invoice.case_id == "PAY-001"
        for invoice in store.invoices
    )

    assert any(
        event.case_id == "PAY-001"
        for event in store.gateway_events
    )

    assert any(
        event.case_id == "PAY-001"
        for event in store.webhook_events
    )

    assert any(
        event.case_id == "PAY-001"
        for event in store.audit_events
    )
    
def test_pay_002_contains_duplicate_capture():
    store = PaymentRecordStore("data/records")

    events = [
        event
        for event in store.gateway_events
        if event.case_id == "PAY-002"
        and event.event_type.value == "payment_captured"
    ]

    assert len(events) == 2
    assert events[0].amount == events[1].amount


def test_pay_003_contains_full_refund():
    store = PaymentRecordStore("data/records")

    invoice = next(
        invoice
        for invoice in store.invoices
        if invoice.case_id == "PAY-003"
    )

    refund = next(
        refund
        for refund in store.refunds
        if refund.case_id == "PAY-003"
    )

    assert refund.amount == invoice.amount
    assert invoice.status.value == "paid"


def test_pay_004_contains_refund_amount_disagreement():
    store = PaymentRecordStore("data/records")

    refund = next(
        refund
        for refund in store.refunds
        if refund.case_id == "PAY-004"
    )

    audit = next(
        event
        for event in store.audit_events
        if event.case_id == "PAY-004"
        and event.event_type == "internal_refund_recorded"
    )

    assert refund.amount == 250

    assert audit.reason is not None
    assert "200.00" in audit.reason

def test_pay_005_chargeback_occurs_after_settlement():
    store = PaymentRecordStore("data/records")

    chargeback = next(
        event
        for event in store.gateway_events
        if event.case_id == "PAY-005"
        and event.event_type.value == "chargeback_created"
    )

    settlement = next(
        settlement
        for settlement in store.settlements
        if settlement.case_id == "PAY-005"
    )

    assert settlement.settled_at is not None
    assert chargeback.occurred_at > settlement.settled_at
    
def test_pay_006_has_authorization_without_capture():
    store = PaymentRecordStore("data/records")

    events = [
        event
        for event in store.gateway_events
        if event.case_id == "PAY-006"
    ]

    event_types = {event.event_type.value for event in events}

    assert "payment_authorized" in event_types
    assert "payment_captured" not in event_types


def test_pay_007_settlement_window_has_expired():
    store = PaymentRecordStore("data/records")

    settlement = next(
        settlement
        for settlement in store.settlements
        if settlement.case_id == "PAY-007"
    )

    assert settlement.expected_by is not None
    assert settlement.settled_at is None


def test_pay_008_contains_currency_mismatch():
    store = PaymentRecordStore("data/records")

    invoice = next(
        invoice
        for invoice in store.invoices
        if invoice.case_id == "PAY-008"
    )

    payment = next(
        event
        for event in store.gateway_events
        if event.case_id == "PAY-008"
        and event.event_type.value == "payment_captured"
    )

    assert invoice.amount == payment.amount
    assert invoice.currency != payment.currency
    
def test_pay_009_payment_points_to_wrong_invoice():
    store = PaymentRecordStore("data/records")

    payment = next(
        event
        for event in store.gateway_events
        if event.case_id == "PAY-009"
        and event.event_type.value == "payment_captured"
    )

    intended_invoice = next(
        invoice
        for invoice in store.invoices
        if invoice.invoice_id == "INV-1009"
    )

    assert payment.invoice_reference != intended_invoice.invoice_id

    referenced_invoice = next(
        invoice
        for invoice in store.invoices
        if invoice.invoice_id == payment.invoice_reference
    )

    assert referenced_invoice.status.value == "paid"
    assert intended_invoice.status.value == "unpaid"


def test_pay_010_contains_duplicate_webhook_delivery():
    store = PaymentRecordStore("data/records")

    webhooks = [
        event
        for event in store.webhook_events
        if event.case_id == "PAY-010"
    ]

    assert len(webhooks) == 2
    assert webhooks[0].webhook_id == webhooks[1].webhook_id
    assert webhooks[0].gateway_event_id == webhooks[1].gateway_event_id


def test_pay_011_is_still_inside_settlement_window():
    from reconcilex.domain.case_input_loader import load_case_input

    store = PaymentRecordStore("data/records")

    case_input = load_case_input(
        "data/inputs/cases.json",
        "PAY-011",
    )

    settlement = next(
        settlement
        for settlement in store.settlements
        if settlement.case_id == "PAY-011"
    )

    assert settlement.expected_by is not None
    assert settlement.settled_at is None
    assert case_input.observed_at < settlement.expected_by


def test_pay_012_remains_ambiguous():
    store = PaymentRecordStore("data/records")

    payment = next(
        event
        for event in store.gateway_events
        if event.case_id == "PAY-012"
    )

    webhook = next(
        event
        for event in store.webhook_events
        if event.case_id == "PAY-012"
    )

    audits = [
        event
        for event in store.audit_events
        if event.case_id == "PAY-012"
    ]

    assert payment.invoice_reference != "INV-1012"
    assert webhook.http_status == 500
    assert webhook.processing_status == "failed"

    assert audits == []
    
def test_every_case_has_case_input_and_observable_invoice():
    store = PaymentRecordStore("data/records")
    case_inputs = load_case_inputs("data/inputs/cases.json")

    input_case_ids = {case.case_id for case in case_inputs}
    invoice_case_ids = {invoice.case_id for invoice in store.invoices}

    expected_case_ids = {
        f"PAY-{number:03d}"
        for number in range(1, 13)
    }

    assert input_case_ids == expected_case_ids
    assert expected_case_ids <= invoice_case_ids


def test_every_known_payment_id_has_gateway_evidence():
    store = PaymentRecordStore("data/records")
    case_inputs = load_case_inputs("data/inputs/cases.json")

    gateway_payment_ids = {
        event.payment_id
        for event in store.gateway_events
    }

    for case in case_inputs:
        if case.known_payment_id is not None:
            assert case.known_payment_id in gateway_payment_ids


def test_all_record_case_ids_are_known():
    store = PaymentRecordStore("data/records")
    case_inputs = load_case_inputs("data/inputs/cases.json")

    known_case_ids = {
        case.case_id
        for case in case_inputs
    }

    all_records = [
        *store.invoices,
        *store.gateway_events,
        *store.webhook_events,
        *store.settlements,
        *store.refunds,
        *store.audit_events,
    ]

    for record in all_records:
        assert record.case_id in known_case_ids


def test_pay_007_is_overdue_at_observation_time():
    store = PaymentRecordStore("data/records")
    case_input = load_case_input(
        "data/inputs/cases.json",
        "PAY-007",
    )

    settlement = next(
        settlement
        for settlement in store.settlements
        if settlement.case_id == "PAY-007"
    )

    assert settlement.expected_by is not None
    assert settlement.settled_at is None
    assert case_input.observed_at > settlement.expected_by


def test_pay_011_is_not_overdue_at_observation_time():
    store = PaymentRecordStore("data/records")
    case_input = load_case_input(
        "data/inputs/cases.json",
        "PAY-011",
    )

    settlement = next(
        settlement
        for settlement in store.settlements
        if settlement.case_id == "PAY-011"
    )

    assert settlement.expected_by is not None
    assert settlement.settled_at is None
    assert case_input.observed_at < settlement.expected_by


def test_pay_012_has_no_decisive_audit_evidence():
    store = PaymentRecordStore("data/records")

    audits = [
        event
        for event in store.audit_events
        if event.case_id == "PAY-012"
    ]

    assert audits == []