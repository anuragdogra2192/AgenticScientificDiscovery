# 🚀 Quick Start Guide - Literature Agent

Welcome to your Agentic Scientific Discovery Lab! Here's how to get up and running in 5 minutes.

## ✅ What You Have

```
✓ Literature Agent    - Searches 250M+ papers across OpenAlex & arXiv
✓ Configuration      - YAML-based agent setup
✓ Examples          - 6 ready-to-run examples
✓ Documentation     - Complete guides and API reference
✓ Dependencies      - All installed and ready
```

## 🏃 Get Started in 3 Steps

### Step 1: Verify Setup (30 seconds)
```bash
cd /Users/adogra/Documents/GitHub/AgenticScientificDiscovery
python -c "from agents.literature_agent import LiteratureAgent; print('✓ Ready!')"
```

### Step 2: Run First Example (1 minute)
```bash
python agents/literature_agent/agent.py
```

You should see papers on "machine learning interpretability" appear!

### Step 3: Try Examples Suite (2 minutes)
```bash
python agents/literature_agent/examples.py
```

This runs 6 different examples showing all capabilities.

## 💡 Common Tasks

### Search for Papers
```python
import asyncio
from agents.literature_agent import LiteratureAgent

async def main():
    agent = LiteratureAgent()
    
    papers = await agent.search_papers(
        "your research topic",
        year_range=(2023, 2026),
        limit=20
    )
    
    for paper in papers:
        print(f"✓ {paper.title}")
        print(f"  by {paper.authors[0]} et al., {paper.publication_year}\n")
    
    await agent.close()

asyncio.run(main())
```

### Find Research Gaps
```python
async def main():
    agent = LiteratureAgent()
    
    papers = await agent.search_papers("your topic", limit=50)
    gaps = await agent.identify_gaps(papers)
    
    print(f"Found {len(gaps)} research gaps:\n")
    for gap in gaps:
        print(f"• {gap.gap_description}")
        print(f"  Priority: {gap.priority_level} | "
              f"Confidence: {gap.confidence:.0%}\n")
    
    await agent.close()

asyncio.run(main())
```

### Generate Full Report
```python
async def main():
    agent = LiteratureAgent()
    
    papers = await agent.search_papers("your topic", limit=100)
    gaps = await agent.identify_gaps(papers)
    report = await agent.generate_report("your topic", papers, gaps)
    
    import json
    with open("report.json", "w") as f:
        json.dump(report, f, indent=2)
    
    print(f"✓ Report saved!")
    print(f"  Papers: {report['statistics']['total_papers']}")
    print(f"  Gaps: {report['statistics']['identified_gaps']}")
    
    await agent.close()

asyncio.run(main())
```

## 📚 Documentation Map

| File | Purpose |
|------|---------|
| **README.md** | Project overview & vision |
| **SETUP.md** | Detailed installation & troubleshooting |
| **ARCHITECTURE.md** | System design & agent patterns |
| **agents/literature_agent/README.md** | Agent-specific documentation |
| **agents/literature_agent/config.yaml** | Configuration reference |

## 🔍 Explore the Code

**Main implementation**: `agents/literature_agent/agent.py`
- `LiteratureAgent` class - Core functionality
- `search_papers()` - Query multiple databases
- `identify_gaps()` - Find research gaps
- `generate_report()` - Create comprehensive reports

**Configuration**: `agents/literature_agent/config.yaml`
- Database setup (OpenAlex, arXiv)
- Search parameters
- Output formats
- Rate limits

**Examples**: `agents/literature_agent/examples.py`
- 6 runnable examples
- Different use cases
- Best practices

## 🎓 Next Steps

1. **Run the examples**: `python agents/literature_agent/examples.py`
2. **Try your own query**: Edit the topic in example code
3. **Read the docs**: Check SETUP.md for detailed info
4. **Explore the code**: See how it works in agent.py
5. **Build more agents**: Follow the pattern to add Hypothesis Agent, etc.

## 🔗 Key Resources

- **OpenAlex**: https://openalex.org (250M+ papers)
- **arXiv**: https://arxiv.org (2M+ preprints)
- **Python Async**: https://docs.python.org/3/library/asyncio.html

## ❓ Troubleshooting

**No results?**
- Try simpler search terms
- Expand year range
- Check internet connection

**Slow performance?**
- Reduce `limit` parameter
- Use only one database instead of all
- Check API rate limits

**Connection errors?**
- Verify internet connection
- Test APIs manually with curl
- Check logs for detailed errors

## 🎯 What's Next

The Literature Agent is just the first specialist! The architecture supports adding:

```
Phase 1: Literature Agent ✅         (Complete)
Phase 2: Hypothesis Agent 🚧         (Planned)
Phase 3: Experiment Agent 🚧         (Planned)
Phase 4: Analysis Agent 🚧           (Planned)
Phase 5: Report Agent 🚧             (Planned)
```

Each agent will work together to automate the entire research pipeline.

## 📞 Support

- Check documentation in SETUP.md
- Review examples in examples.py
- Look at agent configuration in config.yaml
- Test individual components in agent.py

## 🎉 You're Ready!

Your Literature Agent is fully set up and ready to accelerate your research. Happy discovering! 🚀

---

**Questions?** Check SETUP.md for troubleshooting or see examples.py for more use cases.
