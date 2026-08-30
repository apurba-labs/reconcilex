from __future__ import annotations

import json
from typing import Any

from reconcilex.domain.case_input import CaseInput
from reconcilex.investigator.models import InvestigationResult
from reconcilex.llm.provider import LLMProvider
from reconcilex.tools.payment_tools import PaymentTools


BASELINE_SYSTEM_PROMPT = """
You are a payment reconciliation assistant.

Review the reported payment exception and all supplied payment records.

Determine:
- the most likely finding,
- root cause,
- first transaction lifecycle divergence,
- supporting evidence,
- contradictory evidence,
- confidence,
- and the safest recommended next action.

Use only the supplied records.
Do not invent records, identifiers, amounts, states, timestamps,
currencies, or audit events.

If the available evidence cannot establish a root cause,
abstain and recommend human review.

Consequential financial actions require human approval.

Return exactly one structured InvestigationResult.
""".strip()


class DirectBaseline:
    """
    Single-pass reconciliation baseline.

    It receives the available evidence up front and performs one
    structured model call.

    It intentionally has:
    - no adaptive tool selection,
    - no iterative hypothesis loop,
    - no deterministic evidence verifier,
    - no conclusion safety gate.
    """

    def __init__(
        self,
        *,
        provider: LLMProvider,
        tools: PaymentTools,
    ) -> None:
        self.provider = provider
        self.tools = tools

    def investigate(
        self,
        case_input: CaseInput,
        *,
        evidence: dict[str, Any] | None = None,
    ) -> InvestigationResult:
        if evidence is None:
            evidence = self.collect_evidence(
                case_input
            )

        user_prompt = self._build_prompt(
            case_input=case_input,
            evidence=evidence,
        )

        return self.provider.generate_structured(
            system_prompt=BASELINE_SYSTEM_PROMPT,
            user_prompt=user_prompt,
            response_model=InvestigationResult,
        )

    def collect_evidence(
        self,
        case_input: CaseInput,
    ) -> dict[str, Any]:
        context = self.tools.get_case_context(
            case_input.case_id
        )

        invoice_ids = context.get(
            "invoice_ids",
            [],
        )

        payment_ids = context.get(
            "payment_ids",
            [],
        )

        invoices = [
            invoice
            for invoice_id in invoice_ids
            if (
                invoice := self.tools.get_invoice(
                    invoice_id
                )
            )
            is not None
        ]

        gateway_events: list[dict] = []
        webhook_events: list[dict] = []
        settlements: list[dict] = []
        refunds: list[dict] = []
        timelines: list[dict] = []
        audit_events: list[dict] = []

        for payment_id in payment_ids:
            gateway_events.extend(
                self.tools.get_gateway_events(
                    payment_id
                )
            )

            webhook_events.extend(
                self.tools.get_webhook_events(
                    payment_id
                )
            )

            settlements.extend(
                self.tools.get_settlements(
                    payment_id
                )
            )

            refunds.extend(
                self.tools.get_refunds(
                    payment_id
                )
            )

            timelines.extend(
                self.tools.get_payment_timeline(
                    payment_id
                )
            )

            audit_events.extend(
                self.tools.get_audit_events(
                    payment_id
                )
            )

        for invoice_id in invoice_ids:
            audit_events.extend(
                self.tools.get_audit_events(
                    invoice_id
                )
            )

        audit_events = self._deduplicate_records(
            audit_events,
            id_field="audit_id",
        )

        return {
            "case_context": context,
            "invoices": invoices,
            "gateway_events": gateway_events,
            "webhook_events": webhook_events,
            "settlements": settlements,
            "refunds": refunds,
            "audit_events": audit_events,
            "payment_timelines": timelines,
        }

    @staticmethod
    def _deduplicate_records(
        records: list[dict],
        *,
        id_field: str,
    ) -> list[dict]:
        seen: set[str] = set()
        result: list[dict] = []

        for record in records:
            record_id = str(
                record.get(
                    id_field,
                    json.dumps(
                        record,
                        sort_keys=True,
                    ),
                )
            )

            if record_id in seen:
                continue

            seen.add(record_id)
            result.append(record)

        return result

    @staticmethod
    def _build_prompt(
        *,
        case_input: CaseInput,
        evidence: dict[str, Any],
    ) -> str:
        case_payload = case_input.model_dump(
            mode="json",
        )

        return (
            "Investigate this payment exception.\n\n"
            "CASE INPUT:\n"
            f"{json.dumps(case_payload, indent=2)}\n\n"
            "AVAILABLE PAYMENT RECORDS:\n"
            f"{json.dumps(evidence, indent=2)}\n\n"
            "Produce the final investigation result."
        )