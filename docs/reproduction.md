# ReconcileX Reproduction Guide

## Requirements

- Python 3.12+
- `uv`
- OpenAI or Gemini API credentials for live model runs

## Setup

Clone the repository and install dependencies:

```bash
git clone git@github.com:apurba-labs/reconcilex.git
cd reconcilex
uv sync
```

Create the environment file:

```bash
cp .env.example .env
```

Add one or both provider credentials:

```env
OPENAI_API_KEY=
OPENAI_MODEL=gpt-5.6-sol

GEMINI_API_KEY=
GEMINI_MODEL=gemini-3.5-flash
```

## Verify the Project

Run the test suite:

```bash
uv run pytest -q
```

Expected final project result:

```text
132 passed
```

## Generate Synthetic Data

```bash
uv run python scripts/generate_synthetic_dataset.py
```

The benchmark dataset is synthetic and deterministic.

## Run One Advanced Investigation

Example:

```bash
uv run python scripts/run_agent_case.py \
  --provider openai \
  PAY-008
```

Saved trajectories are written under:

```text
outputs/trajectories/
```

## Run One Baseline Investigation

```bash
uv run python scripts/run_baseline_case.py \
  --provider openai \
  PAY-008
```

## Run the Full Baseline

```bash
uv run python scripts/run_baseline.py \
  --provider openai
```

## Evaluate Advanced Results

```bash
uv run python scripts/run_benchmark.py \
  --provider openai
```

## Evaluate Baseline Results

```bash
uv run python scripts/run_baseline_benchmark.py \
  --provider openai
```

## Compare Baseline and Advanced

```bash
uv run python scripts/compare_benchmarks.py \
  --provider openai \
  --advanced openai-final-v1.json
```

The primary comparison uses the same 12 benchmark cases for baseline and advanced OpenAI runs.

## Saved Artifacts

Important generated artifacts are included under:

```text
outputs/trajectories/
outputs/evaluations/
outputs/reports/
```

The human-readable result summary is available at:

```text
docs/evaluation-report.md
```

## Notes

Live model outputs may vary across future provider/model versions.

The included saved trajectories and evaluation artifacts represent the final benchmark run used for the submission.