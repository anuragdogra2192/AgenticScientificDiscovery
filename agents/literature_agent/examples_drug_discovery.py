"""Drug Discovery and Biology Examples for the Literature Agent.

These examples demonstrate the agent's ability to search biomedical literature
using Europe PMC and PubChem, extract molecular evidence, and identify drug
discovery research gaps.
"""

import asyncio
import json
from agents.literature_agent import LiteratureAgent


async def example_1_cancer_drug_search():
    """Example 1: Search for cancer drug discovery literature."""
    print("\n" + "="*70)
    print("EXAMPLE 1: Cancer Drug Discovery Literature Search")
    print("="*70)

    agent = LiteratureAgent()

    try:
        papers = await agent.search_papers(
            query="cancer immunotherapy PD-1 checkpoint inhibitor",
            databases=["europe_pmc", "openalex"],
            year_range=(2020, 2026),
            limit=10,
        )

        print(f"\n✓ Found {len(papers)} papers on cancer immunotherapy\n")

        for i, paper in enumerate(papers[:5], 1):
            print(f"{i}. {paper.title}")
            print(f"   Authors: {', '.join(paper.authors[:2])}...")
            print(f"   Year: {paper.publication_year}")
            if paper.pmcid:
                print(f"   PMCID: {paper.pmcid}")
            if paper.mesh_terms:
                print(f"   MeSH Terms: {', '.join(paper.mesh_terms[:3])}")
            if paper.disease_targets:
                print(f"   Disease Targets: {', '.join(paper.disease_targets)}")
            print()

    finally:
        await agent.close()


async def example_2_compound_screening():
    """Example 2: Search for compound screening and bioactivity data."""
    print("\n" + "="*70)
    print("EXAMPLE 2: Chemical Compound Bioactivity Screening")
    print("="*70)

    agent = LiteratureAgent()

    try:
        compounds = await agent.search_papers(
            query="kinase inhibitor drug candidate",
            databases=["pubchem"],
            limit=10,
        )

        print(f"\n✓ Found {len(compounds)} compound records\n")

        for i, compound in enumerate(compounds[:5], 1):
            print(f"{i}. {compound.title}")
            if compound.compound_cids:
                print(f"   PubChem CIDs: {', '.join(compound.compound_cids)}")
            if compound.molecular_targets:
                print(f"   Molecular Targets: {', '.join(compound.molecular_targets)}")
            if compound.assay_types:
                print(f"   Assay Types: {', '.join(compound.assay_types)}")
            if compound.organism_studied:
                print(f"   Organism: {compound.organism_studied}")
            print()

    finally:
        await agent.close()


async def example_3_drug_resistance_gap():
    """Example 3: Identify drug resistance research gaps."""
    print("\n" + "="*70)
    print("EXAMPLE 3: Drug Resistance Research Gap Analysis")
    print("="*70)

    agent = LiteratureAgent()

    try:
        papers = await agent.search_papers(
            query="antibiotic resistance MRSA multidrug",
            databases=["europe_pmc"],
            year_range=(2019, 2026),
            limit=15,
        )

        print(f"\n✓ Found {len(papers)} papers on antibiotic resistance\n")

        # Analyze gaps
        gaps = await agent.identify_gaps(papers)

        print(f"Identified {len(gaps)} research gaps:\n")

        for i, gap in enumerate(gaps[:4], 1):
            print(f"{i}. {gap.gap_description}")
            print(f"   Priority: {gap.priority_level.upper()}")
            print(f"   Confidence: {gap.confidence:.2%}")
            print(f"   Related papers: {len(gap.related_papers)}")
            print(f"   Potential approaches: {', '.join(gap.potential_approaches[:2])}")
            print()

    finally:
        await agent.close()


