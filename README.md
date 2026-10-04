# 🔬 Agentic Scientific Discovery Lab

An AI-powered lab for accelerating scientific discovery through specialized agents that search literature, generate hypotheses, design experiments, and analyze results—all autonomously.

## 🎯 Vision

Traditional scientific research involves many manual steps:
- ❌ Tedious literature searches across multiple databases
- ❌ Manual synthesis of findings and identification of gaps
- ❌ Ad-hoc hypothesis generation
- ❌ Experimental design by trial and error
- ❌ Result analysis without context

Our solution: **A team of specialist AI agents** that collaborate to accelerate the entire research pipeline.

## 🧠 Agent Architecture

Each agent is specialized for a specific research task:

### 1. 📚 **Literature Agent** (✅ Available)
Searches scientific databases, extracts evidence, and identifies research gaps.
- Queries OpenAlex, arXiv, Semantic Scholar
- Performs citation network analysis
- Detects emerging trends and research gaps
- Generates literature reviews

**Status**: Fully implemented and ready to use
**[Learn more →](agents/literature_agent/README.md)**

### 2. 💡 **Hypothesis Agent** (✅ Available)
Generates novel hypotheses based on literature using Claude Haiku 4.5.
- Analyzes literature patterns and gaps with AI intelligence
- Generates 5-7 novel hypotheses targeting Mtb drug discovery
- Ranks hypotheses by novelty, feasibility, impact, and testability
- Returns structured scoring for decision making

**Status**: Fully implemented with Claude integration and graceful fallback
**[Learn more →](agents/hypothesis_agent/README.md)**

### 3. 🧪 **Experiment Agent** (✅ Available)
Designs rigorous BSL-3 experimental protocols using Claude Haiku 4.5.
- Generates BSL-3 experimental protocols for Mtb targets
- Estimates sample sizes, budgets, and timelines
- Includes safety considerations and risk assessment
- Validates against budget constraints (<$100k)

**Status**: Fully implemented with Claude integration and graceful fallback
**[Learn more →](agents/experiment_agent/README.md)**

### 4. 📊 **Analysis Agent** (✅ Available)
Analyzes experimental results and extracts insights using Claude Haiku 4.5.
- Statistical significance testing (t-tests, ANOVA, Mann-Whitney U)
- MIC reduction and Selectivity Index (SI) interpretation
- Hypothesis confirmation with confidence levels
- Comparison with literature findings
- Implications for in vivo testing

### 5. 📝 **Report Agent** (✅ Available)
Synthesizes findings into publication-ready research papers using Claude.
- APA-formatted paper generation
- Structures results into paper sections (Abstract, Methods, Results, Discussion)
- Generates citations and references
- Exports to Markdown, JSON, and HTML formats
- Identifies follow-up research directions

### 6. 🧬 **Knowledge Graph Agent** (✅ Available)
Extracts semantic relationships from discoveries.
- Entity extraction (targets, compounds, findings, diseases)
- Relationship mapping (targets, inhibits, associates_with, etc.)
- Exports to RDF, Turtle, and JSON-LD formats
- Integrates with external knowledge bases
- Enables future refinement and cross-linking

### 7. 📋 **Experiment Planner Agent** (✅ Available)
Designs multi-protocol comparative experiments.
- Comparative protocol design for complex hypotheses
- Protocol selection and optimization
- Budget-aware experimental planning
- Supports 3-5 parallel experimental approaches
- Validates comparative design rigor

### 8. 🏃 **Experiment Runner Agent** (✅ Available)
Executes and monitors experimental protocols.
- Protocol step execution tracking
- Real-time result monitoring (when connected to lab hardware)
- Automated data collection and logging
- Error handling and protocol adjustments
- Integration with lab management systems (planned)

## 🚀 Quick Start

### Installation
```bash
# Activate virtual environment
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Run the Literature Agent
```bash
python agents/literature_agent/agent.py
```

### Try the Examples
```bash
python agents/literature_agent/examples.py
```

### Use in Your Code
```python
import asyncio
from agents.literature_agent import LiteratureAgent

async def main():
    agent = LiteratureAgent()
    
    # Search for papers
    papers = await agent.search_papers(
        "your research topic",
        year_range=(2023, 2026),
        limit=50
    )
    
    # Identify research gaps
    gaps = await agent.identify_gaps(papers)
    
    # Generate report
    report = await agent.generate_report("your topic", papers, gaps)
    
    await agent.close()

asyncio.run(main())
```

### Run the Complete Discovery Loop

Run the full 6-phase Mtb drug discovery pipeline:

```bash
# CLI mode with auto-approval of experiment design
python run_discovery_loop.py

