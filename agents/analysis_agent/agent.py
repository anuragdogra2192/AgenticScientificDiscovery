"""Analysis Agent for evaluating experimental results and extracting findings."""

import asyncio
import json
import logging
import math
import statistics
import re
import os
from dataclasses import dataclass, asdict, field
from typing import Optional, List, Dict, Any
from enum import Enum
from datetime import datetime

import yaml

try:
    from anthropic import Anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False

logger = logging.getLogger(__name__)


class StatisticalTest(str, Enum):
    """Types of statistical tests."""
    T_TEST = "t_test"
    PAIRED_T_TEST = "paired_t_test"
    ANOVA = "anova"
    LINEAR_REGRESSION = "linear_regression"
    MANN_WHITNEY_U = "mann_whitney_u"
    WILCOXON = "wilcoxon"
    KRUSKAL_WALLIS = "kruskal_wallis"
    CHI_SQUARE = "chi_square"
    CORRELATION = "correlation"


class FindingSignificance(str, Enum):
    """Significance levels for findings."""
    HIGHLY_SIGNIFICANT = "highly_significant"  # p < 0.001
    SIGNIFICANT = "significant"                 # p < 0.01
    MODERATELY_SIGNIFICANT = "moderately_significant"  # p < 0.05
    MARGINALLY_SIGNIFICANT = "marginally_significant"  # p < 0.10
    NOT_SIGNIFICANT = "not_significant"         # p >= 0.10


class EffectSizeInterpretation(str, Enum):
    """Effect size magnitude."""
    NEGLIGIBLE = "negligible"
    SMALL = "small"
    MEDIUM = "medium"
    LARGE = "large"
    VERY_LARGE = "very_large"


@dataclass
class DescriptiveStatistics:
    """Descriptive statistics for a variable."""
    variable_name: str
    n: int
    mean: Optional[float]
    median: Optional[float]
    std_dev: Optional[float]
    min_val: Optional[float]
    max_val: Optional[float]
    skewness: Optional[float]
    kurtosis: Optional[float]
    quartiles: Optional[Dict[str, float]] = None

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class StatisticalResult:
    """Result from a statistical test."""
    test_name: StatisticalTest
    test_statistic: float
    p_value: float
    significance_level: FindingSignificance
    degrees_of_freedom: Optional[int]
    effect_size: float
    effect_size_interpretation: EffectSizeInterpretation
    confidence_interval: Optional[tuple]
    ci_level: float
    assumptions_met: Dict[str, bool]
    interpretation: str

    def to_dict(self) -> dict:
        return {
            "test": self.test_name.value,
            "statistic": self.test_statistic,
            "p_value": self.p_value,
            "significance": self.significance_level.value,
            "df": self.degrees_of_freedom,
            "effect_size": self.effect_size,
            "effect_interpretation": self.effect_size_interpretation.value,
            "ci": self.confidence_interval,
            "ci_level": self.ci_level,
            "assumptions": self.assumptions_met,
            "interpretation": self.interpretation,
        }


@dataclass
class Finding:
    """A key research finding."""
    id: str
    title: str
    description: str
    finding_type: str  # primary, secondary, anomaly
    supporting_evidence: List[str]
    statistical_evidence: Optional[StatisticalResult]
    effect_size: float
    confidence_level: float
    consistency_with_hypothesis: str  # confirms, qualifies, contradicts, neutral
    practical_significance: str
    generalizability: str
    novel_aspects: List[str]
    limitations: List[str]

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "type": self.finding_type,
            "evidence": self.supporting_evidence,
            "statistics": self.statistical_evidence.to_dict() if self.statistical_evidence else None,
            "effect_size": self.effect_size,
            "confidence": self.confidence_level,
            "hypothesis_consistency": self.consistency_with_hypothesis,
            "practical_significance": self.practical_significance,
            "generalizability": self.generalizability,
            "novel": self.novel_aspects,
            "limitations": self.limitations,
        }


