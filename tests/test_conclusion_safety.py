from reconcilex.investigator.conclusion_safety import (
    ConclusionSafetyGate,
)
from reconcilex.investigator.models import (
    EvidenceAssertion,
    EvidenceRef,
    EvidenceSource,
)
from reconcilex.investigator.planner import (
    PlannerAction,
    PlannerActionType,
)


def test_conclusion_gate_allows_explicit_causal_reason():
    gate = ConclusionSafetyGate()

    action = PlannerAction(
        action_type=PlannerActionType.FINISH,
        root_cause="currency_mismatch",
        finding=(
            "Payment application failed because invoice and "
            "payment currencies did not match."
        ),
        first_divergence="payment_recorded",
        confidence=0.98,
        recommended_action="Perform manual currency review.",
        requires_human_approval=True,
        abstained=False,
    )

    evidence = [
        EvidenceRef(
            source=EvidenceSource.INVOICE,
            record_id="INV-1008",
            claim="Invoice currency is EUR.",
            assertions=[
                EvidenceAssertion(
                    field="currency",
                    operator="eq",
                    value="EUR",
                ),
            ],
        ),
        EvidenceRef(
            source=EvidenceSource.GATEWAY_EVENT,
            record_id="GE-8001",
            claim="Gateway payment currency is USD.",
            assertions=[
                EvidenceAssertion(
                    field="currency",
                    operator="eq",
                    value="USD",
                ),
            ],
        ),
        EvidenceRef(
            source=EvidenceSource.AUDIT_EVENT,
            record_id="AUD-8002",
            claim=(
                "Payment application failed because of "
                "currency mismatch."
            ),
            assertions=[
                EvidenceAssertion(
                    field="result",
                    operator="eq",
                    value="failed",
                ),
                EvidenceAssertion(
                    field="reason",
                    operator="eq",
                    value=(
                        "currency_mismatch_invoice_EUR_payment_USD"
                    ),
                ),
            ],
        ),
    ]

    result = gate.verify(
        action,
        evidence,
    )

    assert result.safe is True
    assert result.reason is None


def test_conclusion_gate_rejects_unresolved_causal_ambiguity():
    gate = ConclusionSafetyGate()

    action = PlannerAction(
        action_type=PlannerActionType.FINISH,
        root_cause="incorrect_invoice_reference",
        finding=(
            "The wrong invoice reference caused webhook "
            "processing to fail."
        ),
        first_divergence="payment_captured",
        confidence=1.0,
        recommended_action=(
            "Mark the intended invoice paid."
        ),
        requires_human_approval=True,
        abstained=False,
    )

    evidence = [
        EvidenceRef(
            source=EvidenceSource.GATEWAY_EVENT,
            record_id="GE-12001",
            claim=(
                "Gateway capture references INV-9912."
            ),
            assertions=[
                EvidenceAssertion(
                    field="invoice_reference",
                    operator="eq",
                    value="INV-9912",
                ),
            ],
        ),
        EvidenceRef(
            source=EvidenceSource.WEBHOOK_EVENT,
            record_id="WH-12001",
            claim="Webhook processing failed.",
            assertions=[
                EvidenceAssertion(
                    field="processing_status",
                    operator="eq",
                    value="failed",
                ),
                EvidenceAssertion(
                    field="http_status",
                    operator="eq",
                    value="500",
                ),
            ],
        ),
        EvidenceRef(
            source=EvidenceSource.INVOICE,
            record_id="INV-1012",
            claim="Primary invoice remains unpaid.",
            assertions=[
                EvidenceAssertion(
                    field="status",
                    operator="eq",
                    value="unpaid",
                ),
            ],
        ),
    ]

    result = gate.verify(
        action,
        evidence,
    )

    assert result.safe is False
    assert result.reason is not None
    assert "Multiple plausible causal anomalies" in result.reason


def test_conclusion_gate_allows_agent_abstention():
    gate = ConclusionSafetyGate()

    action = PlannerAction(
        action_type=PlannerActionType.FINISH,
        root_cause=None,
        finding=None,
        confidence=0.3,
        recommended_action="Escalate for human review.",
        requires_human_approval=True,
        abstained=True,
        abstention_reason=(
            "Available evidence cannot distinguish "
            "between plausible causes."
        ),
    )

    result = gate.verify(
        action,
        [],
    )

    assert result.safe is True
    assert result.reason is None


def test_conclusion_gate_rejects_unverified_non_abstaining_conclusion():
    gate = ConclusionSafetyGate()

    action = PlannerAction(
        action_type=PlannerActionType.FINISH,
        root_cause="webhook_failure",
        finding="Webhook processing caused the discrepancy.",
        confidence=0.9,
        recommended_action="Replay webhook.",
        requires_human_approval=True,
        abstained=False,
    )

    result = gate.verify(
        action,
        [],
    )

    assert result.safe is False
    assert result.reason == (
        "A non-abstaining conclusion requires "
        "verified supporting evidence."
    )