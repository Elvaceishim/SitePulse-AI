
from uuid import uuid4

import pytest
from pydantic import ValidationError

from app.models.briefing import (
    BriefingNarrative,
    SiteBriefing,
    InterventionBriefingNote,
)


def test_valid_briefing_narrative():
    site_id = uuid4()
    assessment_id = uuid4()

    briefing = BriefingNarrative(
        executive_summary=(
            "Three sites have active risk signals requiring "
            "supervisor attention."
        ),
        site_summaries=[
            SiteBriefing(
                site_id=site_id,
                assessment_ids=[assessment_id],
                summary=(
                    "The site has a critical heat exposure "
                    "assessment requiring immediate review."
                ),
            )
        ],
        intervention_notes=[
            InterventionBriefingNote(
                assessment_id=assessment_id,
                priority_explanation=(
                    "The heat assessment has the highest "
                    "priority in the current dataset."
                ),
            )
        ],
    )

    assert briefing.site_summaries[0].site_id == site_id
    assert (
        briefing.intervention_notes[0].assessment_id
        == assessment_id
    )


def test_empty_executive_summary_is_rejected():
    with pytest.raises(ValidationError):
        BriefingNarrative(
            executive_summary="",
            site_summaries=[
                {
                    "site_id": str(uuid4()),
                    "summary": "A valid site summary.",
                }
            ],
            intervention_notes=[
                {
                    "assessment_id": str(uuid4()),
                    "note": "A valid intervention note.",
                }
            ],
        )


def test_invalid_site_id_is_rejected():
    with pytest.raises(ValidationError):
        SiteBriefing(
            site_id="not-a-valid-uuid",
            summary="A valid site summary.",
        )


def test_unexpected_fields_are_rejected():
    with pytest.raises(ValidationError):
        SiteBriefing(
            site_id=uuid4(),
            summary="A valid site summary.",
            risk_score=100,
        )


def test_empty_intervention_notes_are_rejected():
    with pytest.raises(ValidationError):
        BriefingNarrative(
            executive_summary=(
                "Three sites have active risk signals requiring "
                "supervisor attention."
            ),
            site_summaries=[
                {
                    "site_id": str(uuid4()),
                    "summary": "A valid site summary.",
                }
            ],
            intervention_notes=[],
        )
