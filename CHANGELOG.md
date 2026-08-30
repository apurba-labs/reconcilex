# Changelog

All notable engineering changes and experiments for ReconcileX are documented here.

ReconcileX was developed for the micro1 Frontier Engineering Challenge 2026.

The project evolved around one central principle:

> Facts are deterministic. Investigation is agentic. Action remains controlled.

---

## [0.1.0] - 2026-08-30

### Problem Definition

ReconcileX began with a specific financial-operations problem:

A payment exception rarely exists in one system.

A gateway may report a successful transaction while an invoice, webhook processor, settlement system, refund record, or audit trail reports something different.

The goal was therefore not to build another chatbot that explains payments.

The goal was to build an investigator that can determine:

1. what actually happened,
2. where the expected payment lifecycle first diverged,
3. what evidence supports that conclusion,
4. whether the evidence is sufficient,
5. and what action is safe to recommend.

---

### Benchmark Foundation

Created a deterministic benchmark of 12 synthetic payment-reconciliation incidents.

Cases cover:

- webhook processing failure,
- duplicate gateway capture,
- full refund not reflected internally,
- partial refund amount mismatch,
- chargeback after settlement,
- authorization without capture,
- missing settlement,
- currency mismatch,
- incorrect payment-reference mapping,
- duplicate webhook processing,
- valid settlement delay,
- conflicting and insufficient evidence.

PAY-011 was introduced as a negative control where no failure should be declared.

PAY-012 was introduced as an ambiguity control where the correct behavior is abstention and human review.

Ground truth is separated from agent-visible case data.

The investigator cannot access benchmark answers during execution.

---

### Synthetic Evidence Layer

Added reproducible synthetic financial records for:

- invoices,
- gateway events,
- webhook events,
- settlements,
- refunds,
- audit events.

Added deterministic dataset generation.

Implemented a structured record store and read-only financial tools.

The tool surface intentionally exposes domain operations rather than raw filesystem, shell, Python, SQL, or mutation capabilities.

---

### Agentic Investigator

Implemented a hypothesis-driven investigation loop.

The investigator can:

- observe a reported payment exception,
- form competing hypotheses,
- select read-only evidence tools,
- inspect financial records,
- reject contradicted hypotheses,
- revise its investigation,
- identify a root cause,
- identify the first lifecycle divergence,
- recommend a next action,
- or abstain when evidence is insufficient.

Investigation state is represented with structured models rather than unstructured chat history.

Captured trajectories preserve the investigation process for evaluation and review.

---

### Provider Abstraction

Added provider-neutral structured-output support.

Validated live execution with:

- OpenAI,
- Gemini.

Provider selection is separated from investigation logic.

This allows the same domain architecture and benchmark cases to be exercised across different model providers.

---

### Evidence Verification

Initial agent outputs demonstrated an important problem:

A model can cite a real record while making a claim that the record does not actually support.

Added deterministic evidence verification to distinguish:

- evidence observed by the agent,
- evidence cited by the agent,
- evidence whose assertions can be verified.

Evidence references contain structured assertions against specific financial records.

The evaluator does not award evidence credit simply because a model mentions a plausible fact.

---

### Negative Evidence Semantics

Negative claims require an actual observation showing absence.

For example, a claim such as:

> no refund exists

cannot be established merely because the model did not mention a refund.

The relevant source must actually be queried and return no matching records.

This prevents absence from being inferred from missing context.

---

### Causal Conclusion Safety

Added a narrow conclusion safety boundary.

The purpose is not to make the LLM incapable of being wrong.

The purpose is to prevent unsupported financial causality from silently becoming an accepted conclusion.

The model may form hypotheses.

Observable evidence remains authoritative.

---

### Human-Control Boundary

The investigator is intentionally read-only.

It can investigate, correlate, verify, recommend, and abstain.

It cannot autonomously:

- capture payments,
- issue refunds,
- replay webhooks,
- mutate invoice state,
- alter ledger state.

Consequential financial actions remain subject to human approval.

---

### Evaluation Harness

Added deterministic evaluation across the 12 benchmark cases.

Metrics include:

- root-cause accuracy,
- first-divergence accuracy,
- abstention accuracy,
- safe-action compliance,
- evidence coverage,
- unsupported claims,
- tool calls,
- reasoning steps.

A strict case pass requires all binary criteria to succeed, complete required-evidence coverage, and zero unsupported claims.

Strict pass count is intentionally reported alongside component metrics rather than replacing them.

