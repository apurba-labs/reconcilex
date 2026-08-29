from __future__ import annotations

from dataclasses import dataclass

from reconcilex.investigator.models import EvidenceRef
from reconcilex.investigator.planner import PlannerAction


@dataclass(frozen=True)
class ConclusionSafetyResult:
    safe: bool
    reason: str | None = None


class ConclusionSafetyGate:
    """
    Deterministic safety boundary for final agent conclusions.

    The agent may discover anomalies and propose hypotheses, but it
    cannot convert multiple unresolved anomalies into a single causal
    conclusion without distinguishing evidence.
    """

    def verify(
        self,
        action: PlannerAction,
        verified_evidence: list[EvidenceRef],
    ) -> ConclusionSafetyResult:
        if action.abstained:
            return ConclusionSafetyResult(safe=True)

        if not action.root_cause:
            return ConclusionSafetyResult(
                safe=False,
                reason=(
                    "A non-abstaining conclusion must provide "
                    "a defensible root cause."
                ),
            )

        if not verified_evidence:
            return ConclusionSafetyResult(
                safe=False,
                reason=(
                    "A non-abstaining conclusion requires "
                    "verified supporting evidence."
                ),
            )

        has_explicit_reason = any(
            self._has_explicit_reason(evidence)
            for evidence in verified_evidence
        )

        has_reference_mismatch = any(
            self._has_assertion(
                evidence,
                field="invoice_reference",
            )
            for evidence in verified_evidence
        )

        has_failed_webhook = any(
            self._has_failed_webhook(evidence)
            for evidence in verified_evidence
        )

        # Multiple plausible anomalies exist, but no record explicitly
        # establishes which anomaly caused the downstream discrepancy.
        if (
            has_reference_mismatch
            and has_failed_webhook
            and not has_explicit_reason
        ):
            return ConclusionSafetyResult(
                safe=False,
                reason=(
                    "Multiple plausible causal anomalies remain "
                    "and no verified evidence explicitly "
                    "distinguishes their causal relationship."
                ),
            )

        return ConclusionSafetyResult(safe=True)

    @staticmethod
    def _has_assertion(
        evidence: EvidenceRef,
        *,
        field: str,
        value: str | None = None,
    ) -> bool:
        for assertion in evidence.assertions:
            if assertion.field != field:
                continue

            if value is None:
                return True

            if str(assertion.value).lower() == value.lower():
                return True

        return False

    @classmethod
    def _has_failed_webhook(
        cls,
        evidence: EvidenceRef,
    ) -> bool:
        if evidence.source.value != "webhook_event":
            return False

        failed_processing = cls._has_assertion(
            evidence,
            field="processing_status",
            value="failed",
        )

        http_failure = any(
            assertion.field == "http_status"
            and str(assertion.value).startswith("5")
            for assertion in evidence.assertions
        )

        return failed_processing or http_failure

    @staticmethod
    def _has_explicit_reason(
        evidence: EvidenceRef,
    ) -> bool:
        return any(
            assertion.field == "reason"
            and bool(str(assertion.value).strip())
            for assertion in evidence.assertions
        )