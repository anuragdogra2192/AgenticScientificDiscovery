"""Example use cases for the Literature Agent."""

import asyncio
import json
from agents.literature_agent import LiteratureAgent


async def example_1_basic_search():
    """Example 1: Basic paper search."""
    print("\n" + "="*60)
    print("EXAMPLE 1: Basic Paper Search")
    print("="*60)

    agent = LiteratureAgent()

    try:
        papers = await agent.search_papers(
            query="attention mechanism transformer",
            year_range=(2020, 2026),
            limit=5,
        )

        print(f"\n✓ Found {len(papers)} papers on attention mechanisms\n")

        for i, paper in enumerate(papers, 1):
            print(f"{i}. {paper.title}")
            print(f"   Authors: {', '.join(paper.authors[:2])}{'...' if len(paper.authors) > 2 else ''}")
            print(f"   Year: {paper.publication_year}")
            print(f"   Citations: {paper.citations_count}")
            if paper.doi:
                print(f"   DOI: {paper.doi}")
            print()

    finally:
        await agent.close()


async def example_2_gap_analysis():
    """Example 2: Identify research gaps."""
    print("\n" + "="*60)
    print("EXAMPLE 2: Research Gap Analysis")
    print("="*60)

    agent = LiteratureAgent()

    try:
        # Search for papers
        papers = await agent.search_papers(
            query="federated learning privacy",
            year_range=(2021, 2026),
            limit=10,
        )

        print(f"\n✓ Searched {len(papers)} papers")

        # Identify gaps
        gaps = await agent.identify_gaps(papers)

        print(f"✓ Identified {len(gaps)} research gaps\n")

        for i, gap in enumerate(gaps, 1):
            print(f"{i}. {gap.gap_description}")
            print(f"   Priority: {gap.priority_level.upper()}")
            print(f"   Confidence: {gap.confidence:.1%}")
            print(f"   Related papers ({len(gap.related_papers)}):")
            for paper_title in gap.related_papers[:2]:
                print(f"     - {paper_title}")
            print()

    finally:
        await agent.close()


async def example_3_comparative_analysis():
    """Example 3: Compare two research areas."""
    print("\n" + "="*60)
    print("EXAMPLE 3: Comparative Literature Analysis")
    print("="*60)

    agent = LiteratureAgent()

    try:
        # Search for both topics
        gnn_papers = await agent.search_papers(
            query="graph neural networks",
            year_range=(2022, 2026),
            limit=5,
        )

        kge_papers = await agent.search_papers(
            query="knowledge graph embedding",
            year_range=(2022, 2026),
            limit=5,
        )

        print(f"\n✓ Graph Neural Networks: {len(gnn_papers)} papers")
        print(f"✓ Knowledge Graph Embeddings: {len(kge_papers)} papers")

        # Compare citation patterns
        gnn_avg_citations = sum(p.citations_count for p in gnn_papers) / len(gnn_papers)
        kge_avg_citations = sum(p.citations_count for p in kge_papers) / len(kge_papers)

        print(f"\nAverage citations:")
        print(f"  GNNs: {gnn_avg_citations:.1f}")
        print(f"  KGEs: {kge_avg_citations:.1f}")

        # Recent trends
        gnn_recent = [p for p in gnn_papers if p.publication_year >= 2025]
        kge_recent = [p for p in kge_papers if p.publication_year >= 2025]

        print(f"\nRecent publications (2025+):")
        print(f"  GNNs: {len(gnn_recent)} papers")
        print(f"  KGEs: {len(kge_recent)} papers")

    finally:
        await agent.close()


