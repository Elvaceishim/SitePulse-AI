from datetime import datetime, timezone, timedelta
from uuid import uuid4

from app.models.site import Site
from app.models.risk import RiskAssessment, RiskCategory, RiskLevel
from app.providers.base import RiskDataProvider


class SyntheticRiskProvider(RiskDataProvider):

    def __init__(self):
        self.sites = self._create_sites()
        self.assessments = self._create_assessments()

    def get_sites(self) -> list[Site]:
        return self.sites

    def get_risk_assessments(self) -> list[RiskAssessment]:
        return self.assessments

    def _create_sites(self) -> list[Site]:
        return [
            Site(
                id=uuid4(),
                name="Lagos Construction Site",
                location="Lagos, Nigeria",
                industry="Construction",
                workforce_size=150,
            ),
            Site(
                id=uuid4(),
                name="Abuja Manufacturing Plant",
                location="Abuja, Nigeria",
                industry="Manufacturing",
                workforce_size=220,
            ),
            Site(
                id=uuid4(),
                name="Kano Agricultural Facility",
                location="Kano, Nigeria",
                industry="Agriculture",
                workforce_size=85,
            ),
        ]

    def _create_assessments(self) -> list[RiskAssessment]:
        now = datetime.now(timezone.utc)

        site_assessments = [
            # Lagos construction site
            {
                "site_index": 0,
                "category": RiskCategory.HEAT,
                "risk_level": RiskLevel.CRITICAL,
                "score": 92,
                "description": "Very high heat exposure during outdoor construction activities.",
                "hours_old": 1,
            },
            {
                "site_index": 0,
                "category": RiskCategory.AIR_QUALITY,
                "risk_level": RiskLevel.MODERATE,
                "score": 55,
                "description": "Moderate air quality concerns around active construction work.",
                "hours_old": 2,
            },

            # Abuja manufacturing plant
            {
                "site_index": 1,
                "category": RiskCategory.OCCUPATIONAL,
                "risk_level": RiskLevel.HIGH,
                "score": 78,
                "description": "Elevated occupational exposure around manufacturing equipment.",
                "hours_old": 3,
            },
            {
                "site_index": 1,
                "category": RiskCategory.HEAT,
                "risk_level": RiskLevel.MODERATE,
                "score": 48,
                "description": "Moderate indoor heat exposure in production areas.",
                "hours_old": 4,
            },

            # Kano agricultural facility
            {
                "site_index": 2,
                "category": RiskCategory.HEAT,
                "risk_level": RiskLevel.HIGH,
                "score": 81,
                "description": "High heat exposure among workers performing outdoor agricultural tasks.",
                "hours_old": 1,
            },
            {
                "site_index": 2,
                "category": RiskCategory.OUTBREAK,
                "risk_level": RiskLevel.MODERATE,
                "score": 42,
                "description": "Moderate environmental outbreak signal requiring monitoring.",
                "hours_old": 6,
            },
        ]

        assessments = []

        for item in site_assessments:
            site = self.sites[item["site_index"]]

            assessment = RiskAssessment(
                site_id=site.id,
                category=item["category"],
                risk_level=item["risk_level"],
                score=item["score"],
                description=item["description"],
                observed_at=now - timedelta(hours=item["hours_old"]),
                source="Synthetic risk provider",
                data_is_synthetic=True,
            )

            assessments.append(assessment)

        return assessments