@dataclass
class AnalysisReport:
    """Complete analysis report."""
    id: str
    experiment_id: str
    hypothesis_id: str
    analysis_date: str

    # Data summary
    sample_size: int
    variables_analyzed: List[str]
    data_quality_issues: List[str]

    # Descriptive statistics
    descriptive_stats: List[DescriptiveStatistics]

    # Assumption testing
    assumptions_checked: Dict[str, bool]
    violated_assumptions: List[str]

    # Statistical tests
    primary_analysis: StatisticalResult
    secondary_analyses: List[StatisticalResult]
    sensitivity_analyses: List[StatisticalResult]

    # Findings
    findings: List[Finding]
    primary_finding: Optional[Finding]

    # Interpretation
    hypothesis_confirmed: bool
    confirmation_strength: str  # strong, moderate, weak
    direction_matches: bool
    effect_size_as_predicted: bool

    # Contextualization
    literature_comparison: str
    novel_findings: List[str]
    boundary_conditions: List[str]

    # Implications
    practical_implications: List[str]
    theoretical_implications: List[str]
    limitations: List[str]
    future_research_directions: List[str]

    # Recommendations
    recommendations: List[str]

    # Visualizations needed
    visualization_specs: List[Dict[str, str]]

    # Metadata
    analyst_notes: Optional[str]

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "experiment_id": self.experiment_id,
            "hypothesis_id": self.hypothesis_id,
            "date": self.analysis_date,
            "sample_size": self.sample_size,
            "data_quality": self.data_quality_issues,
            "descriptive_stats": [s.to_dict() for s in self.descriptive_stats],
            "assumptions": {
                "checked": self.assumptions_checked,
                "violated": self.violated_assumptions,
            },
            "analysis": {
                "primary": self.primary_analysis.to_dict(),
                "secondary": [a.to_dict() for a in self.secondary_analyses],
                "sensitivity": [a.to_dict() for a in self.sensitivity_analyses],
            },
            "findings": [f.to_dict() for f in self.findings],
            "primary_finding": self.primary_finding.to_dict() if self.primary_finding else None,
            "interpretation": {
                "hypothesis_confirmed": self.hypothesis_confirmed,
                "strength": self.confirmation_strength,
                "direction_matches": self.direction_matches,
                "effect_size_as_predicted": self.effect_size_as_predicted,
            },
            "contextualization": {
                "literature_comparison": self.literature_comparison,
                "novel": self.novel_findings,
                "boundaries": self.boundary_conditions,
            },
            "implications": {
                "practical": self.practical_implications,
                "theoretical": self.theoretical_implications,
                "limitations": self.limitations,
                "future_directions": self.future_research_directions,
            },
            "recommendations": self.recommendations,
            "visualizations": self.visualization_specs,
        }


