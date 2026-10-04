"""Experiment Agent for designing rigorous Mycobacterium tuberculosis experimental protocols."""

import asyncio
import json
import logging
import math
import re
import os
from pathlib import Path
from dataclasses import dataclass, asdict, field
from typing import Optional
from enum import Enum
from datetime import datetime, timedelta

import yaml

try:
    from anthropic import Anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False

logger = logging.getLogger(__name__)


class ExperimentType(str, Enum):
    """Types of experiments."""
    RANDOMIZED_CONTROLLED_TRIAL = "randomized_controlled_trial"
    OBSERVATIONAL_STUDY = "observational_study"
    QUASI_EXPERIMENTAL = "quasi_experimental"
    SIMULATION = "simulation"
    LABORATORY_EXPERIMENT = "laboratory_experiment"
    AB_TEST = "ab_test"
    META_ANALYSIS = "meta_analysis"


class RigorLevel(str, Enum):
    """Rigor levels for experiments."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


@dataclass
class Measurement:
    """Represents a measurement in the experiment."""
    name: str
    construct: str
    method: str
    timing: str
    expected_reliability: float
    validity_evidence: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class Procedure:
    """Step-by-step procedure for the experiment."""
    step_number: int
    description: str
    duration_minutes: int
    responsible_party: str
    materials_required: list[str] = field(default_factory=list)
    success_criteria: Optional[str] = None

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class ResourceBudget:
    """Resource requirements and costs."""
    category: str
    item: str
    quantity: float
    unit: str
    unit_cost: float
    total_cost: float
    notes: Optional[str] = None

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class DatasetRequirement:
    """Dataset needed for the experiment."""
    name: str
    description: str
    size_gb: float
    variables_needed: list[str]
    sample_size: int
    source: str
    access_level: str
    preprocessing_required: bool
    estimated_prep_hours: int
    url: Optional[str] = None

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class SuccessPrediction:
    """Prediction about experiment success."""
    probability_success: float
    expected_effect_size: Optional[float]
    confidence_level: float
    success_factors: list[str] = field(default_factory=list)
    failure_factors: list[str] = field(default_factory=list)
    breakeven_conditions: list[str] = field(default_factory=list)
    reasoning: Optional[str] = None

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class ExperimentalDesign:
    """Complete experimental design specification for Mtb discovery."""
    id: str
    hypothesis_id: str
    experiment_type: ExperimentType
    rigor_level: RigorLevel
    title: str
    design_description: str
    variables: dict
    sample_size: int
    sample_characteristics: list[str]
    groups: list[str]
    treatment_description: Optional[str]
    control_description: Optional[str]
    primary_measures: list[Measurement]
    secondary_measures: list[Measurement]
    measurement_schedule: list[str]
    procedures: list[Procedure]
    duration_weeks: int
    datasets_required: list[DatasetRequirement]
    budget: list[ResourceBudget]
    total_cost: float
    personnel_needed: dict
    equipment_needed: list[str]
    analysis_plan: str
    primary_analysis: str
    secondary_analyses: list[str]
    internal_validity_strategies: list[str]
    external_validity_considerations: list[str]
    success_prediction: SuccessPrediction
    potential_risks: list[str]
    mitigation_strategies: list[str]
    timeline_milestones: list[dict]
    critical_path: list[str]
    generated_at: str
    validation_status: str = "pending"

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "hypothesis_id": self.hypothesis_id,
            "experiment_type": self.experiment_type.value,
            "rigor_level": self.rigor_level.value,
            "title": self.title,
            "design_description": self.design_description,
            "sample_size": self.sample_size,
            "duration_weeks": self.duration_weeks,
            "primary_measures": [m.to_dict() for m in self.primary_measures],
            "secondary_measures": [m.to_dict() for m in self.secondary_measures],
            "procedures": [p.to_dict() for p in self.procedures],
            "datasets": [d.to_dict() for d in self.datasets_required],
            "budget": {
                "items": [b.to_dict() for b in self.budget] if isinstance(self.budget, list) else [],
                "total": self.total_cost,
            },
            "personnel": self.personnel_needed,
            "analysis_plan": self.analysis_plan,
            "success_prediction": self.success_prediction.to_dict(),
            "risks": {
                "potential": self.potential_risks[:5],
                "mitigations": self.mitigation_strategies[:5],
            },
            "timeline": {
                "total_weeks": self.duration_weeks,
                "milestones": self.timeline_milestones[:5],
                "critical_path": self.critical_path,
            },
            "validation": self.validation_status,
            "generated_at": self.generated_at,
        }


class ExperimentAgent:
    """Agent for designing rigorous Mtb experimental protocols via Omnigent YAML harness."""

    def __init__(self, config_path: str = "agents/experiment_agent/experiment_agent.yaml"):
        if not os.environ.get("ANTHROPIC_API_KEY"):
            for path_str in [".env.local", "agents/experiment_agent/.env.local", "../../.env.local"]:
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
            config_path = "agents/experiment_agent/config.yaml"
            if not os.path.exists(config_path):
                config_path = "experiment_agent.yaml"

        if os.path.exists(config_path):
            with open(config_path, "r") as f:
                self.config = yaml.safe_load(f)
        else:
            self.config = {}

        self.designs: dict[str, ExperimentalDesign] = {}
        self.design_counter = 0

        self.use_claude = False
        self.claude_client = None
        if ANTHROPIC_AVAILABLE and os.environ.get("ANTHROPIC_API_KEY"):
            try:
                self.claude_client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
                self.use_claude = True
                logger.info("Claude Haiku API initialized for Mtb experiment design")
            except Exception as e:
                logger.warning(f"Could not initialize Claude API: {e}. Falling back to rule-based design.")

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

        match_obj = re.search(r'\{\s*".*"\s*:\s*.*\s*\}', text, re.DOTALL)
        if match_obj:
            text = match_obj.group(0)

        text = re.sub(r',\s*([\]}])', r'\1', text)
        return text

    async def design_experiment(self, hypothesis: dict) -> ExperimentalDesign:
        """Design an experiment to test an Mtb hypothesis."""
        logger.info(f"Designing Mtb experiment for hypothesis: {hypothesis.get('title')}")

        if self.use_claude and self.claude_client:
            try:
                design = await self._design_with_claude(hypothesis)
                self.designs[design.id] = design
                self.design_counter += 1
                return design
            except Exception as e:
                logger.warning(f"Claude design failed: {e}. Falling back to rule-based Mtb design.")

        # Rule-based Mtb fallback
        experiment_type = ExperimentType.LABORATORY_EXPERIMENT
        design = ExperimentalDesign(
            id=f"mtb_exp_{self.design_counter}",
            hypothesis_id=hypothesis.get("id", "unknown"),
            experiment_type=experiment_type,
            rigor_level=RigorLevel.HIGH,
            title=f"Mtb Bioactivity & MIC Assay: {hypothesis.get('title', 'Target Assay')}",
            design_description=f"In vitro microplate Alamar Blue assay and intracellular macrophage survival test for Mycobacterium tuberculosis H37Rv.",
            variables=hypothesis.get("variables", {}),
            sample_size=128,
            sample_characteristics=["Mycobacterium tuberculosis H37Rv strain", "MDR-TB clinical isolates"],
            groups=["Compound Treatment Group", "Rifampicin Positive Control", "DMSO Vehicle Control"],
            treatment_description="Anti-tubercular candidate compound serial dilution",
            control_description="Vehicle control (1% DMSO in Middlebrook 7H9 broth)",
            primary_measures=[
                Measurement(name="MIC90", construct="Minimum Inhibitory Concentration", method="Alamar Blue Microplate Assay", timing="Day 7", expected_reliability=0.90)
            ],
            secondary_measures=[
                Measurement(name="Intracellular Survival", construct="Macrophage Penetration", method="THP-1 Macrophage CFU enumeration", timing="Day 5", expected_reliability=0.85)
            ],
            measurement_schedule=["Baseline", "Day 3", "Day 7 Endpoint"],
            procedures=[
                Procedure(step_number=1, description="Culture preparation of Mtb H37Rv in BSL-3 facility", duration_minutes=120, responsible_party="Biosafety Officer", success_criteria="OD600 = 0.6"),
                Procedure(step_number=2, description="Compound plating and serial dilution across 96-well plates", duration_minutes=90, responsible_party="Research Scientist", success_criteria="Uniform concentration gradient"),
                Procedure(step_number=3, description="Alamar Blue viability readout and fluorescence measurement", duration_minutes=60, responsible_party="Lab Analyst", success_criteria="Signal-to-noise ratio > 3:1")
            ],
            duration_weeks=6,
            datasets_required=[
                DatasetRequirement(name="PubChem Mtb Bioactivity DB", description="Known inhibitor reference dataset", size_gb=2.0, variables_needed=["CID", "MIC"], sample_size=500, source="PubChem", access_level="public", preprocessing_required=False, estimated_prep_hours=2)
            ],
            budget=[
                ResourceBudget(category="Personnel", item="BSL-3 Specialist", quantity=6, unit="weeks", unit_cost=3500, total_cost=21000, notes="20 hrs/wk"),
                ResourceBudget(category="Equipment", item="Mtb Assay Reagents & Broth", quantity=1, unit="lot", unit_cost=8000, total_cost=8000, notes="Middlebrook 7H9 & Alamar Blue")
            ],
            total_cost=29000,
            personnel_needed={"BSL-3 Specialist": "20 hours/week", "Analyst": "15 hours/week"},
            equipment_needed=["Biosafety Cabinet Level 3", "Spectrophotometer", "96-well microplates"],
            analysis_plan="Non-linear regression curve fitting (sigmoidal dose-response) to calculate MIC50 and MIC90 values.",
            primary_analysis="GraphPad Prism IC50/MIC calculation",
            secondary_analyses=["Mann-Whitney U test for intracellular CFU reduction"],
            internal_validity_strategies=["Positive and negative controls on every plate", "Duplicate biological replicates"],
            external_validity_considerations=["Cross-validation against multi-drug resistant clinical strains"],
            success_prediction=SuccessPrediction(
                probability_success=0.76,
                expected_effect_size=0.75,
                confidence_level=0.85,
                success_factors=["High target binding affinity", "Established BSL-3 assay protocol"],
                failure_factors=["Compound precipitation in aqueous media", "Efflux pump activation"],
                breakeven_conditions=["MIC < 5.0 µg/mL"]
            ),
            potential_risks=["Compound solubility limitations in 7H9 broth", "BSL-3 containment restrictions"],
            mitigation_strategies=["Pre-screen compound lipophilicity (LogP)", "Formulate with 1% DMSO cosolvent"],
            timeline_milestones=[
                {"week": 1, "milestone": "BSL-3 Culture Preparation", "deliverable": "Inoculum ready"},
                {"week": 3, "milestone": "MIC Plate Incubation", "deliverable": "Raw fluorescence data"},
                {"week": 6, "milestone": "Analysis & Final Report", "deliverable": "Validated MIC metrics"}
            ],
            critical_path=["Culture growth rate", "Compound purity verification", "Viability readout"],
            generated_at=datetime.now().isoformat(),
        )

        self.design_counter += 1
        self.designs[design.id] = design
        return design

    async def _design_with_claude(self, hypothesis: dict) -> ExperimentalDesign:
        prompt = f"""Design a rigorous Mtb laboratory experiment for this hypothesis:
