"""Example use cases for the Report Agent."""

import asyncio
import json
from agents.analysis_agent import AnalysisAgent
from agents.experiment_agent import ExperimentAgent
from agents.hypothesis_agent import HypothesisAgent
from agents.literature_agent import LiteratureAgent
from agents.report_agent import ReportAgent, OutputFormat


async def example_1_basic_paper_generation():
    """Example 1: Generate a basic research paper."""
    print("\n" + "="*60)
    print("EXAMPLE 1: Basic Research Paper Generation")
    print("="*60)

    # Setup sample data
    hypothesis = {
        "id": "hyp_001",
        "title": "Training efficiency improves with curriculum learning",
        "statement": "If curriculum learning is applied, then training efficiency increases",
        "background": "Neural networks often converge slowly during training",
        "type": "causal",
    }

    literature = [
        {
            "title": "Curriculum Learning",
            "authors": ["Bengio", "Y."],
            "publication_year": 2009,
            "journal": "ICML",
        },
    ]

    analysis = {
        "interpretation": {"hypothesis_confirmed": True},
        "primary_finding": {"title": "Training efficiency improved", "effect_size": 0.72},
        "implications": {
            "theoretical": ["Supports curriculum learning theory"],
            "practical": ["Apply to real systems"],
            "limitations": ["Limited to specific domains"],
            "future_directions": ["Test on larger models"],
        },
        "findings": [{"title": "Primary Finding", "confidence_level": 0.92}],
    }

    design = {
        "experiment_type": "randomized_controlled_trial",
        "sample_size": 100,
        "sample_characteristics": ["expert annotators"],
        "primary_measures": [{"name": "Training efficiency"}],
        "secondary_measures": [{"name": "Model accuracy"}],
        "procedures": [{"step_number": 1, "description": "Setup", "duration_minutes": 30}],
        "analysis_plan": "t-tests comparing conditions",
    }

    agent = ReportAgent()

    try:
        print("\n✍️ Generating paper...\n")
        paper = await agent.generate_paper(hypothesis, literature, analysis, design)

        print(f"✓ Paper generated")
        print(f"  Title: {paper.title}")
        print(f"  Word Count: {paper.word_count}")
        print(f"  Figures: {len(paper.figures)}")
        print(f"  Tables: {len(paper.tables)}")

    finally:
        await agent.close()


async def example_2_paper_export():
    """Example 2: Export paper in multiple formats."""
    print("\n" + "="*60)
    print("EXAMPLE 2: Paper Export Formats")
    print("="*60)

    hypothesis = {
        "title": "Attention improves interpretability",
        "statement": "Attention mechanisms improve model interpretability",
    }

    analysis = {
        "interpretation": {"hypothesis_confirmed": True},
        "primary_finding": {"effect_size": 0.65},
        "implications": {
            "theoretical": ["Confirms theory"],
            "practical": ["Industry applications"],
            "limitations": ["Limited scope"],
            "future_directions": ["Extend to other domains"],
        },
        "findings": [{"confidence_level": 0.88}],
    }

    design = {
        "experiment_type": "laboratory_experiment",
        "sample_size": 80,
        "sample_characteristics": ["computer science students"],
        "primary_measures": [{"name": "Interpretability", "description": "Expert ratings"}],
        "secondary_measures": [{"name": "Trust", "description": "User ratings"}],
        "procedures": [{"step_number": 1, "description": "Study", "duration_minutes": 45}],
        "analysis_plan": "Mixed models with random effects",
    }

    agent = ReportAgent()

    try:
        print("\n✍️ Generating paper...\n")
        paper = await agent.generate_paper(hypothesis, [], analysis, design)

        # Markdown export
        print("Exporting to Markdown...")
        markdown = await agent.export_paper(paper, OutputFormat.MARKDOWN)
        print(f"✓ Markdown: {len(markdown)} characters\n")

        # JSON export
        print("Exporting to JSON...")
        json_export = await agent.export_paper(paper, OutputFormat.JSON)
        print(f"✓ JSON: {len(json_export)} characters\n")

        # BibTeX export
        print("Exporting to BibTeX...")
        bibtex = await agent.export_paper(paper, OutputFormat.BIBTEX)
        print(f"✓ BibTeX: {len(bibtex)} characters\n")

    finally:
        await agent.close()


