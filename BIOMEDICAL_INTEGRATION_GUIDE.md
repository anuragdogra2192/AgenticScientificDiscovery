# Biomedical Integration Guide: Using Biomedical Literature in Downstream Agents

This guide explains how to use the new biomedical features of the Literature Agent (v2.0) with all downstream agents in the pipeline.

## 🧬 Overview

The upgraded **Literature Agent** now returns `BiomedicalRecord` objects with enhanced attributes specifically designed for drug discovery:

| New Field | Type | Purpose | Example |
|-----------|------|---------|---------|
| `pmcid` | str | PubMed Central ID | "PMC1234567" |
| `pmid` | str | PubMed ID | "12345678" |
| `mesh_terms` | list | Medical Subject Headings | ["Neoplasms", "Drug Therapy"] |
| `disease_targets` | list | Disease/condition targets | ["Colorectal Cancer", "Leukemia"] |
| `compound_cids` | list | PubChem Compound IDs | ["1234567", "2345678"] |
| `molecular_targets` | list | Protein/gene targets | ["EGFR", "KRAS", "TP53"] |
| `assay_types` | list | Bioactivity assay methods | ["kinase assay", "ELISA", "MTT"] |
| `organism_studied` | str | Model organism/cell line | "Human HEK293 cells" |
| `full_text_url` | str | Full-text access link | "https://www.ncbi.nlm.nih.gov/..." |

## 🔄 Integration Pattern 1: Hypothesis Agent

### Processing Biomedical Records

```python
from agents.literature_agent import LiteratureAgent
from agents.hypothesis_agent import HypothesisAgent

async def generate_drug_discovery_hypotheses():
    # Phase 1: Search biomedical literature
    lit_agent = LiteratureAgent()
    papers = await lit_agent.search_papers(
        query="EGFR mutation lung cancer therapy",
        databases=["europe_pmc"],
        year_range=(2020, 2026),
        limit=50
    )
    
    # Extract biomedical attributes
    disease_targets = list(set(
        target for paper in papers 
        for target in (paper.disease_targets or [])
    ))
    
    molecular_targets = list(set(
        target for paper in papers 
        for target in (paper.molecular_targets or [])
    ))
    
    # Phase 2: Generate hypotheses with biomedical context
    hyp_agent = HypothesisAgent()
    hypotheses = await hyp_agent.generate_hypotheses(
        papers=[{
            "title": p.title,
            "abstract": p.abstract,
            # NEW: Include biomedical attributes
            "disease_targets": p.disease_targets or [],
            "molecular_targets": p.molecular_targets or [],
            "mesh_terms": p.mesh_terms or [],
            "assay_types": p.assay_types or [],
            "compound_cids": p.compound_cids or [],
        } for p in papers],
        research_gaps=[{
            "description": f"Limited compounds targeting {', '.join(molecular_targets[:2])}",
            "priority_level": "high"
        }],
        query="EGFR mutation-specific inhibitors"
    )
    
    return hypotheses

# Example output with biomedical context:
# Hypothesis {
#   title: "Novel mutation-selective EGFR inhibitor"
#   molecular_targets: ["EGFR L858R", "EGFR DelEx19"],
#   disease_context: "Non-small cell lung cancer",
#   assay_suggestions: ["kinase assay", "cell viability"],
#   overall_score: 0.87
# }
```

### Recommended Hypothesis Strategies for Drug Discovery

```python
# Strategy 1: Target-specific gap bridging
# Use disease_targets and molecular_targets from literature
"Combine results from {disease_targets} literature search
 to propose {molecular_targets} inhibitor"

# Strategy 2: Compound-driven hypotheses
# Use compound_cids from PubChem data
"Scaffold hopping from known actives (CID: {compound_cids})
 to new series with improved properties"

# Strategy 3: Assay-informed hypotheses
# Use assay_types and mesh_terms
"Based on assay types ({assay_types}) in literature,
 propose compound with {properties}"

# Strategy 4: Cross-indication hypotheses
# Use multiple disease_targets
"Target identified in {disease_targets[0]} may address
 unmet need in {disease_targets[1]}"
```

## 🧪 Integration Pattern 2: Experiment Agent

### Using Biomedical Attributes for Experiment Design

