from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


ReviewStatus = Literal[
    "pending",
    "reviewed",
    "requires_follow_up",
]


class InterventionReviewRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: Literal["reviewed", "requires_follow_up"]
    reviewer_name: str = Field(min_length=2, max_length=80)
    comment: str = Field(default="", max_length=1000)


class InterventionReview(BaseModel):
    model_config = ConfigDict(extra="forbid")

    assessment_id: str
    status: ReviewStatus
    reviewer_name: str | None = None
    comment: str = ""
    reviewed_at: datetime | None = None