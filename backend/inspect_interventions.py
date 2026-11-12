from app.providers.synthetic import SyntheticRiskProvider
from app.services.prioritization import prioritize_risks
from app.services.intervention_engine import generate_interventions


provider = SyntheticRiskProvider()

risks = prioritize_risks(
    sites=provider.get_sites(),
    assessments=provider.get_risk_assessments(),
)

interventions = generate_interventions(risks)

print("\nSITEPULSE AI: OPERATIONAL INTERVENTION REPORT")
print("=" * 75)

for index, item in enumerate(interventions, start=1):
    print(f"\nINTERVENTION #{index}")
    print(f"Site: {item.risk.site.name}")
    print(f"Risk category: {item.risk.assessment.category.value}")
    print(f"Risk score: {item.risk.assessment.score}/100")
    print(f"Priority: {item.risk.priority_band.value.upper()}")
    print(f"Urgency: {item.urgency.upper()}")

    print(f"\nEvidence:")
    print(item.risk.assessment.description)

    print(f"\nRecommended action:")
    print(item.recommended_action)

    print(f"\nRationale:")
    print(item.rationale)

    if item.data_warning:
        print(f"\nDATA WARNING: {item.data_warning}")

    print(f"\nHuman review required: {item.requires_human_review}")
    print("-" * 75)