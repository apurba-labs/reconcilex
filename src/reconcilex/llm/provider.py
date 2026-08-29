from __future__ import annotations
from typing import Protocol, TypeVar
from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)


class LLMProvider(Protocol):
    def generate_structured(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
        response_model: type[T],
    ) -> T:
        """
        Generate a structured model response.

        Implementations are responsible for:
        - calling the actual model provider,
        - enforcing structured output,
        - validating against response_model,
        - surfacing provider failures cleanly.

        The investigation layer must not depend on
        provider-specific SDK objects or response formats.
        """
        ...