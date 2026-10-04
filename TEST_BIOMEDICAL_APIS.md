# Testing Guide: Europe PMC and PubChem APIs

This guide shows how to verify that the biomedical API integrations are working correctly.

## 🧪 Quick Test Methods

### Method 1: Run the Examples (Easiest)

```bash
cd /Users/adogra/Documents/GitHub/AgenticScientificDiscovery
python agents/literature_agent/examples_drug_discovery.py
```

**What to expect:**
- First example takes 5-10 seconds
- Shows "✓ Found X papers on cancer immunotherapy"
- Lists paper titles with PMCID fields
- Shows MeSH terms and disease targets
- Examples 2-7 follow similar pattern

### Method 2: Simple Python Test Script

Create a test file:

```python
# test_apis.py
import asyncio
from agents.literature_agent import LiteratureAgent

async def test_europe_pmc():
    """Test Europe PMC API directly."""
    print("\n🧪 Testing Europe PMC API...")
    agent = LiteratureAgent()
    
    try:
        papers = await agent.search_papers(
            query="cancer drug discovery",
            databases=["europe_pmc"],
            year_range=(2020, 2026),
            limit=5
        )
        
        if papers:
            print(f"✅ Europe PMC SUCCESS: Found {len(papers)} papers\n")
            
            for i, paper in enumerate(papers[:3], 1):
                print(f"{i}. {paper.title[:60]}...")
                print(f"   Year: {paper.publication_year}")
                print(f"   PMCID: {paper.pmcid}")
                print(f"   Disease Targets: {paper.disease_targets}")
                print(f"   Molecular Targets: {paper.molecular_targets}")
                print(f"   Mesh Terms: {paper.mesh_terms[:2] if paper.mesh_terms else 'None'}")
                print()
            return True
        else:
            print("❌ Europe PMC FAILED: No papers returned\n")
            return False
    
    except Exception as e:
        print(f"❌ Europe PMC ERROR: {e}\n")
        return False
    
    finally:
        await agent.close()


async def test_pubchem():
    """Test PubChem API directly."""
    print("🧪 Testing PubChem API...")
    agent = LiteratureAgent()
    
    try:
        compounds = await agent.search_papers(
            query="kinase inhibitor",
            databases=["pubchem"],
            limit=5
        )
        
        if compounds:
            print(f"✅ PubChem SUCCESS: Found {len(compounds)} compounds\n")
            
            for i, compound in enumerate(compounds[:3], 1):
                print(f"{i}. {compound.title[:60]}...")
                print(f"   PubChem IDs: {compound.compound_cids}")
                print(f"   Molecular Targets: {compound.molecular_targets}")
                print(f"   Assay Types: {compound.assay_types}")
                print(f"   Organism: {compound.organism_studied}")
                print()
            return True
        else:
            print("❌ PubChem FAILED: No compounds returned\n")
            return False
    
    except Exception as e:
        print(f"❌ PubChem ERROR: {e}\n")
        return False
    
    finally:
        await agent.close()


async def test_combined():
    """Test both APIs together."""
    print("🧪 Testing Combined Search...")
    agent = LiteratureAgent()
    
    try:
        results = await agent.search_papers(
            query="EGFR inhibitor lung cancer",
            databases=["europe_pmc", "pubchem"],
            year_range=(2020, 2026),
            limit=10
        )
        
        if results:
            pmc_papers = [r for r in results if r.pmcid]
            pubchem_compounds = [r for r in results if r.compound_cids]
            
            print(f"✅ COMBINED SUCCESS:")
            print(f"   Total results: {len(results)}")
            print(f"   Europe PMC papers: {len(pmc_papers)}")
            print(f"   PubChem compounds: {len(pubchem_compounds)}\n")
            return True
        else:
            print("❌ COMBINED FAILED: No results\n")
            return False
    
    except Exception as e:
        print(f"❌ COMBINED ERROR: {e}\n")
        return False
    
    finally:
        await agent.close()


async def main():
    """Run all tests."""
    print("=" * 60)
    print("BIOMEDICAL API INTEGRATION TEST")
    print("=" * 60)
    
    results = []
    results.append(("Europe PMC", await test_europe_pmc()))
    results.append(("PubChem", await test_pubchem()))
    results.append(("Combined", await test_combined()))
    
    print("=" * 60)
    print("TEST RESULTS SUMMARY")
    print("=" * 60)
    
    for name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} - {name}")
    
    all_passed = all(r[1] for r in results)
    
    if all_passed:
        print("\n🎉 ALL TESTS PASSED!")
        print("Europe PMC and PubChem APIs are working correctly.")
    else:
        print("\n⚠️  SOME TESTS FAILED")
        print("See errors above for troubleshooting.")
    
    return all_passed


if __name__ == "__main__":
    asyncio.run(main())
```

