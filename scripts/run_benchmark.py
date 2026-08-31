from __future__ import annotations

import argparse
import json
from pathlib import Path

from reconcilex.evaluation.evaluator import (
    EvaluationError,
    evaluate_trajectory,
)
from reconcilex.evaluation.metrics import (
    build_provider_evaluation,
)


TRAJECTORY_ROOT = Path("outputs/trajectories")
EVALUATION_ROOT = Path("outputs/evaluations")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Evaluate saved ReconcileX trajectories."
    )

    parser.add_argument(
        "--provider",
        required=True,
        choices=["openai", "gemini"],
        help="Provider trajectory directory to evaluate.",
    )

    parser.add_argument(
        "--allow-partial",
        action="store_true",
        help=(
            "Allow evaluation of an incomplete benchmark. "
            "Partial results are exploratory and should not "
            "be used for measured-improvement claims."
        ),
    )

    return parser.parse_args()


def main() -> None:
    args = parse_args()

    provider_dir = (
        TRAJECTORY_ROOT
        / args.provider
    )

    if not provider_dir.exists():
        raise SystemExit(
            f"Trajectory directory does not exist: "
            f"{provider_dir}"
        )

    trajectory_paths = sorted(
        provider_dir.glob("PAY-*.json")
    )

    if not trajectory_paths:
        raise SystemExit(
            f"No trajectories found for provider "
            f"{args.provider}"
        )

    evaluations = []

    for path in trajectory_paths:
        try:
            evaluation = evaluate_trajectory(
                path
            )
        except EvaluationError as exc:
            print(
                f"[FAIL] {path.name}: {exc}"
            )
            continue

        evaluations.append(
            evaluation
        )

        status = (
            "PASS"
            if evaluation.passed
            else "FAIL"
        )

        print(
            f"[{status}] "
            f"{evaluation.case_id} "
            f"root={evaluation.root_cause_correct} "
            f"divergence={evaluation.first_divergence_correct} "
            f"abstention={evaluation.abstention_correct} "
            f"action={evaluation.safe_action_compliant} "
            f"evidence={evaluation.evidence_coverage:.2f}"
        )

    EXPECTED_CASE_IDS = {
        f"PAY-{number:03d}"
        for number in range(1, 13)
    }

    found_case_ids = {
        path.stem
        for path in trajectory_paths
    }

    missing_case_ids = (
        EXPECTED_CASE_IDS - found_case_ids
    )

    if missing_case_ids:
        message = (
            "Partial benchmark detected. "
            f"Missing {len(missing_case_ids)} cases: "
            + ", ".join(sorted(missing_case_ids))
        )

        if not args.allow_partial:
            raise SystemExit(
                message
                + "\nRefusing to publish an incomplete benchmark. "
                "Use --allow-partial only for exploratory runs."
            )

        print(
            "\nWARNING: "
            + message
            + "\n"
        )

    provider_result = (
        build_provider_evaluation(
            provider=args.provider,
            cases=evaluations,
        )
    )

    EVALUATION_ROOT.mkdir(
        parents=True,
        exist_ok=True,
    )

    output_path = (
        EVALUATION_ROOT
        / f"{args.provider}.json"
    )

    output_path.write_text(
        json.dumps(
            provider_result.model_dump(),
            indent=2,
        ),
        encoding="utf-8",
    )

    print()
    print(
        f"Provider: {args.provider}"
    )
    print(
        f"Cases: "
        f"{provider_result.passed_cases}/"
        f"{provider_result.total_cases} passed"
    )
    print(
        f"Root cause accuracy: "
        f"{provider_result.root_cause_accuracy:.2%}"
    )
    print(
        f"First divergence accuracy: "
        f"{provider_result.first_divergence_accuracy:.2%}"
    )
    print(
        f"Abstention accuracy: "
        f"{provider_result.abstention_accuracy:.2%}"
    )
    print(
        f"Safe action compliance: "
        f"{provider_result.safe_action_compliance:.2%}"
    )
    print(
        f"Evidence coverage: "
        f"{provider_result.average_evidence_coverage:.2%}"
    )
    print(
        f"Unsupported claim rate: "
        f"{provider_result.unsupported_claim_rate:.2f}"
    )
    print(
        f"Average tool calls: "
        f"{provider_result.average_tool_calls:.2f}"
    )
    print(
        f"Average reasoning steps: "
        f"{provider_result.average_reasoning_steps:.2f}"
    )

    print(
        f"\nSaved evaluation to {output_path}"
    )


if __name__ == "__main__":
    main()