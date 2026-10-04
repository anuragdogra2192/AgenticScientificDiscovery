# Literature Agent 📚

**Status**: ✅ **LIVE with Claude Haiku 4.5**

The Literature Agent searches biomedical literature (Europe PMC, PubChem) for Mycobacterium tuberculosis drug discovery. Uses Claude Haiku to identify research gaps and prioritize findings. Focuses on DprE1, InhA, MmpL3 targets and resistance mechanisms in TB drug development.

## Features

### 🔍 Database Integration
- **OpenAlex**: Comprehensive academic library with 250M+ papers
- **arXiv**: Preprint repository for physics, CS, math, stats, and more
- **Semantic Scholar** (planned): AI-powered research discovery

### 📊 Core Capabilities
- **Full-text search** across multiple databases simultaneously
- **Advanced filtering** by year, topic, author, institution
- **Paper extraction** - automatically parse titles, authors, abstracts, citations
- **Gap identification** - detect unexplored research areas and unanswered questions
- **Trend detection** - identify emerging topics and shifting paradigms
- **Citation network analysis** - understand paper relationships
- **Quality assessment** - evaluate paper impact and relevance

### 📈 Analysis & Synthesis
- Generate literature reviews from search results
- Identify consensus and controversies in the field
- Map the research landscape semantically
- Find underexplored connections between topics
- Highlight future research directions

## Configuration

The agent is configured via `config.yaml`:

```yaml
databases:
  openalex:
    api_url: https://api.openalex.org
    rate_limit: 10  # requests/sec
  
  arxiv:
    api_url: https://arxiv.org/api
    rate_limit: 3   # requests/sec
```

## Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Verify installation
python -c "from agents.literature_agent import LiteratureAgent; print('✓ Ready')"
```

## Usage

### Basic Search
```python
from agents.literature_agent import LiteratureAgent
import asyncio

async def search_literature():
    agent = LiteratureAgent()
    
    papers = await agent.search_papers(
        query="quantum machine learning",
        databases=["openalex", "arxiv"],
        year_range=(2022, 2026),
        limit=50
    )
    
    print(f"Found {len(papers)} papers")
    for paper in papers[:5]:
        print(f"- {paper.title}")
        print(f"  {paper.authors[0]} et al., {paper.publication_year}")
        print(f"  Citations: {paper.citations_count}\n")
    
    await agent.close()

asyncio.run(search_literature())
```

### Identify Research Gaps
```python
async def analyze_gaps():
    agent = LiteratureAgent()
    
    papers = await agent.search_papers(
        "neural network interpretability",
        year_range=(2020, 2026)
    )
    
    gaps = await agent.identify_gaps(papers)
    
    for gap in gaps:
        print(f"Gap: {gap.gap_description}")
        print(f"Priority: {gap.priority_level}")
        print(f"Related papers: {gap.related_papers}")
        print()
    
    await agent.close()

asyncio.run(analyze_gaps())
```

### Generate Comprehensive Report
```python
async def generate_lit_review():
    agent = LiteratureAgent()
    
    papers = await agent.search_papers("reinforcement learning robotics")
    gaps = await agent.identify_gaps(papers)
    
    report = await agent.generate_report(
        query="reinforcement learning robotics",
        papers=papers,
        gaps=gaps
    )
    
    # Save report
    import json
    with open("literature_review.json", "w") as f:
        json.dump(report, f, indent=2)
    
    await agent.close()

asyncio.run(generate_lit_review())
```

## Running the Example

```bash
python agents/literature_agent/agent.py
```

This will:
1. Search for papers on "machine learning interpretability explainability"
2. Identify research gaps
3. Generate a structured report
4. Output results to stdout

## Output Format

Papers are returned as `Paper` objects with:
- `title`: Paper title
- `authors`: List of author names
- `publication_year`: Year of publication
- `journal`: Journal/venue name
- `doi`: Digital Object Identifier
- `abstract`: Paper abstract
- `citations_count`: Number of citations
- `pdf_url`: Link to PDF (when available)
- `openalex_id`: OpenAlex identifier
- `arxiv_id`: arXiv identifier

Research gaps are `ResearchGap` objects with:
- `gap_description`: What is unknown
- `related_papers`: Papers that highlight this gap
- `potential_approaches`: Methods to address the gap
- `priority_level`: high/medium/low
- `confidence`: 0.0-1.0 confidence score

## API Limits

Be mindful of rate limits:
- **OpenAlex**: 10 requests/second (no API key needed)
- **arXiv**: 3 requests/second (no API key needed)
- **Semantic Scholar**: 1 request/second (higher with API key)

The agent includes built-in rate limiting and retry logic.

## Advanced Features

### Custom Search Strategies
Modify `agent.py` to implement custom search logic:
```python
async def custom_search(self, topic: str):
    # 1. Broad semantic search
    results = await self._search_openalex(topic, limit=100)
    
    # 2. Filter by citation impact
    high_impact = [p for p in results if p.citations_count > 50]
    
    # 3. Extract seminal papers (highly cited, older)
    seminal = [p for p in high_impact if p.publication_year < 2020]
    
    # 4. Find recent work (2023+)
    recent = [p for p in results if p.publication_year >= 2023]
    
    return seminal + recent
```

### Extending to More Databases
Add new databases to `config.yaml` and implement parsers in `agent.py`:
```python
async def _search_new_database(self, query, limit):
    response = await self.client.get(...)
    return self._parse_new_format(response)
```

## Troubleshooting

### No results returned
- Check your internet connection
- Verify query is not too narrow
- Try searching OpenAlex first (most comprehensive)
- Check API rate limits haven't been exceeded

### Slow performance
- Reduce `limit` parameter
- Specify narrower `year_range`
- Use specific database instead of all

### Connection errors
- OpenAlex: Requires internet access, no auth
- arXiv: Check if service is temporarily down
- See logs for detailed error messages

## Future Enhancements

- [ ] Support for Google Scholar, Scopus, Web of Science
- [ ] ML-based automatic gap detection
- [ ] Semantic similarity clustering
- [ ] Author profile and collaboration network analysis
- [ ] Topic modeling and LDA analysis
- [ ] Automated literature review generation using LLM
- [ ] Knowledge graph construction
- [ ] Contradition and debate detection
- [ ] Dataset and code artifact discovery

## References

- [OpenAlex Documentation](https://docs.openalex.org)
- [arXiv API Documentation](https://arxiv.org/help/api)
- [Semantic Scholar API](https://www.semanticscholar.org/product/api)

---

Built for the Agentic Scientific Discovery Lab hackathon 🚀
