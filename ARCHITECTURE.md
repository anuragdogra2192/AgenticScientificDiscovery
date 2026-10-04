# Architecture: Agentic Scientific Discovery Lab

## System Overview

```
┌──────────────────────────────────────────────────────────────────────────┐
│                    🔬 Agentic Scientific Discovery Lab                   │
│              (6 Primary Agents + 2 Experiment Agents + CLI)              │
└────────────────────────┬──────────────────────────────────────────────────┘
                         │
        ┌────────────────┴────────────────┐
        │                                 │
┌───────▼──────┐  ┌────────────────┐  ┌──▼──────────────┐
│  Literature  │  │   Hypothesis   │  │ Experiment      │
│    Agent     │  │     Agent      │  │ Agent           │
│   ✅ LIVE    │  │   ✅ LIVE      │  │ ✅ LIVE         │
└───────┬──────┘  └────────────────┘  └──┬──────────────┘
        │      (Claude Haiku 4.5)        │
        ├─────────────────────────────────┤
        │                                 │
┌───────▼──────────────────────────┐  ┌──▼──────────────────┐
│      Analysis Agent              │  │  Report Agent      │
│      ✅ LIVE                      │  │  ✅ LIVE           │
└────────────────────────────────┬─┘  └──┬──────────────────┘
                                 │       │
                    ┌────────────┴──────┴────────┐
                    │                           │
            ┌───────▼────────────┐    ┌────────▼──────────┐
            │ Knowledge Graph    │    │ Master            │
            │ Agent (✅ LIVE)     │    │ Orchestrator      │
            └────────────────────┘    └────────────────────┘
                    │                           │
        ┌───────────┴─────────────────────────┬┘
        │                                     │
   ┌────▼──────┐  ┌────▼──────┐  ┌──────────▼────────┐
   │ Exp        │  │ Exp        │  │ Europe PMC API   │
   │ Planner    │  │ Runner     │  │ PubChem API      │
   │ (✅ LIVE)   │  │ (✅ LIVE)   │  │ .env.local       │
   └────────────┘  └────────────┘  └──────────────────┘
   (Multi-Protocol Design)  (Execution)  (Config & Data)
```

**Status**: All agents fully operational with Claude Haiku 4.5 integration and graceful fallback to rule-based logic.

## Agent Hierarchy

### Level 1: Data Collection
**Literature Agent** ✅ **LIVE with Claude Haiku 4.5**
- Searches Europe PMC & PubChem for biomedical literature
- Extracts paper metadata and relevance scoring
- Identifies research gaps in Mtb drug discovery
- Uses Claude for intelligent gap analysis

```
Input:  Research query (e.g., "DprE1 inhibitors for TB")
        ↓
    [Claude] → Analyze query relevance & context
        ↓
  [Search] → Europe PMC, PubChem APIs
        ↓
 [Extract] → Parse papers, score relevance
        ↓
  [Claude] → Intelligent gap identification
        ↓
Output: Papers + Research gaps + Analysis
```

### Level 2: Knowledge Synthesis
**Hypothesis Agent** ✅ **LIVE with Claude Haiku 4.5**
- Analyzes literature patterns using Claude
- Generates novel anti-tubercular hypotheses (5-7 per request)
- Scores by novelty (0.25), feasibility (0.30), impact (0.25), testability (0.20)
- Returns ranked hypotheses with confidence

```
Input:  Literature findings + research gaps
        ↓
   [Claude] → Analyze patterns, identify opportunities
        ↓
 [Generate] → Create novel Mtb-focused hypotheses
        ↓
   [Score] → Novelty, feasibility, impact, testability
        ↓
Output: Ranked hypotheses with molecular targets
```

### Level 3: Experimental Design
**Experiment Agent** ✅ **LIVE with Claude Haiku 4.5**
- Uses Claude to design rigorous BSL-3 experimental protocols
- Generates sample sizes, budgets, and timelines
- Includes Mtb-specific controls (DMSO, Rifampicin, THP-1 macrophage)
- Validates against budget constraints (<$100k)

```
Input:  Selected hypothesis
        ↓
  [Claude] → Design BSL-3 protocol for Mtb target
        ↓
 [Generate] → Sample size, measures, timeline
        ↓
  [Estimate] → Budget with equipment & facility costs
        ↓
   [Validate] → Risk assessment, mitigation strategies
        ↓
Output: Experimental design + budget + approval summary
```

### Level 4: Result Analysis
**Analysis Agent** ✅ **LIVE with Claude Haiku 4.5**
- Statistical analysis of simulated/real Mtb assay results
- Interprets MIC reduction, intracellular IC50, Selectivity Index (SI)
- Validates hypothesis confirmation with confidence levels
- Generates implications for in vivo testing