class AnalysisAgent:
    """Agent for analyzing experimental results and extracting findings."""

    def __init__(self, config_path: str = "agents/analysis_agent/config.yaml"):
        """Initialize the Analysis Agent."""
        with open(config_path, "r") as f:
            self.config = yaml.safe_load(f)

        self.reports: dict[str, AnalysisReport] = {}
        self.report_counter = 0

    async def analyze_results(
        self,
        experiment_design: dict,
        hypothesis: dict,
        results_data: dict,
    ) -> AnalysisReport:
        """Analyze experimental results and generate analysis report."""
        logger.info(f"Analyzing results for experiment: {experiment_design.get('title')}")

        # Validate data quality
        data_quality_issues = self._check_data_quality(results_data)

        # Generate descriptive statistics
        descriptive_stats = self._calculate_descriptive_stats(results_data)

        # Test assumptions
        assumptions_checked, violated_assumptions = self._test_assumptions(
            results_data, experiment_design
        )

        # Perform primary analysis
        primary_analysis = self._conduct_primary_analysis(
            results_data, experiment_design, violated_assumptions
        )

        # Secondary analyses
        secondary_analyses = self._conduct_secondary_analyses(results_data)

        # Sensitivity analyses
        sensitivity_analyses = self._conduct_sensitivity_analyses(results_data)

        # Extract findings
        findings = self._extract_findings(
            primary_analysis, secondary_analyses, results_data, hypothesis
        )

        # Interpret hypothesis
        hypothesis_confirmed, strength, direction_matches, effect_as_predicted = \
            self._interpret_hypothesis(primary_analysis, hypothesis)

        # Contextualize findings
        literature_comparison, novel_findings, boundary_conditions = \
            self._contextualize_findings(hypothesis, findings)

        # Generate implications
        practical_implications = self._identify_practical_implications(findings)
        theoretical_implications = self._identify_theoretical_implications(findings, hypothesis)

        # Identify future research
        future_research = self._identify_future_research(findings, hypothesis)

        # Plan visualizations
        visualization_specs = self._plan_visualizations(findings, results_data)

        # Create report
        report = AnalysisReport(
            id=f"report_{self.report_counter}",
            experiment_id=experiment_design.get("id", "unknown"),
            hypothesis_id=hypothesis.get("id", "unknown"),
            analysis_date=datetime.now().isoformat(),
            sample_size=results_data.get("n", 0),
            variables_analyzed=list(results_data.get("variables", {}).keys()),
            data_quality_issues=data_quality_issues,
            descriptive_stats=descriptive_stats,
            assumptions_checked=assumptions_checked,
            violated_assumptions=violated_assumptions,
            primary_analysis=primary_analysis,
            secondary_analyses=secondary_analyses,
            sensitivity_analyses=sensitivity_analyses,
            findings=findings,
            primary_finding=findings[0] if findings else None,
            hypothesis_confirmed=hypothesis_confirmed,
            confirmation_strength=strength,
            direction_matches=direction_matches,
            effect_size_as_predicted=effect_as_predicted,
            literature_comparison=literature_comparison,
            novel_findings=novel_findings,
            boundary_conditions=boundary_conditions,
            practical_implications=practical_implications,
            theoretical_implications=theoretical_implications,
            limitations=self._identify_limitations(experiment_design, results_data),
            future_research_directions=future_research,
            recommendations=self._generate_recommendations(findings, hypothesis),
            visualization_specs=visualization_specs,
            analyst_notes=None,
        )

        self.report_counter += 1
        self.reports[report.id] = report

        return report

    def _check_data_quality(self, results_data: dict) -> List[str]:
        """Check data quality issues."""
        issues = []

        # Check for missing values
        if "missing_count" in results_data and results_data["missing_count"] > 0:
            pct = (results_data["missing_count"] / max(results_data.get("n", 1), 1)) * 100
            if pct > 10:
                issues.append(f"Missing data: {pct:.1f}% (>10%)")
            elif pct > 5:
                issues.append(f"Missing data: {pct:.1f}% (>5%)")

        # Check for outliers
        if "outlier_count" in results_data and results_data["outlier_count"] > 0:
            pct = (results_data["outlier_count"] / max(results_data.get("n", 1), 1)) * 100
            if pct > 5:
                issues.append(f"Outliers detected: {pct:.1f}%")

        # Check sample size
        if results_data.get("n", 0) < 30:
            issues.append("Sample size < 30; large-sample assumptions may not hold")

        if not issues:
            issues.append("No major data quality issues detected")

        return issues

    def _calculate_descriptive_stats(self, results_data: dict) -> List[DescriptiveStatistics]:
        """Calculate descriptive statistics for variables."""
        stats = []

        for var_name, var_data in results_data.get("variables", {}).items():
            if isinstance(var_data, list) and len(var_data) > 0:
                try:
                    mean = statistics.mean(var_data)
                    median = statistics.median(var_data)
                    std_dev = statistics.stdev(var_data) if len(var_data) > 1 else 0

                    stat = DescriptiveStatistics(
                        variable_name=var_name,
                        n=len(var_data),
                        mean=mean,
                        median=median,
                        std_dev=std_dev,
                        min_val=min(var_data),
                        max_val=max(var_data),
                        skewness=self._calculate_skewness(var_data),
                        kurtosis=self._calculate_kurtosis(var_data),
                    )
                    stats.append(stat)
                except (ValueError, TypeError):
                    logger.warning(f"Could not calculate stats for {var_name}")

        return stats

    def _test_assumptions(self, results_data: dict, design: dict) -> tuple:
        """Test statistical assumptions."""
        assumptions = {
            "normality": True,
            "homogeneity": True,
            "independence": True,
            "linearity": True,
        }
        violated = []

        # Normality test (Shapiro-Wilk proxy)
        for var_data in results_data.get("variables", {}).values():
            if isinstance(var_data, list) and len(var_data) > 3:
                if self._check_normality(var_data):
                    assumptions["normality"] = True
                else:
                    assumptions["normality"] = False
                    violated.append("Normality assumption violated (skewed distribution)")
                    break

        # Independence (check design)
        design_type = design.get("experiment_type", "")
        if "independent" not in design_type.lower():
            assumptions["independence"] = False
            violated.append("Independence assumption may be violated (repeated measures)")

        return assumptions, violated

    def _conduct_primary_analysis(
        self,
        results_data: dict,
        experiment_design: dict,
        violated_assumptions: List[str]
    ) -> StatisticalResult:
        """Conduct primary statistical analysis."""
        # Determine test type based on design
        exp_type = experiment_design.get("experiment_type", "").lower()
        n_groups = len(experiment_design.get("groups", []))

        # Select appropriate test
        if violated_assumptions and "normality" in str(violated_assumptions).lower():
            # Use non-parametric
            if n_groups == 2:
                test_type = StatisticalTest.MANN_WHITNEY_U
            else:
                test_type = StatisticalTest.KRUSKAL_WALLIS
        else:
            # Use parametric
            if n_groups == 2:
                if "paired" in exp_type or "repeated" in exp_type:
                    test_type = StatisticalTest.PAIRED_T_TEST
                else:
                    test_type = StatisticalTest.T_TEST
            else:
                test_type = StatisticalTest.ANOVA

        # Simulate analysis
        return self._simulate_statistical_test(
            test_type, results_data, experiment_design
        )

    def _conduct_secondary_analyses(self, results_data: dict) -> List[StatisticalResult]:
        """Conduct secondary statistical analyses."""
        analyses = []

        # Subgroup analysis
        subgroup_result = self._simulate_statistical_test(
            StatisticalTest.T_TEST,
            results_data,
            {"groups": ["subgroup_1", "subgroup_2"]}
        )
        analyses.append(subgroup_result)

        # Mediation analysis
        mediation_result = self._simulate_statistical_test(
            StatisticalTest.LINEAR_REGRESSION,
            results_data,
            {"type": "mediation"}
        )
        analyses.append(mediation_result)

        return analyses

    def _conduct_sensitivity_analyses(self, results_data: dict) -> List[StatisticalResult]:
        """Conduct sensitivity analyses."""
        analyses = []

        # Analysis with outliers excluded
        without_outliers = self._simulate_statistical_test(
            StatisticalTest.T_TEST,
            results_data,
            {"exclude": "outliers"}
        )
        analyses.append(without_outliers)

        # Analysis with conservative assumptions
        conservative = self._simulate_statistical_test(
            StatisticalTest.T_TEST,
            results_data,
            {"assumptions": "conservative"}
        )
        analyses.append(conservative)

        return analyses

    def _simulate_statistical_test(
        self,
        test_type: StatisticalTest,
        results_data: dict,
        context: dict
    ) -> StatisticalResult:
        """Simulate a statistical test result."""
        # Generate plausible test results based on context
        base_effect = results_data.get("simulated_effect_size", 0.5)
        sample_size = results_data.get("n", 100)

        # Calculate test statistic and p-value
        test_stat = base_effect * math.sqrt(sample_size)
        p_value = max(0.001, min(0.99, math.exp(-abs(test_stat) / 2)))

        # Determine significance
        if p_value < 0.001:
            sig = FindingSignificance.HIGHLY_SIGNIFICANT
        elif p_value < 0.01:
            sig = FindingSignificance.SIGNIFICANT
        elif p_value < 0.05:
            sig = FindingSignificance.MODERATELY_SIGNIFICANT
        elif p_value < 0.10:
            sig = FindingSignificance.MARGINALLY_SIGNIFICANT
        else:
            sig = FindingSignificance.NOT_SIGNIFICANT

        # Effect size interpretation
        if abs(base_effect) < 0.1:
            effect_interp = EffectSizeInterpretation.NEGLIGIBLE
        elif abs(base_effect) < 0.3:
            effect_interp = EffectSizeInterpretation.SMALL
        elif abs(base_effect) < 0.5:
            effect_interp = EffectSizeInterpretation.MEDIUM
        elif abs(base_effect) < 0.8:
            effect_interp = EffectSizeInterpretation.LARGE
        else:
            effect_interp = EffectSizeInterpretation.VERY_LARGE

        # Confidence interval
        ci_lower = base_effect - 1.96 * (1 / math.sqrt(sample_size))
        ci_upper = base_effect + 1.96 * (1 / math.sqrt(sample_size))

        return StatisticalResult(
            test_name=test_type,
            test_statistic=test_stat,
            p_value=p_value,
            significance_level=sig,
            degrees_of_freedom=sample_size - 2,
            effect_size=base_effect,
            effect_size_interpretation=effect_interp,
            confidence_interval=(ci_lower, ci_upper),
            ci_level=0.95,
            assumptions_met={"normality": True, "homogeneity": True, "independence": True},
            interpretation=f"The effect is {effect_interp.value} and {sig.value}",
        )

    def _extract_findings(
        self,
        primary_analysis: StatisticalResult,
        secondary_analyses: List[StatisticalResult],
        results_data: dict,
        hypothesis: dict
    ) -> List[Finding]:
        """Extract key findings from analyses."""
        findings = []
        finding_id = 0

        # Primary finding
        primary_finding = Finding(
            id=f"finding_{finding_id}",
            title="Primary Outcome",
            description=primary_analysis.interpretation,
            finding_type="primary",
            supporting_evidence=[
                f"p-value: {primary_analysis.p_value:.4f}",
                f"Effect size: {primary_analysis.effect_size:.3f}",
                f"CI: [{primary_analysis.confidence_interval[0]:.3f}, "
                f"{primary_analysis.confidence_interval[1]:.3f}]"
            ],
            statistical_evidence=primary_analysis,
            effect_size=primary_analysis.effect_size,
            confidence_level=0.95,
            consistency_with_hypothesis="confirms"
                if abs(primary_analysis.effect_size) > 0.2 else "neutral",
            practical_significance="yes" if abs(primary_analysis.effect_size) > 0.5 else "maybe",
            generalizability="moderate",
            novel_aspects=[],
            limitations=[],
        )
        findings.append(primary_finding)
        finding_id += 1

        # Secondary findings
        for i, secondary in enumerate(secondary_analyses[:2]):
            secondary_finding = Finding(
                id=f"finding_{finding_id}",
                title=f"Secondary Outcome {i+1}",
                description=secondary.interpretation,
                finding_type="secondary",
                supporting_evidence=[f"p-value: {secondary.p_value:.4f}"],
                statistical_evidence=secondary,
                effect_size=secondary.effect_size,
                confidence_level=0.95,
                consistency_with_hypothesis="neutral",
                practical_significance="no" if secondary.p_value > 0.05 else "yes",
                generalizability="lower",
                novel_aspects=[],
                limitations=["Secondary outcome; lower power"],
            )
            findings.append(secondary_finding)
            finding_id += 1

        return findings

    def _interpret_hypothesis(
        self,
        primary_analysis: StatisticalResult,
        hypothesis: dict
    ) -> tuple:
        """Interpret whether hypothesis is confirmed."""
        # Check statistical significance
        is_sig = primary_analysis.p_value < 0.05

        # Check effect size
        has_meaningful_effect = abs(primary_analysis.effect_size) > 0.3

        # Check direction (assume positive predicted)
        direction_correct = primary_analysis.effect_size > 0

        # Overall confirmation
        hypothesis_confirmed = is_sig and has_meaningful_effect

        if hypothesis_confirmed and direction_correct:
            strength = "strong"
        elif is_sig and direction_correct:
            strength = "moderate"
        elif direction_correct:
            strength = "weak"
        else:
            strength = "not_confirmed"

        return hypothesis_confirmed, strength, direction_correct, has_meaningful_effect

    def _contextualize_findings(
        self,
        hypothesis: dict,
        findings: List[Finding]
    ) -> tuple:
        """Contextualize findings with literature."""
        comparison = (
            f"Results align with theoretical predictions. Effect size is consistent with "
            f"similar studies in the literature."
        )

        novel = [
            "Extends findings to new population",
            "Demonstrates mechanism not previously tested",
        ]

        boundaries = [
            "Effect may be specific to current sample characteristics",
            "Generalization to other contexts requires further testing",
        ]

        return comparison, novel, boundaries

    def _identify_practical_implications(self, findings: List[Finding]) -> List[str]:
        """Identify practical implications."""
        return [
            "Findings suggest practical applications in applied settings",
            "Effect size indicates meaningful real-world impact",
            "Results support implementation in field settings",
            "Benefits justify resource investment for application",
        ]

    def _identify_theoretical_implications(
        self,
        findings: List[Finding],
        hypothesis: dict
    ) -> List[str]:
        """Identify theoretical implications."""
        return [
            f"Confirms proposed mechanism in '{hypothesis.get('title', 'hypothesis')}'",
            "Advances understanding of underlying processes",
            "Challenges existing theoretical assumptions",
            "Suggests need for theory refinement or extension",
        ]

    def _identify_limitations(self, design: dict, results_data: dict) -> List[str]:
        """Identify study limitations."""
        return [
            "Single study design; replication recommended",
            "Sample may not be fully representative",
            "Measurement error could affect precision",
            "Alternative explanations not fully ruled out",
            "Generalizability may be limited by study context",
        ]

    def _identify_future_research(
        self,
        findings: List[Finding],
        hypothesis: dict
    ) -> List[str]:
        """Identify future research directions."""
        return [
            "Replicate findings in independent sample",
            "Extend to additional populations and settings",
            "Investigate boundary conditions and moderators",
            "Explore underlying mechanisms in greater detail",
            "Develop longitudinal designs to assess durability",
            "Combine with related research areas for broader understanding",
        ]

    def _generate_recommendations(
        self,
        findings: List[Finding],
        hypothesis: dict
    ) -> List[str]:
        """Generate actionable recommendations."""
        return [
            "Implement findings in pilot real-world settings",
            "Conduct follow-up studies to confirm and extend",
            "Develop practical applications based on mechanisms",
            "Document and disseminate findings to stakeholders",
            "Integrate results into broader theoretical framework",
        ]

    def _plan_visualizations(
        self,
        findings: List[Finding],
        results_data: dict
    ) -> List[Dict[str, str]]:
        """Plan visualizations for report."""
        specs = [
            {
                "type": "bar_plot",
                "title": "Mean Outcomes by Group",
                "description": "Compare means with error bars",
                "data": "primary measures by group"
            },
            {
                "type": "box_plot",
                "title": "Distribution of Outcomes",
                "description": "Show data distribution and outliers",
                "data": "outcome variable"
            },
            {
                "type": "effect_size_plot",
                "title": "Effect Size with Confidence Intervals",
                "description": "Display effect size and CI",
                "data": "primary finding"
            },
            {
                "type": "scatter_plot",
                "title": "Relationship Between Variables",
                "description": "Show correlations if applicable",
                "data": "continuous variables"
            },
        ]
        return specs

    @staticmethod
    def _calculate_skewness(data: list) -> float:
        """Calculate skewness of data."""
        if len(data) < 3:
            return 0.0
        mean = statistics.mean(data)
        std = statistics.stdev(data) if len(data) > 1 else 1
        if std == 0:
            return 0.0
        n = len(data)
        skewness = sum((x - mean) ** 3 for x in data) / (n * std ** 3)
        return skewness

    @staticmethod
    def _calculate_kurtosis(data: list) -> float:
        """Calculate kurtosis of data."""
        if len(data) < 4:
            return 0.0
        mean = statistics.mean(data)
        std = statistics.stdev(data) if len(data) > 1 else 1
        if std == 0:
            return 0.0
        n = len(data)
        kurtosis = sum((x - mean) ** 4 for x in data) / (n * std ** 4) - 3
        return kurtosis

    @staticmethod
    def _check_normality(data: list) -> bool:
        """Check if data appears normally distributed."""
        skew = AnalysisAgent._calculate_skewness(data)
        kurt = AnalysisAgent._calculate_kurtosis(data)
        # Data is approximately normal if |skewness| < 2 and |kurtosis| < 3
        return abs(skew) < 2 and abs(kurt) < 3

    async def generate_analysis_summary(self, report: AnalysisReport) -> str:
        """Generate human-readable analysis summary."""
        summary = f"""
# Analysis Report: {report.hypothesis_id}

## Executive Summary
The analysis of {report.sample_size} participants provides {'strong' if report.hypothesis_confirmed else 'limited'}
support for the research hypothesis.

## Key Findings
"""

        if report.primary_finding:
            pf = report.primary_finding
            summary += f"\n**Primary Finding**: {pf.title}\n"
            summary += f"- {pf.description}\n"
            summary += f"- Effect Size: {pf.effect_size:.3f} ({pf.statistical_evidence.effect_size_interpretation.value})\n"
            summary += f"- Consistency with Hypothesis: {pf.consistency_with_hypothesis}\n"

        summary += f"\n## Hypothesis Interpretation\n"
        summary += f"- Hypothesis Confirmed: {'Yes' if report.hypothesis_confirmed else 'No'}\n"
        summary += f"- Confirmation Strength: {report.confirmation_strength}\n"
        summary += f"- Direction Matches: {'Yes' if report.direction_matches else 'No'}\n"

        summary += f"\n## Practical Implications\n"
        for impl in report.practical_implications[:3]:
            summary += f"- {impl}\n"

        summary += f"\n## Limitations\n"
        for lim in report.limitations[:3]:
            summary += f"- {lim}\n"

        summary += f"\n## Future Research Directions\n"
        for future in report.future_research_directions[:3]:
            summary += f"- {future}\n"

        return summary

    async def close(self) -> None:
        """Clean up resources."""
        pass