# Or with manual approval checkpoint
python run_discovery_loop.py --no-auto-approve
```

**What it does:**
1. 📚 Searches Europe PMC & PubChem for literature on your research topic
2. 💡 Generates 5-7 testable hypotheses targeting Mtb (DprE1, InhA, MmpL3)
3. 🧪 Designs BSL-3 experimental protocols with budget estimation
4. 📊 Analyzes results and validates hypothesis confirmation
5. 📝 Generates publication-ready research paper (APA format)
6. 🧬 Builds semantic knowledge graph for future use

**Output saved to `./results/`:**
- `workflow_state_TIMESTAMP.json` — Complete workflow state
- `research_paper_TIMESTAMP.md` — Generated paper
- `knowledge_graph_TIMESTAMP.json` — Semantic entities and relationships

### Run the Web UI (Gradio)

Interactive web interface at http://localhost:7860:

```bash
python app.py
```

**Features:**
- Chat interface for research queries
- Live progress updates (6 phases)
- Visual workflow status
- Download results directly

## 📖 Documentation

- **[Setup Guide](SETUP.md)** - Installation and configuration
- **[Literature Agent](agents/literature_agent/README.md)** - Detailed documentation
- **[Examples](agents/literature_agent/examples.py)** - Real-world usage patterns
- **[Agent Config](agents/literature_agent/config.yaml)** - Configuration reference

## 🏗️ Project Structure

```
AgenticScientificDiscovery/
├── agents/
│   ├── literature_agent/          # 📚 Literature search & gap identification
│   │   ├── agent.py               # LiteratureAgent (Claude-powered)
│   │   ├── literature_agent.yaml  # Configuration
│   │   └── examples_drug_discovery.py
│   │
│   ├── hypothesis_agent/          # 💡 Hypothesis generation & scoring
│   │   ├── agent.py               # HypothesisAgent (Claude-powered)
│   │   ├── hypothesis_agent.yaml  # Configuration
│   │   └── examples.py
│   │
│   ├── experiment_agent/          # 🧪 Experiment design
│   │   ├── agent.py               # ExperimentAgent (Claude-powered)
│   │   ├── experiment_agent.yaml  # Configuration
│   │   └── examples.py
│   │
│   ├── experiment_planner/        # 📋 Multi-protocol comparative design
│   │   ├── agent.py               # ExperimentPlannerAgent
│   │   ├── experiment_planner.yaml
│   │   └── examples.py
│   │
│   ├── experiment_runner/         # 🏃 Protocol execution
│   │   ├── agent.py               # ExperimentRunnerAgent
│   │   ├── experiment_runner.yaml
│   │   └── examples.py
│   │
│   ├── analysis_agent/            # 📊 Statistical analysis
│   │   ├── agent.py               # AnalysisAgent (Claude-powered)
│   │   ├── analysis_agent.yaml    # Configuration
│   │   └── examples.py
│   │
│   ├── report_agent/              # 📝 Paper generation
│   │   ├── agent.py               # ReportAgent (Claude-powered)
│   │   ├── report_agent.yaml      # Configuration
│   │   └── examples.py
│   │
│   └── knowledge_graph_agent/     # 🧬 Knowledge extraction
│       ├── agent.py               # KnowledgeGraphAgent (Claude-powered)
│       ├── knowledge_graph_agent.yaml
│       └── examples.py
│
├── run_discovery_loop.py          # Master Orchestrator (CLI)
├── app.py                         # Gradio Web UI
├── orchestrator_config.yaml       # Orchestration config
├── requirements.txt               # Python dependencies
├── CLAUDE.md                      # Claude Code guidance
├── ARCHITECTURE.md                # System architecture
├── ORCHESTRATOR_README.md         # Orchestration details
├── README.md                      # This file
├── SETUP.md                       # Setup guide
├── .env.local.example             # Environment template
├── .gitignore                     # Git ignore rules
└── results/                       # Workflow outputs (auto-created)
```

## 💻 Core Capabilities

### Literature Agent

**Search Across Multiple Databases:**
```python
papers = await agent.search_papers(
    "quantum machine learning",
    databases=["openalex", "arxiv"],
    year_range=(2022, 2026),
    limit=100
)
```

**Identify Research Gaps:**
```python
gaps = await agent.identify_gaps(papers)
for gap in gaps:
    print(f"Gap: {gap.gap_description}")
    print(f"Priority: {gap.priority_level}")
    print(f"Confidence: {gap.confidence:.1%}")