```
Input:  Experimental design + simulated results data
        ↓
 [Analyze] → Statistical tests (t-test, ANOVA, etc.)
        ↓
[Claude] → Interpret findings in Mtb context
        ↓
 [Compare] → Validate against literature benchmarks
        ↓
Output: Analysis report + hypothesis confirmation + implications
```

### Level 5: Knowledge Dissemination
**Report Agent** ✅ **LIVE with Claude Haiku 4.5**
- Generates publication-ready APA-formatted papers
- Structures findings into 6 sections (Abstract, Intro, Methods, Results, Discussion, Conclusion)
- Includes citations, figures, and tables
- Outputs JSON, Markdown, and HTML formats

```
Input:  All prior phases (hypothesis, design, analysis)
        ↓
[Claude] → Compose research paper sections
        ↓
 [Format] → APA citations, figures, tables
        ↓
 [Export] → JSON, Markdown, HTML
        ↓
Output: Publication-ready research paper
```

### Level 6: Knowledge Integration
**Knowledge Graph Agent** ✅ **LIVE with Claude Haiku 4.5**
- Extracts semantic entities (targets, compounds, diseases, findings)
- Builds relationships between entities
- Exports as RDF/Turtle/JSON-LD for integration with external knowledge bases
- Enables future refinement and cross-linking

```
Input:  All discovery phases (hypothesis, experiment, analysis, report)
        ↓
[Claude] → Extract entities and relationships
        ↓
[Build] → Knowledge graph structure
        ↓
[Export] → RDF, Turtle, JSON-LD formats
        ↓
Output: Semantic knowledge graph for integration
```

### Level 7: Experiment Planning
**Experiment Planner Agent** ✅ **LIVE**
- Designs multi-protocol comparative experiments
- Optimizes protocol selection for complex hypotheses
- Integrates with Experiment Agent designs
- Coordinates 3-5 parallel experimental approaches
- Validates comparative design rigor

```
Input:  Selected hypothesis + base experiment design
        ↓
 [Design] → Multi-protocol comparative approach
        ↓
[Optimize] → Protocol selection & resource allocation
        ↓
 [Validate] → Comparative rigor assessment
        ↓
Output: Comparative experimental protocol plan
```

### Level 8: Experiment Execution
**Experiment Runner Agent** ✅ **LIVE**
- Executes and monitors experimental protocols
- Tracks protocol step completion
- Real-time result monitoring and logging
- Automated data collection (when hardware connected)
- Error handling and protocol adjustments

```
Input:  Approved experimental protocol
        ↓
[Execute] → Run protocol steps
        ↓
[Monitor] → Track progress & results
        ↓
 [Collect] → Automated data gathering
        ↓
[Adjust] → Handle errors & adapt
        ↓
Output: Experimental results data + execution log
```

## Agent Components

### Each Agent Contains:

```
agents/agent_name/
├── agent.py                      # Core implementation
│   ├── Anthropic SDK import      # try: from anthropic import Anthropic
│   ├── ANTHROPIC_AVAILABLE flag  # Graceful fallback support
│   ├── Claude client init        # os.environ.get("ANTHROPIC_API_KEY")
│   ├── _generate_with_claude()   # Claude-powered method
│   ├── _generate_rule_based()    # Fallback implementation
│   └── async methods             # All I/O is async
│
├── agent_name.yaml               # Configuration
│   ├── model: claude-haiku-4-5-20251001
│   ├── temperature: 0.2 or 0.3   # Deterministic vs creative
│   ├── max_tokens: per agent     # Output size limit
│   ├── prompt: domain-specific   # Mtb-focused instructions
│   └── structured JSON require   # Enforce valid JSON
│
├── README.md                     # Documentation
├── examples.py                   # Usage examples
└── __init__.py                   # Package export
```

### Claude Integration Pattern (All Agents)

