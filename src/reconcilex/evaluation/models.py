from __future__ import annotations

from pydantic import BaseModel, Field


class CaseEvaluation(BaseModel):
    case_id: str

    root_cause_correct: bool
    first_divergence_correct: bool
    abstention_correct: bool
    safe_action_compliant: bool

    evidence_coverage: float = Field(ge=0.0, le=1.0)
    unsupported_claims: int = Field(ge=0)

    tool_calls: int = Field(ge=0)
    reasoning_steps: int = Field(ge=0)

    passed: bool

    notes: list[str] = Field(default_factory=list)


class ProviderEvaluation(BaseModel):
    provider: str
    cases: list[CaseEvaluation]

    total_cases: int = Field(ge=0)
    passed_cases: int = Field(ge=0)

    root_cause_accuracy: float = Field(ge=0.0, le=1.0)
    first_divergence_accuracy: float = Field(ge=0.0, le=1.0)
    abstention_accuracy: float = Field(ge=0.0, le=1.0)
    safe_action_compliance: float = Field(ge=0.0, le=1.0)
    average_evidence_coverage: float = Field(ge=0.0, le=1.0)

    unsupported_claim_rate: float = Field(ge=0.0)

    average_tool_calls: float = Field(ge=0.0)
    average_reasoning_steps: float = Field(ge=0.0)