async def example_4_target_validation():
    """Example 4: Search for protein target validation studies."""
    print("\n" + "="*70)
    print("EXAMPLE 4: Protein Target Validation Literature")
    print("="*70)

    agent = LiteratureAgent()

    try:
        papers = await agent.search_papers(
            query="protein target validation CRISPR knockout",
            databases=["europe_pmc", "openalex"],
            year_range=(2020, 2026),
            limit=12,
        )

        print(f"\n✓ Found {len(papers)} papers on target validation\n")

        for i, paper in enumerate(papers[:5], 1):
            print(f"{i}. {paper.title}")
            print(f"   Year: {paper.publication_year}")
            if paper.molecular_targets:
                print(f"   Targets: {', '.join(paper.molecular_targets)}")
            if paper.mesh_terms:
                methods = [t for t in paper.mesh_terms if any(
                    x in t.lower() for x in ["crispr", "knockout", "knockdown"]
                )]
                if methods:
                    print(f"   Methods: {', '.join(methods)}")
            print()

    finally:
        await agent.close()


async def example_5_adme_optimization():
    """Example 5: Search for ADME/PK property optimization studies."""
    print("\n" + "="*70)
    print("EXAMPLE 5: Drug Property Optimization (ADME/PK)")
    print("="*70)

    agent = LiteratureAgent()

    try:
        papers = await agent.search_papers(
            query="ADME properties drug metabolism bioavailability",
            databases=["europe_pmc"],
            year_range=(2018, 2026),
            limit=12,
        )

        print(f"\n✓ Found {len(papers)} papers on drug property optimization\n")

        report = await agent.generate_report(
            query="ADME property optimization",
            papers=papers,
            gaps=[],
        )

        print(f"Literature Report Summary:")
        print(f"  Total papers: {report['statistics']['total_papers']}")
        print(f"  Year range: {report['statistics']['year_range']}")
        print(f"  Average citations: {report['statistics']['avg_citations']:.1f}")
        print()

        for i, paper in enumerate(papers[:5], 1):
            print(f"{i}. {paper.title[:70]}...")
            if paper.full_text_url:
                print(f"   Full text: {paper.full_text_url}")
            print()

    finally:
        await agent.close()


async def example_6_combination_therapy():
    """Example 6: Search for combination therapy studies."""
    print("\n" + "="*70)
    print("EXAMPLE 6: Combination Therapy Research")
    print("="*70)

    agent = LiteratureAgent()

    try:
        papers = await agent.search_papers(
            query="combination therapy synergistic effect drug interaction",
            databases=["europe_pmc"],
            year_range=(2020, 2026),
            limit=15,
        )

        print(f"\n✓ Found {len(papers)} papers on combination therapy\n")

        gaps = await agent.identify_gaps(papers)

        print(f"Key Gaps in Combination Therapy Research:\n")

        high_priority_gaps = [g for g in gaps if g.priority_level == "high"]
        for gap in high_priority_gaps[:3]:
            print(f"  • {gap.gap_description}")
            print(f"    Related to: {', '.join(gap.related_papers[:2])}")
            print()

    finally:
        await agent.close()


async def example_7_clinical_translation():
    """Example 7: Identify clinical translation opportunities."""
    print("\n" + "="*70)
    print("EXAMPLE 7: Preclinical to Clinical Translation Gaps")
    print("="*70)

    agent = LiteratureAgent()

    try:
        papers = await agent.search_papers(
            query="preclinical to clinical translation IND application",
            databases=["europe_pmc"],
            year_range=(2019, 2026),
            limit=15,
        )

        print(f"\n✓ Found {len(papers)} papers on clinical translation\n")

        gaps = await agent.identify_gaps(papers)

        print(f"Clinical Translation Gaps:\n")

        for gap in gaps[:5]:
            print(f"  • {gap.gap_description}")
            print(f"    Priority: {gap.priority_level} | Confidence: {gap.confidence:.1%}")
            print()

    finally:
        await agent.close()


async def main():
    """Run all examples."""
    print("\n" + "="*70)
    print("DRUG DISCOVERY LITERATURE AGENT - COMPREHENSIVE EXAMPLES")
    print("="*70)

    # Run examples
    await example_1_cancer_drug_search()
    await example_2_compound_screening()
    await example_3_drug_resistance_gap()
    await example_4_target_validation()
    await example_5_adme_optimization()
    await example_6_combination_therapy()
    await example_7_clinical_translation()

    print("\n" + "="*70)
    print("✅ ALL EXAMPLES COMPLETED")
    print("="*70 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