```python
from agents.experiment_agent import ExperimentAgent

async def design_drug_discovery_experiment(hypothesis):
    exp_agent = ExperimentAgent()
    
    # Create experiment design with biomedical context
    design = await exp_agent.design_experiment(
        hypothesis={
            "title": hypothesis.title,
            "molecular_targets": hypothesis.molecular_targets,
            "disease_context": hypothesis.disease_context,
            # NEW: From literature agent
            "suggested_assay_types": hypothesis.get("assay_types", []),
            "organism_suggestions": hypothesis.get("organism_studied", ""),
            "compound_starting_points": hypothesis.get("compound_cids", []),
        }
    )
    
    return design

# Design will include:
# - experiment_type: Based on assay_types from literature
# - sample_size: Number of compounds to screen
# - assay_plan: Protocols matching suggested assay_types
# - datasets_needed: 
#     - PubChem bioactivity data for selected compounds
#     - Reference compounds from literature
#     - Target protein structures
# - resource_estimate:
#     - Assay equipment and reagents
#     - Compound library or synthesis
#     - Reference standards
```

### Drug Discovery Experiment Types

When biomedical context is available:

```python
# Experiment Type 1: High-Throughput Screening (HTS)
{
    "type": "High-Throughput Screening",
    "sample_size": 1000,
    "assay_types": ["primary_kinase", "selectivity_panel"],
    "datasets": ["PubChem compounds", "target structures"],
    "budget": "$200,000",
    "timeline": "12 weeks"
}

# Experiment Type 2: Structure-Activity Relationship (SAR)
{
    "type": "SAR Study",
    "sample_size": 100,
    "assay_types": ["kinase_dose_response", "cell_viability"],
    "datasets": ["literature compounds", "chemical series"],
    "budget": "$75,000",
    "timeline": "8 weeks"
}

# Experiment Type 3: Target Validation
{
    "type": "Target Validation",
    "sample_size": 50,
    "assay_types": ["target_engagement", "off_target_specificity"],
    "datasets": ["molecular_targets", "selectivity_data"],
    "budget": "$50,000",
    "timeline": "6 weeks"
}

# Experiment Type 4: ADME/PK Study
{
    "type": "ADME Profiling",
    "sample_size": 20,
    "assay_types": ["solubility", "permeability", "metabolism"],
    "datasets": ["lead_compounds", "reference_standards"],
    "budget": "$40,000",
    "timeline": "6 weeks"
}
```

## 📊 Integration Pattern 3: Analysis Agent

### Interpreting Results in Biomedical Context

```python
from agents.analysis_agent import AnalysisAgent

async def analyze_drug_discovery_results(
    design, hypothesis, experimental_results
):
    ana_agent = AnalysisAgent()
    
    report = await ana_agent.analyze_results(
        experimental_design=design,
        hypothesis={
            "title": hypothesis.title,
            "molecular_targets": hypothesis.molecular_targets,
            "disease_targets": hypothesis.disease_targets,
            "assay_types": hypothesis.suggested_assay_types,
        },
        results_data={
            "n": design.sample_size,
            "compounds_tested": design.sample_size,
            "hits_found": len(experimental_results.get("hits", [])),
            "potency_data": experimental_results.get("ic50_values"),
            "selectivity_data": experimental_results.get("selectivity"),
            "cellular_data": experimental_results.get("cell_viability"),
            "target_engagement": experimental_results.get("target_binding"),
            "variables": {
                "compound_series": list(experimental_results.keys()),
                "assay_types": design.assay_types,
            }
        }
    )
    
    return report

# Analysis output with biomedical interpretation:
# {
#   "hypothesis_confirmed": True,
#   "primary_finding": {
#       "description": "Novel dual EGFR/HER2 inhibitor superior",
#       "effect_size": 0.82,
#       "p_value": 0.0001,
#       "clinical_significance": "Medium effect"
#   },
#   "target_engagement": {
#       "molecular_targets": ["EGFR", "HER2"],
#       "selectivity": ">100-fold over off-targets",
#       "mechanism_validated": True
#   },
#   "findings": [
#       "Hit rate 8.5% for dual-targeting compounds",
#       "Selectivity maintained in panel of 100 kinases",
#       "Cell-based activity correlates with potency",
#       "Lead candidates demonstrate target engagement"
#   ]
# }
```