```

**Generate Reports:**
```python
report = await agent.generate_report(
    query="your topic",
    papers=papers,
    gaps=gaps
)
# JSON structure with statistics, papers, and findings
```

## 🔧 Tech Stack

- **Language**: Python 3.10+
- **HTTP**: httpx (async)
- **Config**: YAML
- **APIs**: OpenAlex, arXiv, Semantic Scholar (planned)

## 📊 Data Sources

### Biomedical Literature & Chemical Databases

| Source | Coverage | Focus | Authentication |
|--------|----------|-------|-----------------|
| **Europe PMC API** | 50M+ biomedical papers | Mycobacterium tuberculosis drug discovery | Free, no auth |
| **PubChem API** | 200M+ chemical compounds | Drug compounds, structures, properties | Free, no auth |
| **Claude Haiku 4.5** | Training data to 2024 | AI-powered analysis, hypothesis generation, experiment design | API key required |

### Data Integration

- **Literature Agent**: Queries Europe PMC for Mtb-focused publications and PubChem for chemical compound data
- **Hypothesis Agent**: Uses Claude to analyze literature patterns and generate DprE1, InhA, MmpL3 targeting hypotheses
- **Experiment Agent**: Uses Claude to design BSL-3 protocols optimized for Mtb targets with budget validation
- **Analysis Agent**: Uses Claude to interpret MIC values, Selectivity Index, and intracellular assay results
- **Report Agent**: Uses Claude to synthesize publication-ready APA-formatted papers
- **Knowledge Graph Agent**: Uses Claude to extract entities and relationships from all discovery phases

### No Rate Limiting Constraints
- Europe PMC API: Unlimited queries with respectful usage
- PubChem API: High request limits for automated access
- Claude API: Bounded by token usage (budget-aware)

## 🎓 Use Cases

### Academic Research
- Accelerate literature reviews
- Identify unexplored research areas
- Find collaboration opportunities
- Track field evolution

### Corporate R&D
- Competitive intelligence
- Technology scouting
- Innovation pipeline
- IP landscape analysis

### Science Policy
- Research trend analysis
- Funding gap identification
- Emerging field detection
- Evidence synthesis

## 🚦 Roadmap

### Phase 1: Literature (✅ Complete)
- [x] Europe PMC & PubChem search
- [x] Paper parsing and extraction
- [x] Research gap identification with Claude
- [x] Literature review generation

### Phase 2: Hypothesis Generation (✅ Complete)
- [x] Literature pattern analysis
- [x] Hypothesis generation (Claude Haiku 4.5)
- [x] Feasibility assessment
- [x] Novelty, feasibility, impact, testability scoring

### Phase 3: Experiment Design (✅ Complete)
- [x] BSL-3 experimental protocol generation (Claude)
- [x] Budget estimation and validation
- [x] Comparative protocol planning
- [x] Success prediction and risk assessment

### Phase 4: Analysis (✅ Complete)
- [x] Statistical testing (t-test, ANOVA, Mann-Whitney U)
- [x] MIC reduction & Selectivity Index analysis
- [x] Hypothesis confirmation with confidence
- [x] Literature contextualization

### Phase 5: Reporting (✅ Complete)
- [x] Publication-ready paper generation (Claude)
- [x] APA-formatted citations
- [x] Multi-format export (Markdown, JSON, HTML)
- [x] Visualization and table generation

### Phase 6: Knowledge Graph (✅ Complete)
- [x] Entity extraction (targets, compounds, findings)
- [x] Relationship mapping
- [x] RDF/Turtle/JSON-LD export
- [x] Knowledge base integration

### Future Enhancements (🔄 In Progress)
- [ ] Real experiment runner (lab hardware integration)
- [ ] Advanced feedback loops (multi-round refinement)
- [ ] Cost optimization (Haiku vs Opus selection)
- [ ] Collaborative approval workflows (Slack/email)
- [ ] Performance analytics dashboard
- [ ] Persistent knowledge accumulation database

## 📚 Resources

## 📄 License

MIT License - Use freely for your hackathon and beyond!

## 🎉 Hackathon Details
Built for: **Hack-Nation 7th Global AI Hackathon**
---

Happy discovering! 🚀
---

## 👥 Team

**NextExperiment**

### Contacts
- **Anurag Dogra** — Software Engineering, HPC, AI/ML Architecture
  - Email: anuragdogra2192@gmail.com
  - Role: Lead Developer
  
- **Monika Rangole** — Scientific Domain Expertise, BioPhysics, Mtb Drug Discovery Focus
  - Email: monikarangole13@gmail.com
  - Role: Domain Expert

---
