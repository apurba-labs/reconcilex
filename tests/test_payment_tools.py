from reconcilex.domain.record_loader import PaymentRecordStore
from reconcilex.tools.payment_tools import PaymentTools


def make_tools() -> PaymentTools:
    store = PaymentRecordStore("data/records")
    return PaymentTools(store)


def test_get_case_context():
    tools = make_tools()

    context = tools.get_case_context("PAY-001")

    assert context["invoice_ids"] == ["INV-1001"]
    assert context["payment_ids"] == ["PI-1001"]


def test_get_invoice():
    tools = make_tools()

    invoice = tools.get_invoice("INV-1001")

    assert invoice is not None
    assert invoice["status"] == "unpaid"
    assert invoice["amount"] == "500.00"


def test_get_gateway_events():
    tools = make_tools()

    events = tools.get_gateway_events("PI-1001")

    assert len(events) == 2
    assert events[-1]["event_type"] == "payment_captured"


def test_get_failed_webhook():
    tools = make_tools()

    events = tools.get_webhook_events("PI-1001")

    assert len(events) == 1
    assert events[0]["http_status"] == 500
    assert events[0]["processing_status"] == "failed"


def test_get_payment_timeline_is_ordered():
    tools = make_tools()

    timeline = tools.get_payment_timeline("PI-1001")

    assert len(timeline) == 3

    timestamps = [
        event["timestamp"]
        for event in timeline
    ]

    assert timestamps == sorted(timestamps)


def test_tools_do_not_expose_benchmark_truth():
    tools = make_tools()

    context = tools.get_case_context("PAY-001")

    forbidden_fields = {
        "expected_root_cause",
        "required_evidence",
        "misleading_evidence",
        "allowed_actions",
        "prohibited_actions",
        "divergence_stage",
    }

    assert forbidden_fields.isdisjoint(context.keys())