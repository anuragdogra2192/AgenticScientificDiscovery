# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 🏗️ Project Overview

**Agentic Scientific Discovery Lab** — An autonomous research pipeline that uses specialized AI agents to accelerate scientific discovery. The system runs a 6-phase workflow:

1. **Literature Discovery** → Search and extract biomedical literature
2. **Hypothesis Generation** → Synthesize testable hypotheses from literature
3. **Experiment Planning** → Design experiments with budgets and timelines
4. **Result Analysis** → Statistical analysis and interpretation
5. **Report Generation** → Publication-ready research papers
6. **Knowledge Graph** → Semantic extraction of findings

**Domain Focus**: Mycobacterium tuberculosis (Mtb) drug discovery with BSL-3 assay protocols, target-based screening (DprE1, InhA), and in vitro cytotoxicity validation.

**AI Backbone**: All agents use Claude Haiku 4.5 (model: `claude-haiku-4-5-20251001`) with graceful fallback to rule-based logic when API unavailable.

## ⚡ Quick Setup

```bash
# 1. Create environment file
cp .env.local.example .env.local

# 2. Add Anthropic API key to .env.local
# Get key from https://console.anthropic.com/api_keys
ANTHROPIC_API_KEY=sk-ant-v1-YOUR_KEY_HERE

# 3. Verify setup
python setup_claude.py

# 4. Install dependencies (if needed)
pip install -r requirements.txt
pip install anthropic gradio
```

## 🚀 Common Commands

### Run Full Pipeline (CLI)
```bash
# Run entire discovery workflow with auto-approve
python run_discovery_loop.py

# Run with manual approval checkpoint at experiment design phase
# (Interactive prompts require manual yes/no responses)
python run_discovery_loop.py --no-auto-approve
```

### Run Web UI (Gradio)
```bash
# Launch interactive web interface at http://localhost:7860
python app.py
```

### Test Specific Agent
```bash
# Test hypothesis generation
python agents/hypothesis_agent/examples.py

# Test experiment design
python agents/experiment_agent/examples.py

# Test literature search (Mtb-focused)
python agents/literature_agent/examples_drug_discovery.py

# Test analysis
python agents/analysis_agent/examples.py

# Test report generation
python agents/report_agent/examples.py
```

### Verify Setup
```bash
python setup_claude.py
```

## 🏛️ Architecture & Key Files

### Agent System (8 Agents)
Each agent inherits from a base pattern and can use Claude or fallback to rules:

```
agents/
├── literature_agent/       # Biomedical literature search (Europe PMC, PubChem)
│   ├── agent.py           # LiteratureAgent class with _generate_with_claude()
│   └── literature_agent.yaml
│
├── hypothesis_agent/      # Generate testable hypotheses (novelty, feasibility, impact, testability scores)
│   ├── agent.py           # HypothesisAgent with _generate_with_claude()
│   └── hypothesis_agent.yaml
│
├── experiment_agent/      # Design BSL-3 Mtb assays with budget/timeline
│   ├── agent.py           # ExperimentAgent with _design_with_claude()
│   └── experiment_agent.yaml
│
├── analysis_agent/        # Statistical analysis of experimental results
│   ├── agent.py           # AnalysisAgent ready for _analyze_with_claude()
│   └── analysis_agent.yaml
│
├── report_agent/          # Generate publication-ready papers
│   ├── agent.py           # ReportAgent with _generate_with_claude()
│   └── report_agent.yaml
│
├── knowledge_graph_agent/ # Extract semantic relationships
│   ├── agent.py           # KnowledgeGraphAgent with RDF/Turtle/JSON-LD export
│   └── knowledge_graph_agent.yaml
│
├── experiment_planner/    # Multi-protocol comparative design
│   └── agent.py           # ExperimentPlannerAgent
│
└── experiment_runner/     # Protocol execution
    └── agent.py           # ExperimentRunnerAgent
```

### Orchestration (Main Entry Points)

```
run_discovery_loop.py      # CLI orchestrator - runs full 6-phase workflow
                           # DiscoveryOrchestrator class manages state, phases, feedback loops
                           
app.py                     # Gradio web UI wrapper
                           # run_discovery_chat() async function streams progress to UI
                           
orchestrator_config.yaml   # Phase config, approval checkpoints, feedback loops
```