```python
class MyAgent:
    def __init__(self, config_path):
        # Load YAML config
        self.config = yaml.safe_load(open(config_path))
        
        # Try to initialize Claude Haiku
        self.use_claude = False
        self.claude_client = None
        if ANTHROPIC_AVAILABLE and os.environ.get("ANTHROPIC_API_KEY"):
            try:
                self.claude_client = Anthropic(api_key=...)
                self.use_claude = True
                logger.info("Claude Haiku API initialized")
            except Exception as e:
                logger.warning(f"Could not init Claude: {e}")
    
    async def generate_result(self, inputs):
        # Try Claude first
        if self.use_claude and self.claude_client:
            try:
                return await self._generate_with_claude(inputs)
            except Exception as e:
                logger.warning(f"Claude failed: {e}. Using rule-based.")
        
        # Fallback to rule-based logic (always works)
        return self._generate_rule_based(inputs)
    
    async def _generate_with_claude(self, inputs):
        # Prompt with JSON requirement
        prompt = f"""You are a specialist in X.
        Return ONLY valid JSON with this structure:
        {{"field1": "value", ...}}
        
        INPUT: {json.dumps(inputs)}"""
        
        response = self.claude_client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=self.config.get("max_tokens", 2048),
            temperature=self.config.get("temperature", 0.2),
            messages=[{"role": "user", "content": prompt}]
        )
        
        # Clean and parse JSON
        json_str = self._extract_json_content(response.content[0].text)
        return MyDataClass(**json.loads(json_str))
    
    def _generate_rule_based(self, inputs):
        # Fallback logic (deterministic, no API needed)
        return MyDataClass(...)
```

## Data Flow

### Example: Complete Discovery Pipeline (with Claude Integration)

```
RESEARCH QUESTION
    ↓
┌─────────────────────────────────────────┐
│ Phase 1: Literature Discovery           │
│ (LiteratureAgent with Claude)           │
└────────┬────────────────────────────────┘
         │
         ├─→ [Claude] Analyze query relevance
         │
         ├─→ [Europe PMC API] Search biomedical literature
         │   └─→ Parse results, score relevance
         │
         ├─→ [PubChem API] Search chemical compounds
         │   └─→ Extract compound properties
         │
         └─→ [Claude] Identify research gaps
             └─→ Return: Papers + Gaps + Analysis
                 ↓
    ┌──────────────────────────────────────┐
    │ Papers: List[Paper]                  │
    │ Gaps: List[ResearchGap]              │
    │ Gap scores with confidence           │
    └──────────────────────────────────────┘
                 ↓
┌─────────────────────────────────────────┐
│ Phase 2: Hypothesis Generation          │
│ (HypothesisAgent with Claude)           │
└────────┬────────────────────────────────┘
         │
         └─→ [Claude] Generate 5-7 hypotheses
             ├─→ Analyze literature patterns
             ├─→ Suggest Mtb targets (DprE1, InhA, MmpL3)
             ├─→ Score: novelty, feasibility, impact, testability
             └─→ Return: Ranked hypotheses
                 ↓
    ┌──────────────────────────────────────┐
    │ Hypotheses: List[Hypothesis]         │
    │ Scores: {novelty, feasibility, ...}  │
    │ Selected: Hypothesis (top-ranked)    │
    └──────────────────────────────────────┘
                 ↓
┌─────────────────────────────────────────┐
│ Phase 3: Experiment Design              │
│ (ExperimentAgent with Claude)           │
└────────┬────────────────────────────────┘
         │
         └─→ [Claude] Design BSL-3 protocol
             ├─→ Sample size calculation
             ├─→ Mtb controls: DMSO, Rifampicin, THP-1
             ├─→ Budget: equipment + facility costs
             ├─→ Timeline & milestones
             └─→ Return: ExperimentalDesign
                 ↓
    ┌──────────────────────────────────────┐
    │ Design: ExperimentalDesign           │
    │ Protocol: BSL-3 procedures           │
    │ Budget: <$100k (validated)           │
    │ Timeline: 12 weeks                   │
    └──────────────────────────────────────┘
                 ↓
        [Human Approval Gate] ← Optional
                 ↓
┌─────────────────────────────────────────┐
│ Phase 4: Result Analysis                │
│ (AnalysisAgent with Claude)             │
└────────┬────────────────────────────────┘
         │
         └─→ [Claude] Analyze experimental results
             ├─→ Statistical tests (t-test, ANOVA)
             ├─→ MIC reduction, IC50 interpretation
             ├─→ Selectivity Index (SI) validation
             ├─→ Hypothesis confirmation
             └─→ Return: AnalysisReport
                 ↓
    ┌──────────────────────────────────────┐
    │ Report: AnalysisReport               │
    │ Finding: Hypothesis confirmed/reject │
    │ Strength: High/Medium/Low            │
    │ Implications: For in vivo testing    │
    └──────────────────────────────────────┘
                 ↓
┌─────────────────────────────────────────┐
│ Phase 5: Report Generation              │
│ (ReportAgent with Claude)               │
└────────┬────────────────────────────────┘
         │
         └─→ [Claude] Generate research paper
             ├─→ Abstract (250 words)
             ├─→ Introduction (background, gaps)
             ├─→ Methods (BSL-3 protocols)
             ├─→ Results (findings + statistics)
             ├─→ Discussion (implications)
             ├─→ Conclusion (next steps)
             └─→ Return: ResearchPaper
                 ↓
    ┌──────────────────────────────────────┐
    │ Paper: ResearchPaper                 │
    │ Format: Markdown/JSON/HTML           │
    │ Status: Publication-ready            │
    └──────────────────────────────────────┘
                 ↓
┌─────────────────────────────────────────┐
│ Phase 6: Knowledge Graph Integration    │
│ (KnowledgeGraphAgent with Claude)       │
└────────┬────────────────────────────────┘
         │
         └─→ [Claude] Extract semantic entities
             ├─→ Targets: DprE1, InhA, etc.
             ├─→ Compounds: Lead inhibitors
             ├─→ Findings: MIC values, SI scores
             ├─→ Relationships: targets, inhibits, etc.
             └─→ Export: RDF/Turtle/JSON-LD
                 ↓
    ┌──────────────────────────────────────┐
    │ KnowledgeGraph: Semantic web data    │
    │ Entities: 10+ types                  │
    │ Relationships: Linked data format    │
    │ Export formats: JSON-LD, RDF, etc.   │
    └──────────────────────────────────────┘
                 ↓
            ✅ COMPLETE
            
            Results saved to ./results/
            - workflow_state_TIMESTAMP.json
            - research_paper_TIMESTAMP.md
            - knowledge_graph_TIMESTAMP.json
```

