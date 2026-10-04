# Report Agent 📝

**Status**: ✅ **LIVE with Claude Haiku 4.5**

The Report Agent synthesizes Mycobacterium tuberculosis findings into publication-ready research papers. Uses Claude Haiku to generate APA-formatted papers with proper structure (Abstract, Methods, Results, Discussion, Conclusion). Includes citations, figures/tables, and knowledge graph exports for BSL-3 Mtb assay results.

## Features

### 📄 Paper Generation
- **Structured Paper Sections**: Abstract, Introduction, Methodology, Results, Discussion, Conclusion
- **Professional Content**: Auto-generated based on analysis and hypothesis
- **Citation Management**: Automatic citation extraction and formatting
- **Metadata**: Title, authors, keywords, word count
- **Quality Writing**: Clear, accurate, professional scientific writing

### 📚 Citation Management
- **Multiple Formats**: APA, Chicago, Harvard, MLA
- **Citation Extraction**: From literature and methodology
- **In-text Formatting**: Paraphrases and direct quotes
- **BibTeX Export**: For citation managers
- **DOI/URL Linking**: Proper reference linking

### 📊 Figure & Table Planning
- **Figure Specifications**: 
  * Descriptive (bar, box, scatter plots)
  * Inferential (confidence intervals, forest plots)
  * Comparative (group comparisons, time series)
  * Data visualization (heatmaps, networks)

- **Table Specifications**:
  * Descriptive statistics
  * Results tables
  * Correlation matrices
  * Model comparisons

- **Comprehensive Captions**: Clear, informative captions with recommendations

### 🗂️ Output Formats
- **Markdown**: For version control and collaboration
- **HTML**: Interactive, web-ready version
- **JSON**: Structured data for processing
- **BibTeX**: Citation library format
- **PDF** (planned): Professional print-ready

### 🧠 Knowledge Graph Export
- **Entity Representation**: Research questions, hypotheses, findings, mechanisms
- **Relationships**: Addresses, tests, supports, contradicts, enables
- **RDF/Turtle/JSON-LD**: Multiple export formats
- **Semantic Linking**: Connects research components
- **Cytoscape Format**: For visualization

### 📋 Supplementary Materials
- **Raw Data**: Anonymized datasets
- **Analysis Code**: Reproducible scripts
- **Extended Analyses**: Additional figures and tables
- **Protocols**: Detailed methodological protocols
- **Instruments**: Questionnaires and measurement scales

## Installation

```bash
# Dependencies already included
pip install -r ../../requirements.txt
```

## Usage

### Basic Paper Generation

```python
import asyncio
from agents.report_agent import ReportAgent

async def generate_paper():
    agent = ReportAgent()
    
    hypothesis = {
        "title": "Your research hypothesis",
        "statement": "If X then Y",
        "background": "Context for the research",
    }
    
    literature = [
        {
            "title": "Related work",
            "authors": ["Author"],
            "publication_year": 2023,
        }
    ]
    
    analysis = {
        "interpretation": {"hypothesis_confirmed": True},
        "primary_finding": {"effect_size": 0.65},
        "implications": {
            "theoretical": ["Theory advances"],
            "practical": ["Real-world applications"],
            "limitations": ["Study constraints"],
            "future_directions": ["Next steps"],
        },
    }
    
    design = {
        "experiment_type": "randomized_controlled_trial",
        "sample_size": 120,
        "sample_characteristics": ["adult participants"],
        "primary_measures": [{"name": "Outcome"}],
        "procedures": [{"description": "Study procedure"}],
        "analysis_plan": "t-tests comparing groups",
    }
    
    paper = await agent.generate_paper(
        hypothesis, literature, analysis, design
    )
    
    print(f"Paper: {paper.title}")
    print(f"Word count: {paper.word_count}")
    
    await agent.close()

asyncio.run(generate_paper())
```

### Export to Different Formats