### Configuration Files

```
.env.local                 # ⚠️ SECRETS (never commit)
                           # ANTHROPIC_API_KEY=sk-ant-v1-...
                           # CLAUDE_MODEL=claude-haiku-4-5-20251001
                           # CLAUDE_TIMEOUT=30
                           # Protected by .gitignore
                           
agents/*/agent_*.yaml      # Agent-specific: model, temperature, prompts
                           # Temperature tuning:
                           #   - 0.2 for deterministic tasks (experiment, analysis)
                           #   - 0.3 for creative tasks (hypothesis, report)
```

### Output Directories

```
results/                   # Workflow outputs (created automatically)
├── workflow_state_*.json  # Complete state after each phase
├── research_paper_*.md    # Generated paper in Markdown
└── knowledge_graph_*.json # Semantic entities and relationships
```

## 🤖 Claude Integration Pattern

Every agent follows this pattern:

### 1. Initialization (Load Config + Try Claude)
```python
class MyAgent:
    def __init__(self):
        # Load YAML config
        self.config = yaml.safe_load(open("agent.yaml"))
        
        # Try to initialize Claude
        self.use_claude = False
        if os.environ.get("ANTHROPIC_API_KEY"):
            self.claude_client = Anthropic(api_key=...)
            self.use_claude = True
```

### 2. Main Method (Try Claude, Fallback to Rules)
```python
async def generate_result(self, inputs):
    if self.use_claude and self.claude_client:
        try:
            return await self._generate_with_claude(inputs)
        except Exception as e:
            logger.warning(f"Claude failed: {e}. Using rule-based.")
    
    # Rule-based fallback
    return self._generate_rule_based(inputs)
```

### 3. Claude Method (Structured JSON Prompt)
```python
async def _generate_with_claude(self, inputs):
    prompt = f"""You are a specialist in X.
    Return ONLY valid JSON with structure:
    {{"field1": "value", "field2": [...], ...}}"""
    
    response = self.claude_client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=2048,
        temperature=0.2,  # Lower = deterministic
        messages=[{"role": "user", "content": prompt}]
    )
    
    data = json.loads(response.content[0].text)
    return MyDataClass(**data)
```

## 📊 Orchestration Workflow

### Phase Flow with Feedback Loops

```
RESEARCH_QUESTION
       ↓
    [Phase 1: Literature]
       ↓
    [Phase 2: Hypothesis] ← Feedback loop if low confidence
       ↓
    [Phase 3: Experiment Design] → Human Approval (optional)
       ↓
    [Phase 4: Analysis]
       ↓
    [Phase 5: Report]
       ↓
    [Phase 6: Knowledge Graph]
       ↓
    COMPLETE
```

### Key State Object (DiscoveryState)
Managed by `DiscoveryOrchestrator` and saved to `./results/`:
- `research_question`: Input query
- `papers`: Literature search results
- `hypotheses`: Generated and ranked hypotheses
- `selected_hypothesis`: Chosen for experiment
- `experimental_design`: Protocol, budget, timeline
- `analysis_report`: Statistical results and findings
- `research_paper`: Generated publication
- `knowledge_graph`: Entities and relationships

### Approval Checkpoints
- **After Experiment Design**: Required (can skip with `auto_approve=True`)
- **After Analysis**: Optional (auto-approves if p < 0.05 and effect_size ≥ 0.3)

## 🎯 Mtb Drug Discovery Domain

### Key Targets
- **DprE1**: Decaprenylphosphoribosyl transferase (cell wall synthesis)
- **InhA**: Enoyl-acyl carrier protein reductase (mycolic acid synthesis)
- **MmpL3**: Mycolic acid transporter

### Assay Protocols
- **MIC Testing**: Minimum inhibitory concentration (Alamar Blue microplate)
- **THP-1 Macrophage**: Intracellular survival and cytotoxicity
- **Selectivity Index (SI)**: Ratio of mammalian CC50 to Mtb IC50 (threshold: SI > 10)

### Safety Level
- **BSL-3** containment requirements
- Standard Middlebrook 7H9 growth medium
- H37Rv reference strain used in assays

