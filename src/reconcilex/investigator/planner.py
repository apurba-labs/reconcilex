from __future__ import annotations
from enum import Enum
from typing import Protocol
from pydantic import BaseModel, Field

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


class PlannedToolCall(BaseModel):
    tool_name: str
    arguments: dict[str, str] = Field(default_factory=dict)


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

    evidence: list[EvidenceRef] = Field(default_factory=list)

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
        """
        Decide the next investigation step.

        The planner may:
        - propose or revise a hypothesis,
        - request an approved tool call,
        - reject/support a hypothesis,
        - finish with a conclusion,
        - abstain when evidence is insufficient.

        It must not directly access evaluator ground truth.
        """
        ...