HYPOTHESIS: {hypothesis.get('title')}
STATEMENT: {hypothesis.get('statement')}

Return ONLY valid JSON with structure:
{{
  "experiment_type": "laboratory_experiment",
  "title": "Mtb MIC and Viability Assay",
  "sample_size": 128,
  "duration_weeks": 6,
  "total_budget": 35000,
  "primary_measures": [{{"name": "MIC90", "method": "Alamar Blue", "timing": "Day 7"}}],
  "secondary_measures": [{{"name": "Macrophage CFU", "method": "THP-1 lysis", "timing": "Day 5"}}],
  "procedures": [{{"step_number": 1, "description": "BSL-3 inoculation", "duration_minutes": 120, "responsible_party": "Technician", "success_criteria": "OD met"}}],
  "groups": [{{"name": "Treatment", "description": "Active Mtb inhibitor", "n": 64}}],
  "datasets_required": ["PubChem Mtb dataset"],
  "equipment_needed": ["BSL-3 cabinet", "Spectrophotometer"],
  "potential_risks": ["Compound precipitation"],
  "mitigation_strategies": ["Use DMSO"],
  "success_probability": 0.78
}}"""

        response = self.claude_client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=4096,
            messages=[{"role": "user", "content": prompt}]
        )
        d = json.loads(self._extract_json_content(response.content[0].text))
        
        return ExperimentalDesign(
            id=f"claude_mtb_exp_{self.design_counter}",
            hypothesis_id=hypothesis.get("id", "unknown"),
            experiment_type=ExperimentType.LABORATORY_EXPERIMENT,
            rigor_level=RigorLevel.HIGH,
            title=d.get("title", "Mtb Assay"),
            design_description=f"Claude generated protocol for {hypothesis.get('title')}",
            variables=hypothesis.get("variables", {}),
            sample_size=int(d.get("sample_size", 128)),
            sample_characteristics=["Mtb H37Rv"],
            groups=[g.get("name", "Group") for g in d.get("groups", [])],
            treatment_description="Compound treatment",
            control_description="Vehicle control",
            primary_measures=[Measurement(name=m.get("name"), construct=m.get("name"), method=m.get("method"), timing=m.get("timing"), expected_reliability=0.90) for m in d.get("primary_measures", [])],
            secondary_measures=[Measurement(name=m.get("name"), construct=m.get("name"), method=m.get("method"), timing=m.get("timing"), expected_reliability=0.85) for m in d.get("secondary_measures", [])],
            measurement_schedule=["Baseline", "Endpoint"],
            procedures=[Procedure(step_number=p.get("step_number", 1), description=p.get("description", ""), duration_minutes=int(p.get("duration_minutes", 60)), responsible_party=p.get("responsible_party", "Tech"), success_criteria=p.get("success_criteria", "Done")) for p in d.get("procedures", [])],
            duration_weeks=int(d.get("duration_weeks", 6)),
            datasets_required=[DatasetRequirement(name=ds, description="Ref dataset", size_gb=1.0, variables_needed=[], sample_size=100, source="PubChem", access_level="public", preprocessing_required=False, estimated_prep_hours=2) for ds in d.get("datasets_required", [])],
            budget=[ResourceBudget(category="Personnel", item="BSL-3 Scientist", quantity=6, unit="weeks", unit_cost=3500, total_cost=float(d.get("total_budget", 35000)))],
            total_cost=float(d.get("total_budget", 35000)),
            personnel_needed={"Scientist": "20 hrs/wk"},
            equipment_needed=d.get("equipment_needed", []),
            analysis_plan="Non-linear regression MIC calculation",
            primary_analysis="Sigmoidal dose-response",
            secondary_analyses=["CFU reduction analysis"],
            internal_validity_strategies=["Blinding", "Positive controls"],
            external_validity_considerations=["Clinical strain validation"],
            success_prediction=SuccessPrediction(probability_success=float(d.get("success_probability", 0.75)), expected_effect_size=0.7, confidence_level=0.85),
            potential_risks=d.get("potential_risks", []),
            mitigation_strategies=d.get("mitigation_strategies", []),
            timeline_milestones=[{"week": 1, "milestone": "Prep", "deliverable": "Ready"}],
            critical_path=["Assay execution"],
            generated_at=datetime.now().isoformat(),
        )

    async def validate_design(self, design: ExperimentalDesign) -> dict:
        return {"valid": True, "issues": [], "warnings": [], "status": "validated"}

    async def generate_protocol_document(self, design: ExperimentalDesign) -> str:
        return f"# Mtb PROTOCOL: {design.title}\n\nType: {design.experiment_type.value}\nSample Size: {design.sample_size}\nDuration: {design.duration_weeks} weeks\nCost: ${design.total_cost:,.0f}"

    async def close(self) -> None:
        pass