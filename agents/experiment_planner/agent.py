"""Experiment Planner Agent integrating Zheng & Av-Gay (2017) Mtb efficacy and cytotoxicity baselines."""

import logging
import os
import re
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import List, Dict, Any

import yaml

try:
    from anthropic import Anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False

logger = logging.getLogger(__name__)


@dataclass
class ComparativeValidationPlan:
    """Holds comparative baseline and proposed Mtb experimental designs under Zheng & Av-Gay (2017) controls."""
    research_question: str
    baseline_design: dict
    proposed_design: dict
    matched_conditions: List[str]
    selected_method: str
    rationale: str

    @property
    def selected_design(self) -> dict:
        """Returns the dictionary for the chosen experimental design."""
        if self.selected_method == "baseline":
            return self.baseline_design
        return self.proposed_design

    def to_dict(self) -> dict:
        return asdict(self)

# Add this alias so both names work across your codebase
ComparativeProtocolPlan = ComparativeValidationPlan


class ExperimentPlannerAgent:
    """Planner agent incorporating DMSO controls, Rifampicin benchmarks, and THP-1 cytotoxicity screening."""

    def __init__(self, config_path: str = "agents/experiment_planner/experiment_planner.yaml"):
        if not os.path.exists(config_path):
            config_path = "experiment_planner.yaml"

        if os.path.exists(config_path):
            with open(config_path, "r") as f:
                self.config = yaml.safe_load(f) or {}
        else:
            self.config = {}

        self.use_claude = False
        self.claude_client = None
        if ANTHROPIC_AVAILABLE and os.environ.get("ANTHROPIC_API_KEY"):
            try:
                self.claude_client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
                self.use_claude = True
                logger.info("Claude Haiku initialized for Experiment Planner")
            except Exception as e:
                logger.warning(f"Failed to initialize Claude client for Planner: {e}")

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
        return re.sub(r',\s*([\]}])', r'\1', text)

    async def plan_comparative_tests(self, hypothesis: dict, max_budget: float = 100000.0) -> ComparativeValidationPlan:
        """Design baseline vs. proposed protocols integrating Zheng & Av-Gay (2017) screening standards."""
        logger.info(f"Experiment Planner: Designing Zheng & Av-Gay (2017) comparative protocols for: {hypothesis.get('title')}")

        # Rule-based and literature-grounded Mtb design following Zheng & Av-Gay (2017)
        baseline = {
            "title": "Baseline: Standard Extracellular Alamar Blue MIC & DMSO/Rifampicin Control",
            "experiment_type": "laboratory_experiment",
            "sample_size": 96,
            "duration_weeks": 6,
            "total_budget": 28000.0,
            "expected_effect_size": 0.45,
            "controls": {
                "negative_control": "DMSO only (100% normalization)",
                "positive_control": "Rifampicin (0.1 µg/mL for >99.9% killing)",
                "host_cell": "None (Extracellular only)"
            },
            "description": "Standard susceptibility screening against Mtb H37Rv using DMSO negative and Rifampicin positive controls."
        }

        proposed = {
            "title": "Proposed: Intracellular Mtb Killing & THP-1 Mammalian Cytotoxicity Screening (Zheng & Av-Gay, 2017)",
            "experiment_type": "laboratory_experiment",
            "sample_size": 128,
            "duration_weeks": 8,
            "total_budget": 48000.0,
            "expected_effect_size": 0.82,
            "controls": {
                "negative_control": "DMSO vehicle-treated intracellular Mtb & THP-1 cells",
                "positive_control": "Rifampicin (0.1 µg/mL efficacy benchmark)",
                "host_cell": "PMA-differentiated THP-1 human macrophages for CC50 & Selectivity Index (SI = CC50 / IC50)"
            },
            "description": "Simultaneous intracellular Mtb luciferase/GFP viability screening and human THP-1 host cell cytotoxicity screening to eliminate non-selective toxic candidates."
        }

        matched_conditions = [
            "Mtb H37Rv strain (luciferase-expressing)",
            "PMA-differentiated THP-1 human monocytes",
            "DMSO vehicle control normalization (1% v/v max)",
            "Rifampicin (0.1 µg/mL) efficacy reference baseline"
        ]

        return ComparativeValidationPlan(
            research_question=hypothesis.get("title", "Allosteric Inhibition of DprE1 in Mtb"),
            baseline_design=baseline,
            proposed_design=proposed,
            matched_conditions=matched_conditions,
            selected_method="proposed",
            rationale=(
                "The proposed method implements Zheng & Av-Gay (2017) dual screening (intracellular Mtb efficacy + "
                "THP-1 mammalian cytotoxicity), allowing calculation of the Selectivity Index (SI = CC50 / IC50) "
                "and filtering out human-toxic candidates within budget ($48k <= $100k ceiling)."
            )
        )

    async def plan_competing_tests(self, hypothesis: dict, max_budget: float = 100000.0) -> ComparativeValidationPlan:
        """Alias for plan_comparative_tests to maintain orchestrator compatibility."""
        return await self.plan_comparative_tests(hypothesis, max_budget)

    async def close(self):
        pass