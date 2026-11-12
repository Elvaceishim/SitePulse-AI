from app.providers.synthetic import SyntheticRiskProvider
from app.services.prioritization import prioritize_risks
from app.services.intervention_engine import generate_interventions


def get_test_interventions():
    provider = SyntheticRiskProvider()

    risks = prioritize_risks(
        provider.get_sites(),
        provider.get_risk_assessments(),
    )

    return generate_interventions(risks)


def test_one_intervention_is_generated_per_risk():
    interventions = get_test_interventions()

    assert len(interventions) == 6


def test_critical_risk_gets_immediate_review():
    interventions = get_test_interventions()

    critical = [
        item for item in interventions
        if item.risk.priority_band.value == "critical"
    ]

    assert len(critical) == 1
    assert critical[0].urgency == "immediate_review"


def test_high_risk_gets_urgent_review():
    interventions = get_test_interventions()

    high_risks = [
        item for item in interventions
        if item.risk.priority_band.value == "high"
    ]

    assert len(high_risks) == 2

    for item in high_risks:
        assert item.urgency == "urgent_review"


def test_every_intervention_requires_human_review():
    interventions = get_test_interventions()

    assert all(
        item.requires_human_review
        for item in interventions
    )


def test_stale_assessment_generates_data_warning():
    interventions = get_test_interventions()

    stale = [
        item for item in interventions
        if item.risk.is_stale
    ]

    assert len(stale) == 1
    assert stale[0].data_warning is not None


def test_recommendations_are_grounded_in_risk_categories():
    interventions = get_test_interventions()

    for item in interventions:
        assert item.recommended_action
        assert item.rationale
        assert item.risk.assessment.description

def test_heat_recommendations_consider_site_industry():
    interventions = get_test_interventions()

    heat_interventions = [
        item for item in interventions
        if item.risk.assessment.category.value == "heat"
    ]

    construction = next(
        item for item in heat_interventions
        if item.risk.site.industry == "Construction"
    )

    manufacturing = next(
        item for item in heat_interventions
        if item.risk.site.industry == "Manufacturing"
    )

    assert "outdoor activities" in construction.recommended_action
    assert "indoor temperature" in manufacturing.recommended_action.lower()