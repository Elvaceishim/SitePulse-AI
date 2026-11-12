
from app.models.risk import RiskCategory, RiskLevel
from app.models.prioritization import PrioritizedRisk
from app.models.intervention import InterventionDraft


def get_action_guidance(risk: PrioritizedRisk) -> dict:
    category = risk.assessment.category
    industry = risk.site.industry.lower()

    if category == RiskCategory.HEAT:
        if industry in {"construction", "agriculture"}:
            return {
                "action": (
                    "Review the site's heat exposure controls, access to "
                    "drinking water, shaded or cool recovery areas, and "
                    "approved work-rest procedures for outdoor activities."
                ),
                "rationale": (
                    "The assessment indicates heat exposure during "
                    "outdoor work activities. The site's industry and "
                    "working environment should inform the control review."
                ),
            }

        if industry == "manufacturing":
            return {
                "action": (
                    "Review indoor temperature conditions, heat-generating "
                    "equipment, ventilation effectiveness, hydration access, "
                    "and approved worker recovery procedures."
                ),
                "rationale": (
                    "The assessment indicates heat exposure in a "
                    "manufacturing environment. Indoor heat sources and "
                    "working conditions should be reviewed."
                ),
            }

        return {
            "action": (
                "Review heat exposure controls, hydration access, "
                "worker recovery arrangements, and approved work-rest "
                "procedures."
            ),
            "rationale": (
                "The assessment indicates heat exposure that requires "
                "a review of applicable workplace controls."
            ),
        }

    guidance = {
        RiskCategory.AIR_QUALITY: {
            "action": (
                "Review air-quality monitoring results, identify potential "
                "exposure sources, and verify the effectiveness of existing "
                "source controls, ventilation, and approved protective "
                "equipment."
            ),
            "rationale": (
                "The assessment indicates an air-quality concern that "
                "requires a review of workplace exposure controls."
            ),
        },

        RiskCategory.OCCUPATIONAL: {
            "action": (
                "Review the reported workplace hazard, inspect the relevant "
                "equipment and work area, and verify applicable guarding, "
                "isolation, training, and approved safety procedures."
            ),
            "rationale": (
                "The assessment indicates an occupational exposure around "
                "workplace equipment. The specific hazard should be "
                "verified before selecting additional controls."
            ),
        },

        RiskCategory.OUTBREAK: {
            "action": (
                "Verify the outbreak signal with the appropriate health "
                "or environmental authority and follow established site "
                "reporting and response procedures."
            ),
            "rationale": (
                "The assessment indicates an environmental outbreak signal "
                "that requires verification and appropriate monitoring."
            ),
        },

        RiskCategory.COLD: {
            "action": (
                "Review cold-exposure conditions, worker protection, "
                "available warming facilities, and approved exposure "
                "management procedures."
            ),
            "rationale": (
                "The assessment indicates potential cold exposure that "
                "requires a review of worker protection measures."
            ),
        },
    }

    return guidance[category]


def generate_intervention(
    risk: PrioritizedRisk,
) -> InterventionDraft:

    guidance = get_action_guidance(risk)

    if risk.priority_band == RiskLevel.CRITICAL:
        urgency = "immediate_review"

    elif risk.priority_band == RiskLevel.HIGH:
        urgency = "urgent_review"

    elif risk.priority_band == RiskLevel.MODERATE:
        urgency = "scheduled_review"

    else:
        urgency = "routine_monitoring"

    data_warning = None

    if risk.is_stale:
        data_warning = (
            "This assessment is stale. Verify current site conditions "
            "and obtain an updated assessment before relying on it."
        )

    return InterventionDraft(
        risk=risk,
        recommended_action=guidance["action"],
        rationale=guidance["rationale"],
        urgency=urgency,
        requires_human_review=True,
        data_warning=data_warning,
    )


def generate_interventions(
    risks: list[PrioritizedRisk],
) -> list[InterventionDraft]:

    return [
        generate_intervention(risk)
        for risk in risks
    ]
