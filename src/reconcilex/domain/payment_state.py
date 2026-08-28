from enum import Enum

class PaymentState(str, Enum):
    INVOICE_CREATED = "invoice_created"
    PAYMENT_INITIATED = "payment_initiated"
    AUTHORIZED = "authorized"
    CAPTURED = "captured"
    WEBHOOK_RECEIVED = "webhook_received"
    PAYMENT_RECORDED = "payment_recorded"
    INVOICE_PAID = "invoice_paid"
    SETTLED = "settled"


PAYMENT_LIFECYCLE = [
    PaymentState.INVOICE_CREATED,
    PaymentState.PAYMENT_INITIATED,
    PaymentState.AUTHORIZED,
    PaymentState.CAPTURED,
    PaymentState.WEBHOOK_RECEIVED,
    PaymentState.PAYMENT_RECORDED,
    PaymentState.INVOICE_PAID,
    PaymentState.SETTLED,
]