## Biomedical Data Sources

Each agent uses specialized data sources:

### Literature Agent
- **Europe PMC API**: Biomedical literature with Mtb focus
- **PubChem API**: Chemical compound information
- Uses Claude for relevance scoring and gap analysis

### Experiment Agent
- **Mtb Assay Protocols**: MIC testing, THP-1 macrophage assays
- **Budget/Resource Templates**: Validated cost estimates
- Claude designs specific BSL-3 protocols for given targets

### All Agents
- **Claude Haiku 4.5 API**: Primary intelligence layer
- **Rule-Based Fallback**: Deterministic logic when API unavailable

## Configuration Hierarchy

```yaml
# agents/hypothesis_agent/hypothesis_agent.yaml
version: "2.0"
name: "hypothesis-agent"

executor:
  harness: claude-sdk
  model: claude-haiku-4-5-20251001
  temperature: 0.3  # Creative (vs 0.2 for deterministic)
  max_tokens: 2048

prompt: |
  You are an expert Mtb drug discovery scientist.
  Generate 5-7 novel hypotheses targeting DprE1, InhA, or MmpL3.
  Score each by: novelty (0.25), feasibility (0.30), impact (0.25), testability (0.20)
  Return ONLY valid JSON with hypotheses array.

# .env.local
ANTHROPIC_API_KEY=sk-ant-v1-...
CLAUDE_MODEL=claude-haiku-4-5-20251001
CLAUDE_TIMEOUT=30
CLAUDE_DEBUG=false
CLAUDE_MAX_TOKENS=2048
```

When agent loads:
1. Try to load ANTHROPIC_API_KEY from .env.local
2. Initialize Claude Haiku client (if key available)
3. Parse agent YAML config
4. Set temperature, token limits, model
5. Ready for use (with Claude or fallback)

## Async/Await Architecture

All agents use Python async for:
- Non-blocking Claude API calls
- Concurrent biomedical API queries
- Efficient resource usage
- Responsive CLI execution

```python
async def run_discovery_loop(research_question):
    # Run all phases sequentially with proper state management
    state = DiscoveryState()
    
    # Phase 1: Literature (parallel searches)
    state.papers = await asyncio.gather(
        literature_agent.search_europe_pmc(research_question),
        literature_agent.search_pubchem(research_question)
    )
    
    # Phase 2: Hypothesis (Claude)
    state.hypotheses = await hypothesis_agent.generate_hypotheses(
        state.papers
    )
    
    # Phase 3-6: Sequential phases
    state.experiment = await experiment_agent.design_experiment(...)
    state.analysis = await analysis_agent.analyze_results(...)
    state.paper = await report_agent.generate_paper(...)
    state.kg = await kg_agent.build_knowledge_graph(...)
    
    return state
```

## Error Handling & Resilience

Each agent implements graceful fallback:

```python
async def generate_result(self, inputs):
    # Try Claude first
    if self.use_claude and self.claude_client:
        try:
            result = await self._generate_with_claude(inputs)
            logger.info("Claude generation successful")
            return result
        except anthropic.APIError as e:
            logger.warning(f"Claude API error: {e}. Using rule-based fallback.")
        except json.JSONDecodeError as e:
            logger.warning(f"JSON parse error: {e}. Retrying or falling back.")
    
    # Fallback: Rule-based logic (always works)
    logger.info("Using rule-based generation (offline mode)")
    return self._generate_rule_based(inputs)
```

