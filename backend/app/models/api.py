
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict

from app.models.site import Site
from app.models.risk import RiskAssessment
from app.models.prioritization import PrioritizedRisk
from app.models.intervention import InterventionDraft
from app.models.briefing import BriefingNarrative


class SupervisorBriefingResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    data_source: Literal["synthetic"] = "synthetic"
    generated_at: datetime

    sites: list[Site]
    risk_assessments: list[RiskAssessment]
    prioritized_risks: list[PrioritizedRisk]
    interventions: list[InterventionDraft]

    briefing: BriefingNarrative
