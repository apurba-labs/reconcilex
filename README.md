# ReconcileX

**Agentic payment reconciliation that separates financial facts from AI reasoning.**

> Facts are deterministic. Investigation is agentic. Action remains controlled.

ReconcileX investigates payment exceptions across fragmented financial systems, determines where the expected transaction lifecycle first diverged from observed reality, verifies its conclusions against evidence, and recommends a safe next action for human review.

It was built for the **micro1 Frontier Engineering Challenge 2026**.

---

## The Problem

A payment can look successful in one system and failed in another.

A gateway may report a successful capture while:

- the invoice remains unpaid,
- a webhook failed,
- a settlement is missing,
- a refund was not reflected,
- a payment was mapped to the wrong invoice,
- or multiple systems contain conflicting evidence.

These incidents are difficult because financial truth is distributed across several systems.

A generic chatbot can produce a plausible explanation, but plausible is not enough for financial operations.

ReconcileX is designed around a stricter question:

> What can the system actually prove from observable financial evidence?

---

## Expected Payment Lifecycle

ReconcileX models the expected lifecycle as:

```text
INVOICE_CREATED
        ↓
PAYMENT_INITIATED
        ↓
AUTHORIZED
        ↓
CAPTURED
        ↓
WEBHOOK_RECEIVED
        ↓
PAYMENT_RECORDED
        ↓
INVOICE_PAID
        ↓
SETTLED
```

An investigation attempts to identify the **first divergence** between this expected lifecycle and the observed records.

---

## Architecture

```text
Payment Exception
       │
       ▼
Case Input
       │
       ▼
Agent Investigator
       │
       ├── forms hypotheses
       ├── selects read-only tools
       ├── gathers evidence
       ├── rejects contradictions
       └── revises its investigation
       │
       ▼
Deterministic Payment Tools
       │
       ├── invoices
       ├── gateway events
       ├── webhooks
       ├── settlements
       ├── refunds
       └── audit events
       │
       ▼
Evidence Verification
       │
       ▼
Conclusion Safety Gate
       │
       ▼
Investigation Report
       │
       ├── root cause
       ├── first divergence
       ├── evidence
       ├── confidence
       ├── safe recommendation
       └── abstention / human review
```

The LLM controls the investigation.

It does **not** control the financial facts.

---

## Deterministic vs Agentic Boundary

ReconcileX deliberately separates responsibilities.

### Deterministic code establishes facts

Python tools retrieve and verify:

- invoice state
- gateway events
- webhook processing
- settlements
- refunds
- audit events
- payment timelines

### The agent investigates ambiguity

The model can:

- form hypotheses
- choose what evidence to inspect
- compare competing explanations
- revise its reasoning
- identify likely causal divergence
- recommend a next step
- abstain when evidence is insufficient

### Financial mutation remains controlled

The agent cannot autonomously:

- capture a payment
- issue a refund
- replay a webhook
- mutate an invoice
- change ledger state

Consequential actions remain human-controlled.

---

## Benchmark

ReconcileX includes **12 deterministic payment-reconciliation cases**.

They cover:

| Case | Scenario |
|---|---|
| PAY-001 | Captured payment with failed webhook processing |
| PAY-002 | Duplicate gateway capture |
| PAY-003 | Full refund not reflected on invoice |
| PAY-004 | Partial refund amount mismatch |
| PAY-005 | Chargeback not reflected after settlement |
| PAY-006 | Authorization never captured |
| PAY-007 | Captured payment missing from settlement |
| PAY-008 | Currency mismatch during payment application |
| PAY-009 | Payment mapped to the wrong invoice |
| PAY-010 | Duplicate webhook processed twice |
| PAY-011 | Valid settlement delay — no failure |
| PAY-012 | Conflicting evidence — human review required |

The final two cases are deliberate controls.

PAY-011 tests whether the investigator can avoid inventing a problem.

PAY-012 tests whether it can abstain when evidence cannot justify a single root cause.

---

## Baseline vs Advanced Evaluation

The primary measured experiment compares the same OpenAI model on the same 12 benchmark cases.

### Baseline

The baseline receives all available evidence in one static prompt and produces one structured response.

It has no:

- adaptive tool use
- iterative investigation
- evidence verifier
- causal conclusion safety gate

### Advanced ReconcileX

The advanced system adds:

- adaptive read-only tool use
- hypothesis-driven investigation
- contradiction handling
- deterministic evidence verification
- conclusion safety checks
- explicit abstention behavior

### Results

| Metric | Baseline | Advanced | Delta |
|---|---:|---:|---:|
| Root cause accuracy | 25.00% | 50.00% | **+25.00 pp** |
| First-divergence accuracy | 33.33% | 41.67% | **+8.33 pp** |
| Evidence coverage | 42.50% | 71.25% | **+28.75 pp** |
| Abstention accuracy | 83.33% | 58.33% | **-25.00 pp** |
| Safe-action compliance | 91.67% | 91.67% | **0.00 pp** |
| Unsupported claim rate | 0.00% | 0.00% | **0.00 pp** |
| Strict case passes | 0/12 | 2/12 | **+2 cases** |

