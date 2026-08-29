from enum import Enum
from pydantic import BaseModel, Field

class StepType(str, Enum):
    HYPOTHESIS = "hypothesis"
    TOOL_CALL = "tool_call"
    OBSERVATION = "observation"
    DECISION = "decision"
    FINAL = "final"


class DecisionType(str, Enum):
    SUPPORT = "support"
    REJECT = "reject"
    REVISE = "revise"
    CONTINUE = "continue"
    ABSTAIN = "abstain"
    COMPLETE = "complete"


class ToolCall(BaseModel):
    tool_name: str
    arguments: dict[str, str] = Field(default_factory=dict)


class InvestigationStep(BaseModel):
    step_number: int
    step_type: StepType

    hypothesis_id: str | None = None
    content: str

    tool_call: ToolCall | None = None
    observation_record_ids: list[str] = Field(default_factory=list)

    decision: DecisionType | None = None


class InvestigationTrajectory(BaseModel):
    case_id: str

    steps: list[InvestigationStep] = Field(default_factory=list)

    completed: bool = False
    abstained: bool = False

    def add_step(
        self,
        *,
        step_type: StepType,
        content: str,
        hypothesis_id: str | None = None,
        tool_call: ToolCall | None = None,
        observation_record_ids: list[str] | None = None,
        decision: DecisionType | None = None,
    ) -> InvestigationStep:
        step = InvestigationStep(
            step_number=len(self.steps) + 1,
            step_type=step_type,
            hypothesis_id=hypothesis_id,
            content=content,
            tool_call=tool_call,
            observation_record_ids=observation_record_ids or [],
            decision=decision,
        )

        self.steps.append(step)

        if decision == DecisionType.COMPLETE:
            self.completed = True

        if decision == DecisionType.ABSTAIN:
            self.completed = True
            self.abstained = True

        return step