```python
from agents.report_agent import OutputFormat

# Export to Markdown
markdown = await agent.export_paper(paper, OutputFormat.MARKDOWN)
with open("paper.md", "w") as f:
    f.write(markdown)

# Export to JSON
json_data = await agent.export_paper(paper, OutputFormat.JSON)
with open("paper.json", "w") as f:
    f.write(json_data)

# Export citations to BibTeX
bibtex = await agent.export_paper(paper, OutputFormat.BIBTEX)
with open("references.bib", "w") as f:
    f.write(bibtex)
```

### Access Paper Components

```python
# Title and metadata
print(f"Title: {paper.title}")
print(f"Authors: {', '.join(paper.authors)}")
print(f"Keywords: {', '.join(paper.keywords)}")

# Main sections
print(f"Abstract: {paper.abstract[:100]}...")
print(f"Introduction: {paper.introduction[:100]}...")

# Supporting materials
print(f"Figures: {len(paper.figures)}")
for fig in paper.figures:
    print(f"  Figure {fig.number}: {fig.title}")

print(f"Tables: {len(paper.tables)}")
for table in paper.tables:
    print(f"  Table {table.number}: {table.title}")

print(f"References: {len(paper.citations)}")

# Supplementary
for material, description in paper.supplementary_materials.items():
    print(f"  {material}: {description}")
```

### Access Knowledge Graph

```python
kg = paper.knowledge_graph_export

# Entities
for entity_id, entity in kg["entities"].items():
    print(f"{entity['label']} ({entity['type']})")

# Relationships
for rel in kg["relationships"]:
    print(f"{rel['source']} --{rel['relation']}--> {rel['target']}")

# Properties
for entity, props in kg["properties"].items():
    print(f"{entity}: confidence={props.get('confidence')}")
```

## Paper Structure

### Abstract
- **Length**: 250 words max
- **Elements**: Background, objective, method, results, conclusions
- **Purpose**: Standalone summary of entire study

### Introduction
- **Purpose**: Establish context and motivation
- **Typical length**: 800-1500 words
- **Elements**: Background, literature review, gaps, research question, hypothesis, significance

### Methodology
- **Purpose**: Enable replication
- **Typical length**: 1000-2000 words
- **Elements**: Design rationale, sample, measures, procedures, analysis plan

### Results
- **Purpose**: Present findings objectively
- **Typical length**: 1000-1500 words
- **Elements**: Sample description, preliminary analyses, primary results, effect sizes, secondary findings

### Discussion
- **Purpose**: Interpret and contextualize
- **Typical length**: 1500-2500 words
- **Elements**: Summary, literature comparison, implications, limitations, future research

### Conclusion
- **Purpose**: Synthesize key takeaways
- **Typical length**: 200-400 words
- **Elements**: Key findings, broader significance, next steps

## Citation Formats

### APA 7th Edition Example
```
Vaswani, A., Shazeer, N., et al. (2017). Attention is all you need. 
Advances in Neural Information Processing Systems. 
https://doi.org/10.5555/3295222.3295349
```

### BibTeX Example
```bibtex
@article{Vaswani2017,
  author = {Vaswani, A. and Shazeer, N.},
  year = {2017},
  title = {Attention is All You Need},
  journal = {NIPS},
  doi = {10.5555/3295222.3295349}
}
```

## Figure Types

| Type | Purpose | Example |
|------|---------|---------|
| **Bar Plot** | Compare means | Group treatment effects |
| **Box Plot** | Show distributions | Outcome variability |
| **Scatter Plot** | Show relationships | Correlation between variables |
| **Forest Plot** | Effect size comparison | Multiple studies meta-analysis |
| **Time Series** | Track trends | Longitudinal outcomes |
| **Heatmap** | Show patterns | Correlation matrices |

## Table Types

| Type | Purpose | Example |
|------|---------|---------|
| **Descriptive Stats** | Sample summary | Demographics, baseline measures |
| **Results Table** | Primary findings | Means, SDs, test statistics |
| **Correlation Matrix** | Variable relationships | Intercorrelations |
| **Model Comparisons** | Compare models | R², parameters, fit indices |
| **Subgroup Analyses** | Stratified results | Results by group |

## Knowledge Graph Export

### Entities
- Research question
- Hypothesis
- Methodology
- Finding
- Evidence
- Mechanism
- Boundary condition
- Implication
- Future direction

