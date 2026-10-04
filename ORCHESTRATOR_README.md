# Master Orchestration Loop: The Scientific Discovery Engine

The **Master Orchestrator** is the conductor that connects all 5 specialist agents into a seamless, intelligent research pipeline with feedback loops, human oversight, and knowledge graph generation.

## 🎼 The Orchestration Symphony

```
                    RESEARCH QUESTION
                            ↓
        ┌───────────────────────────────────────┐
        │   📚 PHASE 1: LITERATURE DISCOVERY   │
        │   Search papers, identify gaps        │
        └───────────────────────┬───────────────┘
                                ↓
        ┌───────────────────────────────────────┐
        │   💡 PHASE 2: HYPOTHESIS GENERATION  │
        │   Generate and score ideas            │
        └───────────────────────┬───────────────┘
                                ↓
                    ┌──────────────────┐
                    │ Feedback Loop?   │
                    │ (Low confidence) │
                    └────────┬─────────┘
                    YES ↙           ↘ NO
                      ↙               ↘
            [Refine Literature]      [Continue]
                      ↖               ↗
                        ↘           ↙
                            ↓
        ┌───────────────────────────────────────┐
        │   🧪 PHASE 3: EXPERIMENT DESIGN      │
        │   Protocol, budget, timeline          │
        └───────────────────────┬───────────────┘
                                ↓
                    ┌──────────────────────┐
                    │ 👤 HUMAN APPROVAL    │
                    │ Review & Validate    │
                    └────────┬─────────────┘
                   Approved ↙    ↘ Rejected
                      ↙            ↘
                    ↙ YES       NO  ↘ STOP
                   ↙                  
        ┌───────────────────────────────────────┐
        │   📊 PHASE 4: RESULT ANALYSIS        │
        │   Statistics, findings, implications  │
        └───────────────────────┬───────────────┘
                                ↓
        ┌───────────────────────────────────────┐
        │   📝 PHASE 5: REPORT GENERATION      │
        │   Publication-ready paper             │
        └───────────────────────┬───────────────┘
                                ↓
                    ┌──────────────────┐
                    │ 🌐 KNOWLEDGE GRAPH│
                    │ Export & Update  │
                    └────────┬─────────┘
                            ↓
                  ✅ COMPLETE & READY
```

## 🚀 Quick Start

### Basic Usage

```python
import asyncio
from run_discovery_loop import DiscoveryOrchestrator

async def main():
    orchestrator = DiscoveryOrchestrator()
    
    state = await orchestrator.run_discovery_loop(
        research_question="Your research question here",
        literature_limit=50,
        auto_approve=False  # Set to True to skip human approval
    )
    
    print(f"✨ Workflow complete!")

asyncio.run(main())
```

### Run from Command Line

```bash
python run_discovery_loop.py
```

## 📋 Configuration

The orchestrator is configured via `orchestrator_config.yaml`:

### Phase Configuration

Each phase has:
- **Input requirements**: What data is needed
- **Output requirements**: What data is produced
- **Quality checks**: Validation rules
- **Dependencies**: Which phases must complete first
- **Human approval**: Whether review is needed

Example:
```yaml
phase_3_experiment:
  name: Experiment Design
  dependencies:
    - phase_2_hypothesis
  human_approval_required: true
  quality_checks:
    - budget_reasonable: "<=100000"
    - sample_size_adequate: ">=30"
```

### Feedback Loop Configuration

```yaml
feedback_loop:
  enabled: true
  trigger_conditions:
    - hypothesis_not_confirmed
    - low_confidence_findings
  max_iterations: 3
```

### Approval Checkpoints

```yaml
approval_checkpoints:
  after_experiment_design:
    required: true
    approval_role: "Research Lead"
    timeout_hours: 24
```

## 🔄 The Five Phases

### Phase 1: Literature Discovery
**Input**: Research question
**Output**: Papers, gaps

```python
await orchestrator._phase_literature(
    agent, 
    "your research question",
    limit=50
)
```

