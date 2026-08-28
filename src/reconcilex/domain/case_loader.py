from pathlib import Path
import yaml

from .case import BenchmarkCase


def load_case(path: str | Path) -> BenchmarkCase:
    path = Path(path)

    with path.open("r", encoding="utf-8") as file:
        data = yaml.safe_load(file)

    return BenchmarkCase.model_validate(data)


def load_cases(directory: str | Path) -> list[BenchmarkCase]:
    directory = Path(directory)

    return [
        load_case(path)
        for path in sorted(directory.glob("PAY-*.yaml"))
    ]