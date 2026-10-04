"""Hypothesis Agent for generating testable scientific hypotheses."""

import asyncio
import json
import logging
import re
from dataclasses import dataclass, field, asdict
from typing import Optional, Callable
from enum import Enum
from datetime import datetime

import yaml

logger = logging.getLogger(__name__)


class HypothesisType(str, Enum):
    """Types of hypotheses."""
    CAUSAL = "causal"
    ASSOCIATIVE = "associative"
    COMPARATIVE = "comparative"
    MECHANISTIC = "mechanistic"
    PREDICTIVE = "predictive"
    BOUNDARY_CONDITION = "boundary_condition"
    META = "meta"


class ComplexityLevel(str, Enum):
    """Hypothesis complexity levels."""
    SIMPLE = "simple"
    MODERATE = "moderate"
    COMPLEX = "complex"


@dataclass
class Variable:
    """Represents a research variable."""
    name: str
    description: str
    measurement_method: str
    expected_range: Optional[str] = None
    unit: Optional[str] = None

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class Prediction:
    """Represents a specific, testable prediction."""
    statement: str
    measurable: bool
    success_criterion: str
    test_method: Optional[str] = None
    expected_effect_size: Optional[str] = None

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class Hypothesis:
    """Represents a testable scientific hypothesis."""
    id: str
    title: str
    statement: str
    background: str
    predictions: list[Prediction]
    hypothesis_type: HypothesisType
    complexity: ComplexityLevel

    # Variables
    independent_variables: list[Variable]
    dependent_variables: list[Variable]
    control_variables: list[Variable]

    # Assumptions and constraints
    assumptions: list[str]
    alternative_hypotheses: list[str]

    # Scoring
    novelty_score: float
    feasibility_score: float
    impact_score: float
    testability_score: float
    overall_score: float

    # Metadata
    related_papers: list[str]
    resources_needed: list[str]
    timeline_estimate: str
    risk_factors: list[str]
    generated_at: str

    # Source
    source_gaps: list[str] = field(default_factory=list)
    source_strategy: str = ""
    confidence: float = 0.8

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "title": self.title,
            "statement": self.statement,
            "background": self.background,
            "type": self.hypothesis_type.value,
            "complexity": self.complexity.value,
            "predictions": [p.to_dict() for p in self.predictions],
            "variables": {
                "independent": [v.to_dict() for v in self.independent_variables],
                "dependent": [v.to_dict() for v in self.dependent_variables],
                "control": [v.to_dict() for v in self.control_variables],
            },
            "assumptions": self.assumptions,
            "alternative_hypotheses": self.alternative_hypotheses,
            "scoring": {
                "novelty": self.novelty_score,
                "feasibility": self.feasibility_score,
                "impact": self.impact_score,
                "testability": self.testability_score,
                "overall": self.overall_score,
                "confidence": self.confidence,
            },
            "resources": self.resources_needed,
            "timeline": self.timeline_estimate,
            "risk_factors": self.risk_factors,
            "related_papers": self.related_papers[:5],
            "source": {
                "strategy": self.source_strategy,
                "gaps_addressed": self.source_gaps,
            },
            "generated_at": self.generated_at,
        }


