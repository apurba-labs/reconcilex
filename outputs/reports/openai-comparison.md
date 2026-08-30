# ReconcileX Openai Benchmark Comparison

| Metric | Baseline | Advanced | Delta |
|---|---:|---:|---:|
| Root cause accuracy | 25.00% | 50.00% | +25.00 pp |
| First divergence accuracy | 33.33% | 41.67% | +8.33 pp |
| Abstention accuracy | 83.33% | 58.33% | -25.00 pp |
| Safe action compliance | 91.67% | 91.67% | 0.00 pp |
| Evidence coverage | 42.50% | 71.25% | +28.75 pp |
| Unsupported claim rate | 0.00% | 0.00% | 0.00 pp |
| Strict case passes | 0/12 | 2/12 | +2 cases |

## Efficiency

- Average tool calls: 0.00 → 6.92
- Average reasoning steps: 1.00 → 22.50

## Interpretation

The baseline is a single-pass model call with all available case evidence supplied up front. The advanced system uses adaptive read-only investigation, structured hypothesis testing, evidence verification, and causal safety controls.

Strict case pass requires all binary criteria to pass, complete required-evidence coverage, and zero unsupported claims. Component metrics are therefore reported alongside strict pass count.
