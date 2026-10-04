# Hypothesis Agent (Insight Agent) 💡

The Hypothesis Agent transforms literature findings and research gaps into clear, testable scientific hypotheses. It uses multiple generation strategies to propose novel ideas and ranks them by novelty, feasibility, impact, and testability.

## Features

### 🧬 Hypothesis Generation Strategies
- **Gap Bridging**: Directly propose mechanisms to address identified research gaps
- **Trend Detection**: Identify patterns in literature and propose their implications
- **Contradiction Resolution**: Suggest hypotheses to reconcile conflicting findings
- **Cross-Domain Synthesis**: Transfer successful approaches from other fields
- **Novel Combination**: Propose new relationships between existing concepts

### ⚖️ Evaluation & Ranking
- **Novelty Score**: How new/original is this hypothesis?
- **Feasibility Score**: Can we actually test this with available resources?
- **Impact Score**: If confirmed, how important would this finding be?
- **Testability Score**: Can we design clear, unambiguous tests?
- **Overall Score**: Weighted combination of all factors

### 📋 Hypothesis Structure
Each hypothesis includes:
- **Clear Statement**: Formal hypothesis (if X, then Y)
- **Variables**: Independent, dependent, and control variables
- **Predictions**: Specific, measurable predictions
- **Assumptions**: Key assumptions that must hold
- **Alternatives**: Other possible explanations
- **Research Design Sketch**: Initial experimental design
- **Risk Assessment**: Potential pitfalls and limitations

### 🎯 Advanced Capabilities
- Multiple generation strategies applied in parallel
- Diversity boost to ensure varied hypothesis types
- Custom ranking weights for different research goals
- Research design sketching for top hypotheses
- Export to JSON for downstream tools

## Installation

```bash
# Dependencies already installed from root requirements.txt
pip install -r ../../requirements.txt
```

## Usage

### Basic Hypothesis Generation

```python
import asyncio
from agents.literature_agent import LiteratureAgent
from agents.hypothesis_agent import HypothesisAgent

async def main():
    # Get literature findings
    lit_agent = LiteratureAgent()
    papers = await lit_agent.search_papers(
        "your research topic",
        limit=50
    )
    gaps = await lit_agent.identify_gaps(papers)
    
    # Generate hypotheses
    hyp_agent = HypothesisAgent()
    hypotheses = await hyp_agent.generate_hypotheses(
        papers=papers,
        research_gaps=gaps,
        query="your research topic"
    )
    
    # Display results
    for hyp in hypotheses[:5]:
        print(f"✓ {hyp.title}")
        print(f"  Overall Score: {hyp.overall_score:.3f}")
        print()
    
    await lit_agent.close()
    await hyp_agent.close()

asyncio.run(main())
```

### Examine Hypothesis Details

```python
# Get top hypothesis
top_hyp = hypotheses[0]

print(f"Title: {top_hyp.title}")
print(f"Type: {top_hyp.hypothesis_type.value}")
print(f"Complexity: {top_hyp.complexity.value}")
print(f"\nStatement: {top_hyp.statement}")

print("\nVariables:")
print("  Independent:")
for var in top_hyp.independent_variables:
    print(f"    - {var.name}: {var.description}")

print("  Dependent:")
for var in top_hyp.dependent_variables:
    print(f"    - {var.name}: {var.description}")

print("\nPredictions:")
for pred in top_hyp.predictions:
    print(f"  - {pred.statement}")
    print(f"    Success Criterion: {pred.success_criterion}")

print("\nAssumptions:")
for assumption in top_hyp.assumptions:
    print(f"  - {assumption}")
```

### Compare Hypotheses by Score

```python
# Sort by different criteria
by_novelty = sorted(hypotheses, key=lambda h: h.novelty_score, reverse=True)
by_feasibility = sorted(hypotheses, key=lambda h: h.feasibility_score, reverse=True)
by_impact = sorted(hypotheses, key=lambda h: h.impact_score, reverse=True)
by_testability = sorted(hypotheses, key=lambda h: h.testability_score, reverse=True)

print("Most Novel:")
for h in by_novelty[:3]:
    print(f"  {h.title} ({h.novelty_score:.2f})")

print("\nMost Feasible:")
for h in by_feasibility[:3]:
    print(f"  {h.title} ({h.feasibility_score:.2f})")

print("\nHighest Impact:")
for h in by_impact[:3]:
    print(f"  {h.title} ({h.impact_score:.2f})")

print("\nMost Testable:")
for h in by_testability[:3]:
    print(f"  {h.title} ({h.testability_score:.2f})")
```

