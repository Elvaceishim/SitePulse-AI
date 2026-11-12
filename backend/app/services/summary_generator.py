from app.models.intervention import InterventionDraft


def generate_executive_summary(
    interventions: list[InterventionDraft],
) -> str:

    if not interventions:
        raise ValueError("At least one intervention is required.")

    sites = {}
    priority_counts = {}
    category_counts = {}

    for item in interventions:
        site = item.risk.site
        assessment = item.risk.assessment

        sites[site.id] = site.name

        priority = item.risk.priority_band.value
        priority_counts[priority] = (
            priority_counts.get(priority, 0) + 1
        )

        category = assessment.category.value
        category_counts[category] = (
            category_counts.get(category, 0) + 1
        )

    highest_priority = max(
        interventions,
        key=lambda item: item.risk.assessment.score,
    )

    stale_count = sum(
        1 for item in interventions if item.risk.is_stale
    )

    categories = ", ".join(
        sorted(category_counts.keys())
    )

    return (
        f"The briefing covers {len(sites)} sites and "
        f"{len(interventions)} risk assessments across "
        f"the following categories: {categories}. "
        f"The highest-priority assessment is "
        f"{highest_priority.risk.assessment.category.value} "
        f"at {highest_priority.risk.site.name}, with a score "
        f"of {highest_priority.risk.assessment.score:g}/100 "
        f"and a {highest_priority.risk.priority_band.value} "
        f"priority band. "
        f"{stale_count} assessment(s) require verification "
        f"because their data is stale."
    )