## 📝 Integration Pattern 4: Report Agent

### Generating Biomedical Research Papers

```python
from agents.report_agent import ReportAgent

async def generate_drug_discovery_paper(
    literature, hypothesis, design, analysis
):
    rep_agent = ReportAgent()
    
    paper = await rep_agent.generate_paper(
        hypothesis={
            "title": hypothesis.title,
            "molecular_targets": hypothesis.molecular_targets,
            "disease_context": hypothesis.disease_context,
            "assay_types": hypothesis.assay_types,
        },
        literature_findings=[{
            "title": p.title,
            "authors": p.authors,
            "year": p.publication_year,
            "pmcid": p.pmcid,
            "disease_targets": p.disease_targets,
            "molecular_targets": p.molecular_targets,
            "mesh_terms": p.mesh_terms,
            "full_text_url": p.full_text_url,
        } for p in literature],
        analysis_report=analysis.to_dict(),
        experiment_design=design.to_dict(),
    )
    
    return paper

# Paper sections auto-generated with biomedical context:

# Introduction
# - Background on disease_targets (cancer, Alzheimer's, etc.)
# - Current treatment landscape
# - Mechanism of molecular_targets
# - Rationale for dual-target approach
# - Cites 40+ papers from Europe PMC

# Methods
# - Compound selection rationale
# - assay_types and protocols
# - organism_studied and cell lines
# - Statistical analysis methods

# Results
# - Hit identification from screening
# - Potency comparison (IC50s, Kd)
# - Selectivity across kinase panel
# - Cellular target engagement
# - SAR analysis

# Discussion
# - Comparison with known compounds (from PubChem)
# - Mechanism discussion (molecular_targets)
# - Clinical implications for disease_targets
# - Limitations and future directions
# - Connection to research gaps from literature

# References
# - 60+ citations
# - Primarily from Europe PMC search
# - Includes PubChem compound references
# - All with DOI and hyperlinks
```

## 🔗 Complete Drug Discovery Workflow