**Key principles:**
- No crashes on API failure (fallback ensures continuity)
- All intermediate state saved to `./results/`
- Errors logged but don't block workflow
- User never sees "API key missing" — just gets rule-based results

## Extensibility Points

### 1. Add New Claude-Powered Agent
```python
# In agents/new_agent/agent.py
from anthropic import Anthropic

class NewAgent:
    def __init__(self):
        # Load config
        self.config = yaml.safe_load(open("new_agent.yaml"))
        
        # Initialize Claude
        if ANTHROPIC_AVAILABLE and os.environ.get("ANTHROPIC_API_KEY"):
            self.claude_client = Anthropic(...)
            self.use_claude = True
    
    async def generate_something(self, inputs):
        if self.use_claude and self.claude_client:
            try:
                return await self._generate_with_claude(inputs)
            except Exception as e:
                logger.warning(f"Claude failed: {e}")
        return self._generate_rule_based(inputs)
```

### 2. Add New Data Source to Literature Agent
```python
# In agents/literature_agent/agent.py
async def _search_new_api(self, query, limit):
    # Implement API call
    results = await httpx.AsyncClient().get(
        f"https://api.example.com/search?q={query}",
        timeout=10
    )
    papers = [Paper(**item) for item in results.json()]
    return papers

# In literature_agent.yaml
databases:
  new_api:
    url: https://api.example.com
    rate_limit: 5
```

### 3. Add New Mtb Target to Hypothesis Agent
- Update prompts in `hypothesis_agent.yaml` with new target
- Agent will automatically generate hypotheses for it
- Claude focuses generation on specified targets

### 4. Add New Agent to Orchestrator
```python
# In run_discovery_loop.py
async def _phase_custom(self):
    agent = CustomAgent()
    result = await agent.run(self.state)
    self.state.custom_result = result
    return result
```

## Performance Characteristics

### Full Workflow (6 Phases)
| Phase | Time | Notes |
|-------|------|-------|
| Phase 1: Literature | 5-10s | Parallel API calls |
| Phase 2: Hypothesis | 2-3s | Claude generation |
| Phase 3: Experiment | 2-3s | Claude design |
| Phase 4: Analysis | 1-2s | Statistical tests |
| Phase 5: Report | 3-5s | Claude paper gen |
| Phase 6: Knowledge Graph | 1-2s | Entity extraction |
| **Total** | **15-25s** | End-to-end with Claude |

### Scalability
- **Claude token budget**: ~15,000 tokens per full run ($0.10 cost)
- **Biomedical APIs**: 5-10 parallel calls per agent
- **Memory**: ~50MB for full workflow state
- **Results persist**: `./results/` directory

## Testing Strategy

```bash
# Unit test: Agent in isolation
python agents/hypothesis_agent/examples.py

# Integration test: Full pipeline
python run_discovery_loop.py

# Offline test (no Claude API key)
unset ANTHROPIC_API_KEY
python run_discovery_loop.py  # Uses rule-based fallback

# Web UI test
python app.py  # Launch at http://localhost:7860
```

## Monitoring & Logging

Each agent logs:
- **Claude API calls**: Model, tokens, latency
- **Fallback activation**: When Claude unavailable
- **Biomedical API calls**: Source, results count, latency
- **Processing times**: Per phase
- **Error tracking**: With recovery attempts

```python
logger.info("Claude Haiku API initialized for Mtb hypothesis generation")
logger.debug(f"Generated {len(hypotheses)} hypotheses with scores")
logger.warning(f"Claude unavailable, using rule-based hypothesis generation")
logger.error(f"Europe PMC API error: {error_details}")
```

## Future Architecture Enhancements

1. **Real Experiment Runner**: Execute BSL-3 assays on lab hardware
2. **Feedback Loop Enhancement**: Multi-round hypothesis refinement
3. **Multi-Hypothesis Comparison**: Compare 3-5 top hypotheses in parallel
4. **Advanced Approval Workflow**: Slack/email integration for approvals
5. **Performance Analytics Dashboard**: Track phase durations, costs, success rates
6. **Persistent Database**: Long-term knowledge accumulation
7. **Collaborative Review**: Multi-user approval and comments
8. **Cost Optimization**: Swap Claude Haiku for Opus for complex phases as needed

---

This architecture supports the complete research pipeline from question to publication with intelligent AI agents, graceful offline fallback, and extensibility for new capabilities.
