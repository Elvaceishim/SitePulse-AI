from app.providers.synthetic import SyntheticRiskProvider
from app.services.prioritization import prioritize_risks


provider = SyntheticRiskProvider()

results = prioritize_risks(
    sites=provider.get_sites(),
    assessments=provider.get_risk_assessments(),
)

print("\nSITEPULSE AI: PRIORITISED RISK REPORT")
print("=" * 65)

for index, item in enumerate(results, start=1):
    print(f"\nPriority #{index}")
    print(f"Site: {item.site.name}")
    print(f"Industry: {item.site.industry}")
    print(f"Risk: {item.assessment.category.value}")
    print(f"Score: {item.assessment.score}/100")
    print(f"Priority: {item.priority_band.value.upper()}")
    print(f"Assessment age: {item.age_hours} hours")
    print(f"Stale: {'Yes' if item.is_stale else 'No'}")
    print(
        f"Other risk signals at site: "
        f"{item.other_assessments_at_site}"
    )
    print(f"Evidence: {item.assessment.description}")
    print("-" * 65)