### Phase 2: Hypothesis Generation
**Input**: Papers, gaps
**Output**: Ranked hypotheses

```python
await orchestrator._phase_hypothesis(agent, question)
```

**Feedback**: If hypotheses have low confidence, automatically refine literature search

### Phase 3: Experiment Design
**Input**: Selected hypothesis
**Output**: Experimental protocol, budget, timeline

```python
await orchestrator._phase_experiment(agent)
```

**Human Gate**: Requires approval before proceeding (optional)

### Phase 4: Result Analysis
**Input**: Experimental design + simulated results
**Output**: Findings, implications, hypothesis confirmation

```python
await orchestrator._phase_analysis(agent)
```

### Phase 5: Report Generation
**Input**: All prior phases
**Output**: Publication-ready paper + knowledge graph

```python
await orchestrator._phase_report(agent)
```

## 👤 Human Approval System

### Approval Checkpoints

The orchestrator includes two main approval points:

1. **After Experiment Design** (Required)
   - Review protocol, budget, and risks
   - Approve or reject
   - Timeout: 24 hours

2. **After Analysis** (Optional)
   - Review statistical findings
   - Auto-approve if p < 0.05 and effect size ≥ 0.3

### Approval Summary

When approval is needed, the orchestrator displays:

```
EXPERIMENT DESIGN APPROVAL REQUEST
==================================================
Design Type: randomized_controlled_trial
Hypothesis: [Your hypothesis]

RESOURCES & BUDGET
Sample Size: 120 participants
Total Budget: $45,000
Timeline: 12 weeks

RISK ASSESSMENT
Potential Risks:
  • Insufficient sample size
  • Measurement error
  • Attrition

MITIGATION STRATEGIES
  • Overrecruit 20% buffer
  • Validate instruments
  • Active retention strategies

SUCCESS PREDICTION
Probability of Hypothesis Confirmation: 68%

APPROVAL STATUS: PENDING REVIEW
```

### Auto-Approval Mode

For automation or testing:
```python
state = await orchestrator.run_discovery_loop(
    research_question=question,
    auto_approve=True
)
```

## 🔄 Feedback Loops

The orchestrator implements intelligent feedback:

### When Is Feedback Triggered?
1. **Hypothesis not confirmed** in analysis
2. **Low confidence findings** (< 0.7)
3. **Significant gaps identified**

### What Happens?
1. Refines literature search with additional papers
2. Regenerates hypotheses with expanded knowledge
3. Re-scores and ranks hypotheses
4. Continues to next phase

### Limits
- Maximum 3 feedback iterations (prevents infinite loops)
- Configurable in `orchestrator_config.yaml`

## 📊 State Management

### Persistent State

The orchestrator saves the complete workflow state:

```
state.research_question
state.papers
state.gaps
state.hypotheses
state.selected_hypothesis
state.experimental_design
state.analysis_report
state.research_paper
state.knowledge_graph
```

### Checkpoints

After each phase:
- State is persisted to JSON
- Enables resuming interrupted workflows
- Tracks all approvals and iterations

### Recovery

To resume an interrupted workflow:
```python
# State is automatically saved
# Can be loaded and resumed manually if needed
```

## 📁 Output Files

The orchestrator saves all results in `./results/`:

```
results/
├── workflow_state_TIMESTAMP.json
│   ├─ Complete workflow state
│   ├─ Quality checks
│   └─ Approval history
├── research_paper_TIMESTAMP.md
│   ├─ Full paper
│   ├─ All sections
│   └─ Citations
├── knowledge_graph_TIMESTAMP.json
│   ├─ Entities
│   ├─ Relationships
│   └─ Properties
└── complete_workflow_TIMESTAMP.json
    └─ Summary of entire workflow
```

## ✅ Quality Checks

Each phase validates output:

| Phase | Check | Rule |
|-------|-------|------|
| Literature | min_papers | >= 5 |
| Literature | max_papers | <= 500 |
| Hypothesis | min_hypotheses | >= 3 |
| Hypothesis | novelty_threshold | >= 0.4 |
| Experiment | sample_size | >= 30 |
| Experiment | budget_max | <= $100,000 |
| Analysis | assumptions_checked | required |
| Report | sections_complete | required |

