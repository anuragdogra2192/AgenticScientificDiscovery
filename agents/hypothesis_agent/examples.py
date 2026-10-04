"""Example use cases for the Hypothesis Agent."""

import asyncio
import json
from agents.literature_agent import LiteratureAgent
from agents.hypothesis_agent import HypothesisAgent


async def example_1_basic_hypothesis_generation():
    """Example 1: Generate hypotheses from literature findings."""
    print("\n" + "="*60)
    print("EXAMPLE 1: Basic Hypothesis Generation")
    print("="*60)

    lit_agent = LiteratureAgent()
    hyp_agent = HypothesisAgent()

    try:
        # Get literature
        print("\n🔍 Searching literature...")
        papers = await lit_agent.search_papers(
            "machine learning model interpretability",
            year_range=(2022, 2026),
            limit=15,
        )

        gaps = await lit_agent.identify_gaps(papers)

        print(f"✓ Found {len(papers)} papers and {len(gaps)} gaps\n")

        # Generate hypotheses
        print("💡 Generating hypotheses...")
        hypotheses = await hyp_agent.generate_hypotheses(
            papers=papers,
            research_gaps=gaps,
            query="machine learning model interpretability",
        )

        print(f"\n✓ Generated {len(hypotheses)} hypotheses\n")

        # Display
        for i, hyp in enumerate(hypotheses[:3], 1):
            print(f"{i}. {hyp.title}")
            print(f"   Overall Score: {hyp.overall_score:.3f}")
            print(f"   - Novelty: {hyp.novelty_score:.2f}")
            print(f"   - Feasibility: {hyp.feasibility_score:.2f}")
            print(f"   - Impact: {hyp.impact_score:.2f}")
            print(f"   - Testability: {hyp.testability_score:.2f}")
            print()

    finally:
        await lit_agent.close()
        await hyp_agent.close()


async def example_2_hypothesis_details():
    """Example 2: Examine hypothesis details and structure."""
    print("\n" + "="*60)
    print("EXAMPLE 2: Hypothesis Details & Structure")
    print("="*60)

    lit_agent = LiteratureAgent()
    hyp_agent = HypothesisAgent()

    try:
        papers = await lit_agent.search_papers(
            "federated learning privacy",
            year_range=(2023, 2026),
            limit=10,
        )

        gaps = await lit_agent.identify_gaps(papers)

        hypotheses = await hyp_agent.generate_hypotheses(
            papers=papers,
            research_gaps=gaps,
            query="federated learning privacy",
        )

        if hypotheses:
            print(f"\n📋 Detailed View of Top Hypothesis:\n")
            hyp = hypotheses[0]

            print(f"Title: {hyp.title}")
            print(f"Type: {hyp.hypothesis_type.value}")
            print(f"Complexity: {hyp.complexity.value}\n")

            print(f"Statement:\n{hyp.statement}\n")

            print("Independent Variables:")
            for var in hyp.independent_variables:
                print(f"  • {var.name}: {var.description}")
                print(f"    Measurement: {var.measurement_method}")

            print("\nDependent Variables:")
            for var in hyp.dependent_variables:
                print(f"  • {var.name}: {var.description}")

            print("\nControl Variables:")
            for var in hyp.control_variables:
                print(f"  • {var.name}")

            print("\nPredictions:")
            for i, pred in enumerate(hyp.predictions, 1):
                print(f"  {i}. {pred.statement}")
                print(f"     Success Criterion: {pred.success_criterion}")

            print("\nAssumptions:")
            for assumption in hyp.assumptions:
                print(f"  • {assumption}")

            print("\nAlternative Hypotheses:")
            for alt in hyp.alternative_hypotheses:
                print(f"  • {alt}")

    finally:
        await lit_agent.close()
        await hyp_agent.close()