### Relationships
- **addresses**: Hypothesis addresses gap
- **tested_by**: Finding tests hypothesis
- **supports**: Evidence supports finding
- **contradicts**: Finding contradicts theory
- **enables**: Finding enables future work
- **qualifies**: Boundary condition qualifies finding
- **implies**: Finding implies application
- **extends**: Work extends theory

### Export Formats
- **RDF/XML**: For semantic web
- **Turtle**: Compact RDF format
- **JSON-LD**: JSON-linked data
- **Cytoscape JSON**: For visualization

## Submission Ready Outputs

### Hackathon Submission
- Format: PDF
- Length: 20 pages max
- Sections: Abstract, methods, results, discussion
- Supplementary: Code and data
- Ready: All materials included

### Journal Publication
- Format: Manuscript
- Length: 8,000 words
- Sections: Complete paper
- References: Extensive
- Figures: 4-6 publication-ready

### Conference Paper
- Format: Camera-ready
- Length: 8 pages
- Sections: Core results
- Figures: 2-4 diagrams
- Style: ACM or IEEE proceedings

## Running Examples

```bash
# Run all examples
python agents/report_agent/examples.py

# Run specific example
python -c "
import asyncio
from agents.report_agent.examples import example_1_basic_paper_generation
asyncio.run(example_1_basic_paper_generation())
"
```

## Configuration

Edit `config.yaml` to customize:

**Paper length**:
```yaml
paper_structure:
  main_sections:
    introduction:
      typical_length: 1200  # words
```

**Citation style**:
```yaml
citation_management:
  styles:
    apa:
      version: 7th edition
```

**Output options**:
```yaml
output_formats:
  - markdown
  - html
  - json
```

## Troubleshooting

### Paper seems too short
- Check if all sections are being generated
- Verify analysis includes sufficient detail
- Expand methodology and discussion sections

### Citations not formatting correctly
- Ensure authors list is properly formatted
- Check DOI and URL are included
- Verify year and publication details

### Knowledge graph export empty
- Confirm analysis report includes findings
- Check entity extraction is working
- Verify relationships are properly defined

## Advanced Features

### Custom Paper Templates
```python
class CustomReportAgent(ReportAgent):
    def _generate_introduction(self, hypothesis, literature):
        # Custom introduction logic
        return custom_intro
```

### Integration with Publication Platforms
- Export directly to Overleaf
- Submit to bioRxiv/arXiv
- Format for specific journals

### Citation Cross-Referencing
- Automatic figure/table citations
- Reference numbering
- In-text citation formatting

## Integration with Other Agents

### Input from Analysis Agent
```python
report = await analysis_agent.analyze_results(...)
paper = await report_agent.generate_paper(
    hypothesis, literature, report.to_dict(), design
)
```

### Full Pipeline
```
Literature → Hypothesis → Experiment → Analysis → Report
```

## Output Examples

### Generated Title
"Evidence for Neural Network Optimization Through Curriculum Learning: A Randomized Controlled Trial"

### Generated Abstract
"Background: Training neural networks often proceeds inefficiently with random curriculum. Objective: To test whether structured curriculum learning improves training efficiency. Method: Randomized trial with 120 computer vision tasks assigned to curriculum or control conditions. Results: Curriculum learning significantly improved efficiency (d = 0.72, 95% CI [0.45, 0.98], p = .001). Conclusions: Structured curriculum learning provides a practical method for accelerating training."

## Future Enhancements

- [ ] PDF generation with professional formatting
- [ ] LaTeX export for journals
- [ ] Interactive HTML with live citations
- [ ] Automatic figure generation from data
- [ ] Multi-language support
- [ ] Journal-specific templates
- [ ] Plagiarism detection
- [ ] Accessibility features (WCAG)

## References

- APA Publication Manual (7th ed.)
- Strunk & White: The Elements of Style
- Pinker: The Sense of Style
- Chicago Manual of Style

---

Built for Phase 5 of Agentic Scientific Discovery Lab 🚀

**The Final Phase**: From Research Question to Publication!
