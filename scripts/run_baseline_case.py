from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from reconcilex.baseline.direct_baseline import DirectBaseline
from reconcilex.config import settings
from reconcilex.domain.case_input_loader import load_case_input
from reconcilex.domain.record_loader import PaymentRecordStore
from reconcilex.llm.gemini_provider import GeminiProvider
from reconcilex.llm.openai_provider import OpenAIProvider
from reconcilex.tools.payment_tools import PaymentTools


def build_provider(provider_name: str) -> Any:
    if provider_name == "openai":
        return OpenAIProvider(
            api_key=settings.openai_api_key,
            model=settings.openai_model,
        )

    if provider_name == "gemini":
        return GeminiProvider(
            api_key=settings.gemini_api_key,
            model=settings.gemini_model,
        )

    raise ValueError(
        f"Unsupported provider: {provider_name}"
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description=("Run the single-pass ReconcileX baseline.")
    )

    parser.add_argument(
        "case_id",
        help="Benchmark case ID, for example PAY-008.",
    )

    parser.add_argument(
        "--provider",
        choices=[
            "openai",
            "gemini",
        ],
        default="openai",
    )

    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("outputs/runs"),
        help=(
            "Directory for live baseline artifacts. "
            "Defaults to outputs/runs so committed "
            "benchmark trajectories remain unchanged."
        ),
    )

    args = parser.parse_args()

    case_input = load_case_input(
        "data/inputs/cases.json",
        args.case_id,
    )

    store = PaymentRecordStore("data/records")

    tools = PaymentTools(store)

    provider = build_provider(args.provider)

    baseline = DirectBaseline(
        provider=provider,
        tools=tools,
    )

    evidence = baseline.collect_evidence(case_input)

    result = baseline.investigate(
        case_input,
        evidence=evidence,
    )

    print("\n=== BASELINE INVESTIGATION RESULT ===\n")

    print(
        json.dumps(
            result.model_dump(
                mode="json"
            ),
            indent=2,
        )
    )

    output_dir = (
        args.output_dir
        / f"baseline-{args.provider}"
    )

    output_dir.mkdir(parents=True, exist_ok=True)

    output_path = (
        output_dir
        / f"{args.case_id}.json"
    )

    output_payload = {
        "mode": "baseline",
        "provider": args.provider,
        "model": provider.model,
        "case_id": args.case_id,
        "result": result.model_dump(
            mode="json"
        ),
        "baseline": {
            "strategy": "single_pass_static_evidence",
            "tool_calls": 0,
            "reasoning_steps": 1,
            "adaptive_tool_use": False,
            "evidence_verifier": False,
            "conclusion_safety_gate": False,
            "supplied_evidence": evidence,
        },
    }

    output_path.write_text(
        json.dumps(
            output_payload,
            indent=2,
        ),
        encoding="utf-8",
    )

    print(f"\nSaved baseline result to {output_path}")


if __name__ == "__main__":
    main()