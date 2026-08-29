from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from reconcilex.config import settings
from reconcilex.domain.case_input_loader import load_case_input
from reconcilex.domain.record_loader import PaymentRecordStore
from reconcilex.investigator.agent import AgentInvestigator
from reconcilex.investigator.model_planner import ModelPlanner
from reconcilex.investigator.tool_executor import ToolExecutor
from reconcilex.investigator.verifier import EvidenceVerifier
from reconcilex.llm.gemini_provider import GeminiProvider
from reconcilex.llm.openai_provider import OpenAIProvider
from reconcilex.tools.payment_tools import PaymentTools


def build_provider(provider_name: str) -> Any:
    if provider_name == "gemini":
        return GeminiProvider(
            api_key=settings.gemini_api_key,
            model=settings.gemini_model,
        )

    if provider_name == "openai":
        return OpenAIProvider(
            api_key=settings.openai_api_key,
            model=settings.openai_model,
        )

    raise ValueError(
        f"Unsupported provider: {provider_name}"
    )


def build_agent(
    provider_name: str,
) -> tuple[AgentInvestigator, Any]:
    store = PaymentRecordStore("data/records")
    tools = PaymentTools(store)

    provider = build_provider(provider_name)

    agent = AgentInvestigator(
        planner=ModelPlanner(provider),
        executor=ToolExecutor(tools),
        verifier=EvidenceVerifier(store),
        max_steps=12,
    )

    return agent, provider


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run a ReconcileX agent investigation."
    )

    parser.add_argument(
        "case_id",
        help="Benchmark case ID, for example PAY-008.",
    )

    parser.add_argument(
        "--provider",
        choices=["gemini", "openai"],
        default="gemini",
        help="LLM provider to use. Defaults to gemini.",
    )

    args = parser.parse_args()

    case_input = load_case_input(
        "data/inputs/cases.json",
        args.case_id,
    )

    agent, provider = build_agent(args.provider)

    result, trajectory = agent.investigate(case_input)

    print("\n=== INVESTIGATION RESULT ===\n")
    print(
        json.dumps(
            result.model_dump(mode="json"),
            indent=2,
        )
    )

    print("\n=== AGENT TRAJECTORY ===\n")
    print(
        json.dumps(
            trajectory.model_dump(mode="json"),
            indent=2,
        )
    )

    output_dir = (
        Path("outputs/trajectories")
        / args.provider
    )
    output_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    output_path = output_dir / f"{args.case_id}.json"

    output_payload = {
        "provider": args.provider,
        "model": provider.model,
        "case_id": args.case_id,
        "result": result.model_dump(mode="json"),
        "trajectory": trajectory.model_dump(mode="json"),
    }

    output_path.write_text(
        json.dumps(
            output_payload,
            indent=2,
        ),
        encoding="utf-8",
    )

    print(
        f"\nSaved trajectory to {output_path}"
    )


if __name__ == "__main__":
    main()