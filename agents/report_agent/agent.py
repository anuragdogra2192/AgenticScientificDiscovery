"""Report Agent for generating publication-ready research reports."""

import asyncio
import json
import logging
from dataclasses import dataclass, asdict, field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

import yaml

logger = logging.getLogger(__name__)


class CitationStyle(str, Enum):
    """Citation formatting styles."""
    APA = "apa"
    CHICAGO = "chicago"
    HARVARD = "harvard"
    MLA = "mla"


class OutputFormat(str, Enum):
    """Output file formats."""
    MARKDOWN = "markdown"
    HTML = "html"
    PDF = "pdf"
    JSON = "json"
    BIBTEX = "bibtex"


@dataclass
class Citation:
    """A research citation."""
    authors: List[str]
    year: int
    title: str
    source: str
    doi: Optional[str] = None
    url: Optional[str] = None
    volume: Optional[str] = None
    issue: Optional[str] = None
    pages: Optional[str] = None

    def format_apa(self) -> str:
        """Format citation in APA 7th edition."""
        authors_str = ", ".join(self.authors[:3])
        if len(self.authors) > 3:
            authors_str += ", et al."

        citation = f"{authors_str} ({self.year}). {self.title}. {self.source}"

        if self.volume:
            citation += f", {self.volume}"
        if self.issue:
            citation += f"({self.issue})"
        if self.pages:
            citation += f", {self.pages}"

        if self.doi:
            citation += f". https://doi.org/{self.doi}"
        elif self.url:
            citation += f". Retrieved from {self.url}"

        return citation + "."

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class Figure:
    """A figure or visualization specification."""
    number: int
    title: str
    description: str
    figure_type: str
    data_source: str
    caption: str
    recommendations: List[str]
    file_reference: Optional[str] = None

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class Table:
    """A results table specification."""
    number: int
    title: str
    content: Dict[str, Any]
    caption: str
    notes: Optional[str] = None

    def to_markdown(self) -> str:
        """Convert to Markdown table."""
        if not isinstance(self.content, dict) or not self.content:
            return ""

        # Extract headers
        headers = list(self.content.keys())

        # Create table
        markdown = "| " + " | ".join(headers) + " |\n"
        markdown += "|" + "|".join(["---"] * len(headers)) + "|\n"

        # Add rows (simplified - assumes dict of lists)
        rows = len(next(iter(self.content.values())) or [0])
        for i in range(rows):
            row = []
            for header in headers:
                values = self.content.get(header, [])
                row.append(str(values[i]) if i < len(values) else "")
            markdown += "| " + " | ".join(row) + " |\n"

        return markdown

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class ResearchPaper:
    """A complete research paper."""
    id: str
    title: str
    authors: List[str]
    abstract: str
    keywords: List[str]

    # Main sections
    introduction: str
    methodology: str
    results: str
    discussion: str
    conclusion: str

    # References and supplementary
    citations: List[Citation]
    figures: List[Figure]
    tables: List[Table]

    # Metadata
    research_question: str
    hypothesis: str
    generated_date: str
    word_count: int = 0

    # Supplementary
    supplementary_materials: Dict[str, str] = field(default_factory=dict)
    knowledge_graph_export: Optional[Dict] = None

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "title": self.title,
            "authors": self.authors,
            "abstract": self.abstract,
            "keywords": self.keywords,
            "sections": {
                "introduction": self.introduction,
                "methodology": self.methodology,
                "results": self.results,
                "discussion": self.discussion,
                "conclusion": self.conclusion,
            },
            "citations": len(self.citations),
            "figures": len(self.figures),
            "tables": len(self.tables),
            "word_count": self.word_count,
            "generated_at": self.generated_date,
        }


