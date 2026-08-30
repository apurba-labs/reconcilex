from __future__ import annotations

import argparse
import json
from pathlib import Path

from reconcilex.evaluation.evaluator import (
    CaseEvaluator,
    EvaluationError,
    load_ground_truth,
)
from reconcilex.evaluation.metrics import (
    build_provider_evaluation,
)
from reconcilex.investigator.models import (
    InvestigationResult,
)


TRAJECTORY_ROOT = Path("outputs/trajectories")
EVALUATION_ROOT = Path("outputs/evaluations")

EXPECTED_CASE_IDS = {
    f"PAY-{number:03d}"
    for number in range(1, 13)
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Evaluate saved ReconcileX single-pass "
            "baseline results."
        )
    )

    parser.add_argument(
        "--provider",
        required=True,
        choices=["openai", "gemini"],
    )

    return parser.parse_args()


def evaluate_baseline_artifact(
    path: Path,
):
    try:
        artifact = json.loads(
            path.read_text(
                encoding="utf-8",
            )
        )
    except (OSError, json.JSONDecodeError) as exc:
        raise EvaluationError(
            f"Could not load baseline artifact "
            f"{path}: {exc}"
        ) from exc

    case_id = artifact.get("case_id")

    if not case_id:
        raise EvaluationError(
            "Baseline artifact is missing case_id."
        )

    result_data = artifact.get("result")

    if not isinstance(result_data, dict):
        raise EvaluationError(
            f"Baseline artifact {case_id} "
            "is missing result."
        )

    result = InvestigationResult.model_validate(
        result_data
    )

    if result.case_id != case_id:
        raise EvaluationError(
            f"Result case mismatch: "
            f"artifact={case_id}, "
            f"result={result.case_id}"
        )

    ground_truth = load_ground_truth(
        case_id
    )

    evaluator = CaseEvaluator()

    return evaluator.evaluate(
        result=result,
        ground_truth=ground_truth,
        tool_calls=0,
        reasoning_steps=1,
        trajectory_steps=[],
    )


def main() -> None:
    args = parse_args()

    provider_name = (
        f"baseline-{args.provider}"
    )

    provider_dir = (
        TRAJECTORY_ROOT
        / provider_name
    )

    if not provider_dir.exists():
        raise SystemExit(
            f"Baseline directory does not exist: "
            f"{provider_dir}"
        )

    artifact_paths = sorted(
        provider_dir.glob("PAY-*.json")
    )

    if not artifact_paths:
        raise SystemExit(
            f"No baseline artifacts found for "
            f"{args.provider}"
        )

    evaluations = []

    for path in artifact_paths:
        try:
            evaluation = (
                evaluate_baseline_artifact(
                    path
                )
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

    found_case_ids = {
        path.stem
        for path in artifact_paths
    }

    missing_case_ids = (
        EXPECTED_CASE_IDS
        - found_case_ids
    )

    if missing_case_ids:
        print(
            "\nWARNING: partial baseline benchmark. "
            f"Missing {len(missing_case_ids)} cases: "
            + ", ".join(
                sorted(missing_case_ids)
            )
            + "\n"
        )

    provider_result = (
        build_provider_evaluation(
            provider=provider_name,
            cases=evaluations,
        )
    )

    EVALUATION_ROOT.mkdir(
        parents=True,
        exist_ok=True,
    )

    output_path = (
        EVALUATION_ROOT
        / f"{provider_name}.json"
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
        f"Provider: {provider_name}"
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