```python
import asyncio
from agents.literature_agent import LiteratureAgent
from agents.hypothesis_agent import HypothesisAgent
from agents.experiment_agent import ExperimentAgent
from agents.analysis_agent import AnalysisAgent
from agents.report_agent import ReportAgent

async def full_drug_discovery_pipeline():
    """Complete drug discovery research automation."""
    
    # PHASE 1: Literature Discovery
    print("📚 Searching biomedical literature...")
    lit_agent = LiteratureAgent()
    papers = await lit_agent.search_papers(
        query="EGFR L858R mutation therapy resistance",
        databases=["europe_pmc", "pubchem"],
        year_range=(2020, 2026),
        limit=50
    )
    gaps = await lit_agent.identify_gaps(papers)
    print(f"  Found {len(papers)} papers, {len(gaps)} gaps")
    
    # Extract biomedical context
    disease_targets = list(set(
        t for p in papers for t in (p.disease_targets or [])
    ))
    molecular_targets = list(set(
        t for p in papers for t in (p.molecular_targets or [])
    ))
    assay_types = list(set(
        t for p in papers for t in (p.assay_types or [])
    ))
    
    # PHASE 2: Hypothesis Generation with biomedical context
    print("💡 Generating hypotheses...")
    hyp_agent = HypothesisAgent()
    hypotheses = await hyp_agent.generate_hypotheses(
        papers=[{
            "title": p.title,
            "abstract": p.abstract,
            "disease_targets": p.disease_targets,
            "molecular_targets": p.molecular_targets,
            "assay_types": p.assay_types,
        } for p in papers],
        research_gaps=[{
            "description": g.gap_description,
            "priority_level": g.priority_level
        } for g in gaps],
        query="EGFR L858R-selective inhibitors"
    )
    selected = hypotheses[0]
    print(f"  Generated {len(hypotheses)} hypotheses, score: {selected.overall_score:.3f}")
    
    # PHASE 3: Experiment Design
    print("🧪 Designing experiment...")
    exp_agent = ExperimentAgent()
    design = await exp_agent.design_experiment(
        hypothesis={
            **selected.to_dict(),
            "assay_types": assay_types,
            "disease_targets": disease_targets,
        }
    )
    print(f"  Design: {design.experiment_type.value}")
    print(f"  Budget: ${design.total_cost:,.0f}")
    print(f"  Timeline: {design.duration_weeks} weeks")
    
    # Simulate experiment results
    simulated_results = {
        "compounds_tested": design.sample_size,
        "hits_found": int(design.sample_size * 0.08),
        "lead_compounds": 5,
        "effect_size": 0.75,
        "p_value": 0.0001,
    }
    
    # PHASE 4: Analysis
    print("📊 Analyzing results...")
    ana_agent = AnalysisAgent()
    analysis = await ana_agent.analyze_results(
        experimental_design=design,
        hypothesis={
            **selected.to_dict(),
            "molecular_targets": molecular_targets,
        },
        results_data=simulated_results
    )
    print(f"  Hypothesis confirmed: {analysis.hypothesis_confirmed}")
    print(f"  Effect size: {analysis.primary_finding.effect_size:.3f}")
    
    # PHASE 5: Report Generation
    print("📝 Generating paper...")
    rep_agent = ReportAgent()
    paper = await rep_agent.generate_paper(
        hypothesis=selected.to_dict(),
        literature_findings=[{
            "title": p.title,
            "authors": p.authors[:3],
            "year": p.publication_year,
            "disease_targets": p.disease_targets,
            "molecular_targets": p.molecular_targets,
        } for p in papers[:20]],
        analysis_report=analysis.to_dict(),
        experiment_design=design.to_dict(),
    )
    print(f"  Paper: {paper.title}")
    print(f"  Word count: {paper.word_count}")
    print(f"  Figures: {len(paper.figures)}")
    print(f"  Tables: {len(paper.tables)}")
    print(f"  References: {len(paper.citations)}")
    
    # PHASE 6: Knowledge Graph Export
    if paper.knowledge_graph_export:
        print("🧠 Knowledge graph created")
        print(f"  Entities: {len(paper.knowledge_graph_export.get('entities', []))}")
        print(f"  Relationships: {len(paper.knowledge_graph_export.get('relationships', []))}")
    
    print("\n✅ COMPLETE DRUG DISCOVERY PIPELINE FINISHED!")
    print(f"📄 Paper ready for publication")
    print(f"📊 Results saved to ./results/")
    
    return {
        "papers": len(papers),
        "hypotheses": len(hypotheses),
        "design": design,
        "analysis": analysis,
        "paper": paper,
    }

# Run the pipeline
if __name__ == "__main__":
    result = asyncio.run(full_drug_discovery_pipeline())
```

## 🎯 Key Considerations

### 1. Data Availability
- Not all papers have all biomedical fields
- Some fields may be None/empty
- Check before using: `if paper.molecular_targets:`

### 2. Field Interpretation
- `mesh_terms`: Medical Subject Headings from PubMed
- `disease_targets`: Extracted from text/MeSH, may need validation
- `molecular_targets`: Protein/gene names (may need standardization)
- `compound_cids`: Valid PubChem IDs for compound lookup

### 3. Downstream Processing
- Convert lists to sets to remove duplicates
- Standardize target names (gene symbols, protein names)
- Validate MeSH terms against official hierarchy
- Map chemical compounds to standardized names

### 4. Performance Considerations
- Paper searches may take 10-30 seconds
- PubChem queries rate-limited to 5 req/sec
- Europe PMC queries rate-limited to 10 req/sec
- Cache results locally with `cache_dir` setting

## 🔗 Full Pipeline Execution

Use the Master Orchestrator for complete automation:

```python
from run_discovery_loop import DiscoveryOrchestrator

async def run_full_pipeline():
    orchestrator = DiscoveryOrchestrator()
    
    state = await orchestrator.run_discovery_loop(
        research_question="Novel EGFR L858R-selective inhibitors",
        literature_limit=100,
        auto_approve=True
    )
    
    # Results saved automatically
    return state
```

## 📚 Related Documentation

- `agents/literature_agent/DRUG_DISCOVERY_GUIDE.md` - Complete Literature Agent API
- `agents/literature_agent/config.yaml` - Configuration reference
- `DRUG_DISCOVERY_PIPELINE.md` - Complete workflow visualization
- `ORCHESTRATOR_README.md` - Master orchestrator usage

---

**Biomedical integration complete!** Ready for drug discovery research automation! 🧬
