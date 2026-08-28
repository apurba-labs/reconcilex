from datetime import datetime
from decimal import Decimal
from enum import Enum

from pydantic import BaseModel


class InvoiceStatus(str, Enum):
    UNPAID = "unpaid"
    PAID = "paid"
    REFUNDED = "refunded"
    PARTIALLY_REFUNDED = "partially_refunded"


class GatewayEventType(str, Enum):
    PAYMENT_INITIATED = "payment_initiated"
    PAYMENT_AUTHORIZED = "payment_authorized"
    PAYMENT_CAPTURED = "payment_captured"
    PAYMENT_REFUNDED = "payment_refunded"
    CHARGEBACK_CREATED = "chargeback_created"


class InvoiceRecord(BaseModel):
    invoice_id: str
    case_id: str

    customer_id: str

    amount: Decimal
    currency: str

    status: InvoiceStatus

    created_at: datetime
    updated_at: datetime


class GatewayEvent(BaseModel):
    event_id: str
    case_id: str

    payment_id: str
    invoice_reference: str

    event_type: GatewayEventType

    amount: Decimal
    currency: str

    occurred_at: datetime


class WebhookEvent(BaseModel):
    webhook_id: str
    case_id: str

    gateway_event_id: str
    payment_id: str

    event_type: str

    http_status: int
    processing_status: str

    occurred_at: datetime


class SettlementRecord(BaseModel):
    settlement_id: str
    case_id: str

    payment_id: str

    gross_amount: Decimal
    net_amount: Decimal
    currency: str

    status: str

    expected_by: datetime | None = None
    settled_at: datetime | None = None


class RefundRecord(BaseModel):
    refund_id: str
    case_id: str

    payment_id: str
    invoice_id: str

    amount: Decimal
    currency: str

    status: str

    created_at: datetime


class AuditEvent(BaseModel):
    audit_id: str
    case_id: str

    entity_type: str
    entity_id: str

    event_type: str
    result: str

    reason: str | None = None

    occurred_at: datetime