### Get Research Design Sketch

```python
expanded = await hyp_agent.expand_hypothesis(hypotheses[0])

print("Research Design:")
print(expanded["expanded"]["research_design_sketch"])

print("\nNext Steps:")
for step in expanded["expanded"]["next_steps"]:
    print(f"  • {step}")
```

### Custom Ranking Weights

```python
# Prioritize feasibility
feasibility_weights = {
    "novelty": 0.15,
    "feasibility": 0.50,  # High weight
    "impact": 0.20,
    "testability": 0.15,
}

ranked = await hyp_agent.rank_hypotheses(
    hypotheses,
    weights=feasibility_weights
)

print("Feasibility-Optimized Ranking:")
for h in ranked[:5]:
    print(f"  {h.title} ({h.overall_score:.3f})")
```

### Export Hypotheses

```python
import json

# Convert to dict
hypothesis_dicts = [h.to_dict() for h in hypotheses[:10]]

# Save to file
with open("hypotheses.json", "w") as f:
    json.dump({
        "query": "your topic",
        "total": len(hypotheses),
        "hypotheses": hypothesis_dicts
    }, f, indent=2)
```

## Hypothesis Types

| Type | Description | Example |
|------|-------------|---------|
| **Causal** | X causes Y | Attention mechanism causes improved interpretability |
| **Associative** | X correlates with Y | Model complexity correlates with interpretability difficulty |
| **Comparative** | A > B on dimension X | Method A is more efficient than Method B |
| **Mechanistic** | Here's how X works | Attention works by concentrating representation power |
| **Predictive** | X predicts future Y | Emerging topics predict future research directions |
| **Boundary Condition** | X applies when Z holds | Effect is stronger for transformers than RNNs |
| **Meta** | About research process | Interdisciplinary work generates more novel hypotheses |

## Complexity Levels

| Level | Description | Characteristics |
|-------|-------------|-----------------|
| **Simple** | Single variable relationship | Few variables, clear direction |
| **Moderate** | Multiple variables, one mechanism | 2-3 variables, one primary pathway |
| **Complex** | Multi-mechanism, conditional effects | 4+ variables, multiple pathways |

## Scoring System

### Novelty (Weight: 0.25)
Measures how original the hypothesis is relative to existing literature.
- **High novelty**: Addresses gaps, few existing papers
- **Low novelty**: Restates existing findings

Calculated by:
- Literature overlap: How many papers already address this?
- Concept uniqueness: Are the variable combinations new?

### Feasibility (Weight: 0.30)
Measures whether we can realistically test this hypothesis.
- **High feasibility**: Simple design, available data/resources
- **Low feasibility**: Requires rare equipment or long timelines

Calculated by:
- Complexity level (simple > complex)
- Resource requirements
- Timeline estimate
- Data availability

### Impact (Weight: 0.25)
Measures potential importance if the hypothesis is confirmed.
- **High impact**: Addresses major field questions
- **Low impact**: Incremental knowledge

Calculated by:
- Field relevance: How many related papers?
- Problem importance: Cited frequently?
- Application potential: Practical uses?

### Testability (Weight: 0.20)
Measures how clearly we can design a test.
- **High testability**: Clear variables, specific predictions
- **Low testability**: Vague constructs, unmeasurable

Calculated by:
- Variable clarity: Are they well-defined?
- Prediction specificity: Are success criteria clear?
- Measurability: Can we quantify outcomes?
- Falsifiability: Could we prove it wrong?

## Configuration

Edit `config.yaml` to customize:

**Scoring weights:**
```yaml
evaluation:
  novelty:
    weight: 0.25
  feasibility:
    weight: 0.30
  impact:
    weight: 0.25
  testability:
    weight: 0.20
```

**Generation strategies:**
```yaml
generation_strategies:
  gap_bridging:
    weight: 0.25
  trend_detection:
    weight: 0.20
  cross_domain_synthesis:
    weight: 0.20
  # etc.
```

**Output options:**
```yaml
output:
  include_scoring_rationale: true
  include_confidence_intervals: true
  include_research_design_sketch: true
```

## Common Patterns

### Pattern 1: Find Most Novel Ideas
```python
by_novelty = sorted(hypotheses, key=lambda h: h.novelty_score, reverse=True)
novel_ideas = by_novelty[:5]
```