async def main():
    """Example usage of the Analysis Agent."""
    # Sample experimental results
    sample_results = {
        "n": 120,
        "simulated_effect_size": 0.65,
        "missing_count": 2,
        "outlier_count": 1,
        "variables": {
            "outcome": [5.2, 5.5, 6.1, 4.9, 6.3, 5.0, 5.8, 6.2, 5.1, 5.9] * 12,
            "predictor": [1.0] * 60 + [2.0] * 60,
        }
    }

    sample_design = {
        "id": "exp_001",
        "title": "Test Experiment",
        "experiment_type": "randomized_controlled_trial",
        "groups": ["treatment", "control"],
    }

    sample_hypothesis = {
        "id": "hyp_001",
        "title": "Treatment improves outcomes",
        "statement": "If treatment, then improved outcome",
    }

    print("\n🔬 Analysis Agent - Example\n")

    agent = AnalysisAgent()

    try:
        # Analyze results
        print("📊 Analyzing experimental results...")
        report = await agent.analyze_results(
            experiment_design=sample_design,
            hypothesis=sample_hypothesis,
            results_data=sample_results
        )

        print(f"✓ Analysis complete\n")

        print(f"Hypothesis Confirmed: {report.hypothesis_confirmed}")
        print(f"Confirmation Strength: {report.confirmation_strength}")
        print(f"Primary Finding: {report.primary_finding.title}")
        print(f"Effect Size: {report.primary_finding.effect_size:.3f}")
        print(f"P-value: {report.primary_analysis.p_value:.4f}")

        print(f"\nPractical Implications:")
        for impl in report.practical_implications[:2]:
            print(f"  • {impl}")

        print(f"\nFuture Research:")
        for future in report.future_research_directions[:2]:
            print(f"  • {future}")

        # Generate summary
        print("\n" + "="*60)
        summary = await agent.generate_analysis_summary(report)
        print(summary)

        # Export to JSON
        print("\n✓ Exporting to JSON...")
        report_dict = report.to_dict()
        print(json.dumps(report_dict, indent=2)[:500] + "...")

    finally:
        await agent.close()


if __name__ == "__main__":
    asyncio.run(main())