async def example_3_full_pipeline():
    """Example 3: Complete end-to-end pipeline to paper."""
    print("\n" + "="*60)
    print("EXAMPLE 3: Full Pipeline to Publication-Ready Paper")
    print("="*60)

    lit_agent = LiteratureAgent()
    hyp_agent = HypothesisAgent()
    exp_agent = ExperimentAgent()
    ana_agent = AnalysisAgent()
    rep_agent = ReportAgent()

    try:
        print("\n🔄 Running complete pipeline...\n")

        # Phase 1: Literature
        print("1️⃣ Searching literature...")
        papers = await lit_agent.search_papers("neural network optimization", limit=5)
        gaps = await lit_agent.identify_gaps(papers)

        # Phase 2: Hypothesis
        print("2️⃣ Generating hypotheses...")
        hypotheses = await hyp_agent.generate_hypotheses(papers, gaps, "optimization")

        # Phase 3: Experiment
        print("3️⃣ Designing experiment...")
        design = await exp_agent.design_experiment(hypotheses[0].to_dict())

        # Phase 4: Analysis
        print("4️⃣ Analyzing results...")
        results = {
            "n": design.sample_size,
            "simulated_effect_size": 0.58,
            "variables": {"outcome": [5.0 + i*0.01 for i in range(design.sample_size)]},
        }
        report = await ana_agent.analyze_results(design.to_dict(), hypotheses[0].to_dict(), results)

        # Phase 5: Report
        print("5️⃣ Generating publication-ready paper...\n")
        paper = await rep_agent.generate_paper(
            hypothesis=hypotheses[0].to_dict(),
            literature_findings=[p.to_dict() if hasattr(p, 'to_dict') else p for p in papers],
            analysis_report=report.to_dict(),
            experiment_design=design.to_dict(),
        )

        print("✅ Pipeline Complete!\n")
        print(f"Research Question: {hypotheses[0].title}")
        print(f"Papers Found: {len(papers)}")
        print(f"Result: Hypothesis {'CONFIRMED' if report.hypothesis_confirmed else 'NOT CONFIRMED'}")
        print(f"Paper Generated: {paper.title}")
        print(f"Word Count: {paper.word_count}")
        print(f"Ready for: Conference submission, Journal publication, Hackathon entry")

    finally:
        await lit_agent.close()
        await hyp_agent.close()
        await exp_agent.close()
        await ana_agent.close()
        await rep_agent.close()


async def example_4_citation_management():
    """Example 4: Citation management and formatting."""
    print("\n" + "="*60)
    print("EXAMPLE 4: Citation Management & Formatting")
    print("="*60)

    from agents.report_agent import Citation

    # Create citations
    citations = [
        Citation(
            authors=["Vaswani", "A.", "Shazeer", "N."],
            year=2017,
            title="Attention is All You Need",
            source="Advances in Neural Information Processing Systems",
            doi="10.5555/3295222.3295349",
        ),
        Citation(
            authors=["Bengio", "Y.", "Courville", "A.", "Vincent", "P."],
            year=2013,
            title="Representation Learning: A Review",
            source="IEEE Transactions on Pattern Analysis",
        ),
    ]

    print("\n📚 Citation Formats:\n")

    print("APA Format:")
    for cite in citations:
        print(f"  {cite.format_apa()}\n")

    print("\nBibTeX Format:")
    for i, cite in enumerate(citations, 1):
        authors = " and ".join(cite.authors)
        print(f"@article{{ref{i},")
        print(f"  author = {{{authors}}},")
        print(f"  year = {{{cite.year}}},")
        print(f"  title = {{{cite.title}}},")
        print(f"  journal = {{{cite.source}}}")
        if cite.doi:
            print(f"  doi = {{{cite.doi}}}")
        print("}\n")


async def example_5_knowledge_graph():
    """Example 5: Knowledge graph export."""
    print("\n" + "="*60)
    print("EXAMPLE 5: Knowledge Graph Export")
    print("="*60)

    hypothesis = {
        "title": "Attention mechanisms improve model interpretability",
        "statement": "If X then Y",
    }

    analysis = {
        "interpretation": {"hypothesis_confirmed": True},
        "primary_finding": {"effect_size": 0.7},
        "implications": {"theoretical": ["Theory 1"], "practical": ["Practice 1"]},
        "findings": [{"confidence_level": 0.9}],
    }

    design = {
        "experiment_type": "randomized_controlled_trial",
        "sample_size": 100,
        "sample_characteristics": ["expert annotators"],
        "primary_measures": [{"name": "Score"}],
        "secondary_measures": [{"name": "Rating"}],
        "procedures": [{"step_number": 1, "description": "Step", "duration_minutes": 30}],
        "analysis_plan": "t-test",
    }

    agent = ReportAgent()

    try:
        print("\n📊 Generating knowledge graph...\n")
        paper = await agent.generate_paper(hypothesis, [], analysis, design)

        kg = paper.knowledge_graph_export

        print("Entities:")
        for ent_id, entity in kg.get("entities", {}).items():
            print(f"  • {entity.get('label', 'Unknown')} (type: {entity.get('type')})")

        print("\nRelationships:")
        for rel in kg.get("relationships", []):
            print(f"  • {rel.get('source')} --{rel.get('relation')}--> {rel.get('target')}")

        print("\nProperties:")
        for ent, props in kg.get("properties", {}).items():
            print(f"  • {ent}: {props}")

        print("\n✓ Knowledge graph ready for export to RDF/JSON-LD/Turtle formats")

    finally:
        await agent.close()


async def main():
    """Run all examples."""
    print("\n📝 Report Agent - Example Use Cases\n")

    examples = [
        ("Basic Paper Generation", example_1_basic_paper_generation),
        ("Export Formats", example_2_paper_export),
        ("Full Pipeline", example_3_full_pipeline),
        ("Citation Management", example_4_citation_management),
        ("Knowledge Graph", example_5_knowledge_graph),
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
