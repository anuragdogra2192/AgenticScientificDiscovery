"""Experiment Agent for designing rigorous experimental protocols."""

import asyncio
import json
import logging
import math
import re
import os
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
    expected_reliability: float  # 0-1, Cronbach's alpha
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
    category: str  # personnel, equipment, services
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
    access_level: str  # public, restricted, restricted_with_approval
    preprocessing_required: bool
    estimated_prep_hours: int
    url: Optional[str] = None

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class SuccessPrediction:
    """Prediction about experiment success."""
    probability_success: float  # 0-1
    expected_effect_size: Optional[float]
    confidence_level: float  # 0-1
    success_factors: list[str]
    failure_factors: list[str]
    breakeven_conditions: list[str]

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class ExperimentalDesign:
    """Complete experimental design specification."""
    id: str
    hypothesis_id: str
    experiment_type: ExperimentType
    rigor_level: RigorLevel
    title: str

    # Design details
    design_description: str
    variables: dict  # {"independent": [...], "dependent": [...], "control": [...]}
    sample_size: int
    sample_characteristics: list[str]

    # Groups/conditions
    groups: list[str]
    treatment_description: Optional[str]
    control_description: Optional[str]

    # Measurements
    primary_measures: list[Measurement]
    secondary_measures: list[Measurement]
    measurement_schedule: list[str]  # Baseline, post-intervention, follow-up

    # Procedures
    procedures: list[Procedure]
    duration_weeks: int

    # Datasets
    datasets_required: list[DatasetRequirement]

    # Resources
    budget: list[ResourceBudget]
    total_cost: float
    personnel_needed: dict  # {role: hours_per_week}
    equipment_needed: list[str]

    # Analysis
    analysis_plan: str
    primary_analysis: str
    secondary_analyses: list[str]

    # Validation
    internal_validity_strategies: list[str]
    external_validity_considerations: list[str]

    # Prediction
    success_prediction: SuccessPrediction

    # Risks
    potential_risks: list[str]
    mitigation_strategies: list[str]

    # Timeline
    timeline_milestones: list[dict]
    critical_path: list[str]

    # Metadata
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
                "items": [b.to_dict() for b in self.budget],
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
    """Agent for designing rigorous experimental protocols."""

    def __init__(self, config_path: str = "agents/experiment_agent/config.yaml"):
        """Initialize the Experiment Agent."""
        with open(config_path, "r") as f:
            self.config = yaml.safe_load(f)

        self.designs: dict[str, ExperimentalDesign] = {}
        self.design_counter = 0

        # Initialize Claude client if API key available
        self.use_claude = False
        self.claude_client = None
        if ANTHROPIC_AVAILABLE and os.environ.get("ANTHROPIC_API_KEY"):
            try:
                self.claude_client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
                self.use_claude = True
                logger.info("Claude Haiku API initialized for experiment design")
            except Exception as e:
                logger.warning(f"Could not initialize Claude API: {e}. Falling back to rule-based design.")
                self.use_claude = False
        elif ANTHROPIC_AVAILABLE:
            logger.warning("ANTHROPIC_API_KEY not set. Falling back to rule-based experiment design.")
        else:
            logger.warning("anthropic library not installed. Using rule-based experiment design.")

    async def design_experiment(self, hypothesis: dict) -> ExperimentalDesign:
        """Design an experiment to test a hypothesis using Claude or rule-based fallback."""
        logger.info(f"Designing experiment for hypothesis: {hypothesis.get('title')}")

        # Try Claude first if available
        if self.use_claude and self.claude_client:
            try:
                logger.info("Using Claude Haiku for experiment design")
                design = await self._design_with_claude(hypothesis)
                logger.info(f"Claude designed experiment with budget: ${design.total_cost:,.0f}")
                return design
            except Exception as e:
                logger.warning(f"Claude design failed: {e}. Falling back to rule-based.")
                self.use_claude = False

        # Fallback: Rule-based design
        logger.info("Using rule-based experiment design")

        # Select appropriate experiment type
        experiment_type = self._select_experiment_type(hypothesis)

        # Design the experiment
        design = ExperimentalDesign(
            id=f"exp_{self.design_counter}",
            hypothesis_id=hypothesis.get("id", "unknown"),
            experiment_type=experiment_type,
            rigor_level=self._determine_rigor_level(hypothesis),
            title=self._generate_design_title(hypothesis),
            design_description=self._design_description(hypothesis, experiment_type),
            variables=hypothesis.get("variables", {}),
            sample_size=self._calculate_sample_size(hypothesis),
            sample_characteristics=self._define_sample(hypothesis),
            groups=self._define_groups(hypothesis, experiment_type),
            treatment_description=self._describe_treatment(hypothesis),
            control_description=self._describe_control(hypothesis),
            primary_measures=self._define_measures(hypothesis, primary=True),
            secondary_measures=self._define_measures(hypothesis, primary=False),
            measurement_schedule=self._define_measurement_schedule(experiment_type),
            procedures=self._generate_procedures(hypothesis, experiment_type),
            duration_weeks=self._estimate_duration(experiment_type, hypothesis),
            datasets_required=self._identify_datasets(hypothesis),
            budget=self._estimate_budget(hypothesis, experiment_type),
            total_cost=0,  # Will be calculated
            personnel_needed=self._define_personnel(hypothesis, experiment_type),
            equipment_needed=self._list_equipment(hypothesis, experiment_type),
            analysis_plan=self._plan_analysis(hypothesis, experiment_type),
            primary_analysis=self._primary_analysis(hypothesis),
            secondary_analyses=self._secondary_analyses(hypothesis),
            internal_validity_strategies=self._internal_validity_strategies(experiment_type),
            external_validity_considerations=self._external_validity_considerations(hypothesis),
            success_prediction=await self._predict_success(hypothesis, experiment_type),
            potential_risks=self._identify_risks(hypothesis, experiment_type),
            mitigation_strategies=self._mitigation_strategies(hypothesis),
            timeline_milestones=self._generate_timeline(experiment_type),
            critical_path=self._identify_critical_path(experiment_type),
            generated_at=datetime.now().isoformat(),
        )

        # Calculate total cost
        design.total_cost = sum(item.total_cost for item in design.budget)

        self.design_counter += 1
        self.designs[design.id] = design

        return design

    def _select_experiment_type(self, hypothesis: dict) -> ExperimentType:
        """Select appropriate experiment type based on hypothesis."""
        hyp_type = hypothesis.get("type", "mechanistic")
        complexity = hypothesis.get("complexity", "moderate")

        # Map hypothesis type to experiment type
        if hyp_type == "causal":
            return ExperimentType.RANDOMIZED_CONTROLLED_TRIAL
        elif hyp_type == "mechanistic":
            return ExperimentType.LABORATORY_EXPERIMENT
        elif hyp_type == "predictive":
            return ExperimentType.SIMULATION
        elif hyp_type == "boundary_condition":
            return ExperimentType.QUASI_EXPERIMENTAL
        else:
            return ExperimentType.OBSERVATIONAL_STUDY

    def _determine_rigor_level(self, hypothesis: dict) -> RigorLevel:
        """Determine required rigor level."""
        hyp_type = hypothesis.get("type", "mechanistic")

        if hyp_type in ["causal", "mechanistic"]:
            return RigorLevel.HIGH
        elif hyp_type in ["predictive", "comparative"]:
            return RigorLevel.MEDIUM
        else:
            return RigorLevel.LOW

    def _generate_design_title(self, hypothesis: dict) -> str:
        """Generate a descriptive title for the experiment."""
        hyp_title = hypothesis.get("title", "Hypothesis")
        return f"Experimental Test: {hyp_title}"

    def _design_description(self, hypothesis: dict, exp_type: ExperimentType) -> str:
        """Generate experiment design description."""
        type_descriptions = {
            ExperimentType.RANDOMIZED_CONTROLLED_TRIAL:
                "We will randomly assign participants to treatment and control conditions",
            ExperimentType.OBSERVATIONAL_STUDY:
                "We will measure variables in naturally occurring groups",
            ExperimentType.QUASI_EXPERIMENTAL:
                "We will use matched comparison groups without random assignment",
            ExperimentType.SIMULATION:
                "We will test the hypothesis using computational simulation",
            ExperimentType.LABORATORY_EXPERIMENT:
                "We will create a controlled laboratory environment",
            ExperimentType.AB_TEST:
                "We will conduct an online A/B test with continuous monitoring",
            ExperimentType.META_ANALYSIS:
                "We will synthesize results from existing studies",
        }

        return type_descriptions.get(
            exp_type,
            "We will conduct an experiment to test the hypothesis."
        )

    def _calculate_sample_size(self, hypothesis: dict) -> int:
        """Calculate required sample size."""
        hyp_type = hypothesis.get("type", "mechanistic")
        complexity = hypothesis.get("complexity", "moderate")

        # Base sample size by complexity
        base_sizes = {
            "simple": 64,
            "moderate": 128,
            "complex": 200,
        }

        base = base_sizes.get(complexity, 128)

        # Adjust for effect size expectations
        effect_size = hypothesis.get("scoring", {}).get("impact", 0.5)

        # Higher impact = expect larger effect = smaller sample needed
        if effect_size > 0.7:
            multiplier = 0.8
        elif effect_size < 0.4:
            multiplier = 1.5
        else:
            multiplier = 1.0

        return int(base * multiplier)

    def _define_sample(self, hypothesis: dict) -> list[str]:
        """Define sample characteristics."""
        return [
            "Randomized from target population",
            "Matched on key demographic variables",
            "Inclusion criteria explicitly defined",
            "Exclusion criteria specified",
            "Recruitment strategy documented",
        ]

    def _define_groups(self, hypothesis: dict, exp_type: ExperimentType) -> list[str]:
        """Define experimental groups/conditions."""
        if exp_type == ExperimentType.RANDOMIZED_CONTROLLED_TRIAL:
            return ["Treatment", "Control"]
        elif exp_type in [ExperimentType.QUASI_EXPERIMENTAL, ExperimentType.OBSERVATIONAL_STUDY]:
            return ["Group A", "Group B"]
        elif exp_type == ExperimentType.LABORATORY_EXPERIMENT:
            return ["Experimental", "Control"]
        elif exp_type == ExperimentType.AB_TEST:
            return ["Variant A", "Variant B"]
        else:
            return ["Primary Condition", "Comparison Condition"]

    def _describe_treatment(self, hypothesis: dict) -> str:
        """Describe the treatment/intervention."""
        statement = hypothesis.get("statement", "")
        return f"Apply intervention based on: {statement[:100]}"

    def _describe_control(self, hypothesis: dict) -> str:
        """Describe the control condition."""
        return "Waitlist control / Standard practice / No intervention"

    def _define_measures(self, hypothesis: dict, primary: bool = True) -> list[Measurement]:
        """Define measurements for the experiment."""
        measures = []

        dependent_vars = hypothesis.get("variables", {}).get("dependent", [])

        if primary:
            # Primary measures from dependent variables
            for i, var in enumerate(dependent_vars[:2]):
                measure = Measurement(
                    name=f"{var.get('name', 'Outcome')}",
                    construct=var.get("description", "Primary outcome"),
                    method=var.get("measurement_method", "Quantitative assessment"),
                    timing="Baseline, Post-intervention (4 weeks), Follow-up (8 weeks)",
                    expected_reliability=0.80,
                    validity_evidence=[
                        "Validated in prior literature",
                        "Pilot test with target population",
                    ]
                )
                measures.append(measure)
        else:
            # Secondary measures
            measure = Measurement(
                name="Process measure",
                construct="Implementation fidelity",
                method="Structured observation",
                timing="During intervention",
                expected_reliability=0.75,
            )
            measures.append(measure)

        return measures

    def _define_measurement_schedule(self, exp_type: ExperimentType) -> list[str]:
        """Define when measurements occur."""
        if exp_type == ExperimentType.AB_TEST:
            return ["Real-time", "Daily summary", "Weekly analysis"]
        elif exp_type == ExperimentType.SIMULATION:
            return ["Initialization", "Mid-run", "Final output"]
        else:
            return ["Baseline", "Post-intervention", "Follow-up"]

    def _generate_procedures(
        self,
        hypothesis: dict,
        exp_type: ExperimentType
    ) -> list[Procedure]:
        """Generate step-by-step procedures."""
        procedures = [
            Procedure(
                step_number=1,
                description="Screen and recruit participants",
                duration_minutes=30,
                responsible_party="Research coordinator",
                materials_required=["Screening form", "Information sheet"],
                success_criteria="Recruit target sample size"
            ),
            Procedure(
                step_number=2,
                description="Informed consent and baseline assessment",
                duration_minutes=45,
                responsible_party="Research assistant",
                materials_required=["Consent form", "Baseline survey", "Measurement instruments"],
                success_criteria="100% completion rate"
            ),
            Procedure(
                step_number=3,
                description="Random assignment (if RCT)",
                duration_minutes=10,
                responsible_party="Research coordinator",
                materials_required=["Randomization algorithm", "Assignment notification"],
                success_criteria="Successful allocation"
            ),
            Procedure(
                step_number=4,
                description="Intervention delivery",
                duration_minutes=60,
                responsible_party="Study interventionist",
                materials_required=["Intervention protocol", "Materials"],
                success_criteria="Protocol adherence > 90%"
            ),
            Procedure(
                step_number=5,
                description="Post-intervention assessment",
                duration_minutes=45,
                responsible_party="Research assistant",
                materials_required=["Outcome measures", "Blinded assessor"],
                success_criteria="100% completion rate"
            ),
            Procedure(
                step_number=6,
                description="Data management and quality check",
                duration_minutes=30,
                responsible_party="Data manager",
                materials_required=["Data entry system", "Validation rules"],
                success_criteria="Zero critical errors"
            ),
        ]

        return procedures

    def _estimate_duration(self, exp_type: ExperimentType, hypothesis: dict) -> int:
        """Estimate experiment duration in weeks."""
        config_type = exp_type.value
        default_duration = self.config.get("experiment_types", {}).get(
            config_type, {}
        ).get("typical_duration_weeks", 8)

        # Adjust based on sample size
        sample_size = self._calculate_sample_size(hypothesis)
        if sample_size > 500:
            default_duration += 4

        return default_duration

    def _identify_datasets(self, hypothesis: dict) -> list[DatasetRequirement]:
        """Identify required datasets."""
        datasets = []

        sample_size = self._calculate_sample_size(hypothesis)

        dataset = DatasetRequirement(
            name="Primary study dataset",
            description="Main data for testing the hypothesis",
            size_gb=max(1.0, sample_size / 10000),
            variables_needed=[
                v.get("name", "var")
                for v in hypothesis.get("variables", {}).get("independent", [])
            ],
            sample_size=sample_size,
            source="To be collected or identified",
            access_level="public",
            preprocessing_required=True,
            estimated_prep_hours=8,
        )
        datasets.append(dataset)

        return datasets

    def _estimate_budget(
        self,
        hypothesis: dict,
        exp_type: ExperimentType
    ) -> list[ResourceBudget]:
        """Estimate resource requirements and costs."""
        budget = []

        # Personnel costs
        duration = self._estimate_duration(exp_type, hypothesis)

        personnel_roles = [
            ("Principal Investigator", 5, 150),
            ("Postdoc/Senior Researcher", 30, 75),
            ("Graduate Student", 25, 25),
            ("Research Assistant", 20, 20),
        ]

        for role, hours_week, hourly_rate in personnel_roles:
            total_hours = hours_week * duration
            total_cost = total_hours * hourly_rate

            if total_cost > 0:
                budget.append(ResourceBudget(
                    category="Personnel",
                    item=role,
                    quantity=duration,
                    unit="weeks",
                    unit_cost=hours_week * hourly_rate,
                    total_cost=total_cost,
                    notes=f"{hours_week} hours/week"
                ))

        # Equipment/Services
        if exp_type in [ExperimentType.LABORATORY_EXPERIMENT]:
            budget.append(ResourceBudget(
                category="Equipment",
                item="Lab consumables",
                quantity=1,
                unit="month",
                unit_cost=200,
                total_cost=200 * duration,
                notes="Estimated consumables per month"
            ))

        if exp_type == ExperimentType.AB_TEST:
            budget.append(ResourceBudget(
                category="Services",
                item="Platform/hosting",
                quantity=duration,
                unit="weeks",
                unit_cost=100,
                total_cost=100 * duration,
            ))

        # Data/Computational
        sample_size = self._calculate_sample_size(hypothesis)
        storage_cost = max(10, sample_size / 100)  # GB

        budget.append(ResourceBudget(
            category="Services",
            item="Cloud storage and computing",
            quantity=storage_cost,
            unit="GB",
            unit_cost=0.05,
            total_cost=storage_cost * 0.05 * duration,
        ))

        return budget

    def _define_personnel(self, hypothesis: dict, exp_type: ExperimentType) -> dict:
        """Define personnel requirements."""
        return {
            "Principal Investigator": "5 hours/week",
            "Study Coordinator": "30 hours/week",
            "Research Assistant": "20 hours/week",
            "Data Manager": "10 hours/week",
        }

    def _list_equipment(self, hypothesis: dict, exp_type: ExperimentType) -> list[str]:
        """List required equipment."""
        equipment = ["Computers", "Data management system"]

        if exp_type == ExperimentType.LABORATORY_EXPERIMENT:
            equipment.extend(["Measurement instruments", "Lab space", "Calibration equipment"])

        if exp_type == ExperimentType.SIMULATION:
            equipment.extend(["High-performance computing", "Modeling software"])

        return equipment

    def _plan_analysis(self, hypothesis: dict, exp_type: ExperimentType) -> str:
        """Plan data analysis approach."""
        hyp_type = hypothesis.get("type", "mechanistic")

        plans = {
            "causal": "Intent-to-treat analysis with group comparisons",
            "mechanistic": "Pathway analysis with mediation testing",
            "predictive": "Model validation with cross-validation",
            "associative": "Correlation and regression analysis",
        }

        return plans.get(hyp_type, "Standard statistical analysis")

    def _primary_analysis(self, hypothesis: dict) -> str:
        """Specify primary statistical analysis."""
        sample_size = self._calculate_sample_size(hypothesis)

        if sample_size > 100:
            return "Mixed-effects modeling with group and time effects"
        else:
            return "Independent samples t-test or ANOVA"

    def _secondary_analyses(self, hypothesis: dict) -> list[str]:
        """Specify secondary analyses."""
        return [
            "Subgroup analysis by demographic characteristics",
            "Sensitivity analysis with alternative assumptions",
            "Effect size estimation with 95% confidence intervals",
        ]

    def _internal_validity_strategies(self, exp_type: ExperimentType) -> list[str]:
        """Strategies to ensure internal validity."""
        strategies = [
            "Clearly operationalize all variables",
            "Standardized measurement instruments",
            "Documented protocols with quality checks",
        ]

        if exp_type == ExperimentType.RANDOMIZED_CONTROLLED_TRIAL:
            strategies.extend([
                "Random assignment to conditions",
                "Blinded outcome assessment",
                "Intent-to-treat analysis",
            ])

        return strategies

    def _external_validity_considerations(self, hypothesis: dict) -> list[str]:
        """Considerations for generalizability."""
        return [
            "Clear inclusion/exclusion criteria",
            "Representative sampling when possible",
            "Documentation of sample characteristics",
            "Discussion of boundary conditions",
            "Recommendations for future research contexts",
        ]

    async def _predict_success(
        self,
        hypothesis: dict,
        exp_type: ExperimentType
    ) -> SuccessPrediction:
        """Predict probability of successful hypothesis confirmation."""
        # Base probability on hypothesis strength and feasibility
        novelty = hypothesis.get("scoring", {}).get("novelty", 0.5)
        feasibility = hypothesis.get("scoring", {}).get("feasibility", 0.5)
        impact = hypothesis.get("scoring", {}).get("impact", 0.5)
        testability = hypothesis.get("scoring", {}).get("testability", 0.5)

        # Success probability increases with clarity but decreases with novelty
        # (novel hypotheses less likely to be confirmed)
        probability = (
            0.3 +  # Base rate
            testability * 0.2 +  # Clear design
            feasibility * 0.15 +
            (0.5 - novelty) * 0.15  # Well-trodden territory
        )

        # Adjust for experiment type rigor
        rigor_multipliers = {
            ExperimentType.RANDOMIZED_CONTROLLED_TRIAL: 1.0,
            ExperimentType.LABORATORY_EXPERIMENT: 0.95,
            ExperimentType.QUASI_EXPERIMENTAL: 0.85,
            ExperimentType.SIMULATION: 0.80,
            ExperimentType.OBSERVATIONAL_STUDY: 0.75,
            ExperimentType.AB_TEST: 0.80,
            ExperimentType.META_ANALYSIS: 0.90,
        }

        probability *= rigor_multipliers.get(exp_type, 0.8)
        probability = max(0.1, min(0.95, probability))  # Bound 0.1-0.95

        return SuccessPrediction(
            probability_success=probability,
            expected_effect_size=hypothesis.get("scoring", {}).get("impact", 0.5),
            confidence_level=testability,
            success_factors=[
                "Clear hypothesis and operationalizations",
                "Adequate statistical power",
                "High measurement reliability",
                "Strong protocol adherence",
                "Minimal confounding",
            ],
            failure_factors=[
                "Insufficient sample size",
                "Measurement unreliability",
                "Uncontrolled confounds",
                "Implementation fidelity issues",
                "Attrition or missing data",
            ],
            breakeven_conditions=[
                "At least 80% statistical power",
                "Effect size ≥ 0.3 standard deviations",
                "Measurement reliability > 0.70",
                "Protocol adherence > 90%",
            ]
        )

    def _identify_risks(self, hypothesis: dict, exp_type: ExperimentType) -> list[str]:
        """Identify potential risks."""
        risks = [
            "Insufficient statistical power due to smaller than expected effect",
            "Measurement unreliability introducing noise",
            "Uncontrolled confounding variables",
            "Sample attrition reducing statistical power",
            "Implementation fidelity issues with intervention",
            "Generalizability concerns with specific sample",
            "Ethical considerations in intervention delivery",
        ]

        return risks[:5]

    def _mitigation_strategies(self, hypothesis: dict) -> list[str]:
        """Mitigation strategies for identified risks."""
        return [
            "Conduct power analysis and increase sample size if needed",
            "Use validated, reliable measurement instruments",
            "Identify and measure potential confounds",
            "Implement retention strategies to minimize attrition",
            "Use detailed protocols with fidelity monitoring",
            "Pre-register hypotheses and analysis plan",
            "Plan for multiple waves of replication",
        ]

    def _generate_timeline(self, exp_type: ExperimentType) -> list[dict]:
        """Generate project timeline with milestones."""
        duration = self.config.get("experiment_types", {}).get(
            exp_type.value, {}
        ).get("typical_duration_weeks", 8)

        milestones = [
            {
                "week": 1,
                "milestone": "Protocol finalization and IRB approval",
                "deliverable": "Approved protocol"
            },
            {
                "week": max(2, duration // 4),
                "milestone": "Recruitment and baseline assessment",
                "deliverable": f"Enrolled all {100 if duration < 10 else 200} participants"
            },
            {
                "week": max(3, duration // 2),
                "milestone": "Intervention delivery completed",
                "deliverable": "All interventions administered"
            },
            {
                "week": max(4, duration * 3 // 4),
                "milestone": "Post-intervention assessment",
                "deliverable": "All outcome data collected"
            },
            {
                "week": duration,
                "milestone": "Data analysis and report",
                "deliverable": "Final results and manuscript ready"
            },
        ]

        return milestones

    def _identify_critical_path(self, exp_type: ExperimentType) -> list[str]:
        """Identify critical path items."""
        return [
            "IRB approval",
            "Participant recruitment",
            "Intervention training and fidelity",
            "Outcome assessment and data collection",
            "Data analysis and interpretation",
        ]

    async def validate_design(self, design: ExperimentalDesign) -> dict:
        """Validate the experimental design."""
        issues = []
        warnings = []

        # Check sample size adequacy
        if design.sample_size < 30:
            issues.append("Sample size very small; power may be insufficient")

        # Check measurement reliability
        avg_reliability = sum(
            m.expected_reliability
            for m in design.primary_measures
        ) / max(1, len(design.primary_measures))

        if avg_reliability < 0.70:
            warnings.append(f"Average measurement reliability ({avg_reliability:.2f}) below recommended 0.70")

        # Check timeline feasibility
        total_person_weeks = sum(
            hours / 40 for hours in [
                int(h.split()[0]) if h else 0
                for h in design.personnel_needed.values()
            ]
        ) * design.duration_weeks

        if total_person_weeks > 2000:
            warnings.append("High personnel burden; consider streamlining")

        design.validation_status = "validated" if not issues else "needs_revision"

        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "warnings": warnings,
            "status": design.validation_status,
        }

    async def generate_protocol_document(self, design: ExperimentalDesign) -> str:
        """Generate a detailed protocol document."""
        doc = f"""
# RESEARCH PROTOCOL

## Title
{design.title}

## Hypothesis
{design.variables.get('hypothesis', 'To be tested')}

## Experiment Type
{design.experiment_type.value.replace('_', ' ').title()}

## Sample Size
{design.sample_size} participants

## Duration
{design.duration_weeks} weeks

## Research Procedures

"""
        for proc in design.procedures:
            doc += f"""
### Step {proc.step_number}: {proc.description}
- Duration: {proc.duration_minutes} minutes
- Responsible: {proc.responsible_party}
- Success Criteria: {proc.success_criteria}

"""

        doc += f"""
## Primary Outcomes

"""
        for measure in design.primary_measures:
            doc += f"""
- **{measure.name}**: {measure.construct}
  - Method: {measure.method}
  - Expected Reliability: {measure.expected_reliability:.2f}

"""

        doc += f"""
## Data Analysis Plan

{design.analysis_plan}

### Primary Analysis
{design.primary_analysis}

### Secondary Analyses
"""
        for analysis in design.secondary_analyses:
            doc += f"- {analysis}\n"

        doc += f"""

## Resources Required

### Personnel
"""
        for role, hours in design.personnel_needed.items():
            doc += f"- {role}: {hours}\n"

        doc += f"""

### Budget Summary
Total Estimated Cost: ${design.total_cost:,.0f}

### Equipment
"""
        for equipment in design.equipment_needed:
            doc += f"- {equipment}\n"

        return doc

    async def _design_with_claude(self, hypothesis: dict) -> ExperimentalDesign:
        """Design an experiment using Claude Haiku API."""
        # Prepare prompt for Claude
        prompt = f"""You are an expert research methodology specialist. Design a rigorous experiment to test this hypothesis.

HYPOTHESIS: {hypothesis.get('title')}
STATEMENT: {hypothesis.get('statement')}
BACKGROUND: {hypothesis.get('background', '')}

VARIABLES:
Independent: {hypothesis.get('independent_variables', [])}
Dependent: {hypothesis.get('dependent_variables', [])}
Control: {hypothesis.get('control_variables', [])}

Design an experiment with:
1. Clear experimental type (randomized_controlled_trial, laboratory_experiment, simulation, etc.)
2. Appropriate sample size and characteristics
3. Detailed procedures and measurements
4. Realistic timeline and budget estimation
5. Identified datasets or resources needed

Return ONLY valid JSON with this structure (no other text):
{{
  "experiment_type": "laboratory_experiment|randomized_controlled_trial|simulation|...",
  "title": "Clear experiment title",
  "sample_size": 120,
  "duration_weeks": 12,
  "total_budget": 45000,
  "primary_measures": [
    {{"name": "measure_name", "method": "measurement method", "timing": "when measured"}}
  ],
  "secondary_measures": [
    {{"name": "measure_name", "method": "measurement method", "timing": "when measured"}}
  ],
  "procedures": [
    {{"phase": "Phase name", "description": "What happens", "duration": "Time"}}
  ],
  "groups": [
    {{"name": "Treatment", "description": "What group receives", "n": 60}}
  ],
  "datasets_required": ["Dataset 1", "Dataset 2"],
  "equipment_needed": ["Equipment 1"],
  "potential_risks": ["Risk 1", "Risk 2"],
  "mitigation_strategies": ["Mitigation 1"],
  "success_prediction_probability": 0.68
}}"""

        # Call Claude
        response = self.claude_client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=2048,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )

        # Parse response
        response_text = response.content[0].text
        json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
        if not json_match:
            raise ValueError("Claude did not return valid JSON")

        design_data = json.loads(json_match.group())

        # Convert to ExperimentalDesign object
        experiment_type = ExperimentType(design_data.get("experiment_type", "laboratory_experiment"))

        design = ExperimentalDesign(
            id=f"claude_exp_{self.design_counter}",
            hypothesis_id=hypothesis.get("id", "unknown"),
            experiment_type=experiment_type,
            rigor_level=RigorLevel.HIGH,
            title=design_data.get("title", "Experiment"),
            design_description=f"Experiment designed by Claude: {design_data.get('title')}",
            variables={},
            sample_size=int(design_data.get("sample_size", 100)),
            sample_characteristics="Specified in procedures",
            groups=[
                Group(
                    name=g.get("name", "Group"),
                    description=g.get("description", ""),
                    n=int(g.get("n", 50)),
                )
                for g in design_data.get("groups", [])
            ],
            treatment_description="See procedures",
            control_description="See procedures",
            primary_measures=[
                Measurement(
                    name=m.get("name", ""),
                    construct=m.get("name", ""),
                    method=m.get("method", ""),
                    timing=m.get("timing", ""),
                    expected_reliability=0.8,
                )
                for m in design_data.get("primary_measures", [])
            ],
            secondary_measures=[
                Measurement(
                    name=m.get("name", ""),
                    construct=m.get("name", ""),
                    method=m.get("method", ""),
                    timing=m.get("timing", ""),
                    expected_reliability=0.7,
                )
                for m in design_data.get("secondary_measures", [])
            ],
            measurement_schedule="As specified in procedures",
            procedures=[
                Procedure(
                    phase=p.get("phase", ""),
                    description=p.get("description", ""),
                    duration=p.get("duration", ""),
                    personnel_required="Research team",
                )
                for p in design_data.get("procedures", [])
            ],
            duration_weeks=int(design_data.get("duration_weeks", 12)),
            datasets_required=design_data.get("datasets_required", []),
            budget=design_data.get("total_budget", 50000),
            total_cost=float(design_data.get("total_budget", 50000)),
            equipment_needed=design_data.get("equipment_needed", []),
            potential_risks=design_data.get("potential_risks", []),
            mitigation_strategies=design_data.get("mitigation_strategies", []),
            success_prediction=SuccessPrediction(
                probability_success=float(design_data.get("success_prediction_probability", 0.65)),
                confidence_level=0.7,
                reasoning="Determined by Claude analysis",
            ),
            created_at=datetime.now().isoformat(),
        )

        self.design_counter += 1
        return design

    async def close(self) -> None:
        """Clean up resources."""
        pass


async def main():
    """Example usage of the Experiment Agent."""
    from agents.hypothesis_agent import Hypothesis, HypothesisType, ComplexityLevel

    # Create a sample hypothesis
    sample_hypothesis = {
        "id": "hyp_001",
        "title": "Attention mechanisms improve model interpretability",
        "statement": "If we use attention mechanisms, then model interpretability increases",
        "type": "causal",
        "complexity": "moderate",
        "scoring": {
            "novelty": 0.65,
            "feasibility": 0.75,
            "impact": 0.80,
            "testability": 0.72,
        },
        "variables": {
            "independent": [{"name": "attention_mechanism", "description": "Presence of attention"}],
            "dependent": [{"name": "interpretability", "description": "Model explanation quality"}],
        }
    }

    print("🧪 Experiment Agent - Example\n")
    print(f"Hypothesis: {sample_hypothesis['title']}\n")

    agent = ExperimentAgent()

    try:
        # Design experiment
        print("📐 Designing experimental protocol...")
        design = await agent.design_experiment(sample_hypothesis)

        print(f"\n✓ Experiment design completed\n")

        print(f"Experiment Type: {design.experiment_type.value}")
        print(f"Rigor Level: {design.rigor_level.value}")
        print(f"Sample Size: {design.sample_size}")
        print(f"Duration: {design.duration_weeks} weeks")
        print(f"Total Budget: ${design.total_cost:,.0f}")
        print(f"\nSuccess Probability: {design.success_prediction.probability_success:.1%}")

        # Validate
        print("\n✓ Validating design...")
        validation = await agent.validate_design(design)

        print(f"Valid: {validation['valid']}")
        if validation['issues']:
            print("Issues:")
            for issue in validation['issues']:
                print(f"  - {issue}")
        if validation['warnings']:
            print("Warnings:")
            for warning in validation['warnings']:
                print(f"  - {warning}")

        # Generate protocol document
        print("\n📄 Generating protocol document...")
        protocol = await agent.generate_protocol_document(design)
        print("\nProtocol (first 1000 chars):")
        print(protocol[:1000] + "...")

        # Show JSON export
        print("\n📊 Design Summary (JSON):")
        import json
        design_dict = design.to_dict()
        print(json.dumps(design_dict, indent=2)[:500] + "...")

    finally:
        await agent.close()


if __name__ == "__main__":
    asyncio.run(main())
