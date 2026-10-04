"""Mycobacterium tuberculosis Hypothesis Agent Examples."""

import asyncio
import json
from agents.literature_agent import LiteratureAgent
from agents.hypothesis_agent import HypothesisAgent


async def main():
    print("\n" + "="*70)
    print("MYCOBACTERIUM TUBERCULOSIS HYPOTHESIS AGENT EXAMPLES")
    print("="*70)

    lit_agent = LiteratureAgent()
    hyp_agent = HypothesisAgent()

    try:
        papers = await lit_agent.search_papers(
            "Mycobacterium tuberculosis DprE1 inhibitor drug resistance",
            year_range=(2021, 2026),
            limit=10,
        )

        gaps = await lit_agent.identify_gaps(papers)
        print(f"\n✓ Found {len(papers)} Mtb papers and {len(gaps)} research gaps.")

        hypotheses = await hyp_agent.generate_hypotheses(
            papers=papers,
            research_gaps=gaps,
            query="Mycobacterium tuberculosis DprE1 inhibitor drug resistance",
        )

        print(f"✓ Generated {len(hypotheses)} testable Mtb hypotheses:\n")

        for i, hyp in enumerate(hypotheses[:3], 1):
            print(f"{i}. {hyp.title}")
            print(f"   Statement: {hyp.statement}")
            print(f"   Overall Score: {hyp.overall_score:.3f} (Novelty: {hyp.novelty_score}, Feasibility: {hyp.feasibility_score})")
            print(f"   Resources: {', '.join(hyp.resources_needed)}")
            print()

    finally:
        await lit_agent.close()
        await hyp_agent.close()

    print("="*70)
    print("✅ MTB HYPOTHESIS EXAMPLES COMPLETED")
    print("="*70 + "\n")


if __name__ == "__main__":
    asyncio.run(main())