The advanced architecture doubled root-cause accuracy and substantially improved evidence coverage.

It also exposed a real regression: abstention accuracy decreased.

That failure is retained rather than tuned away.

The result reinforces an important design lesson:

> Better causal reasoning does not automatically mean safer decision-making.

See [`docs/evaluation-report.md`](docs/evaluation-report.md) for the full interpretation.

---

## Why Strict Passes Are Harsh

A strict benchmark pass requires:

- correct root cause
- correct first divergence
- correct abstention behavior
- safe recommended action
- complete required-evidence coverage
- zero unsupported claims

This means a case can diagnose the root cause correctly and still fail the strict benchmark.

ReconcileX intentionally reports the component metrics rather than hiding them behind one aggregate score.

---

## Provider Support

ReconcileX supports structured investigation using:

- OpenAI
- Gemini

The full primary baseline-versus-advanced comparison uses OpenAI across the same 12 cases.

The Gemini baseline was also executed across all 12 cases.

Only two advanced Gemini trajectories were captured in the current evaluation run, so those results are retained as partial artifacts and are **not** presented as a baseline-versus-advanced improvement claim.

---

## Example Investigation

Run PAY-008 with the advanced investigator:

```bash
uv run python scripts/run_agent_case.py \
  --provider openai \
  PAY-008
```

PAY-008 contains a payment captured and settled in USD against an invoice denominated in EUR.

The investigator must determine that the failure occurred during payment application rather than simply treating gateway success as proof that the invoice should be marked paid.

---

## Run the Project

### Requirements

- Python 3.12+
- `uv`
- an OpenAI or Gemini API key for live model runs

Install dependencies:

```bash
uv sync
```

Configure environment:

```bash
cp .env.example .env
```

Then set one or both provider credentials.

Example:

```env
OPENAI_API_KEY=
OPENAI_MODEL=gpt-5.6-sol

GEMINI_API_KEY=
GEMINI_MODEL=gemini-3.5-flash
```

---

## Run Tests

```bash
uv run pytest -q
```

Current test suite:

```text
132 passed
```

---

## Generate the Deterministic Dataset

```bash
uv run python scripts/generate_synthetic_dataset.py
```

The benchmark data is synthetic and reproducible.

---

## Run the Single-Pass Baseline

One case:

```bash
uv run python scripts/run_baseline_case.py \
  --provider openai \
  PAY-008
```

All baseline cases:

```bash
uv run python scripts/run_baseline.py \
  --provider openai
```

---

## Evaluate Saved Trajectories

Advanced:

```bash
uv run python scripts/run_benchmark.py \
  --provider openai
```

Baseline:

```bash
uv run python scripts/run_baseline_benchmark.py \
  --provider openai
```

Generate the comparison:

```bash
uv run python scripts/compare_benchmarks.py \
  --provider openai \
  --advanced openai-final-v1.json
```

---

## Repository Structure

```text
data/
  cases/               hidden benchmark ground truth
  inputs/              investigation case inputs
  records/             synthetic financial records

src/reconcilex/
  agent/                investigator runtime
  baseline/             single-pass baseline
  evaluation/           deterministic evaluator
  investigator/         investigation domain models
  tools/                read-only financial tools

scripts/
  generate_synthetic_dataset.py
  run_agent_case.py
  run_baseline_case.py
  run_baseline.py
  run_benchmark.py
  run_baseline_benchmark.py
  compare_benchmarks.py

outputs/
  trajectories/         captured model investigations
  evaluations/          benchmark results
  reports/              baseline-vs-advanced reports

docs/
  evaluation-report.md
```

---

## Safety Philosophy

ReconcileX does not sandbox a powerful financial agent and hope it behaves.

It gives the agent only the minimum read-only capabilities required to investigate.

A model may reason incorrectly, but unsupported financial causality should not silently become an accepted conclusion or an autonomous financial mutation.

The most valuable decision an autonomous financial investigator can make is sometimes:

> There is not enough evidence to act.

---

## Key Engineering Takeaway

More reasoning steps do not guarantee safer financial reasoning.

The better investigator is not the one that thinks longer.

It is the one that gathers enough evidence to make the safest defensible conclusion — and knows when the evidence is insufficient.

---

## Development Methodology

AI coding and reasoning assistants were used throughout development to accelerate implementation, test generation, debugging, and iteration.

Architectural decisions — including the deterministic/agentic boundary, read-only financial tool surface, benchmark design, evidence semantics, abstention policy, causal safety checks, and evaluation criteria — were designed and reviewed by the project author.

Generated changes were validated through:

- automated tests
- deterministic benchmark cases
- live provider runs
- captured investigation trajectories
- explicit baseline-versus-advanced evaluation

Failed or misleading model behavior was retained where useful as evaluation evidence rather than tuned away.

---

## Status

ReconcileX is an experimental financial-investigation system built for the micro1 Frontier Engineering Challenge 2026.

It is designed to investigate and recommend.

It is **not** designed to autonomously mutate financial state.