"""Mycobacterium tuberculosis Experiment Agent Examples."""

import asyncio
import json
from agents.literature_agent import LiteratureAgent
from agents.hypothesis_agent import HypothesisAgent
from agents.experiment_agent import ExperimentAgent


async def main():
    print("\n" + "="*70)
    print("MYCOBACTERIUM TUBERCULOSIS EXPERIMENT AGENT EXAMPLES")
    print("="*70)

    lit_agent = LiteratureAgent()
    hyp_agent = HypothesisAgent()
    exp_agent = ExperimentAgent()

    try:
        # 1. Search literature for Mtb target
        print("\n📚 Searching Mtb literature...")
        papers = await lit_agent.search_papers(
            "Mycobacterium tuberculosis DprE1 inhibitor drug resistance",
            year_range=(2021, 2026),
            limit=5,
        )
        gaps = await lit_agent.identify_gaps(papers)

        # 2. Generate Mtb hypothesis
        print("💡 Generating hypotheses...")
        hypotheses = await hyp_agent.generate_hypotheses(
            papers=papers,
            research_gaps=gaps,
            query="Mycobacterium tuberculosis DprE1 inhibitor drug resistance",
        )

        if hypotheses:
            target_hyp = hypotheses[0]
            print(f"✓ Selected Hypothesis: {target_hyp.title}\n")

            # 3. Design Mtb Experiment
            print("📐 Designing Mtb BSL-3 laboratory experiment protocol...")
            design = await exp_agent.design_experiment(target_hyp.to_dict())

            print(f"\n✓ Experiment Protocol Designed Successfully:\n")
            print(f"  • Title       : {design.title}")
            print(f"  • Type        : {design.experiment_type.value}")
            print(f"  • Sample Size : {design.sample_size} wells / subjects")
            print(f"  • Duration    : {design.duration_weeks} weeks")
            print(f"  • Total Cost  : ${design.total_cost:,.0f}")
            print(f"  • Success Prob: {design.success_prediction.probability_success:.1%}")
            
            print("\nPrimary Measures:")
            for m in design.primary_measures:
                print(f"  • {m.name} ({m.method}) - Timing: {m.timing}")

            print("\nKey Risks & Mitigations:")
            for risk, mit in zip(design.potential_risks[:2], design.mitigation_strategies[:2]):
                print(f"  • Risk: {risk}")
                print(f"    Mitigation: {mit}")
            print()

    finally:
        await lit_agent.close()
        await hyp_agent.close()
        await exp_agent.close()

    print("="*70)
    print("✅ MTB EXPERIMENT AGENT EXAMPLES COMPLETED")
    print("="*70 + "\n")


if __name__ == "__main__":
    asyncio.run(main())