async def example_3_hypothesis_comparison():
    """Example 3: Compare hypotheses by scores."""
    print("\n" + "="*60)
    print("EXAMPLE 3: Hypothesis Comparison & Ranking")
    print("="*60)

    lit_agent = LiteratureAgent()
    hyp_agent = HypothesisAgent()

    try:
        papers = await lit_agent.search_papers(
            "quantum machine learning",
            year_range=(2022, 2026),
            limit=12,
        )

        gaps = await lit_agent.identify_gaps(papers)

        hypotheses = await hyp_agent.generate_hypotheses(
            papers=papers,
            research_gaps=gaps,
            query="quantum machine learning",
        )

        print(f"\n📊 Comparing {len(hypotheses)} Generated Hypotheses:\n")

        # Sort by different criteria
        print("Top 3 by Overall Score:")
        by_overall = sorted(hypotheses, key=lambda h: h.overall_score, reverse=True)
        for i, hyp in enumerate(by_overall[:3], 1):
            print(f"  {i}. {hyp.title} ({hyp.overall_score:.3f})")

        print("\nMost Novel:")
        by_novelty = sorted(hypotheses, key=lambda h: h.novelty_score, reverse=True)
        for i, hyp in enumerate(by_novelty[:3], 1):
            print(f"  {i}. {hyp.title} ({hyp.novelty_score:.2f})")

        print("\nMost Feasible:")
        by_feasibility = sorted(
            hypotheses,
            key=lambda h: h.feasibility_score,
            reverse=True
        )
        for i, hyp in enumerate(by_feasibility[:3], 1):
            print(f"  {i}. {hyp.title} ({hyp.feasibility_score:.2f})")

        print("\nHighest Impact:")
        by_impact = sorted(hypotheses, key=lambda h: h.impact_score, reverse=True)
        for i, hyp in enumerate(by_impact[:3], 1):
            print(f"  {i}. {hyp.title} ({hyp.impact_score:.2f})")

        print("\nMost Testable:")
        by_testability = sorted(
            hypotheses,
            key=lambda h: h.testability_score,
            reverse=True
        )
        for i, hyp in enumerate(by_testability[:3], 1):
            print(f"  {i}. {hyp.title} ({hyp.testability_score:.2f})")

    finally:
        await lit_agent.close()
        await hyp_agent.close()


async def example_4_research_design_sketch():
    """Example 4: Generate research design sketches."""
    print("\n" + "="*60)
    print("EXAMPLE 4: Research Design Sketches")
    print("="*60)

    lit_agent = LiteratureAgent()
    hyp_agent = HypothesisAgent()

    try:
        papers = await lit_agent.search_papers(
            "reinforcement learning sample efficiency",
            year_range=(2023, 2026),
            limit=10,
        )

        gaps = await lit_agent.identify_gaps(papers)

        hypotheses = await hyp_agent.generate_hypotheses(
            papers=papers,
            research_gaps=gaps,
            query="reinforcement learning sample efficiency",
        )

        if hypotheses:
            print(f"\n📐 Research Design for Top Hypothesis:\n")
            expanded = await hyp_agent.expand_hypothesis(hypotheses[0])

            print(expanded["expanded"]["research_design_sketch"])

            print("\nNext Steps:")
            for i, step in enumerate(expanded["expanded"]["next_steps"], 1):
                print(f"  {i}. {step}")

    finally:
        await lit_agent.close()
        await hyp_agent.close()


async def example_5_multi_domain_hypotheses():
    """Example 5: Generate cross-domain hypotheses."""
    print("\n" + "="*60)
    print("EXAMPLE 5: Cross-Domain Hypothesis Generation")
    print("="*60)

    lit_agent = LiteratureAgent()
    hyp_agent = HypothesisAgent()

    try:
        # Search for papers
        papers = await lit_agent.search_papers(
            "neural networks biological learning",
            year_range=(2023, 2026),
            limit=10,
        )

        gaps = await lit_agent.identify_gaps(papers)

        # Generate with explicit domain
        hypotheses = await hyp_agent.generate_hypotheses(
            papers=papers,
            research_gaps=gaps,
            query="neural networks biological learning",
            domain="machine_learning,neuroscience",
        )

        print(f"\n🌉 Cross-Domain Hypotheses:\n")

        cross_domain = [
            h for h in hypotheses
            if h.source_strategy == "cross_domain_synthesis"
        ]

        if cross_domain:
            for hyp in cross_domain[:2]:
                print(f"Hypothesis: {hyp.title}")
                print(f"Strategy: {hyp.source_strategy}")
                print(f"Impact Score: {hyp.impact_score:.2f}")
                print(f"Statement: {hyp.statement}\n")

    finally:
        await lit_agent.close()
        await hyp_agent.close()


