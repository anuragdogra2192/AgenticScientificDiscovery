"""Mycobacterium tuberculosis Drug Discovery Examples for the Literature Agent.

These examples demonstrate the agent's ability to search biomedical literature
for Mtb-specific targets, screen anti-tubercular compounds via PubChem, 
and analyze drug resistance gaps.
"""

import asyncio
import json
from agents.literature_agent import LiteratureAgent


async def example_1_tb_drug_search():
    """Example 1: Search for Mycobacterium tuberculosis drug discovery literature."""
    print("\n" + "="*70)
    print("EXAMPLE 1: Mycobacterium tuberculosis Target & Inhibitor Search")
    print("="*70)

    agent = LiteratureAgent()

    try:
        papers = await agent.search_papers(
            query="Mycobacterium tuberculosis DprE1 inhibitor drug discovery",
            databases=["europe_pmc", "openalex"],
            year_range=(2020, 2026),
            limit=10,
        )

        print(f"\n✓ Found {len(papers)} papers on Mtb DprE1 inhibitors\n")

        for i, paper in enumerate(papers[:5], 1):
            print(f"{i}. {paper.title}")
            print(f"   Authors: {', '.join(paper.authors[:2])}...")
            print(f"   Year: {paper.publication_year}")
            if paper.pmcid:
                print(f"   PMCID: {paper.pmcid}")
            if paper.molecular_targets:
                print(f"   Molecular Targets: {', '.join(paper.molecular_targets)}")
            print()

    finally:
        await agent.close()


async def example_2_tb_compound_screening():
    """Example 2: Search for anti-tubercular compound screening and bioactivity data."""
    print("\n" + "="*70)
    print("EXAMPLE 2: Anti-Tubercular Chemical Compound Screening (PubChem)")
    print("="*70)

    agent = LiteratureAgent()

    try:
        compounds = await agent.search_papers(
            query="Bedaquiline",
            databases=["pubchem"],
            limit=5,
        )

        print(f"\n✓ Found {len(compounds)} anti-tubercular compound records\n")

        for i, compound in enumerate(compounds[:5], 1):
            print(f"{i}. {compound.title}")
            if compound.compound_cids:
                print(f"   PubChem CIDs: {', '.join(compound.compound_cids)}")
            if compound.assay_types:
                print(f"   Assay Types: {', '.join(compound.assay_types)}")
            print()

    finally:
        await agent.close()


async def example_3_tb_drug_resistance_gap():
    """Example 3: Identify MDR/XDR-TB drug resistance research gaps."""
    print("\n" + "="*70)
    print("EXAMPLE 3: MDR/XDR-TB Drug Resistance Gap Analysis")
    print("="*70)

    agent = LiteratureAgent()

    try:
        papers = await agent.search_papers(
            query="multidrug resistant tuberculosis efflux pump resistance mechanism",
            databases=["europe_pmc"],
            year_range=(2019, 2026),
            limit=15,
        )

        print(f"\n✓ Found {len(papers)} papers on Mtb drug resistance mechanisms\n")

        gaps = await agent.identify_gaps(papers)

        print(f"Identified {len(gaps)} Mtb research gaps:\n")

        for i, gap in enumerate(gaps[:4], 1):
            print(f"{i}. {gap.gap_description}")
            print(f"   Priority: {gap.priority_level.upper()}")
            print(f"   Confidence: {gap.confidence:.2%}")
            print(f"   Related papers: {len(gap.related_papers)}")
            print(f"   Potential approaches: {', '.join(gap.potential_approaches[:2])}")
            print()

    finally:
        await agent.close()


async def example_4_tb_target_validation():
    """Example 4: Search for Mtb cell wall target validation studies (InhA, MmpL3, Pks13)."""
    print("\n" + "="*70)
    print("EXAMPLE 4: Mtb Cell Wall Target Validation (InhA & MmpL3)")
    print("="*70)

    agent = LiteratureAgent()

    try:
        papers = await agent.search_papers(
            query="Mycobacterium tuberculosis InhA MmpL3 target validation genetic knockdown",
            databases=["europe_pmc", "openalex"],
            year_range=(2020, 2026),
            limit=12,
        )

        print(f"\n✓ Found {len(papers)} papers on Mtb target validation\n")

        for i, paper in enumerate(papers[:5], 1):
            print(f"{i}. {paper.title}")
            print(f"   Year: {paper.publication_year}")
            if paper.molecular_targets:
                print(f"   Targets: {', '.join(paper.molecular_targets)}")
            print()

    finally:
        await agent.close()


