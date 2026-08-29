from enum import Enum
from pydantic import BaseModel, Field

class HypothesisStatus(str, Enum):
    ACTIVE = "active"
    SUPPORTED = "supported"
    REJECTED = "rejected"
    INCONCLUSIVE = "inconclusive"


class EvidenceRef(BaseModel):
    source: str
    record_id: str
    claim: str


class Hypothesis(BaseModel):
    hypothesis_id: str
    description: str
    status: HypothesisStatus = HypothesisStatus.ACTIVE
    supporting_evidence: list[EvidenceRef] = Field(default_factory=list)
    contradicting_evidence: list[EvidenceRef] = Field(default_factory=list)


class InvestigationResult(BaseModel):
    case_id: str
    reported_issue: str

    hypotheses: list[Hypothesis] = Field(default_factory=list)

    finding: str | None = None
    root_cause: str | None = None
    first_divergence: str | None = None

    evidence: list[EvidenceRef] = Field(default_factory=list)
    contradictory_evidence: list[EvidenceRef] = Field(default_factory=list)

    confidence: float = Field(ge=0.0, le=1.0)

    recommended_action: str
    requires_human_approval: bool

    abstained: bool = False
    abstention_reason: str | None = None