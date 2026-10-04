# 🔬 Agentic Scientific Discovery Lab - Team NextExperiment

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

### Configure Claude API

Create a `.env.local` file in the project root with your Anthropic API key:

```bash
# Create .env.local file
cat > .env.local << 'EOF'
# Anthropic Claude API Configuration
# Get your API key from: https://console.anthropic.com/api_keys

# Your Anthropic API key (required for Claude Haiku integration)
ANTHROPIC_API_KEY=sk-ant-v1-YOUR_API_KEY_HERE

# Claude Model (default: claude-haiku-4-5-20251001)
CLAUDE_MODEL=claude-haiku-4-5-20251001

# Request timeout in seconds (default: 30)
CLAUDE_TIMEOUT=30

# Enable detailed logging (true/false)
CLAUDE_DEBUG=false

# Max tokens per request (default: 2048)
CLAUDE_MAX_TOKENS=2048
EOF
```

**Setup Steps:**
1. Get your API key from [console.anthropic.com/api_keys](https://console.anthropic.com/api_keys)
2. Replace `YOUR_API_KEY_HERE` with your actual key (format: `sk-ant-v1-...`)
3. Save the file (`.env.local` is protected by `.gitignore` — never commit it)
4. Verify setup with: `python setup_claude.py`

**Note:** If `.env.local` is missing, the system falls back to rule-based logic (no Claude API calls).

### Run the Experiment
```bash
python run_discovery_loop.py
```
### Run the custom prompt
```bash
python run_discovery_loop.py "Allosteric covalent inhibition of DprE1 in multidrug-resistant Mycobacterium tuberculosis combined with PMA-differentiated THP-1 mammalian cytotoxicity screening to establish a high Selectivity Index (SI > 10) and bypass efflux resistance."
```

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
- [ ] Advanced feedback loops (multi-round refinement)
- [ ] Cost optimization (Haiku vs Opus selection)
- [ ] More Gaurdrails and AI Governance and Safety
- [ ] End to End Evals and observability
- [ ] Collaborative approval workflows (Slack/email)
- [ ] Performance analytics dashboard
- [ ] Persistent knowledge accumulation database
- [ ] WebUI
- [ ] Real experiment runner (lab hardware integration)

## 📚 References

### Primary Research Foundation

**Zheng X, Av-Gay Y.** System for Efficacy and Cytotoxicity Screening of Inhibitors Targeting Intracellular Mycobacterium tuberculosis. *J Vis Exp*. 2017 Apr 5;(122):55273. doi: 10.3791/55273. PMID: 28448028; PMCID: PMC5564477.

**Relevance**: This paper establishes the gold-standard BSL-3 in vitro assay protocols for Mycobacterium tuberculosis drug screening, including:
- MIC (Minimum Inhibitory Concentration) testing methodology
- THP-1 macrophage-based intracellular survival assays
- Cytotoxicity assessment for Selectivity Index (SI) calculation
- Control strain: Mtb H37Rv

Our Agentic Scientific Discovery Lab uses these protocols as the baseline for experiment design, result interpretation, and hypothesis validation in the Mtb drug discovery pipeline.

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
