"""Examples for the Experiment Planner Agent in Mycobacterium tuberculosis Research."""

import asyncio
from agents.experiment_planner.agent import ExperimentPlannerAgent


async def main():
    print("\n" + "="*70)
    print("EXPERIMENT PLANNER AGENT - Mtb COMPARATIVE PROTOCOL EXAMPLES")
    print("="*70)

    planner = ExperimentPlannerAgent()

    try:
        # Sample Mtb hypothesis dictionary
        sample_hypothesis = {
            "id": "mtb_hyp_001",
            "title": "Allosteric Inhibition of DprE1 in MDR-TB",
            "statement": "Targeting the DprE1 enzyme via novel covalent benzothiazinone analogues will bypass existing efflux resistance in Mycobacterium tuberculosis.",
            "complexity": "moderate"
        }

        print(f"\n🔍 Planning competing protocols for hypothesis: '{sample_hypothesis['title']}'...")
        
        plan = await planner.plan_competing_tests(sample_hypothesis, max_budget=100000.0)

        print(f"\n✓ Protocol Plan Generated Successfully!\n")
        print(f"  • Baseline Design  : {plan.baseline_design.get('title')} (${plan.baseline_design.get('total_budget', 0):,.0f})")
        print(f"  • Proposed Design  : {plan.proposed_design.get('title')} (${plan.proposed_design.get('total_budget', 0):,.0f})")
        print(f"  • Selected Protocol: {plan.selected_design.get('title')}")
        print(f"  • Selection Rationale: {plan.rationale}\n")

    finally:
        await planner.close()

    print("="*70)
    print("✅ EXPERIMENT PLANNER EXAMPLES COMPLETED")
    print("="*70 + "\n")


if __name__ == "__main__":
    asyncio.run(main())