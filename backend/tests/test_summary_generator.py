from app.providers.synthetic import SyntheticRiskProvider
from app.services.prioritization import prioritize_risks
from app.services.intervention_engine import generate_interventions
from app.services.summary_generator import generate_executive_summary


def get_test_interventions():
    provider = SyntheticRiskProvider()

    prioritized = prioritize_risks(
        provider.get_sites(),
        provider.get_risk_assessments(),
    )

    return generate_interventions(prioritized)


def test_summary_includes_site_and_assessment_counts():
    interventions = get_test_interventions()

    summary = generate_executive_summary(interventions)

    assert "3 sites" in summary
    assert "6 risk assessments" in summary


def test_summary_includes_all_risk_categories():
    interventions = get_test_interventions()

    summary = generate_executive_summary(interventions)

    for category in ["heat", "air_quality", "occupational", "outbreak"]:
        assert category in summary


def test_summary_identifies_highest_priority_assessment():
    interventions = get_test_interventions()

    summary = generate_executive_summary(interventions)

    assert "Lagos Construction Site" in summary
    assert "92/100" in summary
    assert "critical" in summary


def test_summary_reports_stale_assessments():
    interventions = get_test_interventions()

    summary = generate_executive_summary(interventions)

    assert "1 assessment(s) require verification" in summary


def test_empty_interventions_are_rejected():
    import pytest

    with pytest.raises(ValueError):
        generate_executive_summary([])