async def example_6_export_hypotheses():
    """Example 6: Export hypotheses to JSON."""
    print("\n" + "="*60)
    print("EXAMPLE 6: Export Hypotheses to JSON")
    print("="*60)

    lit_agent = LiteratureAgent()
    hyp_agent = HypothesisAgent()

    try:
        papers = await lit_agent.search_papers(
            "attention mechanisms transformers",
            year_range=(2023, 2026),
            limit=8,
        )

        gaps = await lit_agent.identify_gaps(papers)

        hypotheses = await hyp_agent.generate_hypotheses(
            papers=papers,
            research_gaps=gaps,
            query="attention mechanisms transformers",
        )

        print(f"\n✓ Exporting {len(hypotheses[:2])} hypotheses to JSON\n")

        export = {
            "query": "attention mechanisms transformers",
            "generated_at": hypotheses[0].generated_at if hypotheses else None,
            "total_hypotheses": len(hypotheses),
            "top_hypotheses": [h.to_dict() for h in hypotheses[:2]],
        }

        print(json.dumps(export, indent=2))

        # Could save to file
        with open("/tmp/hypotheses.json", "w") as f:
            json.dump(export, f, indent=2)

        print("\n✓ Saved to /tmp/hypotheses.json")

    finally:
        await lit_agent.close()
        await hyp_agent.close()


async def example_7_hypothesis_refinement():
    """Example 7: Refine hypotheses with custom weights."""
    print("\n" + "="*60)
    print("EXAMPLE 7: Hypothesis Refinement & Custom Ranking")
    print("="*60)

    lit_agent = LiteratureAgent()
    hyp_agent = HypothesisAgent()

    try:
        papers = await lit_agent.search_papers(
            "causal inference machine learning",
            year_range=(2023, 2026),
            limit=10,
        )

        gaps = await lit_agent.identify_gaps(papers)

        hypotheses = await hyp_agent.generate_hypotheses(
            papers=papers,
            research_gaps=gaps,
            query="causal inference machine learning",
        )

        print(f"\n⚖️ Ranking with Custom Weights:\n")

        # Default ranking
        print("Default Ranking (Equal weights):")
        for i, hyp in enumerate(hypotheses[:3], 1):
            print(f"  {i}. {hyp.title} ({hyp.overall_score:.3f})")

        # Feasibility-focused ranking
        feasibility_weights = {
            "novelty": 0.15,
            "feasibility": 0.5,  # High weight on feasibility
            "impact": 0.20,
            "testability": 0.15,
        }

        ranked = await hyp_agent.rank_hypotheses(
            hypotheses,
            weights=feasibility_weights
        )

        print("\nFeasibility-Focused Ranking:")
        for i, hyp in enumerate(ranked[:3], 1):
            print(f"  {i}. {hyp.title} ({hyp.overall_score:.3f})")

        # Impact-focused ranking
        impact_weights = {
            "novelty": 0.20,
            "feasibility": 0.20,
            "impact": 0.45,  # High weight on impact
            "testability": 0.15,
        }

        ranked = await hyp_agent.rank_hypotheses(
            hypotheses,
            weights=impact_weights
        )

        print("\nImpact-Focused Ranking:")
        for i, hyp in enumerate(ranked[:3], 1):
            print(f"  {i}. {hyp.title} ({hyp.overall_score:.3f})")

    finally:
        await lit_agent.close()
        await hyp_agent.close()


async def main():
    """Run all examples."""
    print("\n🧪 Hypothesis Agent - Example Use Cases\n")

    examples = [
        ("Basic Generation", example_1_basic_hypothesis_generation),
        ("Hypothesis Details", example_2_hypothesis_details),
        ("Comparison & Ranking", example_3_hypothesis_comparison),
        ("Research Design", example_4_research_design_sketch),
        ("Cross-Domain", example_5_multi_domain_hypotheses),
        ("Export to JSON", example_6_export_hypotheses),
        ("Refinement", example_7_hypothesis_refinement),
    ]

    for i, (name, func) in enumerate(examples, 1):
        try:
            await func()
        except Exception as e:
            print(f"\n❌ Error in {name}: {e}")
            print("   (This might be due to API limits or connectivity issues)")

    print("\n" + "="*60)
    print("✅ Examples completed!")
    print("="*60 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
