
import pytest
from pydantic import ValidationError

from app.models.site import Site
from app.models.risk import (
    RiskAssessment,
    RiskCategory,
    RiskLevel,
)


def test_valid_site_creation():
    site = Site(
        name="Lagos Construction Site",
        location="Lagos, Nigeria",
        industry="Construction",
        workforce_size=150,
    )

    assert site.name == "Lagos Construction Site"
    assert site.workforce_size == 150
    assert site.active is True
    assert site.id is not None


def test_site_rejects_invalid_workforce_size():
    with pytest.raises(ValidationError):
        Site(
            name="Lagos Site",
            location="Lagos",
            industry="Construction",
            workforce_size=0,
        )


def test_valid_risk_assessment():
    assessment = RiskAssessment(
        site_id="12345678-1234-5678-1234-567812345678",
        category=RiskCategory.HEAT,
        risk_level=RiskLevel.HIGH,
        score=85,
        description="Elevated heat exposure detected.",
        source="Synthetic provider",
    )

    assert assessment.score == 85
    assert assessment.category == RiskCategory.HEAT
    assert assessment.data_is_synthetic is True


def test_risk_score_cannot_exceed_100():
    with pytest.raises(ValidationError):
        RiskAssessment(
            site_id="12345678-1234-5678-1234-567812345678",
            category=RiskCategory.HEAT,
            risk_level=RiskLevel.HIGH,
            score=120,
            description="Elevated heat exposure detected.",
            source="Synthetic provider",
        )


def test_risk_score_cannot_be_negative():
    with pytest.raises(ValidationError):
        RiskAssessment(
            site_id="12345678-1234-5678-1234-567812345678",
            category=RiskCategory.HEAT,
            risk_level=RiskLevel.HIGH,
            score=-5,
            description="Elevated heat exposure detected.",
            source="Synthetic provider",
        )


def test_invalid_risk_category_is_rejected():
    with pytest.raises(ValidationError):
        RiskAssessment(
            site_id="12345678-1234-5678-1234-567812345678",
            category="earthquake",
            risk_level=RiskLevel.HIGH,
            score=85,
            description="Test assessment.",
            source="Synthetic provider",
        )


def test_assessment_generates_unique_ids():
    common = {
        "site_id": "12345678-1234-5678-1234-567812345678",
        "category": RiskCategory.HEAT,
        "risk_level": RiskLevel.HIGH,
        "score": 85,
        "description": "Elevated heat exposure detected.",
        "source": "Synthetic provider",
    }

    first = RiskAssessment(**common)
    second = RiskAssessment(**common)

    assert first.id != second.id


def test_timestamp_is_timezone_aware():
    assessment = RiskAssessment(
        site_id="12345678-1234-5678-1234-567812345678",
        category=RiskCategory.HEAT,
        risk_level=RiskLevel.HIGH,
        score=85,
        description="Elevated heat exposure detected.",
        source="Synthetic provider",
    )

    assert assessment.observed_at.tzinfo is not None
