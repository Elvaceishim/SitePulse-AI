from datetime import datetime, timezone
from enum import Enum
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, ConfigDict


class RiskCategory(str, Enum):
    HEAT = "heat"
    AIR_QUALITY = "air_quality"
    COLD = "cold"
    OCCUPATIONAL = "occupational"
    OUTBREAK = "outbreak"


class RiskLevel(str, Enum):
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    CRITICAL = "critical"


class RiskAssessment(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: UUID = Field(default_factory=uuid4)

    site_id: UUID

    category: RiskCategory

    risk_level: RiskLevel

    score: float = Field(
        ge=0,
        le=100,
    )

    description: str = Field(
        min_length=5,
        max_length=1000,
    )

    observed_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    source: str = Field(
        min_length=2,
        max_length=100,
    )

    data_is_synthetic: bool = True