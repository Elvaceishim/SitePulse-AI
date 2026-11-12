
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class SiteBriefing(BaseModel):
    model_config = ConfigDict(extra="forbid")

    site_id: UUID

    assessment_ids: list[UUID] = Field(
        min_length=1,
        max_length=50,
    )

    summary: str = Field(min_length=10, max_length=400)


class InterventionBriefingNote(BaseModel):
    model_config = ConfigDict(extra="forbid")

    assessment_id: UUID

    priority_explanation: str = Field(
        min_length=10,
        max_length=400,
    )


class BriefingNarrative(BaseModel):
    """Structured narrative returned by the LLM."""

    model_config = ConfigDict(extra="forbid")

    executive_summary: str = Field(
        min_length=20,
        max_length=800,
    )

    site_summaries: list[SiteBriefing] = Field(
        min_length=1,
        max_length=20,
    )

    intervention_notes: list[InterventionBriefingNote] = Field(
        min_length=1,
        max_length=50,
    )