**Run the test:**
```bash
python test_apis.py
```

**Expected output:**
```
✅ Europe PMC SUCCESS: Found 12 papers
✅ PubChem SUCCESS: Found 8 compounds
✅ COMBINED SUCCESS: Total results 20
🎉 ALL TESTS PASSED!
```

## 🔍 Manual API Testing (curl commands)

### Test 1: Europe PMC Direct API Call

```bash
# Search Europe PMC directly
curl -X GET \
  "https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=cancer+drug&pageSize=5&resultType=core&format=json" \
  -H "Accept: application/json"
```

**Expected response:**
```json
{
  "resultList": {
    "result": [
      {
        "title": "Cancer drug discovery...",
        "pmcid": "1234567",
        "pubYear": "2023",
        "abstract": "...",
        "meshHeadingList": {
          "meshHeading": [
            {"descriptorName": "Neoplasms"},
            {"descriptorName": "Drug Therapy"}
          ]
        }
      }
    ]
  },
  "hitCount": 50000
}
```

### Test 2: PubChem Direct API Call

```bash
# Search PubChem for compounds
curl -X GET \
  "https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/search/json?q=kinase+inhibitor&type=cid" \
  -H "Accept: application/json"
```

**Expected response:**
```json
{
  "IdentifierList": {
    "CID": [
      1234567,
      2345678,
      3456789
    ]
  }
}
```

## 🛠️ Troubleshooting

### Issue 1: "No results found"

**Possible causes:**
- Query too specific or using non-standard terminology
- Network connectivity issue
- API temporarily down

**Solutions:**
```python
# Try simpler queries
await agent.search_papers("cancer", databases=["europe_pmc"], limit=5)
await agent.search_papers("aspirin", databases=["pubchem"], limit=5)

# Check internet connection
import httpx
async with httpx.AsyncClient() as client:
    response = await client.get("https://www.google.com")
    print(f"Internet: {response.status_code}")
```

### Issue 2: "Connection timeout"

**Solutions:**
```python
# Increase timeout
agent.client = httpx.AsyncClient(timeout=60.0)

# Try one API at a time
papers = await agent.search_papers("cancer", databases=["europe_pmc"])
```

### Issue 3: "Empty biomedical fields"

**Explanation:**
- Not all papers have MeSH terms
- Disease targets depend on paper content
- Some queries may not return structured data

**Verify it's still working:**
```python
# Check if papers were found
if papers:
    print(f"Found {len(papers)} papers")
    print(f"With disease targets: {sum(1 for p in papers if p.disease_targets)}")
    print(f"With molecular targets: {sum(1 for p in papers if p.molecular_targets)}")
```

## 📊 Validation Checklist

### Europe PMC Integration

- [ ] Can search with `databases=["europe_pmc"]`
- [ ] Returns `BiomedicalRecord` objects
- [ ] `pmcid` field is populated
- [ ] `mesh_terms` list contains MeSH headings
- [ ] `disease_targets` extracted from MeSH
- [ ] `molecular_targets` identified
- [ ] `full_text_url` points to PMC article

**Test command:**
```python
papers = await agent.search_papers(
    "Alzheimer's disease tau protein",
    databases=["europe_pmc"],
    limit=1
)
assert papers[0].pmcid is not None, "PMCID missing!"
assert papers[0].mesh_terms, "MeSH terms missing!"
print("✅ Europe PMC working correctly")
```

### PubChem Integration

