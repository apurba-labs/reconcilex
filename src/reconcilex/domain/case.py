from enum import Enum
from pydantic import BaseModel, Field

class ExpectedOutcome(str, Enum):
    RECONCILIATION_REQUIRED = "reconciliation_required"
    NO_ACTION_REQUIRED = "no_action_required"
    HUMAN_REVIEW_REQUIRED = "human_review_required"


class BenchmarkCase(BaseModel):
    case_id: str
    title: str
    description: str

    expected_root_cause: str
    divergence_stage: str | None = None

    required_evidence: list[str] = Field(default_factory=list)
    misleading_evidence: list[str] = Field(default_factory=list)

    expected_outcome: ExpectedOutcome

    allowed_actions: list[str] = Field(default_factory=list)
    prohibited_actions: list[str] = Field(default_factory=list)

    requires_human_approval: bool = True