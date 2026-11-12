
from app.providers.synthetic import SyntheticRiskProvider
from app.services.prioritization import prioritize_risks
from app.services.intervention_engine import generate_interventions

from app.services.briefing_generator import (
    BriefingGenerator,
    BriefingGenerationError,
)

from app.services.briefing_evaluator import (
    BriefingEvaluator,
    BriefingEvaluationError,
)


def main():
    provider = SyntheticRiskProvider()

    sites = provider.get_sites()
    assessments = provider.get_risk_assessments()

    risks = prioritize_risks(
        sites=sites,
        assessments=assessments,
    )

    interventions = generate_interventions(risks)

    print("\nSITEPULSE AI: SUPERVISOR BRIEFING")
    print("=" * 70)
    print("Data source: SYNTHETIC")
    print(f"Sites monitored: {len(sites)}")
    print(f"Risk assessments: {len(risks)}")
    print(f"Interventions proposed: {len(interventions)}")

    print("\nGenerating AI briefing...")

    try:
        generator = BriefingGenerator()
        briefing = generator.generate(interventions)

    except BriefingGenerationError as exc:
        print(f"\nBriefing generation failed: {exc}")
        return

    print("\nEXECUTIVE SUMMARY")
    print("-" * 70)
    print(briefing.executive_summary)

    sites_by_id = {
        site.id: site
        for site in sites
    }

    print("\nSITE SUMMARIES")
    print("-" * 70)

    for summary in briefing.site_summaries:
        site = sites_by_id[summary.site_id]

        print(f"\n{site.name}")
        print(summary.summary)

    notes_by_assessment_id = {
        note.assessment_id: note.priority_explanation
        for note in briefing.intervention_notes
    }

    print("\nPRIORITISED INTERVENTIONS")
    print("-" * 70)

    for index, intervention in enumerate(interventions, start=1):
        risk = intervention.risk
        assessment = risk.assessment

        print(f"\n#{index}: {risk.site.name}")
        print(f"Category: {assessment.category.value}")
        print(f"Priority: {risk.priority_band.value.upper()}")
        print(f"Score: {assessment.score}/100")
        print(f"Urgency: {intervention.urgency}")
        print(f"Observed: {assessment.observed_at.isoformat()}")
        print(f"Source: {assessment.source}")

        print(f"\nEvidence: {assessment.description}")
        print(f"Action: {intervention.recommended_action}")

        print(
            "Priority explanation: "
            f"{notes_by_assessment_id[assessment.id]}"
        )

        if intervention.data_warning:
            print(f"WARNING: {intervention.data_warning}")

        print(
            f"Human review required: "
            f"{intervention.requires_human_review}"
        )

        print("-" * 70)

    # --------------------------------------------------
    # BRIEFING QUALITY EVALUATION
    # --------------------------------------------------

    print("\nEVALUATING BRIEFING QUALITY")
    print("=" * 70)

    try:
        evaluator = BriefingEvaluator()

        evaluation = evaluator.evaluate(
            briefing=briefing,
            interventions=interventions,
        )

    except BriefingEvaluationError as exc:
        print(f"\nBriefing evaluation failed: {exc}")
        return

    print(f"\nOverall evaluation: {evaluation.overall_status.upper()}")

    print("\nINTERVENTION EXPLANATION EVALUATIONS")
    print("-" * 70)

    interventions_by_id = {
        item.risk.assessment.id: item
        for item in interventions
    }

    for result in evaluation.intervention_evaluations:
        intervention = interventions_by_id[result.assessment_id]
        assessment = intervention.risk.assessment

        print(f"\nSite: {intervention.risk.site.name}")
        print(f"Category: {assessment.category.value}")
        print(f"Priority: {intervention.risk.priority_band.value.upper()}")

        print(f"Evidence grounding: {result.evidence_grounding}")
        print(f"Priority consistency: {result.priority_consistency}")
        print(f"Freshness handling: {result.freshness_handling}")
        print(f"Usefulness: {result.usefulness}")

        print("Unsupported claims:")

        if result.unsupported_claims:
            for claim in result.unsupported_claims:
                print(f"  - {claim}")
        else:
            print("  None reported")

        print(f"Feedback: {result.feedback}")
        print("-" * 70)

    print("\nSITE SUMMARY EVALUATIONS")
    print("-" * 70)

    for result in evaluation.site_summary_evaluations:
        site = sites_by_id[result.site_id]

        print(f"\nSite: {site.name}")
        print(f"Risk coverage: {result.risk_coverage}")
        print(f"Evidence grounding: {result.evidence_grounding}")

        print("Unsupported claims:")

        if result.unsupported_claims:
            for claim in result.unsupported_claims:
                print(f"  - {claim}")
        else:
            print("  None reported")

        print(f"Feedback: {result.feedback}")
        print("-" * 70)

    print("\nNOTE")
    print(
        "This evaluation is AI-generated and requires human review. "
        "It does not constitute an independent safety assessment."
    )


if __name__ == "__main__":
    main()
