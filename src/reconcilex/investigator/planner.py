from __future__ import annotations

from enum import Enum
from typing import Protocol

from pydantic import BaseModel, ConfigDict, Field

from reconcilex.domain.case_input import CaseInput
from reconcilex.investigator.models import EvidenceRef
from reconcilex.investigator.trajectory import (
    DecisionType,
    InvestigationTrajectory,
)


class PlannerActionType(str, Enum):
    CALL_TOOL = "call_tool"
    DECIDE = "decide"
    FINISH = "finish"


class PlannedToolArguments(BaseModel):
    model_config = ConfigDict(extra="forbid")

    case_id: str | None = None
    invoice_id: str | None = None
    payment_id: str | None = None
    entity_id: str | None = None


class PlannedToolCall(BaseModel):
    model_config = ConfigDict(extra="forbid")

    tool_name: str
    arguments: PlannedToolArguments = Field(
        default_factory=PlannedToolArguments
    )


class PlannerDecision(BaseModel):
    hypothesis_id: str
    decision: DecisionType
    reason: str


class PlannerAction(BaseModel):
    action_type: PlannerActionType

    hypothesis_id: str | None = None
    hypothesis: str | None = None

    tool_call: PlannedToolCall | None = None
    decision: PlannerDecision | None = None

    evidence: list[EvidenceRef] = Field(
        default_factory=list
    )

    finding: str | None = None
    root_cause: str | None = None
    first_divergence: str | None = None
    recommended_action: str | None = None
    confidence: float | None = None
    requires_human_approval: bool | None = None

    abstained: bool = False
    abstention_reason: str | None = None


class InvestigationPlanner(Protocol):
    def next_action(
        self,
        case_input: CaseInput,
        trajectory: InvestigationTrajectory,
    ) -> PlannerAction:
        ...