import json
from pathlib import Path

from .case_input import CaseInput


def load_case_inputs(
    path: str | Path,
) -> list[CaseInput]:
    path = Path(path)

    with path.open("r", encoding="utf-8") as file:
        records = json.load(file)

    return [
        CaseInput.model_validate(record)
        for record in records
    ]


def load_case_input(
    path: str | Path,
    case_id: str,
) -> CaseInput:
    cases = load_case_inputs(path)

    for case in cases:
        if case.case_id == case_id:
            return case

    raise KeyError(f"Unknown case: {case_id}")