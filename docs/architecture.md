# ReconcileX Architecture

ReconcileX is designed around one boundary:

> Facts are deterministic. Investigation is agentic. Action remains controlled.

## System Flow

```text
Payment Exception
      ↓
Case Input
      ↓
Agent Investigator
      ↓
Read-only Financial Tools
      ↓
Evidence Verification
      ↓
Conclusion Safety Gate
      ↓
Investigation Result
```

## Deterministic Layer

Financial facts are retrieved and verified with Python.

The agent uses read-only tools for:

- invoices
- gateway events
- webhook events
- settlements
- refunds
- audit events
- payment timelines

The model does not read benchmark ground truth and does not directly inspect raw files, SQL, shell, or mutable financial systems.

## Agentic Layer

The LLM is responsible for investigation, not financial truth.

It can:

- form hypotheses,
- decide which evidence to inspect,
- compare competing explanations,
- reject contradicted hypotheses,
- revise its conclusion,
- identify the likely root cause,
- identify the first lifecycle divergence,
- recommend a safe next action,
- abstain when evidence is insufficient.

## Evidence Verification

A cited record is not automatically accepted as proof.

ReconcileX verifies structured evidence assertions against the actual retrieved record.

This separates:

1. evidence the model observed,
2. evidence the model cited,
3. evidence that actually supports the claim.

Negative claims also require observation.

For example, `no refund exists` requires querying refund data and observing no matching refund.

## Safety Boundary

The investigator is intentionally read-only.

It cannot autonomously:

- capture a payment,
- issue a refund,
- replay a webhook,
- modify an invoice,
- change ledger state.

The system can recommend consequential actions, but execution remains under human control.

## Evaluation Boundary

Ground truth is evaluator-only.

The investigator cannot access expected root causes, required evidence, allowed actions, or prohibited actions during investigation.

The evaluator measures:

- root-cause accuracy,
- first-divergence accuracy,
- evidence coverage,
- abstention behavior,
- safe-action compliance,
- unsupported claims.

## Design Principle

ReconcileX does not try to make an LLM authoritative over financial state.

The model is useful where ambiguity exists.

Deterministic systems remain authoritative where facts can be established directly.