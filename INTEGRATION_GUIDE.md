# Integration Guide: Literature → Hypothesis Pipeline

This guide shows how to use the Literature Agent and Hypothesis Agent together in an integrated research workflow.

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    Your Research Question                        │
└────────────────────────┬────────────────────────────────────────┘
                         │
        ┌────────────────▼────────────────┐
        │     Literature Agent            │
        │  (Search & Gap Analysis)        │
        └────────────────┬────────────────┘
                         │
            ┌────────────┴────────────┐
            ▼                         ▼
        Papers                   Research Gaps
            │                         │
            └────────────┬────────────┘
                         │
        ┌────────────────▼────────────────┐
        │    Hypothesis Agent             │
        │  (Insight Generation)           │
        └────────────────┬────────────────┘
                         │
            ┌────────────┴───────────────────┐
            │                                │
        ▼──────────────────────────────────▼──
    Ranked Hypotheses
    (Ready for Experiment Agent)
```

## Step-by-Step Pipeline

### Step 1: Search Literature

```python
from agents.literature_agent import LiteratureAgent
import asyncio

async def search_literature(topic: str):
    agent = LiteratureAgent()
    
    try:
        papers = await agent.search_papers(
            query=topic,
            year_range=(2022, 2026),
            limit=50  # Adjust based on topic breadth
        )
        
        return papers
    
    finally:
        await agent.close()

papers = asyncio.run(search_literature("your research topic"))
print(f"✓ Found {len(papers)} papers")
```

### Step 2: Identify Research Gaps

```python
async def identify_gaps(papers):
    agent = LiteratureAgent()
    
    try:
        gaps = await agent.identify_gaps(papers)
        return gaps
    
    finally:
        await agent.close()

gaps = asyncio.run(identify_gaps(papers))
print(f"✓ Identified {len(gaps)} research gaps")

for gap in gaps[:3]:
    print(f"  - {gap.description}")
    print(f"    Priority: {gap.priority_level}")
```

### Step 3: Generate Hypotheses

```python
from agents.hypothesis_agent import HypothesisAgent

async def generate_hypotheses(papers, gaps, query):
    agent = HypothesisAgent()
    
    try:
        hypotheses = await agent.generate_hypotheses(
            papers=papers,
            research_gaps=gaps,
            query=query
        )
        
        return hypotheses
    
    finally:
        await agent.close()

hypotheses = asyncio.run(generate_hypotheses(
    papers,
    gaps,
    "your research topic"
))

print(f"✓ Generated {len(hypotheses)} hypotheses")
```

### Step 4: Analyze and Rank

```python
print("\n📊 Top Hypotheses by Overall Score:\n")

for i, hyp in enumerate(hypotheses[:5], 1):
    print(f"{i}. {hyp.title}")
    print(f"   ID: {hyp.id}")
    print(f"   Type: {hyp.hypothesis_type.value}")
    print(f"   Complexity: {hyp.complexity.value}")
    print(f"   Scores:")
    print(f"     • Novelty:     {hyp.novelty_score:.2f}")
    print(f"     • Feasibility: {hyp.feasibility_score:.2f}")
    print(f"     • Impact:      {hyp.impact_score:.2f}")
    print(f"     • Testability: {hyp.testability_score:.2f}")
    print(f"   ► Overall Score: {hyp.overall_score:.3f}")
    print()
```

### Step 5: Deep Dive into Top Hypothesis

```python
async def explore_hypothesis(hypothesis):
    agent = HypothesisAgent()
    
    try:
        expanded = await agent.expand_hypothesis(hypothesis)
        return expanded
    
    finally:
        await agent.close()

top_hypothesis = hypotheses[0]
expanded = asyncio.run(explore_hypothesis(top_hypothesis))

print(f"\n📋 Detailed View: {top_hypothesis.title}\n")
print(f"Statement: {top_hypothesis.statement}\n")

print("Variables:")
print("  Independent:")
for var in top_hypothesis.independent_variables:
    print(f"    • {var.name}: {var.description}")

print("  Dependent:")
for var in top_hypothesis.dependent_variables:
    print(f"    • {var.name}: {var.description}")

print("\nPredictions:")
for pred in top_hypothesis.predictions:
    print(f"  • {pred.statement}")
    print(f"    ✓ {pred.success_criterion}")

print("\nResearch Design Sketch:")
print(expanded["expanded"]["research_design_sketch"])

print("\nNext Steps:")
for step in expanded["expanded"]["next_steps"]:
    print(f"  → {step}")
```

## Complete Pipeline Script

Here's a complete script combining all steps:

```python
import asyncio
import json
from datetime import datetime
from agents.literature_agent import LiteratureAgent
from agents.hypothesis_agent import HypothesisAgent

