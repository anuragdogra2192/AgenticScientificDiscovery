"""Hypothesis Agent for generating testable Mycobacterium tuberculosis scientific hypotheses powered by Omnigent and Claude."""

import asyncio
import json
import logging
import re
import os
from pathlib import Path
from dataclasses import dataclass, field, asdict
from typing import Optional, Any
from enum import Enum
from datetime import datetime

import yaml

try:
    from anthropic import Anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False

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
    """Agent for generating and ranking anti-tubercular scientific hypotheses."""

    def __init__(self, config_path: str = "agents/hypothesis_agent/hypothesis_agent.yaml"):
        if not os.environ.get("ANTHROPIC_API_KEY"):
            for path_str in [".env.local", "agents/hypothesis_agent/.env.local", "../../.env.local"]:
                env_file = Path(path_str)
                if env_file.exists():
                    with open(env_file) as f:
                        for line in f:
                            line = line.strip()
                            if line and not line.startswith("#") and "=" in line:
                                k, v = line.split("=", 1)
                                if k.strip() == "ANTHROPIC_API_KEY":
                                    os.environ["ANTHROPIC_API_KEY"] = v.strip()
                    break

        if not os.path.exists(config_path):
            config_path = "agents/hypothesis_agent/config.yaml"
            if not os.path.exists(config_path):
                config_path = "hypothesis_agent.yaml"

        if os.path.exists(config_path):
            with open(config_path, "r") as f:
                self.config = yaml.safe_load(f)
        else:
            self.config = {}

        self.hypothesis_counter = 0
        self.use_claude = False
        self.claude_client = None

        if ANTHROPIC_AVAILABLE and os.environ.get("ANTHROPIC_API_KEY"):
            try:
                self.claude_client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
                self.use_claude = True
                logger.info("Claude Haiku API initialized for Mtb hypothesis generation")
            except Exception as e:
                logger.warning(f"Could not initialize Claude API: {e}. Falling back to rule-based generation.")

    @staticmethod
    def _safe_get(obj: Any, attr: str, default: Any = "") -> Any:
        if isinstance(obj, dict):
            return obj.get(attr, default)
        return getattr(obj, attr, default)

    @staticmethod
    def _extract_json_content(text: str) -> str:
        text = text.strip()
        if "```json" in text:
            parts = text.split("```json")
            if len(parts) > 1:
                text = parts[1].split("```")[0].strip()
        elif "```" in text:
            parts = text.split("```")
            if len(parts) > 1:
                text = parts[1].split("```")[0].strip()

        match_array = re.search(r'\[\s*\{.*\}\s*\]', text, re.DOTALL)
        if match_array:
            text = match_array.group(0)
        else:
            match_obj = re.search(r'\{\s*".*"\s*:\s*\[.*\]\s*\}', text, re.DOTALL)
            if match_obj:
                text = match_obj.group(0)

        text = re.sub(r',\s*([\]}])', r'\1', text)
        return text

    async def generate_hypotheses(
        self,
        papers: list,
        research_gaps: list,
        query: str,
        domain: Optional[str] = "Mycobacterium tuberculosis Drug Discovery",
    ) -> list[Hypothesis]:
        """Generate anti-tubercular hypotheses from literature findings."""
        logger.info(f"Generating Mtb hypotheses for query: {query}")

        if self.use_claude and self.claude_client:
            try:
                claude_hypotheses = await self._generate_with_claude(papers, research_gaps, query, domain)
                if claude_hypotheses:
                    return claude_hypotheses
            except Exception as e:
                logger.warning(f"Claude generation failed: {e}. Falling back to rule-based generator.")

        # Rule-based fallback specialized for Mtb
        hypotheses = []
        for i, gap in enumerate(research_gaps[:5]):
            gap_desc = self._safe_get(gap, "gap_description", self._safe_get(gap, "description", ""))
            hypothesis = Hypothesis(
                id=f"mtb_gap_{i}_{self.hypothesis_counter}",
                title=f"Targeting Mtb pathway in {gap_desc[:40]}",
                statement=f"Inhibition of cell wall biosynthesis or efflux mechanisms addressing {gap_desc} will restore bactericidal susceptibility in resistant Mtb strains.",
                background=f"Evidence indicates persistent bottlenecks regarding {gap_desc}.",
                predictions=[
                    Prediction(statement=f"Small-molecule treatment reduces Mtb MIC below 1.0 µg/mL.", measurable=True, success_criterion="MIC < 1.0 µg/mL")
                ],
                hypothesis_type=HypothesisType.MECHANISTIC,
                complexity=ComplexityLevel.MODERATE,
                independent_variables=[Variable(name="compound_concentration", description="Inhibitor dose", measurement_method="µM")],
                dependent_variables=[Variable(name="mic_value", description="Minimum Inhibitory Concentration", measurement_method="Alamar Blue Assay")],
                control_variables=[Variable(name="rifampicin_control", description="Standard antibiotic control", measurement_method="Standardized")],
                assumptions=["Compound penetrates Mtb mycolic acid cell wall"],
                alternative_hypotheses=["Efflux pump upregulation compensates inhibition"],
                novelty_score=0.85,
                feasibility_score=0.80,
                impact_score=0.88,
                testability_score=0.90,
                overall_score=0.86,
                related_papers=[self._safe_get(p, "title", "") for p in papers[:3]],
                resources_needed=["Mtb H37Rv strain", "Alamar Blue assay kit"],
                timeline_estimate="4 weeks",
                risk_factors=["Mtb biosafety level 3 (BSL-3) handling constraints"],
                generated_at=datetime.now().isoformat(),
                source_gaps=[gap_desc],
                source_strategy="rule_based_mtb",
            )
            self.hypothesis_counter += 1
            hypotheses.append(hypothesis)

        return hypotheses

    async def _generate_with_claude(self, papers: list, research_gaps: list, query: str, domain: str) -> list[Hypothesis]:
        papers_summary = json.dumps([
            {"title": self._safe_get(p, "title", ""), "abstract": self._safe_get(p, "abstract", "")[:300]}
            for p in papers[:10]
        ], indent=2)

        gaps_summary = json.dumps([
            {"description": self._safe_get(g, "gap_description", self._safe_get(g, "description", ""))}
            for g in research_gaps[:5]
        ], indent=2)

        prompt = f"""Generate 5 testable anti-tubercular drug discovery hypotheses for Mycobacterium tuberculosis.
RESEARCH QUESTION: {query}
LITERATURE:
{papers_summary}
GAPS:
{gaps_summary}

Return ONLY a valid JSON array of objects with: title, statement, background, hypothesis_type, complexity, predictions (array with statement, success_criterion), novelty_score (0-1), feasibility_score (0-1), impact_score (0-1), testability_score (0-1), resources_needed, risk_factors."""

        response = self.claude_client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=4096,
            messages=[{"role": "user", "content": prompt}]
        )

        hyp_data_list = json.loads(self._extract_json_content(response.content[0].text))
        hypotheses = []

        for i, h in enumerate(hyp_data_list):
            hyp = Hypothesis(
                id=f"claude_mtb_{i}",
                title=h.get("title", ""),
                statement=h.get("statement", ""),
                background=h.get("background", ""),
                predictions=[Prediction(statement=p.get("statement", ""), measurable=True, success_criterion=p.get("success_criterion", "")) for p in h.get("predictions", [])],
                hypothesis_type=HypothesisType(h.get("hypothesis_type", "mechanistic")),
                complexity=ComplexityLevel(h.get("complexity", "moderate")),
                independent_variables=[Variable(name="inhibitor_dose", description="Concentration", measurement_method="µM")],
                dependent_variables=[Variable(name="cell_viability", description="Mtb survival", measurement_method="CFU / Alamar Blue")],
                control_variables=[Variable(name="vehicle", description="DMSO", measurement_method="1%")],
                assumptions=["Target expression in active Mtb"],
                alternative_hypotheses=["Secondary target compensation"],
                novelty_score=float(h.get("novelty_score", 0.8)),
                feasibility_score=float(h.get("feasibility_score", 0.8)),
                impact_score=float(h.get("impact_score", 0.85)),
                testability_score=float(h.get("testability_score", 0.9)),
                overall_score=0.86,
                related_papers=[self._safe_get(p, "title", "") for p in papers[:3]],
                resources_needed=h.get("resources_needed", ["BSL-3 lab", "Mtb strain"]),
                timeline_estimate="3 months",
                risk_factors=h.get("risk_factors", ["Efflux resistance"]),
                generated_at=datetime.now().isoformat(),
                source_strategy="claude_haiku_mtb"
            )
            hypotheses.append(hyp)
        return hypotheses

    async def rank_hypotheses(self, hypotheses: list[Hypothesis], weights: Optional[dict] = None) -> list[Hypothesis]:
        hypotheses.sort(key=lambda h: h.overall_score, reverse=True)
        return hypotheses

    async def expand_hypothesis(self, hypothesis: Hypothesis) -> dict:
        return {
            "hypothesis": hypothesis.to_dict(),
            "expanded": {
                "research_design_sketch": f"Mtb Assay Study: {hypothesis.title}\nStatement: {hypothesis.statement}",
                "potential_pitfalls": hypothesis.risk_factors,
                "success_indicators": [p.success_criterion for p in hypothesis.predictions],
                "literature_support": hypothesis.related_papers,
                "next_steps": ["Run Mtb MIC assay", "Evaluate intracellular macrophage activity"]
            }
        }

    async def close(self) -> None:
        pass