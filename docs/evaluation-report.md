# ReconcileX Evaluation Report

## Experiment

ReconcileX was evaluated on 12 deterministic payment-reconciliation
cases covering webhook failures, duplicate captures, refunds,
chargebacks, missing captures, settlement exceptions, currency mismatch,
incorrect payment mapping, duplicate webhook processing, valid settlement
delay, and conflicting evidence.

The primary experiment compares the same OpenAI model under two
architectures.

### Baseline

The baseline receives the case and available payment evidence in one
static prompt and produces one structured investigation result.

It has:

- no adaptive tool selection
- no iterative hypothesis testing
- no deterministic evidence verification
- no causal conclusion safety gate

### Advanced ReconcileX

The advanced system uses:

- read-only deterministic payment tools
- iterative hypothesis-driven investigation
- evidence-backed conclusions
- deterministic evidence verification
- causal safety checks
- explicit abstention and human-control boundaries

## Results

| Metric | Baseline | Advanced | Delta |
|---|---:|---:|---:|
| Root cause accuracy | 25.00% | 50.00% | +25.00 pp |
| First-divergence accuracy | 33.33% | 41.67% | +8.33 pp |
| Abstention accuracy | 83.33% | 58.33% | -25.00 pp |
| Safe-action compliance | 91.67% | 91.67% | 0.00 pp |
| Evidence coverage | 42.50% | 71.25% | +28.75 pp |
| Unsupported claim rate | 0.00% | 0.00% | 0.00 pp |
| Strict case passes | 0/12 | 2/12 | +2 cases |

The advanced system used an average of 6.92 read-only tool calls and
22.50 recorded reasoning steps per case, compared with one static model
call for the baseline.

## What improved

The largest gain was evidence coverage, increasing by 28.75 percentage
points. Root-cause accuracy doubled from 25% to 50%.

This supports the central ReconcileX hypothesis: structured investigation
helps a model establish a more defensible causal explanation than a
single-pass prompt, even when both receive access to the same underlying
financial evidence.

## What did not improve

Abstention accuracy decreased from 83.33% to 58.33%.

This is an important failure mode rather than a result to hide. The
advanced investigator sometimes committed to a causal explanation where
the benchmark expected a more conservative outcome.

Safe-action compliance remained unchanged at 91.67%, showing that better
investigation quality did not automatically produce better action safety.

These results suggest that causal reasoning and action authorization
should remain separate system concerns.

## Strict-pass interpretation

A strict case pass requires every binary criterion to be correct,
complete required-evidence coverage, and zero unsupported claims.

For this reason, strict pass count is intentionally much harsher than
individual component metrics. ReconcileX reports both rather than using
a single aggregate score that could hide specific failure modes.

## Provider robustness

The baseline runner was also executed successfully across all 12 cases
with Gemini, demonstrating that the baseline and structured-output
interface are provider-independent.

Only two advanced Gemini trajectories were captured in the current
evaluation run. Those partial results are retained as artifacts but are
not used for a baseline-versus-advanced improvement claim because the
case sets are not equivalent.

## Key finding

Financial-agent quality cannot be measured only by whether the final
answer sounds correct.

ReconcileX separately evaluates:

- causal diagnosis
- first lifecycle divergence
- evidence coverage
- abstention behavior
- action safety
- unsupported claims

The experiment shows measurable gains in diagnosis and evidence quality,
while also exposing a regression in abstention behavior.

That tradeoff is itself an important result.

## Evaluation principle

Facts are deterministic. Investigation is agentic. Action remains
controlled.

The model may form a hypothesis, but it does not get to manufacture
financial truth.