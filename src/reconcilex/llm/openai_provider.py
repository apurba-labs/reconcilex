from __future__ import annotations

from typing import TypeVar

from openai import OpenAI
from pydantic import BaseModel


T = TypeVar("T", bound=BaseModel)


class OpenAIProvider:
    def __init__(
        self,
        *,
        api_key: str,
        model: str,
    ) -> None:
        self.client = OpenAI(api_key=api_key)
        self.model = model

    def generate_structured(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
        response_model: type[T],
    ) -> T:
        response = self.client.responses.parse(
            model=self.model,
            instructions=system_prompt,
            input=user_prompt,
            text_format=response_model,
        )

        parsed = response.output_parsed

        if parsed is None:
            raise RuntimeError(
                "OpenAI returned no structured response."
            )

        return parsed