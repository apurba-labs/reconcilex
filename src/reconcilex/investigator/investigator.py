from reconcilex.domain.case_input import CaseInput
from reconcilex.investigator.models import (
    EvidenceRef,
    Hypothesis,
    HypothesisStatus,
    InvestigationResult,
)
from reconcilex.investigator.verifier import EvidenceVerifier
from reconcilex.tools.payment_tools import PaymentTools


class Investigator:
    def __init__(self, tools: PaymentTools, verifier: EvidenceVerifier):
        self.tools = tools
        self.verifier = verifier

    def investigate(self, case_input: CaseInput) -> InvestigationResult:
        if case_input.case_id == "PAY-008":
            return self._investigate_pay_008(case_input)

        raise NotImplementedError(
            f"No deterministic investigation strategy for {case_input.case_id}"
        )

    def _investigate_pay_008(self, case_input: CaseInput) -> InvestigationResult:
        if case_input.primary_invoice_id is None:
            raise ValueError("PAY-008 requires primary_invoice_id.")

        if case_input.known_payment_id is None:
            raise ValueError("PAY-008 requires known_payment_id.")

        invoice_id = case_input.primary_invoice_id
        payment_id = case_input.known_payment_id

        invoice = self.tools.get_invoice(invoice_id)

        if invoice is None:
            raise ValueError(
                f"Invoice {invoice_id} could not be found."
            )

        gateway_events = self.tools.get_gateway_events(payment_id)
        webhook_events = self.tools.get_webhook_events(payment_id)
        audit_events = self.tools.get_audit_events(invoice_id)

        capture = next(
            (
                event
                for event in gateway_events
                if event["event_type"] == "payment_captured"
            ),
            None,
        )

        webhook = next(iter(webhook_events), None)

        application_audit = next(
            (
                event
                for event in audit_events
                if event["event_type"] == "payment_application"
            ),
            None,
        )

        if capture is None:
            raise ValueError(
                f"No capture evidence found for {payment_id}."
            )

        if webhook is None:
            raise ValueError(
                f"No webhook evidence found for {payment_id}."
            )

        if application_audit is None:
            raise ValueError(
                f"No payment application audit found for {invoice_id}."
            )

        webhook_success_evidence = EvidenceRef(
            source="webhook_event",
            record_id=webhook["webhook_id"],
            claim="Webhook processing succeeded successfully.",
        )

        webhook_verification = self.verifier.verify(
            webhook_success_evidence
        )

        webhook_failure_hypothesis = Hypothesis(
            hypothesis_id="H-001",
            description=(
                "Webhook processing failure caused "
                "the invoice to remain unpaid."
            ),
        )

        if webhook_verification.verified:
            webhook_failure_hypothesis.status = (
                HypothesisStatus.REJECTED
            )
            webhook_failure_hypothesis.contradicting_evidence.append(
                webhook_success_evidence
            )
        else:
            webhook_failure_hypothesis.status = (
                HypothesisStatus.INCONCLUSIVE
            )

        invoice_currency_evidence = EvidenceRef(
            source="invoice",
            record_id=invoice["invoice_id"],
            claim=f"Invoice currency is {invoice['currency']}.",
        )

        payment_currency_evidence = EvidenceRef(
            source="gateway_event",
            record_id=capture["event_id"],
            claim=f"Gateway event currency is {capture['currency']}.",
        )

        audit_reason = application_audit.get("reason") or ""

        application_failure_evidence = EvidenceRef(
            source="audit_event",
            record_id=application_audit["audit_id"],
            claim=(
                "Payment application failed because "
                f"{audit_reason}."
            ),
        )

        currency_evidence = [
            invoice_currency_evidence,
            payment_currency_evidence,
            application_failure_evidence,
        ]

        verified_currency_evidence = [
            evidence
            for evidence in currency_evidence
            if self.verifier.verify(evidence).verified
        ]

        currencies_differ = (
            invoice["currency"] != capture["currency"]
        )

        currency_hypothesis = Hypothesis(
            hypothesis_id="H-002",
            description=(
                "The payment could not be applied because "
                "the invoice and payment currencies differ."
            ),
        )

        if (currencies_differ and len(verified_currency_evidence) == len(currency_evidence)):
            currency_hypothesis.status = (HypothesisStatus.SUPPORTED)
            currency_hypothesis.supporting_evidence.extend(verified_currency_evidence)
        else:
            currency_hypothesis.status = (HypothesisStatus.INCONCLUSIVE)

        if currency_hypothesis.status != HypothesisStatus.SUPPORTED:
            return InvestigationResult(
                case_id=case_input.case_id,
                reported_issue=case_input.reported_issue,
                hypotheses=[
                    webhook_failure_hypothesis,
                    currency_hypothesis,
                ],
                finding=None,
                root_cause=None,
                first_divergence=None,
                evidence=[],
                contradictory_evidence=(
                    webhook_failure_hypothesis.contradicting_evidence
                ),
                confidence=0.4,
                recommended_action=(
                    "Request additional payment application evidence "
                    "and escalate for human review."
                ),
                requires_human_approval=True,
                abstained=True,
                abstention_reason=(
                    "The available evidence does not establish "
                    "a unique root cause."
                ),
            )

        return InvestigationResult(
            case_id=case_input.case_id,
            reported_issue=case_input.reported_issue,
            hypotheses=[
                webhook_failure_hypothesis,
                currency_hypothesis,
            ],
            finding=(
                "The payment was captured and the webhook was processed, "
                "but payment application failed because the invoice and "
                "payment currencies differ."
            ),
            root_cause="currency_mismatch",
            first_divergence="payment_recorded",
            evidence=verified_currency_evidence,
            contradictory_evidence=(
                webhook_failure_hypothesis.contradicting_evidence
            ),
            confidence=0.98,
            recommended_action=(
                "Perform manual currency review before reconciling "
                "the payment to the invoice."
            ),
            requires_human_approval=True,
            abstained=False,
            abstention_reason=None,
        )