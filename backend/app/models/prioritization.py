from pydantic import BaseModel, ConfigDict

from app.models.site import Site
from app.models.risk import RiskAssessment, RiskLevel


class PrioritizedRisk(BaseModel):
    model_config = ConfigDict(extra="forbid")

    site: Site
    assessment: RiskAssessment
    priority_band: RiskLevel
    age_hours: float
    is_stale: bool
    other_assessments_at_site: int