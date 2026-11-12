from datetime import datetime, timezone

from app.models.site import Site
from app.models.risk import RiskAssessment, RiskLevel
from app.models.prioritization import PrioritizedRisk


# Prototype thresholds. These will need validation against
# TheHyWing's actual risk methodology and operational requirements.
def get_priority_band(score: float) -> RiskLevel:
    if score < 30:
        return RiskLevel.LOW
    elif score < 60:
        return RiskLevel.MODERATE
    elif score < 90:
        return RiskLevel.HIGH
    return RiskLevel.CRITICAL


def prioritize_risks(
    sites: list[Site],
    assessments: list[RiskAssessment],
    stale_after_hours: float = 6,
    now: datetime | None = None,
) -> list[PrioritizedRisk]:

    if stale_after_hours <= 0:
        raise ValueError("stale_after_hours must be greater than zero")

    if now is None:
        now = datetime.now(timezone.utc)

    if now.tzinfo is None or now.utcoffset() is None:
        raise ValueError("now must be timezone-aware")

    sites_by_id = {site.id: site for site in sites}

    if len(sites_by_id) != len(sites):
        raise ValueError("Duplicate site IDs found")

    for assessment in assessments:
        if assessment.site_id not in sites_by_id:
            raise ValueError(
                f"Assessment {assessment.id} references an unknown site"
            )

    assessment_counts = {}

    for assessment in assessments:
        assessment_counts[assessment.site_id] = (
            assessment_counts.get(assessment.site_id, 0) + 1
        )

    prioritized = []

    for assessment in assessments:
        site = sites_by_id[assessment.site_id]

        observed_at = assessment.observed_at

        if observed_at.tzinfo is None or observed_at.utcoffset() is None:
            raise ValueError(
                f"Assessment {assessment.id} has a timezone-naive timestamp"
            )

        age_hours = max(
            0.0,
            (now - observed_at).total_seconds() / 3600,
        )

        result = PrioritizedRisk(
            site=site,
            assessment=assessment,
            priority_band=get_priority_band(assessment.score),
            age_hours=round(age_hours, 2),
            is_stale=age_hours > stale_after_hours,
            other_assessments_at_site=(
                assessment_counts[assessment.site_id] - 1
            ),
        )

        prioritized.append(result)

    # Highest risk scores appear first.
    # For equal scores, the more recently observed assessment comes first.
    prioritized.sort(
        key=lambda item: (
            -item.assessment.score,
            -item.assessment.observed_at.timestamp(),
        )
    )

    return prioritized