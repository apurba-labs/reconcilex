# ReconcileX Submission

## What problem does it solve?

Payment failures are difficult to investigate because financial state is distributed across multiple systems.

A payment gateway may say a transaction succeeded while the invoice, webhook processor, settlement system, refund service, or audit trail says something different.

ReconcileX investigates these inconsistencies and determines where the expected payment lifecycle first diverged from observed evidence.

## What does ReconcileX do?

ReconcileX is an agentic payment-reconciliation investigator.

It:

- forms competing hypotheses,
- queries read-only financial tools,
- gathers evidence,
- rejects contradicted explanations,
- identifies likely root cause and first divergence,
- verifies evidence,
- recommends a safe next step,
- or abstains when evidence is insufficient.

The agent does not mutate financial state.

## Key Architecture Decision

The central design decision is:

> Facts are deterministic. Investigation is agentic. Action remains controlled.

Python establishes observable financial facts.

The LLM investigates ambiguity between those facts.

Consequential financial actions remain human-controlled.

## Benchmark

The project includes 12 deterministic payment-reconciliation cases covering:

- webhook failures,
- duplicate captures,
- refund inconsistencies,
- chargebacks,
- authorization without capture,
- settlement exceptions,
- currency mismatch,
- payment-reference errors,
- duplicate webhook processing,
- valid no-failure scenarios,
- insufficient evidence.

Two cases are deliberate controls:

- PAY-011 tests whether the agent avoids inventing a failure.
- PAY-012 tests whether the agent abstains when evidence is insufficient.

## Baseline

The baseline receives all available evidence in one static prompt and produces one structured response.

It has no adaptive tool use, iterative hypothesis testing, evidence verifier, or conclusion safety gate.

## Advanced System

The advanced system adds:

- adaptive read-only tool selection,
- hypothesis-driven investigation,
- contradiction handling,
- deterministic evidence verification,
- causal safety checks,
- explicit abstention behavior.

## Measured Results

Primary comparison: OpenAI baseline vs advanced architecture across the same 12 cases.

| Metric | Baseline | Advanced |
|---|---:|---:|
| Root cause accuracy | 25.00% | 50.00% |
| First-divergence accuracy | 33.33% | 41.67% |
| Evidence coverage | 42.50% | 71.25% |
| Abstention accuracy | 83.33% | 58.33% |
| Safe-action compliance | 91.67% | 91.67% |
| Unsupported claim rate | 0.00% | 0.00% |
| Strict passes | 0/12 | 2/12 |

Root-cause accuracy doubled.

Evidence coverage improved by 28.75 percentage points.

Abstention accuracy decreased by 25 percentage points.

That regression is intentionally reported rather than hidden.

## Main Engineering Lesson

Better reasoning does not automatically mean safer reasoning.

The advanced investigator improved causal diagnosis and evidence quality, but became less conservative in some cases.

This suggests that:

- reasoning quality,
- evidence quality,
- abstention policy,
- and action authorization

should remain separate system concerns.

## Safety

The model cannot autonomously:

- capture payments,
- issue refunds,
- replay webhooks,
- mutate invoices,
- change ledger state.

Its role is investigation and recommendation.

## Provider Support

The system supports OpenAI and Gemini.

The full measured improvement claim uses OpenAI across the same 12 baseline and advanced cases.

Gemini baseline was run across all 12 cases.

Only two advanced Gemini trajectories were captured, so those partial results are retained but are not used for a baseline-versus-advanced improvement claim.

## AI-Assisted Development

Coding and reasoning assistants were used to accelerate implementation, debugging, testing, and iteration.

Architecture, safety boundaries, benchmark design, evaluator semantics, experiment design, and final engineering decisions were reviewed by the project author.

Generated changes were validated using:

- automated tests,
- deterministic fixtures,
- live provider runs,
- saved trajectories,
- benchmark evaluation.

## Hot Take

Financial reconciliation is not primarily an LLM problem.

Where facts can be established deterministically, they should be.

Agents are most useful where ambiguity remains between those facts.

The most valuable decision a financial agent can make is sometimes:

> There is not enough evidence to act.