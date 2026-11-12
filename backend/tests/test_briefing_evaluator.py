
import json
from uuid import uuid4

import pytest

from app.models.briefing import (
    BriefingNarrative,
    SiteBriefing,
    InterventionBriefingNote,
)
from app.models.evaluation import BriefingEvaluation
from app.providers.synthetic import SyntheticRiskProvider
from app.services.briefing_evaluator import (
    BriefingEvaluator,
    BriefingEvaluationError,
)
from app.services.intervention_engine import generate_interventions
from app.services.prioritization import prioritize_risks


class MockEvaluatorClient:

    def __init__(self, response):
        self.response = response
        self.received_messages = None

    def generate(self, messages, temperature, max_tokens):
        self.received_messages = messages
        return self.response


def get_test_interventions():
    provider = SyntheticRiskProvider()

    risks = prioritize_risks(
        sites=provider.get_sites(),
        assessments=provider.get_risk_assessments(),
    )

    return generate_interventions(risks)


def make_valid_briefing(interventions):
    sites = {}
    site_summaries = []
    intervention_notes = []

    for item in interventions:
        site = item.risk.site
        assessment = item.risk.assessment

        sites.setdefault(
            site.id,
            {
                "site_id": site.id,
                "assessment_ids": [],
            },
        )

        sites[site.id]["assessment_ids"].append(
            assessment.id
        )

        intervention_notes.append(
            InterventionBriefingNote(
                assessment_id=assessment.id,
                priority_explanation=(
                    f"The {assessment.category.value} assessment "
                    f"has a score of {assessment.score} and "
                    f"a {item.risk.priority_band.value} priority."
                ),
            )
        )

    for site_id, site_data in sites.items():
        site_summaries.append(
            SiteBriefing(
                site_id=site_id,
                assessment_ids=site_data["assessment_ids"],
                summary="The site has multiple risk assessments requiring review.",
            )
        )

    return BriefingNarrative(
        executive_summary=(
            "Three sites have six synthetic risk assessments requiring review."
        ),
        site_summaries=site_summaries,
        intervention_notes=intervention_notes,
    )


def make_valid_evaluation(interventions):
    site_assessments = {}

    for item in interventions:
        site_id = item.risk.site.id
        assessment_id = item.risk.assessment.id

        site_assessments.setdefault(
            site_id,
            [],
        ).append(assessment_id)

    return {
        "overall_status": "pass",
        "intervention_evaluations": [
            {
                "assessment_id": str(item.risk.assessment.id),
                "evidence_grounding": "pass",
                "priority_consistency": "pass",
                "freshness_handling": "pass",
                "usefulness": "pass",
                "unsupported_claims": [],
                "feedback": "The explanation is supported by the supplied assessment data.",
            }
            for item in interventions
        ],
        "site_summary_evaluations": [
            {
                "site_id": str(site_id),
                "assessment_ids_reviewed": [
                    str(assessment_id)
                    for assessment_id in assessment_ids
                ],
                "risk_coverage": "pass",
                "evidence_grounding": "pass",
                "unsupported_claims": [],
                "feedback": "The summary covers the site's supplied risk assessments.",
            }
            for site_id, assessment_ids in site_assessments.items()
        ],
    }


def get_evaluator(interventions, response):
    briefing = make_valid_briefing(interventions)
    client = MockEvaluatorClient(response)

    return (
        BriefingEvaluator(client=client),
        briefing,
        client,
    )


def test_valid_evaluation_is_generated():
    interventions = get_test_interventions()
    response = json.dumps(
        make_valid_evaluation(interventions)
    )

    evaluator, briefing, _ = get_evaluator(
        interventions,
        response,
    )

    evaluation = evaluator.evaluate(
        briefing,
        interventions,
    )

    assert isinstance(evaluation, BriefingEvaluation)
    assert evaluation.overall_status == "pass"
    assert len(evaluation.intervention_evaluations) == 6
    assert len(evaluation.site_summary_evaluations) == 3


def test_empty_interventions_are_rejected():
    evaluator = BriefingEvaluator(
        client=MockEvaluatorClient("{}")
    )

    with pytest.raises(
        ValueError,
        match="At least one intervention",
    ):
        evaluator.evaluate(
            make_valid_briefing(get_test_interventions()),
            [],
        )


def test_invalid_evaluation_json_is_rejected():
    interventions = get_test_interventions()

    evaluator, briefing, _ = get_evaluator(
        interventions,
        "This is not valid JSON",
    )

    with pytest.raises(
        BriefingEvaluationError,
        match="invalid evaluation JSON",
    ):
        evaluator.evaluate(
            briefing,
            interventions,
        )


def test_unknown_assessment_id_is_rejected():
    interventions = get_test_interventions()
    response = make_valid_evaluation(interventions)

    response["intervention_evaluations"][0]["assessment_id"] = (
        str(uuid4())
    )

    evaluator, briefing, _ = get_evaluator(
        interventions,
        json.dumps(response),
    )

    with pytest.raises(
        BriefingEvaluationError,
        match="assessment references",
    ):
        evaluator.evaluate(
            briefing,
            interventions,
        )


def test_missing_site_evaluation_is_rejected():
    interventions = get_test_interventions()
    response = make_valid_evaluation(interventions)

    response["site_summary_evaluations"].pop()

    evaluator, briefing, _ = get_evaluator(
        interventions,
        json.dumps(response),
    )

    with pytest.raises(
        BriefingEvaluationError,
        match="site references",
    ):
        evaluator.evaluate(
            briefing,
            interventions,
        )


def test_duplicate_assessment_evaluation_is_rejected():
    interventions = get_test_interventions()
    response = make_valid_evaluation(interventions)

    duplicate = response["intervention_evaluations"][0].copy()

    response["intervention_evaluations"].append(
        duplicate
    )

    evaluator, briefing, _ = get_evaluator(
        interventions,
        json.dumps(response),
    )

    with pytest.raises(
        BriefingEvaluationError,
        match="duplicate assessment",
    ):
        evaluator.evaluate(
            briefing,
            interventions,
        )


def test_assessment_from_another_site_is_rejected():
    interventions = get_test_interventions()
    response = make_valid_evaluation(interventions)

    first_site = response["site_summary_evaluations"][0]
    second_site = response["site_summary_evaluations"][1]

    first_site["assessment_ids_reviewed"][0] = (
        second_site["assessment_ids_reviewed"][0]
    )

    evaluator, briefing, _ = get_evaluator(
        interventions,
        json.dumps(response),
    )

    with pytest.raises(
        BriefingEvaluationError,
        match="incorrectly assigned site assessments",
    ):
        evaluator.evaluate(
            briefing,
            interventions,
        )


def test_evaluator_receives_briefing_and_risk_data():
    interventions = get_test_interventions()
    response = json.dumps(
        make_valid_evaluation(interventions)
    )

    evaluator, briefing, client = get_evaluator(
        interventions,
        response,
    )

    evaluator.evaluate(
        briefing,
        interventions,
    )

    assert client.received_messages is not None
    assert len(client.received_messages) == 2

    user_message = client.received_messages[1]["content"]

    assert "executive_summary" in user_message
    assert "priority_explanation" in user_message
    assert "assessment_id" in user_message
    assert "recommended_action" in user_message
