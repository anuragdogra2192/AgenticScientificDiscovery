# Literature Agent: Drug Discovery & Biology Edition

The **Literature Agent v2.0** has been adapted for **Drug Discovery and Biology** research, with integrated support for Europe PMC biomedical literature and PubChem chemical compound databases.

## 🧬 What's New in v2.0

### Enhanced Data Sources

| Database | Purpose | API | Format |
|----------|---------|-----|--------|
| **Europe PMC** | Biomedical literature | REST JSON | PubMed Central articles, abstracts, citations |
| **PubChem** | Chemical compounds | REST JSON | Molecular properties, bioactivity assays |
| **OpenAlex** | Fallback academic source | REST JSON | General scientific papers with biomedical content |

### Biomedical Attributes

The Paper dataclass has been extended with drug discovery-specific fields:

```python
# New biomedical fields
pmcid: Optional[str]              # PubMed Central ID
pmid: Optional[str]               # PubMed ID
mesh_terms: Optional[list[str]]   # Medical Subject Headings
disease_targets: Optional[list[str]]  # Disease/condition targets
compound_cids: Optional[list[str]]    # PubChem Compound IDs
molecular_targets: Optional[list[str]] # Protein/molecular targets
assay_types: Optional[list[str]]      # Bioactivity assay types
organism_studied: Optional[str]       # Model organism or cell line
full_text_url: Optional[str]          # Full text access link
```

## 🚀 Quick Start

### Basic Drug Discovery Search

```python
import asyncio
from agents.literature_agent import LiteratureAgent

async def search_drug_targets():
    agent = LiteratureAgent()
    
    try:
        papers = await agent.search_papers(
            query="kinase inhibitor cancer therapy",
            databases=["europe_pmc", "openalex"],
            year_range=(2020, 2026),
            limit=50
        )
        
        for paper in papers:
            if paper.disease_targets:
                print(f"Target: {paper.disease_targets[0]}")
            if paper.mesh_terms:
                print(f"MeSH: {paper.mesh_terms[0]}")
            if paper.compound_cids:
                print(f"PubChem CID: {paper.compound_cids[0]}")
    
    finally:
        await agent.close()

asyncio.run(search_drug_targets())
```

### Compound Screening Search

```python
async def search_compounds():
    agent = LiteratureAgent()
    
    try:
        compounds = await agent.search_papers(
            query="EGFR inhibitor",
            databases=["pubchem"],
            limit=20
        )
        
        for compound in compounds:
            print(f"Compound: {compound.title}")
            print(f"  Targets: {compound.molecular_targets}")
            print(f"  Assays: {compound.assay_types}")
    
    finally:
        await agent.close()

asyncio.run(search_compounds())
```

## 🔬 Use Cases

### 1. Target Identification
```python
# Search for understudied disease targets
papers = await agent.search_papers(
    "novel disease target validation CRISPR",
    databases=["europe_pmc"],
    year_range=(2022, 2026),
    limit=50
)

gaps = await agent.identify_gaps(papers)
# Gaps will highlight unexplored targets and validation methods
```

### 2. Compound Library Search
```python
# Find bioactivity data for compound series
compounds = await agent.search_papers(
    "thienopyridine CDK inhibitor",
    databases=["pubchem"],
    limit=50
)

# Results include molecular properties and assay types
```

### 3. Drug Resistance Analysis
```python
# Identify resistance mechanisms and drug alternatives
papers = await agent.search_papers(
    "drug resistance mechanism MRSA vancomycin",
    databases=["europe_pmc"],
    year_range=(2018, 2026),
    limit=50
)

gaps = await agent.identify_gaps(papers)
# Gaps highlight unaddressed resistance problems
```

### 4. ADME Property Optimization
```python
# Find literature on drug property optimization
papers = await agent.search_papers(
    "ADME properties solubility bioavailability optimization",
    databases=["europe_pmc"],
    limit=30
)

report = await agent.generate_report(
    query="ADME optimization",
    papers=papers,
    gaps=[]
)
```

## 📊 API Reference

### search_papers()

