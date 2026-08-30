from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

CASE_IDS = [
    f"PAY-{number:03d}"
    for number in range(1, 13)
]


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run the ReconcileX baseline benchmark cases."
    )

    parser.add_argument(
        "--provider",
        choices=["openai", "gemini"],
        required=True,
    )

    args = parser.parse_args()

    failures: list[str] = []

    for index, case_id in enumerate(
        CASE_IDS,
        start=1,
    ):
        print(
            f"\n=== [{index}/12] "
            f"{args.provider.upper()} {case_id} ===\n",
            flush=True,
        )
        
        output_path = (
            Path("outputs/trajectories")
            / f"baseline-{args.provider}"
            / f"{case_id}.json"
        )

        if output_path.exists():
            print(
                f"Skipping {case_id}: "
                "artifact already exists.",
                flush=True,
            )
            continue

        completed = subprocess.run(
            [
                sys.executable,
                "scripts/run_baseline_case.py",
                "--provider",
                args.provider,
                case_id,
            ],
            check=False,
        )

        if completed.returncode != 0:
            failures.append(case_id)

    print("\n=== BASELINE RUN COMPLETE ===")
    print(f"Provider: {args.provider}")
    print(
        f"Succeeded: "
        f"{len(CASE_IDS) - len(failures)}/"
        f"{len(CASE_IDS)}"
    )

    if failures:
        print(
            "Failed cases: "
            + ", ".join(failures)
        )
        raise SystemExit(1)

    print("Failed cases: none")


if __name__ == "__main__":
    main()