class HypothesisAgent:
    """Agent for generating and ranking testable scientific hypotheses."""

    def __init__(self, config_path: str = "agents/hypothesis_agent/config.yaml"):
        """Initialize the Hypothesis Agent."""
        with open(config_path, "r") as f:
            self.config = yaml.safe_load(f)

        self.hypotheses: dict[str, Hypothesis] = {}
        self.concept_map: dict[str, list[str]] = {}
        self.hypothesis_counter = 0

    async def generate_hypotheses(
        self,
        papers: list,
        research_gaps: list,
        query: str,
        domain: Optional[str] = None,
    ) -> list[Hypothesis]:
        """Generate hypotheses from literature findings."""
        logger.info(f"Generating hypotheses for query: {query}")

        hypotheses = []

        # Build concept map from papers
        self._build_concept_map(papers)

        # Apply generation strategies
        strategies = self.config["generation_strategies"]

        # Gap-bridging hypotheses
        gap_hypotheses = await self._generate_gap_bridging(
            research_gaps, papers, query
        )
        hypotheses.extend(gap_hypotheses)

        # Trend-based hypotheses
        trend_hypotheses = await self._generate_trend_based(papers, query)
        hypotheses.extend(trend_hypotheses)

        # Cross-domain hypotheses
        cross_hypotheses = await self._generate_cross_domain(papers, query, domain)
        hypotheses.extend(cross_hypotheses)

        # Novel combination hypotheses
        combo_hypotheses = await self._generate_novel_combinations(papers, query)
        hypotheses.extend(combo_hypotheses)

        # Score and rank
        for hyp in hypotheses:
            self._score_hypothesis(hyp, papers)

        # Apply filters and sort
        hypotheses = self._filter_and_rank(hypotheses)

        logger.info(f"Generated {len(hypotheses)} hypotheses")
        return hypotheses

    async def _generate_gap_bridging(
        self,
        gaps: list,
        papers: list,
        query: str,
    ) -> list[Hypothesis]:
        """Generate hypotheses that address identified research gaps."""
        hypotheses = []

        for i, gap in enumerate(gaps[:5]):  # Use top 5 gaps
            gap_desc = gap.get("description", "")
            related_papers = gap.get("related_papers", [])

            # Create hypothesis from gap
            hypothesis = Hypothesis(
                id=f"gap_{i}_{self.hypothesis_counter}",
                title=f"Mechanism underlying {gap_desc.lower()}",
                statement=self._formalize_gap_hypothesis(gap_desc),
                background=f"Multiple papers indicate {gap_desc}. "
                           f"We propose a mechanism to explain this observation.",
                predictions=[
                    Prediction(
                        statement=f"If {gap_desc}, then we expect measurable change "
                                 f"in key variables",
                        measurable=True,
                        success_criterion="Statistically significant effect (p < 0.05)",
                    ),
                    Prediction(
                        statement="Effect size will vary by condition",
                        measurable=True,
                        success_criterion="Significant interaction effect detected",
                    ),
                ],
                hypothesis_type=HypothesisType.MECHANISTIC,
                complexity=ComplexityLevel.MODERATE,
                independent_variables=[
                    Variable(
                        name="primary_factor",
                        description=self._extract_factor(gap_desc),
                        measurement_method="Quantitative measurement",
                    ),
                ],
                dependent_variables=[
                    Variable(
                        name="outcome",
                        description="Resulting measurement or observation",
                        measurement_method="Quantitative or qualitative assessment",
                    ),
                ],
                control_variables=[
                    Variable(
                        name="confound_1",
                        description="Known confounding variable",
                        measurement_method="Monitoring/randomization",
                    ),
                ],
                assumptions=[
                    "Variables are independently measurable",
                    "Effect follows expected theoretical direction",
                    "No hidden confounding variables",
                ],
                alternative_hypotheses=[
                    "The gap is due to methodological differences",
                    "Effect is spurious correlation",
                    "Boundary conditions not yet identified",
                ],
                novelty_score=0.0,  # Will be scored later
                feasibility_score=0.0,
                impact_score=0.0,
                testability_score=0.0,
                overall_score=0.0,
                related_papers=related_papers,
                resources_needed=["Literature review", "Experimental design"],
                timeline_estimate="3-6 months",
                risk_factors=["Measurement validity", "Sample size requirements"],
                generated_at=datetime.now().isoformat(),
                source_gaps=[gap_desc],
                source_strategy="gap_bridging",
            )

            self.hypothesis_counter += 1
            hypotheses.append(hypothesis)

        return hypotheses

    async def _generate_trend_based(
        self,
        papers: list,
        query: str,
    ) -> list[Hypothesis]:
        """Generate hypotheses based on trends in the literature."""
        hypotheses = []

        # Analyze trends
        recent_papers = [p for p in papers if p.get("publication_year", 0) >= 2023]

        if len(recent_papers) > len(papers) * 0.3:  # Growing area
            hypothesis = Hypothesis(
                id=f"trend_growth_{self.hypothesis_counter}",
                title=f"Increasing research attention to {query} indicates paradigm shift",
                statement=f"The surge in {query} research reflects underlying "
                         f"theoretical or practical importance not yet captured "
                         f"by existing frameworks.",
                background=f"We observe {len(recent_papers)} recent papers on "
                           f"{query}, suggesting emerging importance.",
                predictions=[
                    Prediction(
                        statement="Novel methodological approaches will emerge",
                        measurable=True,
                        success_criterion="New methods reported in 2026",
                    ),
                    Prediction(
                        statement="Cross-disciplinary applications will increase",
                        measurable=True,
                        success_criterion="Papers from 3+ disciplines published",
                    ),
                ],
                hypothesis_type=HypothesisType.PREDICTIVE,
                complexity=ComplexityLevel.SIMPLE,
                independent_variables=[
                    Variable(
                        name="time",
                        description="Year of publication",
                        measurement_method="Temporal analysis",
                        unit="years",
                    ),
                ],
                dependent_variables=[
                    Variable(
                        name="research_volume",
                        description="Number of publications",
                        measurement_method="Database query count",
                    ),
                ],
                control_variables=[],
                assumptions=["Publishing trends reflect field importance"],
                alternative_hypotheses=["Interest is cyclical", "Just media hype"],
                novelty_score=0.0,
                feasibility_score=0.0,
                impact_score=0.0,
                testability_score=0.0,
                overall_score=0.0,
                related_papers=[p.get("title", "") for p in recent_papers[:3]],
                resources_needed=["Database access", "Trend analysis tools"],
                timeline_estimate="1-2 months",
                risk_factors=["Confirmation bias", "Publication bias"],
                generated_at=datetime.now().isoformat(),
                source_gaps=["Trend analysis"],
                source_strategy="trend_detection",
            )

            self.hypothesis_counter += 1
            hypotheses.append(hypothesis)

        return hypotheses

    async def _generate_cross_domain(
        self,
        papers: list,
        query: str,
        domain: Optional[str] = None,
    ) -> list[Hypothesis]:
        """Generate hypotheses by transferring approaches across domains."""
        hypotheses = []

        # Common cross-domain transfers
        domains = domain.split(",") if domain else ["machine_learning", "biology"]

        hypothesis = Hypothesis(
            id=f"cross_domain_{self.hypothesis_counter}",
            title=f"Applying {domains[0]} insights to advance {domains[1]} understanding",
            statement=f"Methods and theories from {domains[0]} can illuminate "
                     f"mechanisms in {domains[1]}, specifically regarding {query}.",
            background=f"Parallel developments in {domains[0]} suggest "
                       f"previously unexplored approaches for {domains[1]}.",
            predictions=[
                Prediction(
                    statement=f"Theoretical framework from {domains[0]} predicts "
                             f"patterns in {domains[1]}",
                    measurable=True,
                    success_criterion="Framework explains 40%+ variance",
                ),
            ],
            hypothesis_type=HypothesisType.CAUSAL,
            complexity=ComplexityLevel.COMPLEX,
            independent_variables=[
                Variable(
                    name="transfer_mechanism",
                    description=f"Specific {domains[0]} approach applied",
                    measurement_method="Implementation fidelity assessment",
                ),
            ],
            dependent_variables=[
                Variable(
                    name=f"{domains[1]}_outcome",
                    description=f"Key outcome in {domains[1]}",
                    measurement_method="Domain-specific measurement",
                ),
            ],
            control_variables=[
                Variable(
                    name="domain_differences",
                    description="Domain-specific confounds",
                    measurement_method="Careful experimental design",
                ),
            ],
            assumptions=[
                f"Core mechanisms transfer between {domains[0]} and {domains[1]}",
                "Sufficient isomorphism between domains",
            ],
            alternative_hypotheses=[
                "Domains are too different for transfer",
                "Surface similarity masks deep differences",
            ],
            novelty_score=0.0,
            feasibility_score=0.0,
            impact_score=0.0,
            testability_score=0.0,
            overall_score=0.0,
            related_papers=[p.get("title", "") for p in papers[:3]],
            resources_needed=["Expertise from both domains", "Collaborative team"],
            timeline_estimate="6-12 months",
            risk_factors=["Domain expertise required", "Transfer may not work"],
            generated_at=datetime.now().isoformat(),
            source_gaps=["Cross-domain gap"],
            source_strategy="cross_domain_synthesis",
        )

        self.hypothesis_counter += 1
        hypotheses.append(hypothesis)

        return hypotheses

    async def _generate_novel_combinations(
        self,
        papers: list,
        query: str,
    ) -> list[Hypothesis]:
        """Generate hypotheses by combining existing concepts in new ways."""
        hypotheses = []

        # Extract key concepts from papers
        concepts = self._extract_concepts(papers)

        if len(concepts) >= 2:
            c1, c2 = concepts[0], concepts[1]

            hypothesis = Hypothesis(
                id=f"combo_{self.hypothesis_counter}",
                title=f"Synergistic interaction between {c1} and {c2}",
                statement=f"The combined effect of {c1} and {c2} on {query} "
                         f"exceeds their additive individual effects.",
                background=f"While {c1} and {c2} are individually studied, "
                           f"their interaction in {query} context remains unexplored.",
                predictions=[
                    Prediction(
                        statement=f"{c1} × {c2} shows superadditive effect",
                        measurable=True,
                        success_criterion="Significant interaction (p < 0.05)",
                    ),
                ],
                hypothesis_type=HypothesisType.MECHANISTIC,
                complexity=ComplexityLevel.MODERATE,
                independent_variables=[
                    Variable(
                        name=c1,
                        description=f"First factor: {c1}",
                        measurement_method="Quantitative manipulation",
                    ),
                    Variable(
                        name=c2,
                        description=f"Second factor: {c2}",
                        measurement_method="Quantitative manipulation",
                    ),
                ],
                dependent_variables=[
                    Variable(
                        name="combined_effect",
                        description="Combined outcome measurement",
                        measurement_method="Quantitative assessment",
                    ),
                ],
                control_variables=[],
                assumptions=[
                    f"Independent manipulability of {c1} and {c2}",
                    "Effect is not due to sequential processing",
                ],
                alternative_hypotheses=[
                    "Effects are additive",
                    "One factor dominates",
                    "Interaction is artifactual",
                ],
                novelty_score=0.0,
                feasibility_score=0.0,
                impact_score=0.0,
                testability_score=0.0,
                overall_score=0.0,
                related_papers=[p.get("title", "") for p in papers[:5]],
                resources_needed=["Experimental design", "Statistical expertise"],
                timeline_estimate="4-8 months",
                risk_factors=["Interaction may be absent", "Measurement complexity"],
                generated_at=datetime.now().isoformat(),
                source_gaps=["Novel combination"],
                source_strategy="novel_combination",
            )

            self.hypothesis_counter += 1
            hypotheses.append(hypothesis)

        return hypotheses

    def _score_hypothesis(self, hyp: Hypothesis, papers: list) -> None:
        """Score a hypothesis across multiple dimensions."""
        # Novelty: based on literature overlap
        novelty = self._calculate_novelty(hyp, papers)
        hyp.novelty_score = novelty

        # Feasibility: based on resources needed and complexity
        feasibility = self._calculate_feasibility(hyp)
        hyp.feasibility_score = feasibility

        # Impact: based on field importance and problem relevance
        impact = self._calculate_impact(hyp, papers)
        hyp.impact_score = impact

        # Testability: based on variable clarity and measurability
        testability = self._calculate_testability(hyp)
        hyp.testability_score = testability

        # Overall score (weighted average)
        weights = self.config["evaluation"]
        overall = (
            novelty * weights["novelty"]["weight"] +
            feasibility * weights["feasibility"]["weight"] +
            impact * weights["impact"]["weight"] +
            testability * weights["testability"]["weight"]
        )

        hyp.overall_score = overall

    def _calculate_novelty(self, hyp: Hypothesis, papers: list) -> float:
        """Calculate novelty score (0-1)."""
        # Count how many papers already address this hypothesis
        title_words = set(hyp.title.lower().split())
        overlap_count = 0

        for paper in papers:
            paper_title = paper.get("title", "").lower()
            overlap = len(title_words & set(paper_title.split()))
            if overlap > 2:
                overlap_count += 1

        # Higher overlap = lower novelty
        novelty = max(0.0, 1.0 - (overlap_count / max(len(papers), 1)))
        return novelty

    def _calculate_feasibility(self, hyp: Hypothesis) -> float:
        """Calculate feasibility score (0-1)."""
        score = 0.8  # Start high

        # Reduce for high complexity
        if hyp.complexity == ComplexityLevel.COMPLEX:
            score -= 0.2
        elif hyp.complexity == ComplexityLevel.MODERATE:
            score -= 0.1

        # Reduce if many resources needed
        if len(hyp.resources_needed) > 5:
            score -= 0.15

        # Reduce if long timeline
        if "12" in hyp.timeline_estimate or "months" not in hyp.timeline_estimate:
            score -= 0.1

        return max(0.0, min(1.0, score))

    def _calculate_impact(self, hyp: Hypothesis, papers: list) -> float:
        """Calculate impact score (0-1)."""
        score = 0.7  # Moderate baseline

        # Increase if many related papers (field importance)
        if len(hyp.related_papers) > 10:
            score += 0.2
        elif len(hyp.related_papers) > 5:
            score += 0.1

        # Increase for cross-domain hypotheses
        if hyp.source_strategy == "cross_domain_synthesis":
            score += 0.15

        # Increase for mechanistic hypotheses (often more impactful)
        if hyp.hypothesis_type == HypothesisType.MECHANISTIC:
            score += 0.1

        return min(1.0, score)

    def _calculate_testability(self, hyp: Hypothesis) -> float:
        """Calculate testability score (0-1)."""
        score = 0.75

        # Check for clear variables
        if len(hyp.independent_variables) == 0 or len(hyp.dependent_variables) == 0:
            score -= 0.3

        # Check for measurable predictions
        measurable_preds = sum(1 for p in hyp.predictions if p.measurable)
        if measurable_preds / len(hyp.predictions) < 0.8:
            score -= 0.2

        # Check for clear success criteria
        clear_criteria = sum(
            1 for p in hyp.predictions if len(p.success_criterion) > 10
        )
        if clear_criteria / len(hyp.predictions) < 0.8:
            score -= 0.15

        return max(0.0, min(1.0, score))

    def _filter_and_rank(self, hypotheses: list[Hypothesis]) -> list[Hypothesis]:
        """Filter by quality criteria and rank by overall score."""
        config = self.config
        filters = config["ranking"]["filters"]

        # Apply filters
        filtered = [
            h for h in hypotheses
            if (h.novelty_score >= filters["min_novelty_score"] and
                h.feasibility_score >= filters["min_feasibility_score"] and
                h.impact_score >= filters["min_impact_score"] and
                h.testability_score >= filters["min_testability_score"])
        ]

        # Sort by overall score
        filtered.sort(key=lambda h: h.overall_score, reverse=True)

        # Return top-k
        return filtered[:config["ranking"]["top_k"]]

    def _build_concept_map(self, papers: list) -> None:
        """Build a map of concepts from papers."""
        for paper in papers:
            abstract = paper.get("abstract", "")
            title = paper.get("title", "")
            combined_text = f"{title} {abstract}".lower()

            # Extract common science concepts (simplified)
            concepts = self._extract_concepts_from_text(combined_text)

            for concept in concepts:
                if concept not in self.concept_map:
                    self.concept_map[concept] = []
                self.concept_map[concept].append(paper.get("title", ""))

    @staticmethod
    def _extract_concepts(papers: list, top_k: int = 5) -> list[str]:
        """Extract top concepts from papers."""
        concept_freq = {}

        for paper in papers:
            concepts = HypothesisAgent._extract_concepts_from_text(
                paper.get("title", "").lower()
            )
            for concept in concepts:
                concept_freq[concept] = concept_freq.get(concept, 0) + 1

        sorted_concepts = sorted(
            concept_freq.items(),
            key=lambda x: x[1],
            reverse=True
        )

        return [c[0] for c in sorted_concepts[:top_k]]

    @staticmethod
    def _extract_concepts_from_text(text: str) -> list[str]:
        """Extract key concepts from text."""
        # Simple extraction: look for noun phrases
        words = text.split()
        concepts = []

        # Find multi-word phrases
        for i in range(len(words) - 1):
            phrase = f"{words[i]} {words[i+1]}"
            if len(phrase) > 4:  # Minimum length
                concepts.append(phrase)

        # Add single important words
        important_words = [w for w in words if len(w) > 4 and w.isalpha()]
        concepts.extend(important_words[:5])

        return list(set(concepts))

    @staticmethod
    def _formalize_gap_hypothesis(gap_description: str) -> str:
        """Convert gap description to formal hypothesis."""
        return f"If {gap_description}, then we can identify specific mechanisms " \
               f"explaining this phenomenon through systematic investigation."

    @staticmethod
    def _extract_factor(gap_description: str) -> str:
        """Extract the primary factor from gap description."""
        # Simple heuristic
        words = gap_description.split()
        if len(words) > 2:
            return " ".join(words[:2])
        return gap_description

    async def rank_hypotheses(
        self,
        hypotheses: list[Hypothesis],
        weights: Optional[dict] = None,
    ) -> list[Hypothesis]:
        """Rank hypotheses with custom weights."""
        if weights:
            for hyp in hypotheses:
                hyp.overall_score = (
                    hyp.novelty_score * weights.get("novelty", 0.25) +
                    hyp.feasibility_score * weights.get("feasibility", 0.3) +
                    hyp.impact_score * weights.get("impact", 0.25) +
                    hyp.testability_score * weights.get("testability", 0.2)
                )

        hypotheses.sort(key=lambda h: h.overall_score, reverse=True)
        return hypotheses

    async def expand_hypothesis(self, hypothesis: Hypothesis) -> dict:
        """Expand hypothesis with additional details."""
        return {
            "hypothesis": hypothesis.to_dict(),
            "expanded": {
                "research_design_sketch": self._sketch_research_design(hypothesis),
                "potential_pitfalls": hypothesis.risk_factors,
                "success_indicators": [
                    p.success_criterion for p in hypothesis.predictions
                ],
                "literature_support": hypothesis.related_papers,
                "next_steps": [
                    "Conduct systematic literature review",
                    "Design pilot experiment",
                    "Recruit study participants",
                    "Collect pilot data",
                    "Analyze and refine hypothesis",
                ],
            },
        }

    @staticmethod
    def _sketch_research_design(hypothesis: Hypothesis) -> str:
        """Sketch a research design for testing the hypothesis."""
        design = f"""
Research Design Sketch for: {hypothesis.title}

Study Type: {hypothesis.hypothesis_type.value.upper()}
Complexity: {hypothesis.complexity.value.upper()}

Independent Variables:
"""
        for var in hypothesis.independent_variables:
            design += f"  - {var.name}: {var.description}\n"

        design += "\nDependent Variables:\n"
        for var in hypothesis.dependent_variables:
            design += f"  - {var.name}: {var.description}\n"

        design += "\nControl Variables:\n"
        for var in hypothesis.control_variables:
            design += f"  - {var.name}: {var.description}\n"

        design += f"\nPredicted Outcome: {hypothesis.predictions[0].statement if hypothesis.predictions else 'TBD'}\n"
        design += f"Success Criterion: {hypothesis.predictions[0].success_criterion if hypothesis.predictions else 'TBD'}\n"

        return design

    async def close(self) -> None:
        """Clean up resources."""
        pass


