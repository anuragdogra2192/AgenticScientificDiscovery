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

### 2. 💡 **Hypothesis Agent** (🚧 Coming Soon)
Generates novel hypotheses based on literature and identifies promising research directions.
- Analyzes literature patterns and gaps
- Suggests novel research questions
- Ranks hypotheses by feasibility and impact
- Connects disparate domains

### 3. 🧪 **Experiment Agent** (🚧 Coming Soon)
Designs and simulates experiments to test hypotheses.
- Generates experimental protocols
- Suggests datasets and tools
- Simulates experiments (when applicable)
- Predicts outcome scenarios

### 4. 📊 **Analysis Agent** (🚧 Coming Soon)
Analyzes experimental results and extracts insights.
- Statistical significance testing
- Result visualization
- Comparison with literature findings
- Generates conclusions

### 5. 📝 **Report Agent** (🚧 Coming Soon)
Synthesizes findings into research papers.
- Structures results into papers
- Generates visualizations
- Suggests additional experiments
- Identifies follow-up research

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

## 📖 Documentation

- **[Setup Guide](SETUP.md)** - Installation and configuration
- **[Literature Agent](agents/literature_agent/README.md)** - Detailed documentation
- **[Examples](agents/literature_agent/examples.py)** - Real-world usage patterns
- **[Agent Config](agents/literature_agent/config.yaml)** - Configuration reference

## 🏗️ Project Structure

```
AgenticScientificDiscovery/
├── agents/
│   ├── __init__.py
│   └── literature_agent/          # Literature search & analysis
│       ├── agent.py               # Main implementation
│       ├── config.yaml            # Configuration
│       ├── examples.py            # Usage examples
│       ├── __init__.py
│       └── README.md              # Documentation
├── requirements.txt               # Python dependencies
├── README.md                      # This file
├── SETUP.md                       # Setup guide
└── .git/                          # Version control
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

### Free, No-Auth APIs

| Database | Papers | Coverage | Rate Limit |
|----------|--------|----------|-----------|
| OpenAlex | 250M+ | Broad (all disciplines) | 10 req/s |
| arXiv | 2.3M+ | Physics, CS, Math, Stats | 3 req/s |
| Semantic Scholar | 200M+ | ML-enhanced search | 1 req/s |

All APIs are free and require no authentication.

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
- [x] Multi-database search
- [x] Paper parsing and extraction
- [x] Research gap identification
- [x] Literature review generation

### Phase 2: Hypothesis Generation (🔄 In Progress)
- [ ] Literature pattern analysis
- [ ] Hypothesis generation
- [ ] Feasibility assessment
- [ ] Novelty scoring

### Phase 3: Experiment Design (🚧 Planned)
- [ ] Experimental protocol generation
- [ ] Dataset recommendations
- [ ] Simulation capabilities
- [ ] Success prediction

### Phase 4: Analysis (🚧 Planned)
- [ ] Statistical testing
- [ ] Result interpretation
- [ ] Literature contextualization
- [ ] Finding extraction

### Phase 5: Reporting (🚧 Planned)
- [ ] Paper generation
- [ ] Visualization creation
- [ ] Citation management
- [ ] Collaboration tools

## 🤝 Contributing

We welcome contributions! For a hackathon project, you can:

1. **Add new agents** following the template
2. **Extend existing agents** with new capabilities
3. **Add new data sources** (Google Scholar, Scopus, etc.)
4. **Improve analysis** (ML-based gap detection, clustering, etc.)
5. **Create integrations** (Slack, email, documents, etc.)

## 🐛 Troubleshooting

### API Connection Issues
```bash
# Test OpenAlex
curl -s https://api.openalex.org/works?search=test | head

# Test arXiv
curl -s "https://arxiv.org/api/query?search_query=test&start=0&max_results=1"
```

### Rate Limiting
- OpenAlex: 10 requests/second with politeness (waits between requests)
- arXiv: 3 requests/second
- Semantic Scholar: 1 request/second (higher with API key)

### No Results
- Try simpler, shorter search terms
- Expand year range
- Try different database
- Check internet connection

## 📚 Resources

### Documentation
- [OpenAlex API Docs](https://docs.openalex.org)
- [arXiv API Documentation](https://arxiv.org/help/api)
- [Semantic Scholar API](https://www.semanticscholar.org/product/api)

### Related Work
- [SciPy Conference Talks](https://www.scipy.org/)
- [arXiv Research](https://arxiv.org)
- [Nature Machine Intelligence](https://www.nature.com/natmachintell/)

## 📄 License

MIT License - Use freely for your hackathon and beyond!

## 🎉 Hackathon Details

Built for: **Agentic Scientific Discovery Lab Hackathon**
Version: 1.0.0
Last Updated: October 2026

---

## 🌟 Next Steps

1. **[Setup the project](SETUP.md)** in 5 minutes
2. **[Run examples](agents/literature_agent/examples.py)** to see it in action
3. **[Build your first search](agents/literature_agent/README.md)** on your topic
4. **[Extend the agents](SETUP.md#building-more-agents)** with new capabilities
5. **[Contribute](README.md#contributing)** your improvements

Happy discovering! 🚀
