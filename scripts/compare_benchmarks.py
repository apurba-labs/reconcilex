from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


EVALUATION_ROOT = Path("outputs/evaluations")
REPORT_ROOT = Path("outputs/reports")


METRICS = (
    ("root_cause_accuracy", "Root cause accuracy", True),
    (
        "first_divergence_accuracy",
        "First divergence accuracy",
        True,
    ),
    (
        "abstention_accuracy",
        "Abstention accuracy",
        True,
    ),
    (
        "safe_action_compliance",
        "Safe action compliance",
        True,
    ),
    (
        "average_evidence_coverage",
        "Evidence coverage",
        True,
    ),
    (
        "unsupported_claim_rate",
        "Unsupported claim rate",
        False,
    ),
)


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(
        path.read_text(encoding="utf-8")
    )


def percentage(value: float) -> str:
    return f"{value:.2%}"


def pp(delta: float) -> str:
    sign = "+" if delta > 0 else ""
    return f"{sign}{delta * 100:.2f} pp"


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Compare baseline and advanced "
            "ReconcileX evaluations."
        )
    )

    parser.add_argument(
        "--provider",
        choices=["openai", "gemini"],
        required=True,
    )

    parser.add_argument(
        "--advanced",
        help=(
            "Advanced evaluation filename. "
            "Defaults to <provider>-final-v1.json."
        ),
    )

    args = parser.parse_args()

    baseline_path = (
        EVALUATION_ROOT
        / f"baseline-{args.provider}.json"
    )

    advanced_path = (
        EVALUATION_ROOT
        / (
            args.advanced
            or f"{args.provider}-final-v1.json"
        )
    )

    if not baseline_path.exists():
        raise SystemExit(
            f"Missing baseline evaluation: "
            f"{baseline_path}"
        )

    if not advanced_path.exists():
        raise SystemExit(
            f"Missing advanced evaluation: "
            f"{advanced_path}"
        )

    baseline = load_json(baseline_path)
    advanced = load_json(advanced_path)
    
    if (
        baseline["total_cases"]
        != advanced["total_cases"]
    ):
        raise SystemExit(
            "Cannot compare incomplete benchmarks: "
            f"baseline has {baseline['total_cases']} cases, "
            f"advanced has {advanced['total_cases']} cases."
        )

    metric_rows = []

    for key, label, higher_is_better in METRICS:
        baseline_value = float(
            baseline[key]
        )
        advanced_value = float(
            advanced[key]
        )

        delta = (
            advanced_value
            - baseline_value
        )

        improved = (
            delta > 0
            if higher_is_better
            else delta < 0
        )

        metric_rows.append(
            {
                "metric": key,
                "label": label,
                "baseline": baseline_value,
                "advanced": advanced_value,
                "delta": delta,
                "higher_is_better": higher_is_better,
                "improved": improved,
            }
        )

    baseline_passed = int(
        baseline["passed_cases"]
    )
    advanced_passed = int(
        advanced["passed_cases"]
    )

    comparison = {
        "provider": args.provider,
        "baseline_evaluation": str(
            baseline_path
        ),
        "advanced_evaluation": str(
            advanced_path
        ),
        "total_cases": int(
            advanced["total_cases"]
        ),
        "strict_passes": {
            "baseline": baseline_passed,
            "advanced": advanced_passed,
            "delta": (
                advanced_passed
                - baseline_passed
            ),
        },
        "metrics": metric_rows,
        "efficiency": {
            "average_tool_calls": {
                "baseline": float(
                    baseline["average_tool_calls"]
                ),
                "advanced": float(
                    advanced["average_tool_calls"]
                ),
            },
            "average_reasoning_steps": {
                "baseline": float(
                    baseline[
                        "average_reasoning_steps"
                    ]
                ),
                "advanced": float(
                    advanced[
                        "average_reasoning_steps"
                    ]
                ),
            },
        },
    }

    REPORT_ROOT.mkdir(
        parents=True,
        exist_ok=True,
    )

    json_path = (
        REPORT_ROOT
        / f"{args.provider}-comparison.json"
    )

    json_path.write_text(
        json.dumps(
            comparison,
            indent=2,
        ),
        encoding="utf-8",
    )

    lines = [
        f"# ReconcileX {args.provider.title()} Benchmark Comparison",
        "",
        "| Metric | Baseline | Advanced | Delta |",
        "|---|---:|---:|---:|",
    ]

    for row in metric_rows:
        lines.append(
            f"| {row['label']} "
            f"| {percentage(row['baseline'])} "
            f"| {percentage(row['advanced'])} "
            f"| {pp(row['delta'])} |"
        )

    lines.extend(
        [
            (
                f"| Strict case passes "
                f"| {baseline_passed}/{baseline['total_cases']} "
                f"| {advanced_passed}/{advanced['total_cases']} "
                f"| {advanced_passed - baseline_passed:+d} cases |"
            ),
            "",
            "## Efficiency",
            "",
            (
                "- Average tool calls: "
                f"{baseline['average_tool_calls']:.2f} "
                "→ "
                f"{advanced['average_tool_calls']:.2f}"
            ),
            (
                "- Average reasoning steps: "
                f"{baseline['average_reasoning_steps']:.2f} "
                "→ "
                f"{advanced['average_reasoning_steps']:.2f}"
            ),
            "",
            "## Interpretation",
            "",
            (
                "The baseline is a single-pass model call with all "
                "available case evidence supplied up front. The advanced "
                "system uses adaptive read-only investigation, structured "
                "hypothesis testing, evidence verification, and causal "
                "safety controls."
            ),
            "",
            (
                "Strict case pass requires all binary criteria to pass, "
                "complete required-evidence coverage, and zero unsupported "
                "claims. Component metrics are therefore reported alongside "
                "strict pass count."
            ),
        ]
    )

    md_path = (REPORT_ROOT / f"{args.provider}-comparison.md")

    md_path.write_text(
        "\n".join(lines) + "\n",
        encoding="utf-8",
    )

    print(f"Saved comparison JSON to {json_path}")
    print(f"Saved comparison report to {md_path}")

    print()
    print("\n".join(lines))


if __name__ == "__main__":
    main()