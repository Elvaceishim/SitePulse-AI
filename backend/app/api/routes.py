
from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException

from app.models.api import SupervisorBriefingResponse
from app.models.site import Site
from app.providers.synthetic import SyntheticRiskProvider

from app.services.prioritization import prioritize_risks
from app.services.intervention_engine import generate_interventions
from app.services.briefing_generator import (
    BriefingGenerator,
    BriefingGenerationError,
)

from uuid import UUID

from app.models.review import (
    InterventionReview,
    InterventionReviewRequest,
)
from app.services.review_store import (
    get_review,
    get_reviews,
    initialise_review_store,
    save_review,
)

router = APIRouter()

provider = SyntheticRiskProvider()
initialise_review_store()


@router.get("/sites", response_model=list[Site])
def get_sites():
    return provider.get_sites()


@router.post(
    "/briefings/generate",
    response_model=SupervisorBriefingResponse,
)
def generate_supervisor_briefing():

    sites = provider.get_sites()
    assessments = provider.get_risk_assessments()

    try:
        # Step 1: Prioritise the risk assessments.
        risks = prioritize_risks(
            sites=sites,
            assessments=assessments,
        )

        # Step 2: Generate deterministic interventions.
        interventions = generate_interventions(risks)

        # Step 3: Generate the AI briefing.
        generator = BriefingGenerator()
        briefing = generator.generate(interventions)

    except BriefingGenerationError as exc:
        raise HTTPException(
            status_code=502,
            detail="AI briefing generation failed.",
        ) from exc

    except ValueError as exc:
        raise HTTPException(
            status_code=422,
            detail=str(exc),
        ) from exc

    return SupervisorBriefingResponse(
        data_source="synthetic",
        generated_at=datetime.now(timezone.utc),
        sites=sites,
        risk_assessments=assessments,
        prioritized_risks=risks,
        interventions=interventions,
        briefing=briefing,
    )

@router.get(
    "/interventions/reviews",
    response_model=list[InterventionReview],
)
def list_intervention_reviews():
    return get_reviews()


@router.get(
    "/interventions/{assessment_id}/review",
    response_model=InterventionReview | None,
)
def get_intervention_review(assessment_id: UUID):
    valid_assessment_ids = {
        str(assessment.id)
        for assessment in provider.get_risk_assessments()
    }

    if str(assessment_id) not in valid_assessment_ids:
        raise HTTPException(
            status_code=404,
            detail="Risk assessment not found.",
        )

    return get_review(str(assessment_id))


@router.put(
    "/interventions/{assessment_id}/review",
    response_model=InterventionReview,
)
def submit_intervention_review(
    assessment_id: UUID,
    review: InterventionReviewRequest,
):
    valid_assessment_ids = {
        str(assessment.id)
        for assessment in provider.get_risk_assessments()
    }

    if str(assessment_id) not in valid_assessment_ids:
        raise HTTPException(
            status_code=404,
            detail="Risk assessment not found.",
        )

    return save_review(str(assessment_id), review)