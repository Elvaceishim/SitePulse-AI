
import json
import pytest

from app.models.briefing import BriefingNarrative
from app.providers.synthetic import SyntheticRiskProvider
from app.services.prioritization import prioritize_risks
from app.services.intervention_engine import generate_interventions

from app.services.briefing_generator import (
    BriefingGenerator,
    BriefingGenerationError,
)


class MockLLMClient:

    def __init__(self, response):
        self.response = response
        self.received_messages = None

    def generate(self, messages, **kwargs):
        self.received_messages = messages
        return self.response


def get_test_interventions():
    provider = SyntheticRiskProvider()

    risks = prioritize_risks(
        provider.get_sites(),
        provider.get_risk_assessments(),
    )

    return generate_interventions(risks)


def make_valid_response(interventions):
    site_assessments = {}

    for item in interventions:
        site_id = str(item.risk.site.id)
        assessment_id = str(item.risk.assessment.id)

        site_assessments.setdefault(site_id, []).append(
            assessment_id
        )

    site_summaries = [
        {
            "site_id": site_id,
            "assessment_ids": assessment_ids,
            "summary": (
                "This site has one or more risk assessments "
                "requiring supervisor review."
            ),
        }
        for site_id, assessment_ids in site_assessments.items()
    ]

    return json.dumps({
        "executive_summary": (
            "Three sites have active risk assessments requiring "
            "supervisor attention."
        ),
        "site_summaries": site_summaries,
        "intervention_notes": [
            {
                "assessment_id": str(item.risk.assessment.id),
                "priority_explanation": (
                    f"The {item.risk.assessment.category.value} "
                    "assessment has a priority of "
                    f"{item.risk.priority_band.value}."
                ),
            }
            for item in interventions
        ],
    })


def test_valid_briefing_is_generated():
    interventions = get_test_interventions()

    client = MockLLMClient(
        make_valid_response(interventions)
    )

    generator = BriefingGenerator(client=client)

    briefing = generator.generate(interventions)

    assert isinstance(briefing, BriefingNarrative)
    assert len(briefing.site_summaries) == 3
    assert len(briefing.intervention_notes) == 6


def test_empty_interventions_are_rejected():
    generator = BriefingGenerator(
        client=MockLLMClient("{}")
    )

    with pytest.raises(ValueError):
        generator.generate([])


def test_invalid_json_is_rejected():
    interventions = get_test_interventions()

    generator = BriefingGenerator(
        client=MockLLMClient("This is not JSON.")
    )

    with pytest.raises(BriefingGenerationError):
        generator.generate(interventions)


def test_unknown_assessment_id_is_rejected():
    interventions = get_test_interventions()

    response = json.loads(
        make_valid_response(interventions)
    )

    response["intervention_notes"][0]["assessment_id"] = (
        "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"
    )

    generator = BriefingGenerator(
        client=MockLLMClient(json.dumps(response))
    )

    with pytest.raises(
        BriefingGenerationError,
        match="assessment references",
    ):
        generator.generate(interventions)


def test_missing_site_summary_is_rejected():
    interventions = get_test_interventions()

    response = json.loads(
        make_valid_response(interventions)
    )

    response["site_summaries"].pop()

    generator = BriefingGenerator(
        client=MockLLMClient(json.dumps(response))
    )

    with pytest.raises(
        BriefingGenerationError,
        match="site references",
    ):
        generator.generate(interventions)


def test_duplicate_assessment_id_is_rejected():
    interventions = get_test_interventions()

    response = json.loads(
        make_valid_response(interventions)
    )

    response["intervention_notes"][1]["assessment_id"] = (
        response["intervention_notes"][0]["assessment_id"]
    )

    generator = BriefingGenerator(
        client=MockLLMClient(json.dumps(response))
    )

    with pytest.raises(
        BriefingGenerationError,
        match="duplicate assessment",
    ):
        generator.generate(interventions)


def test_llm_receives_structured_risk_data():
    interventions = get_test_interventions()

    client = MockLLMClient(
        make_valid_response(interventions)
    )

    generator = BriefingGenerator(client=client)
    generator.generate(interventions)

    user_message = client.received_messages[1]["content"]

    assert "Lagos Construction Site" in user_message
    assert "recommended_action" in user_message
    assert "data_is_synthetic" in user_message


def test_assessment_from_another_site_is_rejected():
    interventions = get_test_interventions()
    response = json.loads(make_valid_response(interventions))

    first_site = response["site_summaries"][0]
    second_site = response["site_summaries"][1]

    # Replace the first site's assessment with one
    # that belongs to the second site.
    first_site["assessment_ids"][0] = (
        second_site["assessment_ids"][0]
    )

    briefing = BriefingNarrative.model_validate(response)

    with pytest.raises(
        BriefingGenerationError,
        match="incorrectly assigned assessments",
    ):
        BriefingGenerator._validate_references(
            briefing,
            interventions,
        )



def test_missing_assessment_from_site_summary_is_rejected():
    interventions = get_test_interventions()
    response = json.loads(make_valid_response(interventions))

    # Remove one assessment to simulate incomplete coverage.
    response["site_summaries"][0]["assessment_ids"].pop()

    briefing = BriefingNarrative.model_validate(response)

    with pytest.raises(
        BriefingGenerationError,
        match="incorrectly assigned assessments",
    ):
        BriefingGenerator._validate_references(
            briefing,
            interventions,
        )



def test_duplicate_assessment_within_site_summary_is_rejected():
    interventions = get_test_interventions()
    response = json.loads(make_valid_response(interventions))

    assessment_ids = response["site_summaries"][0]["assessment_ids"]

    # Duplicate an existing assessment reference.
    assessment_ids.append(assessment_ids[0])

    briefing = BriefingNarrative.model_validate(response)

    with pytest.raises(
        BriefingGenerationError,
        match="duplicate assessment",
    ):
        BriefingGenerator._validate_references(
            briefing,
            interventions,
        )