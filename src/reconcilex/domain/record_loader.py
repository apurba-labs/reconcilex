import json
from pathlib import Path
from typing import TypeVar

from pydantic import BaseModel

from .records import (
    AuditEvent,
    GatewayEvent,
    InvoiceRecord,
    RefundRecord,
    SettlementRecord,
    WebhookEvent,
)

T = TypeVar("T", bound=BaseModel)

def _load_records(
    path: Path,
    model: type[T],
) -> list[T]:
    with path.open("r", encoding="utf-8") as file:
        raw_records = json.load(file)

    return [
        model.model_validate(record)
        for record in raw_records
    ]


class PaymentRecordStore:
    def __init__(self, directory: str | Path):
        self.directory = Path(directory)

        self.invoices = _load_records(
            self.directory / "invoices.json",
            InvoiceRecord,
        )

        self.gateway_events = _load_records(
            self.directory / "gateway_events.json",
            GatewayEvent,
        )

        self.webhook_events = _load_records(
            self.directory / "webhook_events.json",
            WebhookEvent,
        )

        self.settlements = _load_records(
            self.directory / "settlements.json",
            SettlementRecord,
        )

        self.refunds = _load_records(
            self.directory / "refunds.json",
            RefundRecord,
        )

        self.audit_events = _load_records(
            self.directory / "audit_events.json",
            AuditEvent,
        )