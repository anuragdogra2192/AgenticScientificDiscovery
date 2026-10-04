# Agentic Scientific Discovery Lab - Setup Guide

Welcome! This guide will help you get your scientific discovery lab up and running with the Literature Agent.

## Prerequisites

- Python 3.10+
- pip (Python package manager)
- Git

## Quick Start (5 minutes)

### 1. Activate Virtual Environment

```bash
source .venv/bin/activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Run the Literature Agent

```bash
python agents/literature_agent/agent.py
```

You should see:
```
🔍 Searching for papers on machine learning interpretability...
Found X papers

1. [Paper title]
   Authors: [author names]
   Year: 2024
   Citations: 123

...
```

## Project Structure

```
AgenticScientificDiscovery/
├── agents/
│   ├── __init__.py
│   └── literature_agent/
│       ├── __init__.py
│       ├── agent.py              # Main agent implementation
│       ├── config.yaml           # Agent configuration
│       ├── README.md             # Literature Agent documentation
│       └── examples.py           # Usage examples
├── requirements.txt              # Python dependencies
├── SETUP.md                      # This file
└── README.md                     # Project overview
```

## Detailed Setup

### Step 1: Create Virtual Environment (if needed)

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### Step 2: Install Dependencies

The project requires:
- **httpx** - Async HTTP client for API calls
- **pyyaml** - Configuration file parsing
- **feedparser** - Feed parsing for arXiv
- **scholarly** - Scholar metadata extraction (optional)
- **aiohttp** - Async HTTP library

```bash
pip install -r requirements.txt
```

### Step 3: Verify Installation

```bash
python -c "from agents.literature_agent import LiteratureAgent; print('✓ Installation successful')"
```

## First Steps

### 1. Basic Search

Create a file `test_search.py`:

```python
import asyncio
from agents.literature_agent import LiteratureAgent

async def main():
    agent = LiteratureAgent()
    
    papers = await agent.search_papers(
        "attention mechanisms transformers",
        limit=5
    )
    
    for paper in papers:
        print(f"• {paper.title}")
    
    await agent.close()

asyncio.run(main())
```

Run it:
```bash
python test_search.py
```

### 2. Explore Research Gaps

```python
import asyncio
from agents.literature_agent import LiteratureAgent

async def main():
    agent = LiteratureAgent()
    
    papers = await agent.search_papers("quantum computing", limit=10)
    gaps = await agent.identify_gaps(papers)
    
    print(f"Found {len(gaps)} research gaps:")
    for gap in gaps:
        print(f"  - {gap.gap_description}")
    
    await agent.close()

asyncio.run(main())
```

### 3. Run Example Suite

```bash
python agents/literature_agent/examples.py
```

This runs 6 comprehensive examples showing:
- Basic paper search
- Gap analysis
- Comparative analysis across topics
- Full literature review generation
- Emerging topics discovery
- BibTeX export

## Configuration

### Modifying Agent Settings

Edit `agents/literature_agent/config.yaml` to:

**Change default search limit:**
```yaml
search:
  default_limit: 100  # was 50
```

**Add/remove databases:**
```yaml
databases:
  openalex:
    enabled: true
  arxiv:
    enabled: false  # disable arXiv
```

**Adjust rate limits (requests per second):**
```yaml
databases:
  openalex:
    rate_limit: 5  # was 10 (slower)
```

## API Information

All databases used are **free and require no API keys**:

### OpenAlex
- Largest academic database (~250M papers)
- No authentication required
- Rate limit: 10 requests/second (with politeness)
- Homepage: https://openalex.org

### arXiv
- Preprints for physics, CS, math, stats
- No authentication required
- Rate limit: 3 requests/second
- Homepage: https://arxiv.org

### Semantic Scholar (future)
- AI-powered research discovery
- Limited free tier
- Required for advanced features

## Common Tasks

### Task 1: Search a Specific Topic

```python
async def search_topic():
    agent = LiteratureAgent()
    papers = await agent.search_papers(
        "your topic here",
        year_range=(2023, 2026),
        limit=50
    )
    # Process papers...
```

### Task 2: Generate Literature Review

```python
async def generate_review():
    agent = LiteratureAgent()
    papers = await agent.search_papers("your topic", limit=100)
    gaps = await agent.identify_gaps(papers)
    report = await agent.generate_report("your topic", papers, gaps)
    
    # Save as JSON
    import json
    with open("review.json", "w") as f:
        json.dump(report, f, indent=2)
```

### Task 3: Monitor Research Trends

```python
async def track_trends():
    agent = LiteratureAgent()
    
    years_data = {}
    for year in range(2022, 2026):
        papers = await agent.search_papers(
            "your topic",
            year_range=(year, year),
            limit=100
        )
        years_data[year] = len(papers)
    
    print("Papers per year:", years_data)
```

### Task 4: Find Seminal Papers

```python
async def find_seminal():
    agent = LiteratureAgent()
    papers = await agent.search_papers("your topic", limit=200)
    
    # Sort by citations
    seminal = sorted(papers, key=lambda p: p.citations_count, reverse=True)
    
    for paper in seminal[:10]:
        print(f"{paper.title} ({paper.citations_count} citations)")
```

## Troubleshooting

### Issue: "Connection refused"
**Solution**: Check internet connection and verify API endpoints are accessible:
```bash
curl -s https://api.openalex.org/works?search=test | head -20
```

### Issue: "Rate limit exceeded"
**Solution**: Reduce request frequency or use caching:
```python
agent.config['search']['default_limit'] = 10  # smaller batches
```

### Issue: "No results returned"
**Solution**: Try broader search terms or different date ranges:
```python
# Instead of: "novel approach to neural networks"
# Try: "neural networks" or "deep learning"

papers = await agent.search_papers("neural networks", year_range=(2020, 2026))
```

### Issue: "aiohttp/httpx connection pool exhausted"
**Solution**: Ensure you're closing the agent:
```python
try:
    # ... do work ...
finally:
    await agent.close()
```

## Next Steps

1. **Explore the Examples**: Run `python agents/literature_agent/examples.py`
2. **Read Documentation**: Check `agents/literature_agent/README.md`
3. **Extend the Agent**: Add new database connectors or analysis capabilities
4. **Build Additional Agents**: Create specialized agents for data analysis, hypothesis generation, etc.

## Building More Agents

The Literature Agent is the first specialist in your lab. To add more agents:

```
agents/
├── literature_agent/          # Existing
│   ├── agent.py
│   ├── config.yaml
│   └── README.md
├── hypothesis_agent/          # New
│   ├── agent.py
│   ├── config.yaml
│   └── README.md
├── experiment_agent/          # New
│   ├── agent.py
│   ├── config.yaml
│   └── README.md
└── __init__.py
```

Each agent follows the same pattern:
1. Configuration (YAML)
2. Implementation (Python)
3. Tests
4. Documentation

## Support & Resources

- **OpenAlex Docs**: https://docs.openalex.org
- **arXiv API**: https://arxiv.org/help/api
- **Python Async**: https://docs.python.org/3/library/asyncio.html
- **YAML Format**: https://yaml.org

## Contributing

To extend the Literature Agent:

1. **Add new database**: Implement `_search_database()` method
2. **Add analysis tools**: Implement new methods in `LiteratureAgent` class
3. **Improve gap detection**: Enhance `identify_gaps()` logic
4. **Add new output formats**: Extend `generate_report()` method

## License

MIT - Feel free to use and modify for your hackathon!

---

Questions? Check the README.md in each agent directory or run the examples!
