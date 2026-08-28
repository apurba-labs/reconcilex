import json
from pathlib import Path

OUTPUT_DIR = Path("data/records")

def write_json(filename: str, records: list[dict]) -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    path = OUTPUT_DIR / filename
    path.write_text(
        json.dumps(records, indent=2),
        encoding="utf-8",
    )


def build_dataset() -> dict[str, list[dict]]:
    invoices: list[dict] = []
    gateway_events: list[dict] = []
    webhook_events: list[dict] = []
    settlements: list[dict] = []
    refunds: list[dict] = []
    audit_events: list[dict] = []

    # PAY-001
    invoices.append(
        {
            "invoice_id": "INV-1001",
            "case_id": "PAY-001",
            "customer_id": "CUS-001",
            "amount": "500.00",
            "currency": "USD",
            "status": "unpaid",
            "created_at": "2026-08-20T10:00:00Z",
            "updated_at": "2026-08-20T10:05:00Z",
        }
    )

    gateway_events.extend(
        [
            {
                "event_id": "GE-1001",
                "case_id": "PAY-001",
                "payment_id": "PI-1001",
                "invoice_reference": "INV-1001",
                "event_type": "payment_authorized",
                "amount": "500.00",
                "currency": "USD",
                "occurred_at": "2026-08-20T10:02:00Z",
            },
            {
                "event_id": "GE-1002",
                "case_id": "PAY-001",
                "payment_id": "PI-1001",
                "invoice_reference": "INV-1001",
                "event_type": "payment_captured",
                "amount": "500.00",
                "currency": "USD",
                "occurred_at": "2026-08-20T10:03:00Z",
            },
        ]
    )

    webhook_events.append(
        {
            "webhook_id": "WH-1001",
            "case_id": "PAY-001",
            "gateway_event_id": "GE-1002",
            "payment_id": "PI-1001",
            "event_type": "payment.captured",
            "http_status": 500,
            "processing_status": "failed",
            "occurred_at": "2026-08-20T10:03:05Z",
        }
    )

    settlements.append(
        {
            "settlement_id": "SET-1001",
            "case_id": "PAY-001",
            "payment_id": "PI-1001",
            "gross_amount": "500.00",
            "net_amount": "485.00",
            "currency": "USD",
            "status": "pending",
            "expected_by": "2026-08-22T23:59:59Z",
            "settled_at": None,
        }
    )

    audit_events.append(
        {
            "audit_id": "AUD-1001",
            "case_id": "PAY-001",
            "entity_type": "invoice",
            "entity_id": "INV-1001",
            "event_type": "payment_webhook_processing",
            "result": "failed",
            "reason": "upstream_invoice_service_http_500",
            "occurred_at": "2026-08-20T10:03:06Z",
        }
    )
    
    # PAY-002
    invoices.append(
        {
            "invoice_id": "INV-1002",
            "case_id": "PAY-002",
            "customer_id": "CUS-002",
            "amount": "300.00",
            "currency": "USD",
            "status": "paid",
            "created_at": "2026-08-20T11:00:00Z",
            "updated_at": "2026-08-20T11:07:00Z",
        }
    )

    gateway_events.extend(
        [
            {
                "event_id": "GE-2001",
                "case_id": "PAY-002",
                "payment_id": "PI-1002",
                "invoice_reference": "INV-1002",
                "event_type": "payment_captured",
                "amount": "300.00",
                "currency": "USD",
                "occurred_at": "2026-08-20T11:03:00Z",
            },
            {
                "event_id": "GE-2002",
                "case_id": "PAY-002",
                "payment_id": "PI-1002",
                "invoice_reference": "INV-1002",
                "event_type": "payment_captured",
                "amount": "300.00",
                "currency": "USD",
                "occurred_at": "2026-08-20T11:03:08Z",
            },
        ]
    )

    webhook_events.extend(
        [
            {
                "webhook_id": "WH-2001",
                "case_id": "PAY-002",
                "gateway_event_id": "GE-2001",
                "payment_id": "PI-1002",
                "event_type": "payment.captured",
                "http_status": 200,
                "processing_status": "processed",
                "occurred_at": "2026-08-20T11:03:02Z",
            },
            {
                "webhook_id": "WH-2002",
                "case_id": "PAY-002",
                "gateway_event_id": "GE-2002",
                "payment_id": "PI-1002",
                "event_type": "payment.captured",
                "http_status": 200,
                "processing_status": "processed",
                "occurred_at": "2026-08-20T11:03:10Z",
            },
        ]
    )

    settlements.append(
        {
            "settlement_id": "SET-2001",
            "case_id": "PAY-002",
            "payment_id": "PI-1002",
            "gross_amount": "600.00",
            "net_amount": "582.00",
            "currency": "USD",
            "status": "settled",
            "expected_by": "2026-08-22T23:59:59Z",
            "settled_at": "2026-08-21T09:00:00Z",
        }
    )

    audit_events.append(
        {
            "audit_id": "AUD-2001",
            "case_id": "PAY-002",
            "entity_type": "invoice",
            "entity_id": "INV-1002",
            "event_type": "payment_application",
            "result": "processed",
            "reason": "invoice_marked_paid_after_first_capture",
            "occurred_at": "2026-08-20T11:03:03Z",
        }
    )

    # PAY-003
    invoices.append(
        {
            "invoice_id": "INV-1003",
            "case_id": "PAY-003",
            "customer_id": "CUS-003",
            "amount": "450.00",
            "currency": "USD",
            "status": "paid",
            "created_at": "2026-08-18T09:00:00Z",
            "updated_at": "2026-08-18T09:10:00Z",
        }
    )

    gateway_events.append(
        {
            "event_id": "GE-3001",
            "case_id": "PAY-003",
            "payment_id": "PI-1003",
            "invoice_reference": "INV-1003",
            "event_type": "payment_captured",
            "amount": "450.00",
            "currency": "USD",
            "occurred_at": "2026-08-18T09:05:00Z",
        }
    )

    webhook_events.append(
        {
            "webhook_id": "WH-3001",
            "case_id": "PAY-003",
            "gateway_event_id": "GE-3001",
            "payment_id": "PI-1003",
            "event_type": "payment.captured",
            "http_status": 200,
            "processing_status": "processed",
            "occurred_at": "2026-08-18T09:05:03Z",
        }
    )

    settlements.append(
        {
            "settlement_id": "SET-3001",
            "case_id": "PAY-003",
            "payment_id": "PI-1003",
            "gross_amount": "450.00",
            "net_amount": "436.50",
            "currency": "USD",
            "status": "settled",
            "expected_by": "2026-08-20T23:59:59Z",
            "settled_at": "2026-08-19T08:00:00Z",
        }
    )

    refunds.append(
        {
            "refund_id": "REF-3001",
            "case_id": "PAY-003",
            "payment_id": "PI-1003",
            "invoice_id": "INV-1003",
            "amount": "450.00",
            "currency": "USD",
            "status": "succeeded",
            "created_at": "2026-08-22T14:00:00Z",
        }
    )

    audit_events.append(
        {
            "audit_id": "AUD-3001",
            "case_id": "PAY-003",
            "entity_type": "invoice",
            "entity_id": "INV-1003",
            "event_type": "refund_state_sync",
            "result": "failed",
            "reason": "invoice_status_update_not_applied",
            "occurred_at": "2026-08-22T14:00:05Z",
        }
    )

    # PAY-004
    invoices.append(
        {
            "invoice_id": "INV-1004",
            "case_id": "PAY-004",
            "customer_id": "CUS-004",
            "amount": "800.00",
            "currency": "USD",
            "status": "paid",
            "created_at": "2026-08-17T12:00:00Z",
            "updated_at": "2026-08-17T12:08:00Z",
        }
    )

    gateway_events.append(
        {
            "event_id": "GE-4001",
            "case_id": "PAY-004",
            "payment_id": "PI-1004",
            "invoice_reference": "INV-1004",
            "event_type": "payment_captured",
            "amount": "800.00",
            "currency": "USD",
            "occurred_at": "2026-08-17T12:04:00Z",
        }
    )

    refunds.append(
        {
            "refund_id": "REF-4001",
            "case_id": "PAY-004",
            "payment_id": "PI-1004",
            "invoice_id": "INV-1004",
            "amount": "250.00",
            "currency": "USD",
            "status": "succeeded",
            "created_at": "2026-08-20T15:00:00Z",
        }
    )

    audit_events.extend(
        [
            {
                "audit_id": "AUD-4001",
                "case_id": "PAY-004",
                "entity_type": "payment",
                "entity_id": "PI-1004",
                "event_type": "internal_refund_recorded",
                "result": "processed",
                "reason": "internal_refund_amount_200.00",
                "occurred_at": "2026-08-20T15:00:02Z",
            },
            {
                "audit_id": "AUD-4002",
                "case_id": "PAY-004",
                "entity_type": "invoice",
                "entity_id": "INV-1004",
                "event_type": "invoice_state_check",
                "result": "processed",
                "reason": "invoice_remains_paid",
                "occurred_at": "2026-08-20T15:00:04Z",
            },
        ]
    )

    # PAY-005
    invoices.append(
        {
            "invoice_id": "INV-1005",
            "case_id": "PAY-005",
            "customer_id": "CUS-005",
            "amount": "1000.00",
            "currency": "USD",
            "status": "paid",
            "created_at": "2026-08-10T08:00:00Z",
            "updated_at": "2026-08-10T08:10:00Z",
        }
    )

    gateway_events.extend(
        [
            {
                "event_id": "GE-5001",
                "case_id": "PAY-005",
                "payment_id": "PI-1005",
                "invoice_reference": "INV-1005",
                "event_type": "payment_captured",
                "amount": "1000.00",
                "currency": "USD",
                "occurred_at": "2026-08-10T08:05:00Z",
            },
            {
                "event_id": "GE-5002",
                "case_id": "PAY-005",
                "payment_id": "PI-1005",
                "invoice_reference": "INV-1005",
                "event_type": "chargeback_created",
                "amount": "1000.00",
                "currency": "USD",
                "occurred_at": "2026-08-25T13:00:00Z",
            },
        ]
    )

    settlements.append(
        {
            "settlement_id": "SET-5001",
            "case_id": "PAY-005",
            "payment_id": "PI-1005",
            "gross_amount": "1000.00",
            "net_amount": "970.00",
            "currency": "USD",
            "status": "settled",
            "expected_by": "2026-08-12T23:59:59Z",
            "settled_at": "2026-08-11T09:00:00Z",
        }
    )

    audit_events.append(
        {
            "audit_id": "AUD-5001",
            "case_id": "PAY-005",
            "entity_type": "invoice",
            "entity_id": "INV-1005",
            "event_type": "chargeback_state_sync",
            "result": "failed",
            "reason": "invoice_status_not_adjusted_after_chargeback",
            "occurred_at": "2026-08-25T13:00:05Z",
        }
    )
    
    # PAY-006
    invoices.append(
        {
            "invoice_id": "INV-1006",
            "case_id": "PAY-006",
            "customer_id": "CUS-006",
            "amount": "275.00",
            "currency": "USD",
            "status": "unpaid",
            "created_at": "2026-08-21T10:00:00Z",
            "updated_at": "2026-08-24T10:00:00Z",
        }
    )

    gateway_events.append(
        {
            "event_id": "GE-6001",
            "case_id": "PAY-006",
            "payment_id": "PI-1006",
            "invoice_reference": "INV-1006",
            "event_type": "payment_authorized",
            "amount": "275.00",
            "currency": "USD",
            "occurred_at": "2026-08-21T10:05:00Z",
        }
    )

    audit_events.append(
        {
            "audit_id": "AUD-6001",
            "case_id": "PAY-006",
            "entity_type": "payment",
            "entity_id": "PI-1006",
            "event_type": "authorization_expired",
            "result": "failed",
            "reason": "authorization_expired_before_capture",
            "occurred_at": "2026-08-24T10:05:00Z",
        }
    )

    # PAY-007
    invoices.append(
        {
            "invoice_id": "INV-1007",
            "case_id": "PAY-007",
            "customer_id": "CUS-007",
            "amount": "620.00",
            "currency": "USD",
            "status": "paid",
            "created_at": "2026-08-19T09:00:00Z",
            "updated_at": "2026-08-19T09:10:00Z",
        }
    )

    gateway_events.append(
        {
            "event_id": "GE-7001",
            "case_id": "PAY-007",
            "payment_id": "PI-1007",
            "invoice_reference": "INV-1007",
            "event_type": "payment_captured",
            "amount": "620.00",
            "currency": "USD",
            "occurred_at": "2026-08-19T09:05:00Z",
        }
    )

    settlements.append(
        {
            "settlement_id": "SET-7001",
            "case_id": "PAY-007",
            "payment_id": "PI-1007",
            "gross_amount": "620.00",
            "net_amount": "601.40",
            "currency": "USD",
            "status": "pending",
            "expected_by": "2026-08-22T23:59:59Z",
            "settled_at": None,
        }
    )

    audit_events.append(
        {
            "audit_id": "AUD-7001",
            "case_id": "PAY-007",
            "entity_type": "payment",
            "entity_id": "PI-1007",
            "event_type": "settlement_status_check",
            "result": "pending",
            "reason": "payment_absent_from_settlement_after_expected_window",
            "occurred_at": "2026-08-25T11:00:00Z",
        }
    )

    # PAY-008
    invoices.append(
        {
            "invoice_id": "INV-1008",
            "case_id": "PAY-008",
            "customer_id": "CUS-008",
            "amount": "1200.00",
            "currency": "EUR",
            "status": "unpaid",
            "created_at": "2026-08-23T14:00:00Z",
            "updated_at": "2026-08-23T14:06:00Z",
        }
    )

    gateway_events.append(
        {
            "event_id": "GE-8001",
            "case_id": "PAY-008",
            "payment_id": "PI-1008",
            "invoice_reference": "INV-1008",
            "event_type": "payment_captured",
            "amount": "1200.00",
            "currency": "USD",
            "occurred_at": "2026-08-23T14:03:00Z",
        }
    )

    webhook_events.append(
        {
            "webhook_id": "WH-8001",
            "case_id": "PAY-008",
            "gateway_event_id": "GE-8001",
            "payment_id": "PI-1008",
            "event_type": "payment.captured",
            "http_status": 200,
            "processing_status": "processed",
            "occurred_at": "2026-08-23T14:03:04Z",
        }
    )

    settlements.append(
        {
            "settlement_id": "SET-8001",
            "case_id": "PAY-008",
            "payment_id": "PI-1008",
            "gross_amount": "1200.00",
            "net_amount": "1164.00",
            "currency": "USD",
            "status": "settled",
            "expected_by": "2026-08-25T23:59:59Z",
            "settled_at": "2026-08-24T09:00:00Z",
        }
    )

    audit_events.extend(
        [
            {
                "audit_id": "AUD-8001",
                "case_id": "PAY-008",
                "entity_type": "payment",
                "entity_id": "PI-1008",
                "event_type": "payment_received",
                "result": "processed",
                "reason": "gateway_capture_received_successfully",
                "occurred_at": "2026-08-23T14:03:05Z",
            },
            {
                "audit_id": "AUD-8002",
                "case_id": "PAY-008",
                "entity_type": "invoice",
                "entity_id": "INV-1008",
                "event_type": "payment_application",
                "result": "failed",
                "reason": "currency_mismatch_invoice_EUR_payment_USD",
                "occurred_at": "2026-08-23T14:03:06Z",
            },
        ]
    )
    
    # PAY-009
    invoices.extend(
        [
            {
                "invoice_id": "INV-1009",
                "case_id": "PAY-009",
                "customer_id": "CUS-009",
                "amount": "350.00",
                "currency": "USD",
                "status": "unpaid",
                "created_at": "2026-08-21T09:00:00Z",
                "updated_at": "2026-08-21T09:10:00Z",
            },
            {
                "invoice_id": "INV-1909",
                "case_id": "PAY-009",
                "customer_id": "CUS-099",
                "amount": "350.00",
                "currency": "USD",
                "status": "paid",
                "created_at": "2026-08-21T08:30:00Z",
                "updated_at": "2026-08-21T09:06:00Z",
            },
        ]
    )

    gateway_events.append(
        {
            "event_id": "GE-9001",
            "case_id": "PAY-009",
            "payment_id": "PI-1009",
            "invoice_reference": "INV-1909",
            "event_type": "payment_captured",
            "amount": "350.00",
            "currency": "USD",
            "occurred_at": "2026-08-21T09:05:00Z",
        }
    )

    webhook_events.append(
        {
            "webhook_id": "WH-9001",
            "case_id": "PAY-009",
            "gateway_event_id": "GE-9001",
            "payment_id": "PI-1009",
            "event_type": "payment.captured",
            "http_status": 200,
            "processing_status": "processed",
            "occurred_at": "2026-08-21T09:05:03Z",
        }
    )

    audit_events.extend(
        [
            {
                "audit_id": "AUD-9001",
                "case_id": "PAY-009",
                "entity_type": "payment",
                "entity_id": "PI-1009",
                "event_type": "payment_reference_resolved",
                "result": "processed",
                "reason": "gateway_reference_resolved_to_INV-1909",
                "occurred_at": "2026-08-21T09:05:04Z",
            },
            {
                "audit_id": "AUD-9002",
                "case_id": "PAY-009",
                "entity_type": "invoice",
                "entity_id": "INV-1909",
                "event_type": "payment_application",
                "result": "processed",
                "reason": "payment_applied_to_referenced_invoice",
                "occurred_at": "2026-08-21T09:05:05Z",
            },
        ]
    )

    # PAY-010
    invoices.append(
        {
            "invoice_id": "INV-1010",
            "case_id": "PAY-010",
            "customer_id": "CUS-010",
            "amount": "525.00",
            "currency": "USD",
            "status": "paid",
            "created_at": "2026-08-22T10:00:00Z",
            "updated_at": "2026-08-22T10:07:00Z",
        }
    )

    gateway_events.append(
        {
            "event_id": "GE-10001",
            "case_id": "PAY-010",
            "payment_id": "PI-1010",
            "invoice_reference": "INV-1010",
            "event_type": "payment_captured",
            "amount": "525.00",
            "currency": "USD",
            "occurred_at": "2026-08-22T10:04:00Z",
        }
    )

    webhook_events.extend(
        [
            {
                "webhook_id": "WH-1010",
                "case_id": "PAY-010",
                "gateway_event_id": "GE-10001",
                "payment_id": "PI-1010",
                "event_type": "payment.captured",
                "http_status": 200,
                "processing_status": "processed",
                "occurred_at": "2026-08-22T10:04:03Z",
            },
            {
                "webhook_id": "WH-1010",
                "case_id": "PAY-010",
                "gateway_event_id": "GE-10001",
                "payment_id": "PI-1010",
                "event_type": "payment.captured",
                "http_status": 200,
                "processing_status": "processed",
                "occurred_at": "2026-08-22T10:04:08Z",
            },
        ]
    )

    audit_events.extend(
        [
            {
                "audit_id": "AUD-10001",
                "case_id": "PAY-010",
                "entity_type": "invoice",
                "entity_id": "INV-1010",
                "event_type": "payment_application",
                "result": "processed",
                "reason": "payment_effect_applied",
                "occurred_at": "2026-08-22T10:04:04Z",
            },
            {
                "audit_id": "AUD-10002",
                "case_id": "PAY-010",
                "entity_type": "invoice",
                "entity_id": "INV-1010",
                "event_type": "payment_application",
                "result": "processed",
                "reason": "duplicate_payment_effect_applied",
                "occurred_at": "2026-08-22T10:04:09Z",
            },
        ]
    )

    # PAY-011
    invoices.append(
        {
            "invoice_id": "INV-1011",
            "case_id": "PAY-011",
            "customer_id": "CUS-011",
            "amount": "410.00",
            "currency": "USD",
            "status": "paid",
            "created_at": "2026-08-24T08:00:00Z",
            "updated_at": "2026-08-24T08:08:00Z",
        }
    )

    gateway_events.append(
        {
            "event_id": "GE-11001",
            "case_id": "PAY-011",
            "payment_id": "PI-1011",
            "invoice_reference": "INV-1011",
            "event_type": "payment_captured",
            "amount": "410.00",
            "currency": "USD",
            "occurred_at": "2026-08-24T08:04:00Z",
        }
    )

    webhook_events.append(
        {
            "webhook_id": "WH-11001",
            "case_id": "PAY-011",
            "gateway_event_id": "GE-11001",
            "payment_id": "PI-1011",
            "event_type": "payment.captured",
            "http_status": 200,
            "processing_status": "processed",
            "occurred_at": "2026-08-24T08:04:03Z",
        }
    )

    settlements.append(
        {
            "settlement_id": "SET-11001",
            "case_id": "PAY-011",
            "payment_id": "PI-1011",
            "gross_amount": "410.00",
            "net_amount": "397.70",
            "currency": "USD",
            "status": "pending",
            "expected_by": "2026-08-27T23:59:59Z",
            "settled_at": None,
        }
    )

    audit_events.append(
        {
            "audit_id": "AUD-11001",
            "case_id": "PAY-011",
            "entity_type": "payment",
            "entity_id": "PI-1011",
            "event_type": "settlement_status_check",
            "result": "pending",
            "reason": "settlement_still_within_expected_window",
            "occurred_at": "2026-08-25T11:00:00Z",
        }
    )

    # PAY-012
    invoices.append(
        {
            "invoice_id": "INV-1012",
            "case_id": "PAY-012",
            "customer_id": "CUS-012",
            "amount": "690.00",
            "currency": "USD",
            "status": "unpaid",
            "created_at": "2026-08-23T15:00:00Z",
            "updated_at": "2026-08-23T15:10:00Z",
        }
    )

    gateway_events.append(
        {
            "event_id": "GE-12001",
            "case_id": "PAY-012",
            "payment_id": "PI-1012",
            "invoice_reference": "INV-9912",
            "event_type": "payment_captured",
            "amount": "690.00",
            "currency": "USD",
            "occurred_at": "2026-08-23T15:05:00Z",
        }
    )

    webhook_events.append(
        {
            "webhook_id": "WH-12001",
            "case_id": "PAY-012",
            "gateway_event_id": "GE-12001",
            "payment_id": "PI-1012",
            "event_type": "payment.captured",
            "http_status": 500,
            "processing_status": "failed",
            "occurred_at": "2026-08-23T15:05:04Z",
        }
    )

    settlements.append(
        {
            "settlement_id": "SET-12001",
            "case_id": "PAY-012",
            "payment_id": "PI-1012",
            "gross_amount": "690.00",
            "net_amount": "669.30",
            "currency": "USD",
            "status": "pending",
            "expected_by": "2026-08-26T23:59:59Z",
            "settled_at": None,
        }
    )


    return {
        "invoices.json": invoices,
        "gateway_events.json": gateway_events,
        "webhook_events.json": webhook_events,
        "settlements.json": settlements,
        "refunds.json": refunds,
        "audit_events.json": audit_events,
    }


def main() -> None:
    dataset = build_dataset()

    for filename, records in dataset.items():
        write_json(filename, records)

    print("Synthetic ReconcileX dataset generated.")
    for filename, records in dataset.items():
        print(f"{filename}: {len(records)} records")


if __name__ == "__main__":
    main()