```python
async def search_papers(
    query: str,
    databases: list[str] = None,
    year_range: tuple[int, int] = None,
    limit: int = None
) -> list[BiomedicalRecord]
```

**Parameters:**
- `query` (str): Research question or drug discovery topic
- `databases` (list[str]): Which sources to query
  - `"europe_pmc"` - Biomedical literature (default)
  - `"pubchem"` - Chemical compounds
  - `"openalex"` - General academic papers
  - `"arxiv"` - Preprints
- `year_range` (tuple[int, int]): Publication years to include
- `limit` (int): Maximum results per database

**Returns:** List of `BiomedicalRecord` objects with biomedical fields populated

### identify_gaps()

```python
async def identify_gaps(
    papers: list[BiomedicalRecord]
) -> list[ResearchGap]
```

Enhanced gap detection for drug discovery topics:
- Untested compounds
- Unexplored drug targets
- Limited bioactivity data
- Novel mechanisms of action
- Drug resistance patterns
- Off-target effects
- ADME optimization opportunities
- Clinical translation gaps

## 🔗 Integration with Downstream Agents

### Hypothesis Agent

The biomedical data flows seamlessly to the Hypothesis Agent:

```python
# Literature findings are passed as-is
papers = await lit_agent.search_papers(
    "cancer immunotherapy PD-1",
    databases=["europe_pmc"]
)

# Hypothesis agent receives enhanced features
hypotheses = await hyp_agent.generate_hypotheses(
    papers=[{
        "title": p.title,
        "disease_targets": p.disease_targets,  # ✨ New field
        "molecular_targets": p.molecular_targets,
        "assay_types": p.assay_types,
        "mesh_terms": p.mesh_terms
    } for p in papers]
)
```

### Experiment Agent

Uses disease targets and assay types for experimental design:

```python
# Experiment planning uses molecular targets
design = await exp_agent.design_experiment(
    hypothesis={
        "molecular_targets": ["EGFR", "ALK"],
        "disease_targets": ["non-small cell lung cancer"],
        "suggested_assay_types": ["kinase assay", "cell viability"]
    }
)
```

### Analysis Agent

Interprets findings in biomedical context:

```python
# Analysis interprets results against known targets
report = await ana_agent.analyze_results(
    design=experimental_design,
    hypothesis={
        "molecular_targets": hyp.molecular_targets,
        "disease_targets": hyp.disease_targets
    },
    results_data=experiment_results
)
```

## 📈 Example Workflow: Complete Drug Discovery Pipeline

```python
async def drug_discovery_workflow():
    """Complete pipeline from literature to hypothesis."""
    
    # Phase 1: Search biomedical literature
    lit_agent = LiteratureAgent()
    papers = await lit_agent.search_papers(
        "Alzheimer's disease amyloid-beta tau protein",
        databases=["europe_pmc"],
        year_range=(2020, 2026),
        limit=50
    )
    
    # Identify research gaps
    gaps = await lit_agent.identify_gaps(papers)
    
    # Phase 2: Generate drug discovery hypotheses
    hyp_agent = HypothesisAgent()
    hypotheses = await hyp_agent.generate_hypotheses(
        papers=[{
            "title": p.title,
            "disease_targets": p.disease_targets or [],
            "mesh_terms": p.mesh_terms or []
        } for p in papers],
        research_gaps=[{
            "description": g.gap_description,
            "related_targets": g.related_papers
        } for g in gaps]
    )
    
    # Phase 3: Design experiments for top hypothesis
    exp_agent = ExperimentAgent()
    selected = hypotheses[0]
    design = await exp_agent.design_experiment(
        selected.to_dict()
    )
    
    # Use biomedical attributes to suggest assay types
    if design.suggested_assay_types:
        print(f"Suggested assays: {design.suggested_assay_types}")
    
    return {
        "papers": len(papers),
        "targets": list(set(t for p in papers 
                          for t in (p.molecular_targets or []))),
        "hypotheses": len(hypotheses),
        "design": design
    }
```

## 🔍 Biomedical Entity Extraction

The agent automatically extracts and categorizes biomedical entities:

