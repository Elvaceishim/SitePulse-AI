from datetime import datetime, timezone, timedelta

import pytest

from app.providers.synthetic import SyntheticRiskProvider
from app.services.prioritization import prioritize_risks, get_priority_band
from app.models.risk import RiskLevel


def test_risks_are_sorted_highest_score_first():
    provider = SyntheticRiskProvider()

    results = prioritize_risks(
        provider.get_sites(),
        provider.get_risk_assessments(),
    )

    scores = [item.assessment.score for item in results]

    assert scores == sorted(scores, reverse=True)


def test_priority_band_is_derived_from_score():
    assert get_priority_band(20) == RiskLevel.LOW
    assert get_priority_band(45) == RiskLevel.MODERATE
    assert get_priority_band(75) == RiskLevel.HIGH
    assert get_priority_band(95) == RiskLevel.CRITICAL


def test_stale_assessments_are_flagged():
    provider = SyntheticRiskProvider()

    now = datetime.now(timezone.utc)

    results = prioritize_risks(
        provider.get_sites(),
        provider.get_risk_assessments(),
        stale_after_hours=6.1,
        now=now,
    )

    stale_results = [
        item for item in results if item.is_stale
    ]

    assert len(stale_results) == 0


def test_old_assessment_is_flagged_as_stale():
    provider = SyntheticRiskProvider()

    now = datetime.now(timezone.utc)

    assessment = provider.get_risk_assessments()[0].model_copy(
        update={"observed_at": now - timedelta(hours=8)}
    )

    results = prioritize_risks(
        provider.get_sites(),
        [assessment],
        now=now,
    )

    assert results[0].is_stale is True


def test_unknown_site_reference_is_rejected():
    provider = SyntheticRiskProvider()

    assessment = provider.get_risk_assessments()[0].model_copy(
        update={"site_id": "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"}
    )

    with pytest.raises(ValueError, match="unknown site"):
        prioritize_risks(
            provider.get_sites(),
            [assessment],
        )


def test_concurrent_assessments_are_counted():
    provider = SyntheticRiskProvider()

    results = prioritize_risks(
        provider.get_sites(),
        provider.get_risk_assessments(),
    )

    lagos_results = [
        item for item in results
        if item.site.name == "Lagos Construction Site"
    ]

    assert len(lagos_results) == 2
    assert all(
        item.other_assessments_at_site == 1
        for item in lagos_results
    )


def test_stale_threshold_must_be_positive():
    provider = SyntheticRiskProvider()

    with pytest.raises(ValueError):
        prioritize_risks(
            provider.get_sites(),
            provider.get_risk_assessments(),
            stale_after_hours=0,
        )