# Architecture: Agentic Scientific Discovery Lab

## System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                     Research Assistant Portal                    │
│              (Future: Web UI, Slack Bot, CLI Tools)              │
└────────────────────────┬────────────────────────────────────────┘
                         │
        ┌────────────────┴────────────────┐
        │                                 │
┌───────▼──────┐  ┌────────────────┐  ┌──▼──────────┐
│  Literature  │  │   Hypothesis   │  │ Experiment  │
│    Agent     │  │     Agent      │  │    Agent    │
│   (Ready)    │  │   (Planning)   │  │  (Planning) │
└───────┬──────┘  └────────────────┘  └──┬──────────┘
        │                                 │
        ├─────────────────────────────────┤
        │                                 │
┌───────▼──────────────────────────┐  ┌──▼──────────────┐
│      Analysis Agent              │  │  Report Agent   │
│      (Planning)                  │  │  (Planning)     │
└────────────────────────────────┬─┘  └──┬──────────────┘
                                 │       │
                    ┌────────────┴──────┴────────┐
                    │                           │
            ┌───────▼────────────┐    ┌────────▼───────┐
            │ Knowledge Graph    │    │  Evidence Base │
            │ (Planning)         │    │  (Planning)    │
            └────────────────────┘    └────────────────┘
                    │                           │
                    └───────────────┬───────────┘
                                    │
        ┌───────────────────────────▼───────────────────────┐
        │         External Data & API Layer                 │
        │  ┌──────────┐  ┌────────┐  ┌───────────────────┐  │
        │  │ OpenAlex │  │ arXiv  │  │ Semantic Scholar  │  │
        │  └──────────┘  └────────┘  └───────────────────┘  │
        └─────────────────────────────────────────────────────┘
```

## Agent Hierarchy

### Level 1: Data Collection
**Literature Agent** ✅
- Searches academic databases
- Extracts paper metadata
- Analyzes citation networks
- Identifies research gaps

```
Input:  Research query
        ↓
       [Search] → OpenAlex, arXiv
        ↓
     [Extract] → Parse papers
        ↓
     [Analyze] → Find patterns
        ↓
Output: Papers + Gaps
```

### Level 2: Knowledge Synthesis
**Hypothesis Agent** (Planned)
- Analyzes literature patterns
- Generates novel hypotheses
- Assesses feasibility
- Prioritizes by impact

```
Input:  Literature + Gaps
        ↓
    [Analyze] → Extract concepts
        ↓
   [Generate] → Create hypotheses
        ↓
    [Evaluate] → Score feasibility
        ↓
Output: Ranked hypotheses
```

### Level 3: Experimental Design
**Experiment Agent** (Planned)
- Designs experimental protocols
- Suggests datasets
- Simulates experiments
- Predicts outcomes

```
Input:  Hypothesis
        ↓
    [Design] → Protocol generation
        ↓
   [Suggest] → Dataset discovery
        ↓
  [Simulate] → Run simulations
        ↓
Output: Experiment plan
```

### Level 4: Result Analysis
**Analysis Agent** (Planned)
- Statistical testing
- Result interpretation
- Contextualization
- Finding extraction

```
Input:  Experimental results
        ↓
    [Analyze] → Statistical tests
        ↓
 [Interpret] → Extract meaning
        ↓
  [Compare] → Literature context
        ↓
Output: Analyzed findings
```

### Level 5: Knowledge Dissemination
**Report Agent** (Planned)
- Paper generation
- Visualization creation
- Citation management
- Future work identification

```
Input:  Findings
        ↓
[Generate] → Paper structure
        ↓
  [Create] → Visualizations
        ↓
  [Format] → Final document
        ↓
Output: Research paper
```

## Agent Components

### Each Agent Contains:

```
agent/
├── agent.py              # Core implementation
│   ├── class Definition  # Main agent class
│   ├── Tool methods      # Specific capabilities
│   └── Utility methods   # Helpers
├── config.yaml           # Configuration
│   ├── name & role       # Agent identity
│   ├── capabilities      # What it can do
│   ├── tools             # Available tools
│   └── parameters        # Tuning knobs
├── README.md             # Documentation
└── examples.py           # Usage examples
```

### Agent Interface (Unified)

```python
class Agent:
    # Initialization
    __init__(config_path: str)
    
    # Core methods (all agents implement)
    async run(input_data: Any) -> Any
    async close() -> None
    
    # Specialized methods per agent
    # (e.g., search_papers, generate_hypotheses, etc.)
```

## Data Flow

### Example: Literature Search Pipeline

```
User Query
    ↓
