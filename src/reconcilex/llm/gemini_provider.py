from __future__ import annotations
from typing import TypeVar

from google import genai
from google.genai import types
from pydantic import BaseModel

from reconcilex.config import settings


T = TypeVar("T", bound=BaseModel)


class GeminiProvider:
    def __init__(
        self,
        *,
        api_key: str | None = None,
        model: str | None = None,
    ) -> None:
        resolved_api_key = api_key or settings.gemini_api_key
        resolved_model = model or settings.gemini_model

        if not resolved_api_key:
            raise ValueError(
                "GEMINI_API_KEY is required to use GeminiProvider."
            )

        if not resolved_model:
            raise ValueError(
                "GEMINI_MODEL is required to use GeminiProvider."
            )

        self.model = resolved_model
        self.client = genai.Client(api_key=resolved_api_key)

    def generate_structured(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
        response_model: type[T],
    ) -> T:
        response = self.client.models.generate_content(
            model=self.model,
            contents=user_prompt,
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
                response_mime_type="application/json",
                response_json_schema=response_model.model_json_schema(),
                temperature=0.2,
            ),
        )

        if not response.text:
            raise RuntimeError(
                "Gemini returned no structured response."
            )

        return response_model.model_validate_json(
            response.text
        )