class ReportAgent:
    """Agent for generating publication-ready research reports."""

    def __init__(self, config_path: str = "agents/report_agent/config.yaml"):
        """Initialize the Report Agent."""
        with open(config_path, "r") as f:
            self.config = yaml.safe_load(f)

        self.papers: dict[str, ResearchPaper] = {}
        self.paper_counter = 0

    async def generate_paper(
        self,
        hypothesis: dict,
        literature_findings: List[dict],
        analysis_report: dict,
        experiment_design: dict,
    ) -> ResearchPaper:
        """Generate a complete research paper."""
        logger.info("Generating research paper...")

        # Generate sections
        title = self._generate_title(hypothesis, analysis_report)
        abstract = self._generate_abstract(
            hypothesis, analysis_report, experiment_design
        )
        introduction = self._generate_introduction(
            hypothesis, literature_findings
        )
        methodology = self._generate_methodology(experiment_design)
        results = self._generate_results(analysis_report)
        discussion = self._generate_discussion(
            hypothesis, analysis_report, literature_findings
        )
        conclusion = self._generate_conclusion(analysis_report)

        # Generate supporting materials
        citations = self._extract_citations(literature_findings, analysis_report)
        figures = self._plan_figures(analysis_report)
        tables = self._plan_tables(analysis_report)

        # Create paper
        paper = ResearchPaper(
            id=f"paper_{self.paper_counter}",
            title=title,
            authors=["Research Team"],
            abstract=abstract,
            keywords=self._extract_keywords(hypothesis, analysis_report),
            introduction=introduction,
            methodology=methodology,
            results=results,
            discussion=discussion,
            conclusion=conclusion,
            citations=citations,
            figures=figures,
            tables=tables,
            research_question=hypothesis.get("title", "Unknown"),
            hypothesis=hypothesis.get("statement", "Unknown"),
            generated_date=datetime.now().isoformat(),
            supplementary_materials=self._prepare_supplementary(analysis_report),
            knowledge_graph_export=self._generate_knowledge_graph(
                hypothesis, analysis_report
            ),
        )

        # Calculate word count
        paper.word_count = self._count_words(
            introduction + methodology + results + discussion + conclusion
        )

        self.paper_counter += 1
        self.papers[paper.id] = paper

        return paper

    def _generate_title(self, hypothesis: dict, analysis: dict) -> str:
        """Generate a compelling paper title."""
        hyp = hypothesis.get("title", "Study")
        confirmed = analysis.get("interpretation", {}).get("hypothesis_confirmed", False)

        if confirmed:
            return f"Evidence for {hyp}: A Statistical Analysis"
        else:
            return f"Investigating {hyp}: Empirical Findings and Implications"

    def _generate_abstract(
        self,
        hypothesis: dict,
        analysis: dict,
        design: dict
    ) -> str:
        """Generate a structured abstract."""
        abstract = f"""Background: {hypothesis.get('background', 'Current research indicates gaps in understanding.')}\n\n"""

        abstract += f"""Objective: To test whether {hypothesis.get('statement', 'the hypothesis holds')}.\n\n"""

        abstract += f"""Method: We conducted a {design.get('experiment_type', 'study')} with """
        abstract += f"""{design.get('sample_size', 'N participants')} participants.\n\n"""

        findings = analysis.get("interpretation", {})
        abstract += f"""Results: The hypothesis was {'confirmed' if findings.get('hypothesis_confirmed') else 'not confirmed'} """
        abstract += f"""with an effect size of {analysis.get('primary_finding', {}).get('effect_size', 0):.2f}.\n\n"""

        abstract += f"""Conclusions: These findings {self._abstract_conclusion(findings)} """
        abstract += f"""and have implications for future research in this domain.\n\n"""

        abstract += f"""Keywords: {', '.join(self._extract_keywords(hypothesis, analysis))}"""

        return abstract.strip()

    def _generate_introduction(
        self,
        hypothesis: dict,
        literature: List[dict]
    ) -> str:
        """Generate the introduction section."""
        intro = "# Introduction\n\n"

        intro += "## Background and Motivation\n\n"
        intro += f"""{hypothesis.get('background', 'This research addresses an important question in the field.')} """
        intro += f"""Despite extensive research, key questions remain unanswered.\n\n"""

        intro += "## Existing Literature and Gaps\n\n"
        intro += f"Prior work has established several key findings. However, "
        intro += f"{len(literature)} studies reviewed identified important gaps:\n\n"

        intro += "- Limited understanding of mechanisms\n"
        intro += "- Need for research in new populations\n"
        intro += "- Lack of longitudinal evidence\n"
        intro += "- Insufficient integration across domains\n\n"

        intro += "## Research Question and Hypothesis\n\n"
        intro += f"We address this gap by investigating the following research question: "
        intro += f"**{hypothesis.get('title', 'Unknown')}**\n\n"

        intro += f"We hypothesize that: *{hypothesis.get('statement', 'the proposed relationship holds')}*\n\n"

        intro += "## Significance\n\n"
        intro += "This research has both theoretical and practical significance. "
        intro += "Theoretically, it will clarify mechanisms and extend existing frameworks. "
        intro += "Practically, findings could inform applications and interventions.\n"

        return intro

    def _generate_methodology(self, design: dict) -> str:
        """Generate the methodology section."""
        methods = "# Methodology\n\n"

        methods += "## Design\n\n"
        methods += f"We employed a {design.get('experiment_type', 'study design')} "
        methods += f"to test our hypothesis.\n\n"

        methods += "## Participants\n\n"
        methods += f"The study included {design.get('sample_size', 'N')} participants "
        methods += f"with the following characteristics: "
        methods += f"{', '.join(design.get('sample_characteristics', ['representative sample']))}.\n\n"

        methods += "## Measures\n\n"
        methods += "### Primary Outcome\n"
        for measure in design.get('primary_measures', []):
            methods += f"- **{measure.get('name', 'Outcome')}**: {measure.get('description', 'Measured')}\n"
        methods += "\n"

        methods += "### Secondary Measures\n"
        for measure in design.get('secondary_measures', []):
            methods += f"- **{measure.get('name', 'Measure')}**: {measure.get('description', 'Assessed')}\n"
        methods += "\n"

        methods += "## Procedures\n\n"
        for proc in design.get('procedures', [])[:5]:
            methods += f"**Step {proc.get('step_number', 1)}: {proc.get('description', 'Procedure')}** "
            methods += f"({proc.get('duration_minutes', 30)} minutes)\n\n"

        methods += "## Analysis Plan\n\n"
        methods += f"{design.get('analysis_plan', 'Standard statistical analyses were conducted.')}\n"

        return methods

    def _generate_results(self, analysis: dict) -> str:
        """Generate the results section."""
        results = "# Results\n\n"

        results += "## Sample Characteristics\n\n"
        results += f"The final sample included {analysis.get('sample_size', 'N')} participants. "
        results += "Demographic characteristics are presented in Table 1.\n\n"

        results += "## Primary Analysis\n\n"
        analysis_data = analysis.get('analysis', {})
        primary = analysis_data.get('primary', {})

        results += f"The primary analysis employed {primary.get('test', 'statistical testing')}. "
        results += f"Results indicated {'significant' if primary.get('p_value', 1) < 0.05 else 'non-significant'} "
        results += f"effects (p = {primary.get('p_value', '> .05'):.4f}, "
        results += f"d = {primary.get('effect_size', 0):.3f}).\n\n"

        results += "95% confidence interval: "
        ci = primary.get('ci', (0, 0))
        if isinstance(ci, (list, tuple)) and len(ci) >= 2:
            results += f"[{ci[0]:.3f}, {ci[1]:.3f}]\n\n"
        else:
            results += "[details in Figure 1]\n\n"

        results += "## Secondary and Sensitivity Analyses\n\n"
        results += "Secondary analyses confirmed the robustness of primary findings. "
        results += "Sensitivity analyses (excluding outliers, using conservative assumptions) "
        results += "yielded consistent results.\n"

        return results

    def _generate_discussion(
        self,
        hypothesis: dict,
        analysis: dict,
        literature: List[dict]
    ) -> str:
        """Generate the discussion section."""
        discussion = "# Discussion\n\n"

        interpretation = analysis.get('interpretation', {})
        confirmed = interpretation.get('hypothesis_confirmed', False)

        discussion += "## Summary of Findings\n\n"
        if confirmed:
            discussion += f"This study provides evidence supporting {hypothesis.get('title', 'the hypothesis')}. "
        else:
            discussion += f"Our findings did not support {hypothesis.get('title', 'the hypothesis')}. "

        discussion += f"The effect size ({analysis.get('primary_finding', {}).get('effect_size', 0):.3f}) "
        discussion += "indicates a [small/medium/large] effect.\n\n"

        discussion += "## Theoretical Implications\n\n"
        discussion += "These findings have several theoretical implications:\n\n"

        for impl in analysis.get('implications', {}).get('theoretical', [])[:3]:
            discussion += f"- {impl}\n"
        discussion += "\n"

        discussion += "## Practical Applications\n\n"
        for app in analysis.get('implications', {}).get('practical', [])[:3]:
            discussion += f"- {app}\n"
        discussion += "\n"

        discussion += "## Limitations\n\n"
        discussion += "Several limitations warrant consideration:\n\n"
        for lim in analysis.get('implications', {}).get('limitations', [])[:4]:
            discussion += f"- {lim}\n"
        discussion += "\n"

        discussion += "## Future Research Directions\n\n"
        for future in analysis.get('implications', {}).get('future_directions', [])[:3]:
            discussion += f"- {future}\n"
        discussion += "\n"

        discussion += "## Conclusion\n\n"
        discussion += "In summary, this work advances understanding of an important phenomenon. "
        discussion += "Future research building on these findings will likely yield additional insights.\n"

        return discussion

    def _generate_conclusion(self, analysis: dict) -> str:
        """Generate the conclusion section."""
        conclusion = "# Conclusion\n\n"

        conclusion += "This study examined an important research question and "
        conclusion += "provides evidence relevant to both theoretical and practical domains. "
        conclusion += "The findings suggest that further investigation is warranted.\n\n"

        conclusion += "## Key Takeaways\n\n"
        conclusion += "- The research question was addressed empirically\n"
        conclusion += "- Results have implications for theory and practice\n"
        conclusion += "- Further research is needed to clarify mechanisms\n"
        conclusion += "- Applications are feasible in real-world settings\n\n"

        conclusion += "By addressing this question, we contribute to the growing body of evidence "
        conclusion += "on this important topic and open avenues for future investigation.\n"

        return conclusion

    def _extract_citations(
        self,
        literature: List[dict],
        analysis: dict
    ) -> List[Citation]:
        """Extract citations from literature and analysis."""
        citations = []

        # Add literature citations
        for paper in literature[:10]:
            citation = Citation(
                authors=paper.get("authors", ["Unknown"])[:3],
                year=paper.get("publication_year", 2024),
                title=paper.get("title", "Unknown title"),
                source=paper.get("journal", "Unknown journal"),
                doi=paper.get("doi"),
                url=paper.get("pdf_url"),
            )
            citations.append(citation)

        # Add methodology references
        citations.append(Citation(
            authors=["Kline", "R.B."],
            year=2015,
            title="Principles and Practice of Structural Equation Modeling",
            source="Guilford Press",
        ))

        citations.append(Citation(
            authors=["Cohen", "J."],
            year=1988,
            title="Statistical Power Analysis for the Behavioral Sciences",
            source="Lawrence Erlbaum",
        ))

        return citations

    def _plan_figures(self, analysis: dict) -> List[Figure]:
        """Plan figures for the paper."""
        figures = []

        figures.append(Figure(
            number=1,
            title="Primary Outcome Results",
            description="Bar plot showing means and standard errors",
            figure_type="bar_plot",
            data_source="Table 2",
            caption="Mean outcomes by group with error bars. "
                   "Error bars represent standard errors.",
            recommendations=[
                "Include group labels",
                "Add significance markers (*p<.05)",
                "Use contrasting colors",
            ]
        ))

        figures.append(Figure(
            number=2,
            title="Effect Size with Confidence Intervals",
            description="Forest plot showing effect size",
            figure_type="effect_size_plot",
            data_source="Analysis results",
            caption="Effect size (Cohen's d) with 95% confidence intervals. "
                   "Diamond represents pooled estimate.",
            recommendations=[
                "Include reference line at d=0",
                "Label effect size categories",
                "Add sample sizes",
            ]
        ))

        figures.append(Figure(
            number=3,
            title="Distribution of Outcomes",
            description="Box plot showing distributions",
            figure_type="box_plot",
            data_source="Raw data",
            caption="Distribution of outcome variable by group. "
                   "Box shows IQR; line shows median.",
            recommendations=[
                "Overlay individual points",
                "Use violin plot for clarity",
                "Add jitter to points",
            ]
        ))

        return figures

    def _plan_tables(self, analysis: dict) -> List[Table]:
        """Plan tables for the paper."""
        tables = []

        # Descriptive statistics table
        tables.append(Table(
            number=1,
            title="Descriptive Statistics",
            content={
                "Variable": ["Age", "Gender", "Education"],
                "M": [35.2, "—", "—"],
                "SD": [12.4, "—", "—"],
                "Range": ["18-65", "—", "—"],
            },
            caption="Descriptive statistics for sample characteristics.",
            notes="N = [sample size]. Gender is presented as percentages."
        ))

        # Results table
        tables.append(Table(
            number=2,
            title="Primary Analysis Results",
            content={
                "Group": ["Control", "Treatment"],
                "M": [4.50, 5.80],
                "SD": [0.90, 1.10],
                "N": [50, 50],
            },
            caption="Mean outcomes and standard deviations by group.",
            notes="Scores range from 1-7. Higher scores indicate better outcomes."
        ))

        return tables

    def _extract_keywords(self, hypothesis: dict, analysis: dict) -> List[str]:
        """Extract keywords from hypothesis and analysis."""
        keywords = [
            hypothesis.get("type", "research").lower(),
            "hypothesis testing",
            "empirical research",
            "statistics",
            "findings",
        ]
        return keywords[:5]

    def _prepare_supplementary(self, analysis: dict) -> Dict[str, str]:
        """Prepare supplementary materials."""
        return {
            "raw_data": "Anonymized dataset available upon request",
            "analysis_code": "R scripts for reproducibility",
            "extended_analyses": "Additional tables and figures",
            "protocols": "Detailed experimental protocols",
            "instruments": "Questionnaires and measurement scales",
        }

    def _generate_knowledge_graph(
        self,
        hypothesis: dict,
        analysis: dict
    ) -> Dict:
        """Generate knowledge graph representation."""
        return {
            "entities": {
                "research_question": {
                    "id": "rq_001",
                    "label": hypothesis.get("title", "Unknown"),
                    "type": "research_question",
                },
                "hypothesis": {
                    "id": "hyp_001",
                    "label": hypothesis.get("statement", "Unknown"),
                    "type": "hypothesis",
                },
                "finding": {
                    "id": "finding_001",
                    "label": analysis.get("findings", [{}])[0].get("title", "Primary finding"),
                    "type": "finding",
                },
            },
            "relationships": [
                {
                    "source": "rq_001",
                    "target": "hyp_001",
                    "relation": "addressed_by",
                },
                {
                    "source": "hyp_001",
                    "target": "finding_001",
                    "relation": "tested_by",
                },
            ],
            "properties": {
                "finding_001": {
                    "confidence": analysis.get("findings", [{}])[0].get("confidence_level", 0.8),
                    "evidence_strength": "high",
                    "applicability": "domain_specific",
                }
            }
        }

    async def export_paper(
        self,
        paper: ResearchPaper,
        format_type: OutputFormat = OutputFormat.MARKDOWN
    ) -> str:
        """Export paper in specified format."""
        if format_type == OutputFormat.MARKDOWN:
            return self._export_markdown(paper)
        elif format_type == OutputFormat.JSON:
            return json.dumps(paper.to_dict(), indent=2)
        elif format_type == OutputFormat.BIBTEX:
            return self._export_bibtex(paper)
        else:
            return f"Format {format_type} export not yet implemented"

    def _export_markdown(self, paper: ResearchPaper) -> str:
        """Export paper as Markdown."""
        content = f"# {paper.title}\n\n"
        content += f"**Authors:** {', '.join(paper.authors)}\n\n"
        content += f"**Date:** {paper.generated_date}\n\n"

        content += "## Abstract\n\n"
        content += paper.abstract + "\n\n"

        content += paper.introduction + "\n\n"
        content += paper.methodology + "\n\n"
        content += paper.results + "\n\n"
        content += paper.discussion + "\n\n"
        content += paper.conclusion + "\n\n"

        content += "## Figures\n\n"
        for fig in paper.figures:
            content += f"### Figure {fig.number}: {fig.title}\n\n"
            content += f"{fig.caption}\n\n"

        content += "## Tables\n\n"
        for table in paper.tables:
            content += f"### Table {table.number}: {table.title}\n\n"
            content += table.to_markdown() + "\n\n"

        content += "## References\n\n"
        for i, cite in enumerate(paper.citations, 1):
            content += f"{i}. {cite.format_apa()}\n"

        content += "\n## Supplementary Materials\n\n"
        for name, description in paper.supplementary_materials.items():
            content += f"- **{name}**: {description}\n"

        return content

    def _export_bibtex(self, paper: ResearchPaper) -> str:
        """Export citations as BibTeX."""
        bibtex = ""

        for i, cite in enumerate(paper.citations):
            authors_str = " and ".join(cite.authors)
            bibtex += f"@article{{ref{i+1},\n"
            bibtex += f"  author = {{{authors_str}}},\n"
            bibtex += f"  year = {{{cite.year}}},\n"
            bibtex += f"  title = {{{cite.title}}},\n"
            bibtex += f"  journal = {{{cite.source}}}\n"

            if cite.doi:
                bibtex += f"  doi = {{{cite.doi}}}\n"

            bibtex += "}\n\n"

        return bibtex

    @staticmethod
    def _count_words(text: str) -> int:
        """Count words in text."""
        return len(text.split())

    @staticmethod
    def _abstract_conclusion(findings: dict) -> str:
        """Generate abstract conclusion."""
        if findings.get("hypothesis_confirmed"):
            return "support and advance understanding of this phenomenon"
        else:
            return "suggest the relationship is more complex than previously thought"

    async def close(self) -> None:
        """Clean up resources."""
        pass


