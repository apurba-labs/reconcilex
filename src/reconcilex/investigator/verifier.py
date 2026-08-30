from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any

from pydantic import BaseModel

from reconcilex.domain.record_loader import PaymentRecordStore
from reconcilex.investigator.models import (
    EvidenceAssertion,
    EvidenceRef,
)


class EvidenceVerification(BaseModel):
    source: str
    record_id: str
    verified: bool
    reason: str


class EvidenceVerifier:
    def __init__(self, store: PaymentRecordStore):
        self.store = store

    def verify(
        self,
        evidence: EvidenceRef,
    ) -> EvidenceVerification:
        record = self._find_record(
            source=evidence.source,
            record_id=evidence.record_id,
        )

        if record is None:
            return EvidenceVerification(
                source=evidence.source,
                record_id=evidence.record_id,
                verified=False,
                reason="Referenced evidence record was not found.",
            )

        if evidence.assertions:
            supported, reason = self._assertions_supported(
                record=record,
                assertions=evidence.assertions,
            )
        else:
            supported, reason = self._claim_supported(
                source=evidence.source,
                claim=evidence.claim,
                record=record,
            )

        return EvidenceVerification(
            source=evidence.source,
            record_id=evidence.record_id,
            verified=supported,
            reason=reason,
        )

    def _find_record(
        self,
        source: str,
        record_id: str,
    ) -> Any | None:
        collections = {
            "invoice": (
                self.store.invoices,
                "invoice_id",
            ),
            "gateway_event": (
                self.store.gateway_events,
                "event_id",
            ),
            "webhook_event": (
                self.store.webhook_events,
                "webhook_id",
            ),
            "settlement": (
                self.store.settlements,
                "settlement_id",
            ),
            "refund": (
                self.store.refunds,
                "refund_id",
            ),
            "audit_event": (
                self.store.audit_events,
                "audit_id",
            ),
        }

        collection = collections.get(source)

        if collection is None:
            return None

        records, id_field = collection

        for record in records:
            if getattr(record, id_field) == record_id:
                return record

        return None

    def _assertions_supported(
        self,
        *,
        record: Any,
        assertions: list[EvidenceAssertion],
    ) -> tuple[bool, str]:
        for assertion in assertions:
            supported, reason = self._verify_assertion(
                record=record,
                assertion=assertion,
            )

            if not supported:
                return False, reason

        return (
            True,
            f"Verified {len(assertions)} structured assertion(s).",
        )

    @staticmethod
    def _verify_assertion(
        *,
        record: Any,
        assertion: EvidenceAssertion,
    ) -> tuple[bool, str]:
        if not hasattr(record, assertion.field):
            return (
                False,
                f"Record does not contain field '{assertion.field}'.",
            )

        actual_value = EvidenceVerifier._normalize_value(
            getattr(record, assertion.field)
        )

        expected_value = EvidenceVerifier._normalize_value(
            assertion.value
        )

        if assertion.operator == "eq":
            verified = actual_value == expected_value

        elif assertion.operator == "neq":
            verified = actual_value != expected_value

        else:
            return (
                False,
                f"Unsupported assertion operator '{assertion.operator}'.",
            )

        if not verified:
            return (
                False,
                (
                    f"Assertion failed: {assertion.field} "
                    f"{assertion.operator} {expected_value!r}; "
                    f"actual value was {actual_value!r}."
                ),
            )

        return (
            True,
            (
                f"Verified {assertion.field} "
                f"{assertion.operator} {expected_value!r}."
            ),
        )

    @staticmethod
    def _normalize_value(
        value: Any,
    ) -> str:
        if isinstance(value, Enum):
            value = value.value

        if value is None:
            return ""

        if isinstance(value, datetime):
            normalized = value.astimezone(timezone.utc)
            return normalized.isoformat().replace("+00:00", "Z")

        if isinstance(value, str):
            candidate = value.strip()

            if candidate.lower() in {"null", "none"}:
                return ""

            try:
                parsed = datetime.fromisoformat(
                    candidate.replace("Z", "+00:00")
                )
            except ValueError:
                return candidate

            if parsed.tzinfo is not None:
                parsed = parsed.astimezone(timezone.utc)

            return parsed.isoformat().replace("+00:00", "Z")

        return str(value)

    def _claim_supported(
        self,
        source: str,
        claim: str,
        record: Any,
    ) -> tuple[bool, str]:
        normalized_claim = claim.lower()

        if source == "invoice":
            return self._verify_invoice_claim(
                normalized_claim,
                record,
            )

        if source == "gateway_event":
            return self._verify_gateway_claim(
                normalized_claim,
                record,
            )

        if source == "webhook_event":
            return self._verify_webhook_claim(
                normalized_claim,
                record,
            )

        if source == "settlement":
            return self._verify_settlement_claim(
                normalized_claim,
                record,
            )

        if source == "refund":
            return self._verify_refund_claim(
                normalized_claim,
                record,
            )

        if source == "audit_event":
            return self._verify_audit_claim(
                normalized_claim,
                record,
            )

        return False, "Unsupported evidence source."

    @staticmethod
    def _verify_invoice_claim(
        claim: str,
        record: Any,
    ) -> tuple[bool, str]:
        status = record.status.value.lower()
        currency = record.currency.lower()

        if "unpaid" in claim:
            return (
                status == "unpaid",
                f"Invoice status is {status}.",
            )

        if "paid" in claim:
            return (
                status == "paid",
                f"Invoice status is {status}.",
            )

        if currency in claim:
            return (
                True,
                f"Invoice currency is {record.currency}.",
            )

        return (
            False,
            "Claim is not deterministically supported by invoice fields.",
        )

    @staticmethod
    def _verify_gateway_claim(
        claim: str,
        record: Any,
    ) -> tuple[bool, str]:
        event_type = record.event_type.value.lower()
        currency = record.currency.lower()

        if "captured" in claim or "capture" in claim:
            return (
                event_type == "payment_captured",
                f"Gateway event type is {event_type}.",
            )

        if "authorized" in claim or "authorization" in claim:
            return (
                event_type == "payment_authorized",
                f"Gateway event type is {event_type}.",
            )

        if "chargeback" in claim:
            return (
                event_type == "chargeback_created",
                f"Gateway event type is {event_type}.",
            )

        if currency in claim:
            return (
                True,
                f"Gateway event currency is {record.currency}.",
            )

        if record.invoice_reference.lower() in claim:
            return (
                True,
                f"Gateway invoice reference is {record.invoice_reference}.",
            )

        return (
            False,
            "Claim is not deterministically supported by gateway fields.",
        )

    @staticmethod
    def _verify_webhook_claim(
        claim: str,
        record: Any,
    ) -> tuple[bool, str]:
        status = record.processing_status.lower()

        if "failed" in claim or "failure" in claim:
            verified = (
                record.http_status >= 400
                or status == "failed"
            )

            return (
                verified,
                (
                    f"Webhook HTTP status is {record.http_status} "
                    f"and processing status is {record.processing_status}."
                ),
            )

        if (
            "succeeded" in claim
            or "successful" in claim
            or "processed" in claim
        ):
            verified = (
                200 <= record.http_status < 300
                and status == "processed"
            )

            return (
                verified,
                (
                    f"Webhook HTTP status is {record.http_status} "
                    f"and processing status is {record.processing_status}."
                ),
            )

        if str(record.http_status) in claim:
            return (
                True,
                f"Webhook HTTP status is {record.http_status}.",
            )

        return (
            False,
            "Claim is not deterministically supported by webhook fields.",
        )

    @staticmethod
    def _verify_settlement_claim(
        claim: str,
        record: Any,
    ) -> tuple[bool, str]:
        status = record.status.lower()

        if "pending" in claim:
            return (
                status == "pending",
                f"Settlement status is {status}.",
            )

        if "settled" in claim:
            return (
                status == "settled",
                f"Settlement status is {status}.",
            )

        return (
            False,
            "Claim is not deterministically supported by settlement fields.",
        )

    @staticmethod
    def _verify_refund_claim(
        claim: str,
        record: Any,
    ) -> tuple[bool, str]:
        status = record.status.lower()

        if "refund" in claim:
            return (
                True,
                (
                    f"Refund {record.refund_id} exists with "
                    f"status {record.status} and amount {record.amount}."
                ),
            )

        if "succeeded" in claim or "successful" in claim:
            return (
                status == "succeeded",
                f"Refund status is {status}.",
            )

        return (
            False,
            "Claim is not deterministically supported by refund fields.",
        )

    @staticmethod
    def _verify_audit_claim(
        claim: str,
        record: Any,
    ) -> tuple[bool, str]:
        event_type = record.event_type.lower()
        result = record.result.lower()
        reason = (record.reason or "").lower()

        if event_type in claim:
            return (
                True,
                f"Audit event type is {record.event_type}.",
            )

        if result in claim:
            return (
                True,
                f"Audit result is {record.result}.",
            )

        if reason and reason in claim:
            return (
                True,
                f"Audit reason is {record.reason}.",
            )

        return (
            False,
            "Claim is not deterministically supported by audit fields.",
        )