async def example_4_full_report():
    """Example 4: Generate comprehensive literature review report."""
    print("\n" + "="*60)
    print("EXAMPLE 4: Comprehensive Literature Review")
    print("="*60)

    agent = LiteratureAgent()

    try:
        query = "neural architecture search AutoML"

        papers = await agent.search_papers(
            query=query,
            year_range=(2019, 2026),
            limit=15,
        )

        gaps = await agent.identify_gaps(papers)

        report = await agent.generate_report(
            query=query,
            papers=papers,
            gaps=gaps,
        )

        print(f"\n✓ Generated comprehensive report\n")
        print(f"Topic: {report['query']}")
        print(f"Papers analyzed: {report['statistics']['total_papers']}")
        print(f"Year range: {report['statistics']['year_range']}")
        print(f"Avg citations: {report['statistics']['avg_citations']:.1f}")
        print(f"Research gaps identified: {report['statistics']['identified_gaps']}")

        print(f"\nTop papers by citations:")
        sorted_papers = sorted(
            report['papers'],
            key=lambda p: p['citations_count'],
            reverse=True
        )
        for paper in sorted_papers[:3]:
            print(f"  - {paper['title'][:60]}...")
            print(f"    Citations: {paper['citations_count']}")

        print(f"\nIdentified research gaps:")
        for gap in report['research_gaps'][:3]:
            print(f"  - {gap['description']}")
            print(f"    Priority: {gap['priority']}")

    finally:
        await agent.close()


async def example_5_emerging_topics():
    """Example 5: Discover emerging research topics."""
    print("\n" + "="*60)
    print("EXAMPLE 5: Emerging Research Topics")
    print("="*60)

    agent = LiteratureAgent()

    try:
        emerging_topics = [
            "quantum machine learning",
            "neuromorphic computing",
            "causal inference machine learning",
            "foundation models reasoning",
            "sustainable AI carbon footprint",
        ]

        print("\nSearching emerging research areas...\n")

        for topic in emerging_topics:
            papers = await agent.search_papers(
                query=topic,
                year_range=(2023, 2026),
                limit=5,
            )

            if papers:
                recent = [p for p in papers if p.publication_year == 2026]
                avg_citations = sum(p.citations_count for p in papers) / len(papers)

                print(f"📈 {topic}")
                print(f"   Papers (2023-2026): {len(papers)}")
                print(f"   2026 publications: {len(recent)}")
                print(f"   Avg citations: {avg_citations:.1f}")
            else:
                print(f"❌ {topic} - No results")

            print()

    finally:
        await agent.close()


async def example_6_export_bibtex():
    """Example 6: Export results in BibTeX format."""
    print("\n" + "="*60)
    print("EXAMPLE 6: Export to BibTeX")
    print("="*60)

    agent = LiteratureAgent()

    try:
        papers = await agent.search_papers(
            query="reinforcement learning multi-agent",
            limit=3,
        )

        print(f"\n✓ Exporting {len(papers)} papers to BibTeX format\n")

        bibtex = generate_bibtex(papers)
        print(bibtex)

        # Save to file
        with open("/tmp/literature_export.bib", "w") as f:
            f.write(bibtex)
        print("\n✓ Saved to /tmp/literature_export.bib")

    finally:
        await agent.close()


def generate_bibtex(papers):
    """Convert papers to BibTeX format."""
    bibtex_entries = []

    for i, paper in enumerate(papers):
        authors = " and ".join(paper.authors[:3])
        if len(paper.authors) > 3:
            authors += " and others"

        entry = f"""@article{{paper{i+1},
  title={{{paper.title}}},
  author={{{authors}}},
  year={{{paper.publication_year}}},
  journal={{{paper.journal or 'Unknown'}}},
"""

        if paper.doi:
            entry += f"  doi={{{paper.doi}}},\n"

        entry += "}\n"
        bibtex_entries.append(entry)

    return "".join(bibtex_entries)


async def main():
    """Run all examples."""
    print("\n🧪 Literature Agent - Example Use Cases\n")

    examples = [
        ("Basic Search", example_1_basic_search),
        ("Gap Analysis", example_2_gap_analysis),
        ("Comparative Analysis", example_3_comparative_analysis),
        ("Full Report", example_4_full_report),
        ("Emerging Topics", example_5_emerging_topics),
        ("BibTeX Export", example_6_export_bibtex),
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
