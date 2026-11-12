from pydantic import BaseModel, ConfigDict, Field

from app.models.prioritization import PrioritizedRisk


class InterventionDraft(BaseModel):
    model_config = ConfigDict(extra="forbid")

    risk: PrioritizedRisk

    recommended_action: str = Field(min_length=10)
    rationale: str = Field(min_length=10)

    urgency: str
    requires_human_review: bool = True
    data_warning: str | None = None