async def complete_research_pipeline(
    topic: str,
    year_range: tuple = (2022, 2026),
    papers_limit: int = 50,
    output_file: str = None
) -> dict:
    """
    Complete pipeline from topic to ranked hypotheses.
    
    Args:
        topic: Research question or topic
        year_range: Publication year range
        papers_limit: Number of papers to search
        output_file: Optional JSON file to save results
    
    Returns:
        Dictionary with papers, gaps, and hypotheses
    """
    
    print(f"\n{'='*60}")
    print(f"🔬 Research Pipeline: {topic}")
    print(f"{'='*60}\n")
    
    # Step 1: Literature Search
    print("📚 Phase 1: Literature Search")
    print("-" * 40)
    
    lit_agent = LiteratureAgent()
    papers = await lit_agent.search_papers(
        query=topic,
        year_range=year_range,
        limit=papers_limit
    )
    print(f"✓ Found {len(papers)} papers ({year_range[0]}-{year_range[1]})")
    
    # Analyze publication trends
    years = {}
    for p in papers:
        year = p.publication_year
        years[year] = years.get(year, 0) + 1
    
    print(f"  Publication distribution:")
    for year in sorted(years.keys()):
        print(f"    {year}: {years[year]} papers")
    
    # Step 2: Gap Analysis
    print("\n🔍 Phase 2: Research Gap Analysis")
    print("-" * 40)
    
    gaps = await lit_agent.identify_gaps(papers)
    print(f"✓ Identified {len(gaps)} research gaps")
    
    print(f"\n  Top gaps:")
    for i, gap in enumerate(gaps[:3], 1):
        print(f"    {i}. {gap.get('description', 'Unknown')}")
        print(f"       Priority: {gap.get('priority_level', 'N/A')}")
    
    await lit_agent.close()
    
    # Step 3: Hypothesis Generation
    print("\n💡 Phase 3: Hypothesis Generation")
    print("-" * 40)
    
    hyp_agent = HypothesisAgent()
    hypotheses = await hyp_agent.generate_hypotheses(
        papers=papers,
        research_gaps=gaps,
        query=topic
    )
    print(f"✓ Generated {len(hypotheses)} candidate hypotheses")
    
    # Step 4: Ranking Analysis
    print("\n⚖️ Phase 4: Hypothesis Ranking Analysis")
    print("-" * 40)
    
    # Group by hypothesis type
    by_type = {}
    for h in hypotheses:
        ht = h.hypothesis_type.value
        by_type[ht] = by_type.get(ht, 0) + 1
    
    print(f"  Hypothesis types:")
    for ht, count in sorted(by_type.items()):
        print(f"    • {ht}: {count}")
    
    # Group by complexity
    by_complexity = {}
    for h in hypotheses:
        c = h.complexity.value
        by_complexity[c] = by_complexity.get(c, 0) + 1
    
    print(f"\n  Complexity distribution:")
    for c, count in sorted(by_complexity.items()):
        print(f"    • {c}: {count}")
    
    # Step 5: Top Hypotheses
    print("\n🏆 Phase 5: Top Hypotheses by Overall Score")
    print("-" * 40)
    
    for i, hyp in enumerate(hypotheses[:5], 1):
        print(f"\n{i}. {hyp.title}")
        print(f"   Type: {hyp.hypothesis_type.value} | "
              f"Complexity: {hyp.complexity.value}")
        print(f"   Scores: Novelty={hyp.novelty_score:.2f}, "
              f"Feasibility={hyp.feasibility_score:.2f}, "
              f"Impact={hyp.impact_score:.2f}, "
              f"Testability={hyp.testability_score:.2f}")
        print(f"   ► Overall: {hyp.overall_score:.3f}")
    
    await hyp_agent.close()
    
    # Compile results
    results = {
        "topic": topic,
        "timestamp": datetime.now().isoformat(),
        "statistics": {
            "papers_found": len(papers),
            "gaps_identified": len(gaps),
            "hypotheses_generated": len(hypotheses),
            "publication_years": years,
            "hypothesis_types": by_type,
            "complexity_distribution": by_complexity,
        },
        "papers": [
            {
                "title": p.get("title"),
                "authors": p.get("authors", [])[:2],
                "year": p.get("publication_year"),
                "citations": p.get("citations_count", 0),
            }
            for p in papers[:5]
        ],
        "gaps": [
            {
                "description": g.get("description"),
                "priority": g.get("priority_level"),
            }
            for g in gaps[:5]
        ],
        "hypotheses": [
            h.to_dict()
            for h in hypotheses[:5]
        ],
    }
    
    # Save results
    if output_file:
        with open(output_file, "w") as f:
            json.dump(results, f, indent=2)
        print(f"\n✓ Results saved to {output_file}")
    
    return results