Failed checks:
- Log warnings
- Request manual review
- Can continue with override

## 🛡️ Error Handling

The orchestrator implements graceful error handling:

### Error Recovery
- **Phase timeout**: Skip, log, continue
- **Quality check fail**: Request review
- **API error**: Retry with backoff
- **Approval timeout**: Escalate to admin

### Preserves State
- All intermediate results saved
- Can resume after fixing errors
- No data loss on failure

## 🔊 Logging

Detailed logging of entire workflow:

```
2026-10-04 10:15:23 - orchestrator - INFO - 🔬 Agentic Scientific Discovery Orchestrator Initialized
2026-10-04 10:15:24 - orchestrator - INFO - Starting discovery loop for: How do attention mechanisms improve interpretability?
2026-10-04 10:15:25 - orchestrator - INFO - 📚 PHASE 1: Literature Discovery
2026-10-04 10:15:35 - orchestrator - INFO - ✓ Found 45 papers
2026-10-04 10:15:36 - orchestrator - INFO - ✓ Identified 8 research gaps
2026-10-04 10:15:37 - orchestrator - INFO - 💡 PHASE 2: Hypothesis Generation & Ranking
...
```

## 🚀 Advanced Features

### Custom Validation

Extend the orchestrator:

```python
class CustomOrchestrator(DiscoveryOrchestrator):
    def _check_quality(self, phase: str, rules: dict) -> None:
        # Custom quality logic
        super()._check_quality(phase, rules)
```

### Custom Approval Logic

```python
async def _request_approval(self, approval_type: str, summary: str):
    # Integration with approval service
    # Slack notification, email approval, database check
    # etc.
```

### Parallel Phases

For future enhancement:
```yaml
phases:
  phase_4_analysis:
    parallel_with: []  # Can add parallel execution
```

## 🧠 Knowledge Graph Integration

Automatic generation after completion:

```python
if self.state.knowledge_graph:
    # Export to RDF/Turtle/JSON-LD
    # Update organizational knowledge base
    # Enable future refinement
```

## 📈 Workflow Metrics

The orchestrator tracks:
- Total execution time
- Time per phase
- Feedback iterations
- Quality check results
- Approval decisions
- Error count and types

## 🔗 Integration Example

### Complete Workflow

```python
async def full_research_pipeline():
    orchestrator = DiscoveryOrchestrator()
    
    # Run the entire workflow
    state = await orchestrator.run_discovery_loop(
        research_question="Your research question",
        literature_limit=50,
        auto_approve=False
    )
    
    # Access results
    if state.research_paper:
        print("✨ Paper ready!")
        print(f"Title: {state.research_paper.title}")
        print(f"Word count: {state.research_paper.word_count}")
    
    # Access knowledge graph
    if state.knowledge_graph:
        print(f"Knowledge entities: {len(state.knowledge_graph['entities'])}")
    
    return state
```

## 🎯 Use Cases

### Academic Research
Complete workflow from question to publication

### Corporate R&D
Automated competitive intelligence and innovation scouting

### Evidence Synthesis
Systematic literature review with structured analysis

### Science Policy
Research landscape analysis and gap identification

### Startup Validation
Market research and technical feasibility studies

## 🔮 Future Enhancements

- [ ] Parallel phase execution
- [ ] Advanced approval workflows (Slack, email)
- [ ] Integration with lab management systems
- [ ] Real experiment runner (not simulated)
- [ ] Multi-hypothesis comparison
- [ ] Collaborative review processes
- [ ] Persistent approval database
- [ ] Performance analytics dashboard

## 📞 Support

For issues or questions:
1. Check logs in `./logs/orchestration.log`
2. Review configuration in `orchestrator_config.yaml`
3. Check saved state in `./results/`
4. Refer to individual agent documentation

---

**The Master Orchestrator**: Where science meets automation. 🚀