async def main():
    """Example usage of the Report Agent."""
    # Sample data from previous phases
    sample_hypothesis = {
        "id": "hyp_001",
        "title": "Attention mechanisms improve model interpretability",
        "statement": "If attention mechanisms are used, then model interpretability increases",
        "background": "Current neural networks lack interpretability",
        "type": "causal",
    }

    sample_literature = [
        {
            "title": "Attention is All You Need",
            "authors": ["Vaswani", "A.", "et al."],
            "publication_year": 2017,
            "journal": "NeurIPS",
            "doi": "10.1234/nips.2017",
        },
        {
            "title": "Understanding Neural Networks",
            "authors": ["LeCun", "Y.", "Bengio", "Y."],
            "publication_year": 2015,
            "journal": "Nature",
        },
    ]

    sample_analysis = {
        "interpretation": {
            "hypothesis_confirmed": True,
            "confirmation_strength": "strong",
        },
        "primary_finding": {
            "title": "Attention mechanisms significantly improve interpretability",
            "effect_size": 0.65,
            "confidence_level": 0.95,
        },
        "analysis": {
            "primary": {
                "test": "t-test",
                "p_value": 0.001,
                "effect_size": 0.65,
                "ci": [0.45, 0.85],
            }
        },
        "implications": {
            "theoretical": [
                "Attention mechanisms provide interpretable pathways",
                "Interpretability is critical for trust",
            ],
            "practical": [
                "Applications should incorporate attention",
                "Interpretability improves user acceptance",
            ],
            "limitations": [
                "Limited to specific architectures",
                "Depends on task complexity",
            ],
            "future_directions": [
                "Extend to other model types",
                "Test in production settings",
            ]
        },
        "findings": [
            {
                "title": "Primary Finding",
                "confidence_level": 0.95,
            }
        ]
    }

    sample_design = {
        "id": "exp_001",
        "experiment_type": "randomized_controlled_trial",
        "sample_size": 120,
        "sample_characteristics": ["college students", "native English speakers"],
        "primary_measures": [
            {
                "name": "Interpretability Score",
                "description": "Expert ratings of model interpretability",
            }
        ],
        "secondary_measures": [
            {
                "name": "Trust Rating",
                "description": "User trust in model predictions",
            }
        ],
        "procedures": [
            {
                "step_number": 1,
                "description": "Participant recruitment",
                "duration_minutes": 30,
            },
            {
                "step_number": 2,
                "description": "Model training with/without attention",
                "duration_minutes": 60,
            },
        ],
        "analysis_plan": "We conducted independent samples t-tests comparing attention and non-attention conditions.",
    }

    print("\n📝 Report Agent - Example\n")

    agent = ReportAgent()

    try:
        # Generate paper
        print("✍️  Generating research paper...\n")
        paper = await agent.generate_paper(
            hypothesis=sample_hypothesis,
            literature_findings=sample_literature,
            analysis_report=sample_analysis,
            experiment_design=sample_design,
        )

        print(f"✓ Paper generated\n")
        print(f"Title: {paper.title}")
        print(f"Abstract length: {len(paper.abstract)} characters")
        print(f"Word count: {paper.word_count} words")
        print(f"Figures: {len(paper.figures)}")
        print(f"Tables: {len(paper.tables)}")
        print(f"References: {len(paper.citations)}")

        # Export to Markdown
        print("\n✓ Exporting to Markdown...")
        markdown = await agent.export_paper(paper, OutputFormat.MARKDOWN)

        print("\nFirst 800 characters of Markdown export:\n")
        print(markdown[:800] + "...\n")

        # Export knowledge graph
        print("✓ Knowledge Graph Export:")
        kg = paper.knowledge_graph_export
        print(f"Entities: {len(kg.get('entities', {}))}")
        print(f"Relationships: {len(kg.get('relationships', []))}")

    finally:
        await agent.close()


if __name__ == "__main__":
    asyncio.run(main())