┌───────────────────────────┐
│  LiteratureAgent.search() │
└────────┬──────────────────┘
         │
         ├─→ [OpenAlex API Call]
         │   ↓
         │   └─→ HTTP Request
         │       ↓
         │       Parse JSON
         │       ↓
         │       Create Paper objects
         │       ↓
         │       Cache results
         │
         └─→ [arXiv API Call]
             ↓
             └─→ HTTP Request
                 ↓
                 Parse XML
                 ↓
                 Create Paper objects
                 ↓
                 Merge & deduplicate
                 ↓
         ┌──────────────────────┐
         │  List[Paper] returned │
         └──────────────────────┘
                 ↓
         ┌──────────────────────┐
         │ Gap Analysis Phase   │
         └────────┬─────────────┘
                  │
                  ├─→ Extract patterns
                  ├─→ Find indicators
                  └─→ Score gaps
                      ↓
              ┌───────────────┐
              │ List[Gap]     │
              └───────────────┘
```

## Database Adapter Pattern

Each database has a standardized adapter:

```python
class DatabaseAdapter:
    async def search(self, query, params) -> List[Paper]:
        # 1. Format query for API
        # 2. Make HTTP request with rate limiting
        # 3. Parse response
        # 4. Convert to Paper objects
        # 5. Return standardized format

class OpenAlexAdapter(DatabaseAdapter):
    async def search(self, query, params):
        # OpenAlex-specific implementation
        
class ArxivAdapter(DatabaseAdapter):
    async def search(self, query, params):
        # arXiv-specific implementation
```

## Configuration Hierarchy

```yaml
# agents/literature_agent/config.yaml
agent:
  name: Literature Agent
  capabilities: [...]
  
databases:
  openalex:
    api_url: https://api.openalex.org
    rate_limit: 10
    
search:
  default_limit: 50
  max_results: 1000
  
output:
  formats: [json, markdown, bibtex]
```

When agent loads:
1. Parse YAML
2. Initialize database clients
3. Configure rate limiters
4. Set output formatters
5. Ready for use

## Async/Await Architecture

All agents use Python async for:
- Non-blocking API calls
- Concurrent database queries
- Efficient resource usage
- Responsive UI

```python
async def search_papers(query):
    # Run searches in parallel
    results = await asyncio.gather(
        search_openalex(query),
        search_arxiv(query),
        search_semantic_scholar(query)
    )
    # All three complete concurrently
    return combine_results(results)
```

## Error Handling & Resilience

Each agent implements:

```python
try:
    result = await api_call()
except RateLimitError:
    await asyncio.sleep(backoff_time)
    result = await api_call()  # retry
except ConnectionError:
    logger.error("API unreachable")
    return cached_result() or []
finally:
    await client.close()
```

## Extensibility Points

### 1. Add New Database
```python
# In config.yaml
databases:
  new_db:
    api_url: https://api.example.com
    rate_limit: 5

# In agent.py
async def _search_new_db(self, query, limit):
    # Implementation
```

### 2. Add New Tool
```python
# In agent.py
async def new_capability(self, input_data):
    # New analysis or processing
    return output_data

# Update config
tools:
  analyze:
    - new_capability
```

### 3. Add New Agent
```
agents/
├── literature_agent/     # Existing
└── new_agent/           # New
    ├── agent.py
    ├── config.yaml
    ├── README.md
    └── examples.py
```

## Performance Characteristics

### Literature Agent

| Operation | Time | Notes |
|-----------|------|-------|
| Search (10 results) | 2-5s | Parallel APIs |
| Search (100 results) | 5-15s | Rate-limited |
| Gap analysis | 1-2s | In-memory |
| Report generation | <1s | JSON assembly |

### Scalability

- **Concurrent searches**: Limited by rate limits
- **Cache**: In-memory, configurable TTL
- **Pagination**: Support for 1000+ results
- **Memory**: ~5-10MB per 1000 papers

## Testing Strategy

```python
# Unit tests
test_paper_parsing()
test_gap_identification()
test_report_generation()

# Integration tests
test_openalex_integration()
test_arxiv_integration()

# End-to-end tests
test_full_search_pipeline()
```

## Monitoring & Logging

Each agent logs:
- API call counts and timing
- Error rates and types
- Cache hit rates
- Processing times

```python
logger.info(f"Found {len(papers)} papers for '{query}'")
logger.debug(f"OpenAlex: {openalex_count}, arXiv: {arxiv_count}")
logger.error(f"API Error: {error_details}")
```

## Future Architecture Enhancements

1. **Agent Communication**: Inter-agent messaging
2. **Workflow Orchestration**: DAG-based research pipelines
3. **Distributed Execution**: Multi-machine agent deployment
4. **Learning**: Agent improvement over time
5. **Persistence**: Database storage for long-term analysis
6. **API Gateway**: Unified interface for all agents

---

This architecture supports rapid expansion from 1 specialist agent to a full multi-agent research assistant.
