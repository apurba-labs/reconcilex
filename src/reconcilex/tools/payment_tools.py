from dataclasses import dataclass
from reconcilex.domain.record_loader import PaymentRecordStore

@dataclass
class PaymentTools:
    store: PaymentRecordStore

    def get_invoice(self, invoice_id: str) -> dict | None:
        for invoice in self.store.invoices:
            if invoice.invoice_id == invoice_id:
                return invoice.model_dump(mode="json")

        return None

    def get_gateway_events(self, payment_id: str) -> list[dict]:
        return [
            event.model_dump(mode="json")
            for event in self.store.gateway_events
            if event.payment_id == payment_id
        ]

    def get_webhook_events(self, payment_id: str) -> list[dict]:
        return [
            event.model_dump(mode="json")
            for event in self.store.webhook_events
            if event.payment_id == payment_id
        ]

    def get_settlements(self, payment_id: str) -> list[dict]:
        return [
            settlement.model_dump(mode="json")
            for settlement in self.store.settlements
            if settlement.payment_id == payment_id
        ]

    def get_refunds(self, payment_id: str) -> list[dict]:
        return [
            refund.model_dump(mode="json")
            for refund in self.store.refunds
            if refund.payment_id == payment_id
        ]

    def get_audit_events(
        self,
        entity_id: str,
    ) -> list[dict]:
        return [
            event.model_dump(mode="json")
            for event in self.store.audit_events
            if event.entity_id == entity_id
        ]
        
    def get_case_context(self, case_id: str) -> dict:
        invoices = [
            invoice.model_dump(mode="json")
            for invoice in self.store.invoices
            if invoice.case_id == case_id
        ]

        gateway_events = [
            event.model_dump(mode="json")
            for event in self.store.gateway_events
            if event.case_id == case_id
        ]

        payment_ids = sorted(
            {
                event.payment_id
                for event in self.store.gateway_events
                if event.case_id == case_id
            }
        )

        return {
            "case_id": case_id,
            "invoice_ids": [
                invoice["invoice_id"]
                for invoice in invoices
            ],
            "payment_ids": payment_ids,
        }
        
    def get_payment_timeline(
        self,
        payment_id: str,
    ) -> list[dict]:
        timeline: list[dict] = []

        for event in self.store.gateway_events:
            if event.payment_id == payment_id:
                timeline.append(
                    {
                        "source": "gateway",
                        "event_type": event.event_type.value,
                        "timestamp": event.occurred_at.isoformat(),
                        "record_id": event.event_id,
                    }
                )

        for event in self.store.webhook_events:
            if event.payment_id == payment_id:
                timeline.append(
                    {
                        "source": "webhook",
                        "event_type": event.event_type,
                        "timestamp": event.occurred_at.isoformat(),
                        "record_id": event.webhook_id,
                        "processing_status": event.processing_status,
                        "http_status": event.http_status,
                    }
                )

        for settlement in self.store.settlements:
            if (
                settlement.payment_id == payment_id
                and settlement.settled_at is not None
            ):
                timeline.append(
                    {
                        "source": "settlement",
                        "event_type": "settlement",
                        "timestamp": settlement.settled_at.isoformat(),
                        "record_id": settlement.settlement_id,
                        "status": settlement.status,
                    }
                )

        for refund in self.store.refunds:
            if refund.payment_id == payment_id:
                timeline.append(
                    {
                        "source": "refund",
                        "event_type": "refund",
                        "timestamp": refund.created_at.isoformat(),
                        "record_id": refund.refund_id,
                        "status": refund.status,
                    }
                )

        return sorted(
            timeline,
            key=lambda item: item["timestamp"],
        )