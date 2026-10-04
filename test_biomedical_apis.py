#!/usr/bin/env python3
"""Quick test script to verify Europe PMC and PubChem APIs are working."""

import asyncio
from agents.literature_agent import LiteratureAgent


async def test_europe_pmc():
    """Test Europe PMC API directly."""
    print("\n" + "="*60)
    print("🧪 TEST 1: Europe PMC API")
    print("="*60)

    agent = LiteratureAgent()

    try:
        print("Searching Europe PMC for: 'cancer drug discovery'...")
        papers = await agent.search_papers(
            query="cancer drug discovery",
            databases=["europe_pmc"],
            year_range=(2020, 2026),
            limit=3
        )

        if papers:
            print(f"\n✅ SUCCESS: Found {len(papers)} papers\n")

            for i, paper in enumerate(papers, 1):
                print(f"{i}. {paper.title[:70]}")
                print(f"   PMCID: {paper.pmcid}")
                print(f"   Year: {paper.publication_year}")
                if paper.disease_targets:
                    print(f"   Disease Targets: {', '.join(paper.disease_targets[:2])}")
                if paper.molecular_targets:
                    print(f"   Molecular Targets: {', '.join(paper.molecular_targets[:2])}")
                if paper.mesh_terms:
                    print(f"   MeSH Terms: {', '.join(paper.mesh_terms[:2])}")
                print()

            return True
        else:
            print("❌ FAILED: No papers returned")
            return False

    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

    finally:
        await agent.close()


async def test_pubchem():
    """Test PubChem API directly."""
    print("\n" + "="*60)
    print("🧪 TEST 2: PubChem API")
    print("="*60)

    agent = LiteratureAgent()

    try:
        print("Searching PubChem for: 'kinase inhibitor'...")
        compounds = await agent.search_papers(
            query="kinase inhibitor",
            databases=["pubchem"],
            limit=3
        )

        if compounds:
            print(f"\n✅ SUCCESS: Found {len(compounds)} compounds\n")

            for i, compound in enumerate(compounds, 1):
                print(f"{i}. {compound.title[:70]}")
                if compound.compound_cids:
                    print(f"   PubChem CIDs: {', '.join(compound.compound_cids[:2])}")
                if compound.molecular_targets:
                    print(f"   Molecular Targets: {', '.join(compound.molecular_targets[:2])}")
                if compound.assay_types:
                    print(f"   Assay Types: {', '.join(compound.assay_types[:2])}")
                if compound.organism_studied:
                    print(f"   Organism: {compound.organism_studied}")
                print()

            return True
        else:
            print("❌ FAILED: No compounds returned")
            return False

    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

    finally:
        await agent.close()


async def test_combined():
    """Test both APIs together."""
    print("\n" + "="*60)
    print("🧪 TEST 3: Combined Search (Europe PMC + PubChem)")
    print("="*60)

    agent = LiteratureAgent()

    try:
        print("Searching both databases for: 'EGFR inhibitor'...")
        results = await agent.search_papers(
            query="EGFR inhibitor",
            databases=["europe_pmc", "pubchem"],
            year_range=(2020, 2026),
            limit=5
        )

        if results:
            pmc_papers = [r for r in results if r.pmcid]
            pubchem_compounds = [r for r in results if r.compound_cids]

            print(f"\n✅ SUCCESS: Found {len(results)} total results\n")
            print(f"   Europe PMC papers: {len(pmc_papers)}")
            print(f"   PubChem compounds: {len(pubchem_compounds)}\n")

            if pmc_papers:
                print("Sample Europe PMC result:")
                p = pmc_papers[0]
                print(f"  • {p.title[:60]}")
                print(f"    PMCID: {p.pmcid}\n")

            if pubchem_compounds:
                print("Sample PubChem result:")
                c = pubchem_compounds[0]
                print(f"  • {c.title[:60]}")
                if c.compound_cids:
                    print(f"    CID: {c.compound_cids[0]}\n")

            return True
        else:
            print("❌ FAILED: No results returned")
            return False

    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

    finally:
        await agent.close()


async def test_gap_detection():
    """Test gap detection on retrieved papers."""
    print("\n" + "="*60)
    print("🧪 TEST 4: Gap Detection on Biomedical Papers")
    print("="*60)

    agent = LiteratureAgent()

    try:
        print("Searching for papers and detecting gaps...")
        papers = await agent.search_papers(
            query="drug resistance antibiotic",
            databases=["europe_pmc"],
            limit=10
        )

        if papers:
            print(f"Found {len(papers)} papers, analyzing for gaps...")
            gaps = await agent.identify_gaps(papers)

            if gaps:
                print(f"\n✅ SUCCESS: Identified {len(gaps)} research gaps\n")

                for i, gap in enumerate(gaps[:3], 1):
                    print(f"{i}. {gap.gap_description}")
                    print(f"   Priority: {gap.priority_level}")
                    print(f"   Confidence: {gap.confidence:.0%}\n")

                return True
            else:
                print("⚠️  No gaps detected (may depend on papers)")
                return True
        else:
            print("❌ FAILED: No papers found")
            return False

    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

    finally:
        await agent.close()


async def main():
    """Run all tests."""
    print("\n" + "="*60)
    print("BIOMEDICAL API INTEGRATION TEST SUITE")
    print("="*60)
    print("\nTesting Europe PMC and PubChem API integrations...")

    results = []

    # Run tests
    results.append(("Europe PMC API", await test_europe_pmc()))
    results.append(("PubChem API", await test_pubchem()))
    results.append(("Combined Search", await test_combined()))
    results.append(("Gap Detection", await test_gap_detection()))

    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60 + "\n")

    for name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status:10} {name}")

    total_passed = sum(1 for _, p in results if p)
    total_tests = len(results)

    print(f"\nTotal: {total_passed}/{total_tests} tests passed")

    if total_passed == total_tests:
        print("\n🎉 ALL TESTS PASSED!")
        print("\nEurope PMC and PubChem APIs are working correctly.")
        print("Ready to use in the drug discovery pipeline!")
        return True
    elif total_passed > 0:
        print(f"\n⚠️  {total_tests - total_passed} test(s) failed")
        print("See errors above for details.")
        return False
    else:
        print("\n❌ ALL TESTS FAILED")
        print("Check your internet connection and API access.")
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)
