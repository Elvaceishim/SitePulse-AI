
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


EvaluationStatus = Literal["pass", "partial", "fail"]


class InterventionExplanationEvaluation(BaseModel):
    model_config = ConfigDict(extra="forbid")

    assessment_id: UUID

    evidence_grounding: EvaluationStatus
    priority_consistency: EvaluationStatus
    freshness_handling: EvaluationStatus
    usefulness: EvaluationStatus

    unsupported_claims: list[str] = Field(default_factory=list)

    feedback: str = Field(min_length=5, max_length=500)


class SiteSummaryEvaluation(BaseModel):
    model_config = ConfigDict(extra="forbid")

    site_id: UUID
    assessment_ids_reviewed: list[UUID] = Field(min_length=1)

    risk_coverage: EvaluationStatus
    evidence_grounding: EvaluationStatus

    unsupported_claims: list[str] = Field(default_factory=list)

    feedback: str = Field(min_length=5, max_length=500)


class BriefingEvaluation(BaseModel):
    model_config = ConfigDict(extra="forbid")

    overall_status: Literal["pass", "needs_review", "fail"]

    intervention_evaluations: list[
        InterventionExplanationEvaluation
    ] = Field(min_length=1)

    site_summary_evaluations: list[
        SiteSummaryEvaluation
    ] = Field(min_length=1)