async def example_5_tb_adme_optimization():
    """Example 5: Search for anti-tubercular ADME/PK and macrophage penetration studies."""
    print("\n" + "="*70)
    print("EXAMPLE 5: Anti-Tubercular ADME & Intracellular Penetration")
    print("="*70)

    agent = LiteratureAgent()

    try:
        papers = await agent.search_papers(
            query="Mycobacterium tuberculosis intracellular macrophage penetration pharmacokinetics ADME",
            databases=["europe_pmc"],
            year_range=(2018, 2026),
            limit=12,
        )

        print(f"\n✓ Found {len(papers)} papers on Mtb ADME and PK/PD optimization\n")

        report = await agent.generate_report(
            query="Mtb ADME & Intracellular Penetration",
            papers=papers,
            gaps=[],
        )

        print(f"Literature Report Summary:")
        print(f"  Total papers: {report['statistics']['total_papers']}")
        print(f"  Year range: {report['statistics']['year_range']}")
        print(f"  Average citations: {report['statistics']['avg_citations']:.1f}")
        print()

    finally:
        await agent.close()


async def example_6_tb_combination_therapy():
    """Example 6: Search for anti-tubercular combination therapy and synergy regimens."""
    print("\n" + "="*70)
    print("EXAMPLE 6: Anti-Tubercular Combination Therapy & Regimen Synergy")
    print("="*70)

    agent = LiteratureAgent()

    try:
        papers = await agent.search_papers(
            query="Mycobacterium tuberculosis combination therapy regimen synergistic interaction",
            databases=["europe_pmc"],
            year_range=(2020, 2026),
            limit=15,
        )

        print(f"\n✓ Found {len(papers)} papers on Mtb combination regimens\n")

        gaps = await agent.identify_gaps(papers)

        print(f"Key Gaps in Mtb Combination Therapy:\n")

        high_priority_gaps = [g for g in gaps if g.priority_level == "high"]
        for gap in high_priority_gaps[:3]:
            print(f"  • {gap.gap_description}")
            print(f"    Related papers: {', '.join(gap.related_papers[:2])}")
            print()

    finally:
        await agent.close()


async def example_7_tb_clinical_translation():
    """Example 7: Identify clinical translation opportunities for novel Mtb drug candidates."""
    print("\n" + "="*70)
    print("EXAMPLE 7: Preclinical to Clinical Translation for Anti-Tubercular Candidates")
    print("="*70)

    agent = LiteratureAgent()

    try:
        papers = await agent.search_papers(
            query="Mycobacterium tuberculosis novel drug candidate clinical trials phase preclinical translation",
            databases=["europe_pmc"],
            year_range=(2019, 2026),
            limit=15,
        )

        print(f"\n✓ Found {len(papers)} papers on Mtb clinical pipeline\n")

        gaps = await agent.identify_gaps(papers)

        print(f"Clinical Translation Gaps:\n")

        for gap in gaps[:5]:
            print(f"  • {gap.gap_description}")
            print(f"    Priority: {gap.priority_level} | Confidence: {gap.confidence:.1%}")
            print()

    finally:
        await agent.close()


async def main():
    """Run all Mycobacterium tuberculosis examples."""
    print("\n" + "="*70)
    print("MYCOBACTERIUM TUBERCULOSIS LITERATURE AGENT - SPECIALIZED EXAMPLES")
    print("="*70)

    await example_1_tb_drug_search()
    await example_2_tb_compound_screening()
    await example_3_tb_drug_resistance_gap()
    await example_4_tb_target_validation()
    await example_5_tb_adme_optimization()
    await example_6_tb_combination_therapy()
    await example_7_tb_clinical_translation()

    print("\n" + "="*70)
    print("✅ ALL MTB EXAMPLES COMPLETED")
    print("="*70 + "\n")


if __name__ == "__main__":
    asyncio.run(main())