async def main():
    """Example usage of the Hypothesis Agent."""
    from agents.literature_agent import LiteratureAgent

    # First, get literature findings
    lit_agent = LiteratureAgent()

    try:
        print("🔍 Searching literature on neural network interpretability...")
        papers = await lit_agent.search_papers(
            "neural network interpretability explainability",
            year_range=(2021, 2026),
            limit=20,
        )

        gaps = await lit_agent.identify_gaps(papers)

        print(f"Found {len(papers)} papers and {len(gaps)} research gaps\n")

        # Now generate hypotheses
        print("💡 Generating testable hypotheses...")
        hyp_agent = HypothesisAgent()

        hypotheses = await hyp_agent.generate_hypotheses(
            papers=papers,
            research_gaps=gaps,
            query="neural network interpretability",
        )

        print(f"\n✓ Generated {len(hypotheses)} hypotheses\n")

        # Display top hypotheses
        for i, hyp in enumerate(hypotheses[:3], 1):
            print(f"{i}. {hyp.title}")
            print(f"   Type: {hyp.hypothesis_type.value} | "
                  f"Complexity: {hyp.complexity.value}")
            print(f"   Scores - Novelty: {hyp.novelty_score:.2f}, "
                  f"Feasibility: {hyp.feasibility_score:.2f}, "
                  f"Impact: {hyp.impact_score:.2f}, "
                  f"Testability: {hyp.testability_score:.2f}")
            print(f"   Overall Score: {hyp.overall_score:.3f}")
            print(f"   Statement: {hyp.statement[:100]}...")
            print()

        # Expand top hypothesis
        print("📋 Detailed view of top hypothesis:\n")
        expanded = await hyp_agent.expand_hypothesis(hypotheses[0])
        print(json.dumps(expanded, indent=2))

    finally:
        await lit_agent.close()
        await hyp_agent.close()


if __name__ == "__main__":
    asyncio.run(main())