---

### Baseline Experiment

Implemented a fair single-pass baseline.

The baseline:

- receives the same underlying case evidence,
- uses the same model provider within a comparison,
- receives all evidence in one static prompt,
- produces one structured result.

It does not use:

- adaptive tool selection,
- iterative hypothesis testing,
- deterministic evidence verification,
- the causal conclusion safety gate.

The baseline is intentionally capable rather than artificially weakened.

Giving it all available evidence up front makes the comparison conservative: the advanced investigator must justify the cost of adaptive investigation.

---

### Primary Measured Experiment

The primary experiment compares OpenAI baseline and advanced architectures across the same 12 cases.

| Metric | Baseline | Advanced | Delta |
|---|---:|---:|---:|
| Root cause accuracy | 25.00% | 50.00% | +25.00 pp |
| First-divergence accuracy | 33.33% | 41.67% | +8.33 pp |
| Evidence coverage | 42.50% | 71.25% | +28.75 pp |
| Abstention accuracy | 83.33% | 58.33% | -25.00 pp |
| Safe-action compliance | 91.67% | 91.67% | 0.00 pp |
| Unsupported claim rate | 0.00% | 0.00% | 0.00 pp |
| Strict case passes | 0/12 | 2/12 | +2 cases |

The advanced system averaged 6.92 read-only tool calls and 22.50 recorded reasoning steps per case.

The baseline used zero adaptive tool calls and one structured model invocation.

---

### What Improved

Root-cause accuracy doubled from 25% to 50%.

Evidence coverage increased by 28.75 percentage points.

First-divergence accuracy improved by 8.33 percentage points.

These results support the hypothesis that structured investigation can improve causal diagnosis and evidence quality compared with a single-pass answer.

---

### What Did Not Improve

Abstention accuracy decreased from 83.33% to 58.33%.

Safe-action compliance remained at 91.67%.

These results were retained rather than tuned away.

They exposed an important architectural lesson:

> Better investigation does not automatically produce safer decisions.

Reasoning quality, evidence quality, abstention policy, and action authorization should be evaluated separately.

---

### Gemini Experiment

The baseline architecture was successfully executed across all 12 benchmark cases using Gemini.

Two advanced Gemini trajectories were also captured.

Because the advanced Gemini run contains only two cases, it is treated as partial diagnostic evidence rather than compared against the 12-case Gemini baseline.

The reporting layer rejects comparisons where baseline and advanced case counts differ.

---

### Reporting

Added reproducible benchmark artifacts for:

- baseline trajectories,
- advanced trajectories,
- provider evaluations,
- baseline evaluations,
- baseline-versus-advanced comparison reports.

Added a human-readable evaluation report explaining both improvements and regressions.

---

### Testing

Expanded the automated test suite throughout development.

Final documentation checkpoint:

```text
132 passed
```

Tests cover deterministic tools, investigation behavior, evidence semantics, safety boundaries, evaluation logic, and benchmark invariants.

---

## Engineering Decisions Retained

Several decisions were deliberately preserved instead of optimized away for benchmark scores.

### No autonomous financial mutations

Read-only investigation remains a hard architectural boundary.

### No ground-truth leakage

Benchmark answers remain evaluator-only.

### No evaluator access to raw records for evidence credit

Evidence must come from the agent's observable investigation and cited evidence chain.

### No fabricated negative evidence

Absence must be observed.

### No tuning toward 12/12

Failures that reveal useful model or architecture behavior remain part of the final evaluation.

### No unfair Gemini comparison

The partial advanced Gemini run is retained but not presented as a measured improvement over the 12-case baseline.

---

## Development Methodology

Coding and reasoning assistants were used to accelerate implementation, debugging, testing, and iteration.

AI-generated changes were not treated as authoritative.

Architectural boundaries, benchmark design, safety policy, evidence semantics, evaluation criteria, experimental interpretation, and final engineering decisions were reviewed by the project author.

Changes were validated using:

- automated tests,
- deterministic fixtures,
- live provider execution,
- saved trajectories,
- benchmark evaluation,
- baseline-versus-advanced comparison.

---

## Key Lesson

The project started with the question:

> How can an AI agent reconcile a payment exception?

The more useful question became:

> Which parts of financial reconciliation should never depend on probabilistic reasoning?

That distinction shaped the final architecture.

Financial facts are established deterministically.

The agent investigates ambiguity between those facts.

Consequential action remains controlled.