```python
# Available entity types
ENTITY_TYPES = [
    "disease",              # Cancer, Alzheimer's, COVID-19
    "drug_name",           # Aspirin, Metformin
    "protein_target",      # EGFR, TP53, BRCA1
    "gene",                # TP53, EGFR genes
    "organism",            # Human, Mouse, E. coli
    "cell_type",           # HEK293, HeLa
    "assay_type",          # ELISA, western blot, RNAi
    "pathway",             # Wnt signaling, MAPK pathway
    "chemical_compound"    # Drug-like molecules
]
```

## 📚 MeSH Term Filtering

Europe PMC results include Medical Subject Headings (MeSH):

```python
# Filter by MeSH terms
papers = await agent.search_papers(
    "drug discovery",
    year_range=(2020, 2026),
    limit=50
)

# Check MeSH terms for specific disease areas
cancer_papers = [p for p in papers if any(
    "neoplasm" in mesh.lower() for mesh in (p.mesh_terms or [])
)]

# Check for experimental methods
crispr_papers = [p for p in papers if any(
    "crispr" in mesh.lower() for mesh in (p.mesh_terms or [])
)]
```

## 🧪 PubChem Integration Details

When querying PubChem:

1. **Compound Search**: Finds compounds matching query
2. **Bioactivity Retrieval**: Gets assay data for each compound
3. **Target Mapping**: Extracts molecular targets
4. **Property Extraction**: Collects molecular weight, formula, etc.

```python
# Results include compound-specific data
compounds = await agent.search_papers(
    "tyrosine kinase inhibitor",
    databases=["pubchem"],
    limit=10
)

for compound in compounds:
    print(f"Name: {compound.title}")
    print(f"PubChem ID: {compound.compound_cids}")
    print(f"Targets: {compound.molecular_targets}")
    print(f"Assay Types: {compound.assay_types}")
    print(f"Organism: {compound.organism_studied}")
```

## ⚙️ Configuration

Edit `agents/literature_agent/config.yaml` to customize:

- Search parameters and limits
- MeSH term priorities
- Drug discovery keywords
- Gap detection keywords
- Cache settings
- Logging level

## 🔄 Workflow Integration

The biomedical Literature Agent fits into the complete pipeline:

```
[📚 Biomedical Literature]
     ↓ (papers + disease/molecular targets)
[💡 Hypothesis Agent] → Drug discovery hypotheses
     ↓ (target molecules + assay types)
[🧪 Experiment Agent] → Experimental design
     ↓ (results data)
[📊 Analysis Agent] → Statistical findings
     ↓ (findings + targets)
[📝 Report Agent] → Publication-ready paper
```

## 📊 Output Formats

Results can be exported as:

```python
# JSON (structured data)
report = await agent.generate_report(query, papers, gaps)
json_data = json.dumps(report)

# Markdown (human-readable)
# BibTeX (citation management)
# RDF (semantic web)
```

## 🛠️ Troubleshooting

### No results from Europe PMC
- Check internet connectivity
- Verify query syntax (use biomedical terms)
- Try simpler query terms
- Check date range

### No results from PubChem
- Compound names must match PubChem naming
- Some queries may return no bioactivity data
- Try SMILES notation or CAS numbers

### Empty biomedical fields
- Some papers may not have MeSH terms
- Not all queries return disease targets
- PubChem results focus on compounds, not disease

## 📖 Examples

Run the comprehensive drug discovery examples:

```bash
python agents/literature_agent/examples_drug_discovery.py
```

Includes:
1. Cancer drug discovery search
2. Compound screening
3. Drug resistance gaps
4. Target validation
5. ADME optimization
6. Combination therapy
7. Clinical translation gaps

## 🚀 Next Steps

After gathering literature and identifying gaps:

1. **Generate hypotheses** with the Hypothesis Agent
2. **Design experiments** with the Experiment Agent
3. **Analyze results** with the Analysis Agent
4. **Generate reports** with the Report Agent

---

**For complete orchestration**, see the Master Orchestrator documentation at `ORCHESTRATOR_README.md`

**Drug Discovery Pipeline Ready!** 🧬