### Pattern 2: Find Easy-to-Test Ideas
```python
by_feasibility = sorted(
    hypotheses,
    key=lambda h: h.feasibility_score,
    reverse=True
)
easy_tests = by_feasibility[:5]
```

### Pattern 3: Find High-Impact Ideas
```python
by_impact = sorted(hypotheses, key=lambda h: h.impact_score, reverse=True)
important_ideas = by_impact[:5]
```

### Pattern 4: Get Research Designs for All Top Hypotheses
```python
for hyp in hypotheses[:10]:
    expanded = await hyp_agent.expand_hypothesis(hyp)
    print(expanded["expanded"]["research_design_sketch"])
```

### Pattern 5: Filter by Multiple Criteria
```python
# Only highly feasible, testable hypotheses
good_hypotheses = [
    h for h in hypotheses
    if h.feasibility_score >= 0.7 and h.testability_score >= 0.7
]
```

## Data Structures

### Hypothesis Object

```python
{
    "id": "hypothesis_id",
    "title": "Clear hypothesis title",
    "statement": "Formal hypothesis statement",
    "background": "Why this matters",
    "type": "causal|associative|mechanistic|etc",
    "complexity": "simple|moderate|complex",
    "predictions": [
        {
            "statement": "Specific prediction",
            "measurable": true,
            "success_criterion": "How to know if confirmed"
        }
    ],
    "variables": {
        "independent": [...],
        "dependent": [...],
        "control": [...]
    },
    "assumptions": [...],
    "alternative_hypotheses": [...],
    "scoring": {
        "novelty": 0.75,
        "feasibility": 0.68,
        "impact": 0.82,
        "testability": 0.71,
        "overall": 0.74
    },
    "resources": [...],
    "timeline": "3-6 months",
    "risk_factors": [...]
}
```

## Running Examples

```bash
# Run all 7 examples
python agents/hypothesis_agent/examples.py

# Or in Python for specific examples
from agents.hypothesis_agent.examples import example_1_basic_hypothesis_generation
asyncio.run(example_1_basic_hypothesis_generation())
```

## Integration with Other Agents

### Input from Literature Agent
```python
# The Hypothesis Agent takes output from Literature Agent
papers = await lit_agent.search_papers(query)
gaps = await lit_agent.identify_gaps(papers)

# Use as input
hypotheses = await hyp_agent.generate_hypotheses(
    papers=papers,
    research_gaps=gaps,
    query=query
)
```

### Output for Experiment Agent
```python
# The Hypothesis Agent output feeds to Experiment Agent
for hyp in hypotheses[:5]:
    experiment_plan = await exp_agent.design_experiment(hyp)
```

## Advanced Features

### Domain-Specific Generation
```python
hypotheses = await hyp_agent.generate_hypotheses(
    papers=papers,
    research_gaps=gaps,
    query="your query",
    domain="machine_learning,neuroscience"
)
```

### Custom Scoring Functions
Extend `HypothesisAgent` to override scoring methods:
```python
class CustomHypothesisAgent(HypothesisAgent):
    def _calculate_novelty(self, hyp, papers):
        # Custom novelty calculation
        return custom_score
```

## Troubleshooting

### No hypotheses generated
- Check that `papers` list is not empty
- Verify `research_gaps` were identified
- Try more papers (larger `limit`)

### Low scoring for all hypotheses
- Hypotheses may genuinely be weak
- Try adjusting scoring weights in config.yaml
- Consider relaxing filters in ranking section

### Hypotheses too similar
- Enable `diversity_boost` in ranking config
- Increase number of generation strategies
- Manually select from different `source_strategy` types

## Future Enhancements

- [ ] LLM-based hypothesis expansion
- [ ] Semantic similarity clustering
- [ ] Automated experiment design generation
- [ ] Hypothesis refinement through feedback
- [ ] Integration with prior work databases
- [ ] Multi-hypothesis comparison visualization
- [ ] Bayesian hypothesis prioritization
- [ ] Automated assumption validation

## References

- Scientific method and hypothesis testing: [Stanford Encyclopedia of Philosophy](https://plato.stanford.edu/entries/physics-experiment/)
- Hypothesis generation strategies: Dunbar & Klahr (2012)
- Research design: Campbell & Stanley (1963)

---

Built for Phase 2 of Agentic Scientific Discovery Lab 🚀