# Run the pipeline
if __name__ == "__main__":
    results = asyncio.run(complete_research_pipeline(
        topic="machine learning model interpretability",
        year_range=(2023, 2026),
        papers_limit=30,
        output_file="research_pipeline_results.json"
    ))
    
    print("\n" + "="*60)
    print("✅ Pipeline Complete!")
    print("="*60)
```

## Filtering and Selection Strategies

### Strategy 1: Most Novel & Feasible

```python
# Balance novelty with implementation feasibility
selected = sorted(
    hypotheses,
    key=lambda h: (h.novelty_score * 0.6 + h.feasibility_score * 0.4),
    reverse=True
)[:5]
```

### Strategy 2: High Impact & Testable

```python
# Focus on meaningful, testable hypotheses
selected = sorted(
    hypotheses,
    key=lambda h: (h.impact_score * 0.6 + h.testability_score * 0.4),
    reverse=True
)[:5]
```

### Strategy 3: Multi-Criteria Selection

```python
# Create diverse portfolio
high_novelty = sorted(hypotheses, key=lambda h: h.novelty_score, reverse=True)[:2]
high_impact = sorted(hypotheses, key=lambda h: h.impact_score, reverse=True)[:2]
high_feasibility = sorted(hypotheses, key=lambda h: h.feasibility_score, reverse=True)[:2]

portfolio = high_novelty + high_impact + high_feasibility
portfolio = list({h.id: h for h in portfolio}.values())  # Remove duplicates
```

## Exporting Results

### Export to JSON

```python
import json

export = {
    "query": "your topic",
    "generated": datetime.now().isoformat(),
    "papers": [p.to_dict() for p in papers],
    "gaps": gaps,
    "hypotheses": [h.to_dict() for h in hypotheses[:10]],
}

with open("research_output.json", "w") as f:
    json.dump(export, f, indent=2)
```

### Export to Markdown

```python
def export_to_markdown(hypotheses, filename: str):
    with open(filename, "w") as f:
        f.write("# Research Hypotheses\n\n")
        
        for i, hyp in enumerate(hypotheses, 1):
            f.write(f"## {i}. {hyp.title}\n\n")
            f.write(f"**Type:** {hyp.hypothesis_type.value}\n")
            f.write(f"**Complexity:** {hyp.complexity.value}\n\n")
            f.write(f"**Statement:** {hyp.statement}\n\n")
            f.write(f"**Overall Score:** {hyp.overall_score:.3f}\n\n")
            
            f.write("### Variables\n\n")
            f.write("**Independent:**\n")
            for var in hyp.independent_variables:
                f.write(f"- {var.name}: {var.description}\n")
            
            f.write("\n**Dependent:**\n")
            for var in hyp.dependent_variables:
                f.write(f"- {var.name}: {var.description}\n")
            
            f.write("\n---\n\n")

export_to_markdown(hypotheses, "hypotheses.md")
```

## Best Practices

### 1. Search Comprehensively
- Use multiple queries and keywords
- Adjust year range to include seminal work
- Consider both cutting-edge (recent) and foundational (older) papers

### 2. Analyze All Gaps
- Don't ignore low-priority gaps
- Some may address interesting cross-domain connections
- Multiple small gaps can form a larger hypothesis

### 3. Diverse Hypotheses
- Select from multiple hypothesis types
- Include different complexity levels
- Mix novel, feasible, impactful, and testable ideas

### 4. Iterative Refinement
- Use feedback from literature review
- Refine based on domain expert knowledge
- Iterate hypothesis generation with different parameters

### 5. Documentation
- Export results for team review
- Document assumptions and rationale
- Track which papers led to which hypotheses

## Next Steps

After ranking hypotheses, feed them to the **Experiment Agent** (Phase 3) to:
- Design specific experimental protocols
- Identify required datasets
- Estimate resource requirements
- Predict experimental outcomes

```python
# Future: Feed to Experiment Agent
from agents.experiment_agent import ExperimentAgent

exp_agent = ExperimentAgent()

for hyp in hypotheses[:5]:
    experiment_plan = await exp_agent.design_experiment(hyp)
    print(f"Experiment Plan for: {hyp.title}")
    print(experiment_plan)
```

## Troubleshooting

### Problem: Too many similar hypotheses
**Solution**: Enable diversity boost in config or manually select from different generation strategies

### Problem: All hypotheses have low scores
**Solution**: 
- Review papers - may indicate immature field
- Relax score thresholds in config
- Try different query terms

### Problem: Hypotheses are too vague
**Solution**:
- Ensure papers have detailed abstracts
- Increase number of papers searched
- Review hypothesis structure and refine variables

---

Questions? Check the individual agent READMEs or run the examples!