## 🔧 Key Configuration Points

### Temperature Tuning
- **Hypothesis Generation** (0.3): Novelty and creativity needed
- **Experiment Design** (0.2): Deterministic, reproducible protocols
- **Analysis** (0.2): Consistent statistical interpretation
- **Report** (0.3): Narrative flow and clarity

### Model Configuration
Edit `agents/*/agent_*.yaml`:
```yaml
executor:
  model: claude-haiku-4-5-20251001
  temperature: 0.2
  max_tokens: 4096
```

### Token Limits
- Hypothesis: 2048 tokens (5-7 hypotheses + scoring)
- Experiment: 4096 tokens (protocol details + budget)
- Analysis: 4096 tokens (statistics + implications)
- Report: 8192 tokens (full paper)

## 🐛 Debugging Tips

### Check API Key Setup
```bash
python setup_claude.py
```

### Test Claude Connection
```python
from anthropic import Anthropic
client = Anthropic(api_key="sk-ant-v1-...")
response = client.messages.create(
    model="claude-haiku-4-5-20251001",
    max_tokens=100,
    messages=[{"role": "user", "content": "test"}]
)
print(response.content[0].text)
```

### Run Without Claude (Offline Testing)
```bash
unset ANTHROPIC_API_KEY
python run_discovery_loop.py  # Uses rule-based fallback
```

### Check Logs
```bash
# Full workflow state saved after each phase
tail -f results/workflow_state_*.json

# Check orchestrator logs
python run_discovery_loop.py 2>&1 | grep -E "Phase|Error|Complete"
```

### Common Issues

| Issue | Solution |
|-------|----------|
| `ANTHROPIC_API_KEY not set` | Run `python setup_claude.py` |
| `401 Unauthorized` | API key format wrong; regenerate from console.anthropic.com |
| `Gradio type="messages" error` | Already fixed in app.py (uses tuple format for Gradio 6.29.1) |
| `JSON parse error from Claude` | Check prompt formatting; may need to adjust `_extract_json_content()` helper |
| `Timeout on long responses` | Increase `CLAUDE_TIMEOUT` in .env.local (default 30s) |

## 📝 Code Style Notes

### Required for Claude Integration
- All Claude prompts must explicitly request **valid JSON output** with structure examples
- Use `_extract_json_content()` helper to clean up responses (handles markdown code blocks)
- Always fallback gracefully if Claude unavailable
- Log warnings, not errors, for fallback activation

### Mtb Domain Specificity
- Prompts reference DprE1, InhA, MmpL3 targets explicitly
- Include BSL-3 safety constraints in experiment design
- Use actual Mtb assay names (Alamar Blue, THP-1, MIC90)
- Selectivity Index (SI > 10) is primary success metric

## 🎓 Examples to Reference

- **Full Pipeline**: `python run_discovery_loop.py`
- **Single Agent**: `python agents/hypothesis_agent/examples.py`
- **Web UI**: `python app.py` (then browse to http://localhost:7860)
- **Mtb-Specific**: `python agents/literature_agent/examples_drug_discovery.py`

## 📚 Additional Resources

- **ORCHESTRATOR_README.md**: Detailed orchestration flow, approval systems, feedback loops
- **CLAUDE_SETUP_GUIDE.md**: Environment configuration, troubleshooting
- **CLAUDE_API_INTEGRATION.md**: Agent integration patterns, JSON structures
- **agents/*/README.md**: Individual agent documentation (if exists)
- **requirements.txt**: Dependencies (includes anthropic, gradio, httpx, pyyaml)

## 🔑 Important Reminders

1. **API Key Security**: `.env.local` is in `.gitignore` — never commit secrets
2. **Fallback Always Works**: If API key missing, agents use rule-based logic automatically
3. **Cost**: ~$0.10 per full pipeline run with Claude Haiku (very affordable)
4. **Token Budget**: Monitor tokens at console.anthropic.com to avoid overages
5. **Offline Mode**: Can run without internet/API key using rule-based agents
6. **Gradio Version**: Currently using 6.29.1 (app.py tuned for this version)

---

**Last Updated**: October 4, 2026 | **Status**: All 8 agents integrated with Claude Haiku 4.5