- [ ] Can search with `databases=["pubchem"]`
- [ ] Returns `BiomedicalRecord` objects
- [ ] `compound_cids` populated with PubChem IDs
- [ ] `molecular_targets` extracted
- [ ] `assay_types` identified
- [ ] `organism_studied` present

**Test command:**
```python
compounds = await agent.search_papers(
    "EGFR inhibitor",
    databases=["pubchem"],
    limit=1
)
assert compounds[0].compound_cids, "PubChem CIDs missing!"
assert compounds[0].molecular_targets, "Targets missing!"
print("✅ PubChem working correctly")
```

### Combined Search

- [ ] Can search both `["europe_pmc", "pubchem"]`
- [ ] Returns mixed results
- [ ] No duplicates
- [ ] All biomedical fields present

**Test command:**
```python
results = await agent.search_papers(
    "kinase cancer drug",
    databases=["europe_pmc", "pubchem"],
    limit=5
)
assert len(results) > 0, "No results!"
pmc_count = sum(1 for r in results if r.pmcid)
pubchem_count = sum(1 for r in results if r.compound_cids)
print(f"✅ Combined: {pmc_count} PMC + {pubchem_count} PubChem")
```

## 📈 Performance Testing

### Expected Response Times

```python
import time

async def benchmark():
    agent = LiteratureAgent()
    
    # Benchmark Europe PMC
    start = time.time()
    papers = await agent.search_papers(
        "cancer", databases=["europe_pmc"], limit=10
    )
    pmc_time = time.time() - start
    print(f"Europe PMC: {pmc_time:.2f}s for {len(papers)} papers")
    
    # Benchmark PubChem
    start = time.time()
    compounds = await agent.search_papers(
        "inhibitor", databases=["pubchem"], limit=10
    )
    pubchem_time = time.time() - start
    print(f"PubChem: {pubchem_time:.2f}s for {len(compounds)} compounds")
    
    # Benchmark combined
    start = time.time()
    combined = await agent.search_papers(
        "cancer", databases=["europe_pmc", "pubchem"], limit=20
    )
    combined_time = time.time() - start
    print(f"Combined: {combined_time:.2f}s for {len(combined)} results")
    
    await agent.close()

asyncio.run(benchmark())
```

**Expected times:**
- Europe PMC single search: 2-5 seconds
- PubChem single search: 1-3 seconds
- Combined search: 5-10 seconds
- Gap detection on 50 papers: ~1 second

## ✅ Success Indicators

### Successful Europe PMC Search
```
✅ Papers found with:
   - Valid titles
   - Author lists
   - Publication years
   - PMCID/PMID
   - Abstracts
   - MeSH terms
   - Disease targets extracted
   - Molecular targets identified
```

### Successful PubChem Search
```
✅ Compounds found with:
   - Valid compound titles
   - PubChem CID(s)
   - Molecular targets
   - Assay types
   - Organism information
   - Bioactivity data
```

### Successful Gap Detection
```
✅ Gaps identified:
   - High priority gaps
   - Confidence levels (0.0-1.0)
   - Related papers listed
   - Potential approaches suggested
```

## 🚀 Next Steps After Validation

Once APIs are confirmed working:

1. **Test with downstream agents:**
   ```python
   papers = await lit_agent.search_papers(...)
   hypotheses = await hyp_agent.generate_hypotheses(papers)
   ```

2. **Test complete pipeline:**
   ```bash
   python run_discovery_loop.py
   ```

3. **Try drug discovery examples:**
   ```bash
   python agents/literature_agent/examples_drug_discovery.py
   ```

## 📞 Debugging

### Enable detailed logging:

```python
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("literature_agent")

# Now run searches with full debug output
papers = await agent.search_papers("cancer", databases=["europe_pmc"])
```

### Check API response directly:

```python
import httpx

async with httpx.AsyncClient() as client:
    # Test Europe PMC
    response = await client.get(
        "https://www.ebi.ac.uk/europepmc/webservices/rest/search",
        params={"query": "cancer", "pageSize": 5, "format": "json"}
    )
    print(f"Europe PMC: {response.status_code}")
    print(response.json()["resultList"]["result"][0])
```

---

**Ready to test?** Start with: `python agents/literature_agent/examples_drug_discovery.py`
