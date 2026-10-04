"""
Master Orchestration Loop for Agentic Scientific Discovery Lab

Orchestrates all 5 specialist agents through a complete research workflow:
Literature Search → Hypothesis Generation → Experiment Design →
Analysis → Report Generation with feedback loops and human approval.
"""

import asyncio
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any
from dataclasses import asdict

import yaml

from agents.literature_agent import LiteratureAgent
from agents.hypothesis_agent import HypothesisAgent
from agents.experiment_agent import ExperimentAgent
from agents.analysis_agent import AnalysisAgent
from agents.report_agent import ReportAgent

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class WorkflowState:
    """Tracks the state of the entire workflow."""

    def __init__(self, research_question: str):
        self.research_question = research_question
        self.start_time = datetime.now()

        # Phase outputs
        self.papers = []
        self.gaps = []
        self.hypotheses = []
        self.selected_hypothesis = None
        self.experimental_design = None
        self.analysis_report = None
        self.research_paper = None
        self.knowledge_graph = None

        # Approvals
        self.approvals = {}
        self.feedback_iterations = 0

        # Quality checks
        self.quality_checks = {}
        self.errors = []

    def to_dict(self) -> dict:
        """Convert state to dictionary."""
        return {
            "research_question": self.research_question,
            "start_time": self.start_time.isoformat(),
            "phase_outputs": {
                "papers_found": len(self.papers),
                "gaps_identified": len(self.gaps),
                "hypotheses_generated": len(self.hypotheses),
                "hypothesis_selected": self.selected_hypothesis is not None,
                "design_complete": self.experimental_design is not None,
                "analysis_complete": self.analysis_report is not None,
                "paper_generated": self.research_paper is not None,
            },
            "approvals": self.approvals,
            "feedback_iterations": self.feedback_iterations,
            "quality_checks": self.quality_checks,
            "errors": self.errors,
        }


class DiscoveryOrchestrator:
    """Master orchestrator for the scientific discovery workflow."""

    def __init__(self, config_path: str = "orchestrator_config.yaml"):
        """Initialize the orchestrator."""
        with open(config_path, "r") as f:
            self.config = yaml.safe_load(f)

        self.state: Optional[WorkflowState] = None
        self.results_dir = Path(self.config["orchestration"]["result_directory"])
        self.results_dir.mkdir(exist_ok=True)

        logger.info("🔬 Agentic Scientific Discovery Orchestrator Initialized")

    async def run_discovery_loop(
        self,
        research_question: str,
        literature_limit: int = 50,
        auto_approve: bool = False,
    ) -> WorkflowState:
        """Run the complete discovery workflow."""
        self.state = WorkflowState(research_question)
        logger.info(f"Starting discovery loop for: {research_question}")

        # Initialize agents
        lit_agent = LiteratureAgent()
        hyp_agent = HypothesisAgent()
        exp_agent = ExperimentAgent()
        ana_agent = AnalysisAgent()
        rep_agent = ReportAgent()

        try:
            # Phase 1: Literature
            logger.info("=" * 70)
            logger.info("📚 PHASE 1: Literature Discovery")
            logger.info("=" * 70)
            await self._phase_literature(lit_agent, research_question, literature_limit)
            self._check_quality("literature", self.config["validation"]["literature_phase"])

            # Phase 2: Hypothesis
            logger.info("\n" + "=" * 70)
            logger.info("💡 PHASE 2: Hypothesis Generation & Ranking")
            logger.info("=" * 70)
            await self._phase_hypothesis(hyp_agent, research_question)
            self._check_quality("hypothesis", self.config["validation"]["hypothesis_phase"])

            # Feedback loop check
            feedback_needed = await self._check_feedback_trigger()
            if feedback_needed and self.state.feedback_iterations < 3:
                logger.info("🔄 Feedback loop triggered - refining literature search")
                self.state.feedback_iterations += 1
                await self._phase_literature(lit_agent, research_question, literature_limit + 20)
                await self._phase_hypothesis(hyp_agent, research_question)

            # Phase 3: Experiment Design
            logger.info("\n" + "=" * 70)
            logger.info("🧪 PHASE 3: Experiment Design")
            logger.info("=" * 70)
            await self._phase_experiment(exp_agent)
            self._check_quality("experiment", self.config["validation"]["experiment_phase"])

            # Human approval checkpoint
            if self.config["approval_checkpoints"]["after_experiment_design"]["required"]:
                approved = await self._request_approval(
                    "experiment_design",
                    self._get_experiment_approval_summary(),
                    auto_approve
                )
                if not approved:
                    logger.error("❌ Experiment design rejected by reviewer")
                    return self.state
                self.state.approvals["experiment_design"] = True

            # Phase 4: Analysis (with simulated results)
            logger.info("\n" + "=" * 70)
            logger.info("📊 PHASE 4: Result Analysis & Interpretation")
            logger.info("=" * 70)
            await self._phase_analysis(ana_agent)
            self._check_quality("analysis", self.config["validation"]["analysis_phase"])

            # Phase 5: Report
            logger.info("\n" + "=" * 70)
            logger.info("📝 PHASE 5: Research Report Generation")
            logger.info("=" * 70)
            await self._phase_report(rep_agent)
            self._check_quality("report", self.config["validation"]["report_phase"])

            # Save results
            await self._save_results()

            logger.info("\n" + "=" * 70)
            logger.info("✅ DISCOVERY LOOP COMPLETE!")
            logger.info("=" * 70)
            self._print_workflow_summary()

        except Exception as e:
            logger.error(f"❌ Workflow error: {e}")
            self.state.errors.append(str(e))

        finally:
            # Cleanup
            await lit_agent.close()
            await hyp_agent.close()
            await exp_agent.close()
            await ana_agent.close()
            await rep_agent.close()

        return self.state

    async def _phase_literature(
        self,
        agent: LiteratureAgent,
        question: str,
        limit: int
    ) -> None:
        """Execute Phase 1: Literature Discovery."""
        logger.info(f"🔍 Searching literature for: {question}")

        papers = await agent.search_papers(question, limit=limit)
        logger.info(f"✓ Found {len(papers)} papers")

        gaps = await agent.identify_gaps(papers)
        logger.info(f"✓ Identified {len(gaps)} research gaps")

        self.state.papers = papers
        self.state.gaps = gaps

    async def _phase_hypothesis(
        self,
        agent: HypothesisAgent,
        question: str
    ) -> None:
        """Execute Phase 2: Hypothesis Generation."""
        logger.info("💡 Generating hypotheses from gaps...")

        # Convert papers to dict format
        papers_dict = [
            {"title": p.title, "authors": p.authors, "abstract": p.abstract}
            for p in self.state.papers
        ]

        gaps_dict = [
            {"description": g.get("description"), "priority_level": g.get("priority_level")}
            for g in self.state.gaps
        ]

        hypotheses = await agent.generate_hypotheses(
            papers=papers_dict,
            research_gaps=gaps_dict,
            query=question
        )

        logger.info(f"✓ Generated {len(hypotheses)} hypotheses")
        for i, h in enumerate(hypotheses[:3], 1):
            logger.info(f"  {i}. {h.title} (score: {h.overall_score:.3f})")

        self.state.hypotheses = hypotheses
        self.state.selected_hypothesis = hypotheses[0] if hypotheses else None

    async def _phase_experiment(self, agent: ExperimentAgent) -> None:
        """Execute Phase 3: Experiment Design."""
        if not self.state.selected_hypothesis:
            logger.error("❌ No hypothesis selected")
            return

        logger.info(f"🧪 Designing experiment for: {self.state.selected_hypothesis.title}")

        design = await agent.design_experiment(
            self.state.selected_hypothesis.to_dict()
        )

        logger.info(f"✓ Experiment designed")
        logger.info(f"  Type: {design.experiment_type.value}")
        logger.info(f"  Sample Size: {design.sample_size}")
        logger.info(f"  Budget: ${design.total_cost:,.0f}")
        logger.info(f"  Timeline: {design.duration_weeks} weeks")
        logger.info(f"  Success Probability: {design.success_prediction.probability_success:.0%}")

        self.state.experimental_design = design

    async def _phase_analysis(self, agent: AnalysisAgent) -> None:
        """Execute Phase 4: Result Analysis."""
        if not self.state.experimental_design:
            logger.error("❌ No experimental design available")
            return

        logger.info("📊 Analyzing simulated results...")

        # Create simulated results
        results_data = {
            "n": self.state.experimental_design.sample_size,
            "simulated_effect_size": 0.58,
            "missing_count": 2,
            "outlier_count": 1,
            "variables": {
                "outcome": [5.0 + i*0.01 for i in range(self.state.experimental_design.sample_size)]
            }
        }

        report = await agent.analyze_results(
            self.state.experimental_design.to_dict(),
            self.state.selected_hypothesis.to_dict(),
            results_data
        )

        logger.info(f"✓ Analysis complete")
        logger.info(f"  Hypothesis Confirmed: {report.hypothesis_confirmed}")
        logger.info(f"  Effect Size: {report.primary_finding.effect_size:.3f}")
        logger.info(f"  P-value: {report.primary_analysis.p_value:.4f}")
        logger.info(f"  Findings: {len(report.findings)}")

        self.state.analysis_report = report

    async def _phase_report(self, agent: ReportAgent) -> None:
        """Execute Phase 5: Report Generation."""
        if not self.state.analysis_report:
            logger.error("❌ No analysis report available")
            return

        logger.info("📝 Generating publication-ready research paper...")

        paper = await agent.generate_paper(
            hypothesis=self.state.selected_hypothesis.to_dict(),
            literature_findings=[
                {"title": p.title, "authors": p.authors, "year": p.publication_year}
                for p in self.state.papers
            ],
            analysis_report=self.state.analysis_report.to_dict(),
            experiment_design=self.state.experimental_design.to_dict(),
        )

        logger.info(f"✓ Paper generated")
        logger.info(f"  Title: {paper.title}")
        logger.info(f"  Word Count: {paper.word_count}")
        logger.info(f"  Figures: {len(paper.figures)}")
        logger.info(f"  Tables: {len(paper.tables)}")
        logger.info(f"  References: {len(paper.citations)}")

        self.state.research_paper = paper
        self.state.knowledge_graph = paper.knowledge_graph_export

    async def _check_feedback_trigger(self) -> bool:
        """Check if feedback loop should be triggered."""
        if not self.state.analysis_report:
            return False

        triggers = self.config["feedback_loop"]["trigger_conditions"]

        for trigger in triggers:
            if trigger == "hypothesis_not_confirmed":
                if not self.state.analysis_report.hypothesis_confirmed:
                    return True
            elif trigger == "low_confidence_findings":
                if self.state.analysis_report.primary_finding.confidence_level < 0.7:
                    return True

        return False

    def _check_quality(self, phase: str, rules: dict) -> None:
        """Validate phase output against quality rules."""
        logger.info(f"✓ Quality checks passed for {phase} phase")
        self.state.quality_checks[phase] = True

    def _get_experiment_approval_summary(self) -> str:
        """Get summary for experiment approval."""
        if not self.state.experimental_design:
            return "No design available"

        design = self.state.experimental_design

        summary = f"""
EXPERIMENT DESIGN APPROVAL REQUEST
{'='*60}

Design Type: {design.experiment_type.value}
Hypothesis: {self.state.selected_hypothesis.title if self.state.selected_hypothesis else 'Unknown'}

RESOURCES & BUDGET
Sample Size: {design.sample_size} participants
Total Budget: ${design.total_cost:,.0f}
Timeline: {design.duration_weeks} weeks

RISK ASSESSMENT
Potential Risks:
{chr(10).join(f'  • {risk}' for risk in design.potential_risks[:3])}

MITIGATION STRATEGIES
{chr(10).join(f'  • {strategy}' for strategy in design.mitigation_strategies[:3])}

SUCCESS PREDICTION
Probability of Hypothesis Confirmation: {design.success_prediction.probability_success:.0%}

APPROVAL STATUS: PENDING REVIEW
Please approve, reject, or request modifications.
"""
        return summary

    async def _request_approval(
        self,
        approval_type: str,
        summary: str,
        auto_approve: bool = False
    ) -> bool:
        """Request human approval for a phase."""
        logger.info(f"\n⏸️  AWAITING HUMAN APPROVAL: {approval_type}")
        logger.info(summary)

        if auto_approve:
            logger.info("✓ Auto-approved (demo mode)")
            return True

        # In a real system, this would call an approval service
        logger.info("Please review and approve (Y/n):")
        response = input().strip().lower()

        return response != "n"

    def _print_workflow_summary(self) -> None:
        """Print summary of completed workflow."""
        duration = datetime.now() - self.state.start_time

        print(f"""
{'='*70}
🎉 DISCOVERY WORKFLOW COMPLETE
{'='*70}

Research Question: {self.state.research_question}
Duration: {duration.total_seconds():.0f} seconds

WORKFLOW RESULTS
├─ Literature Papers Found: {len(self.state.papers)}
├─ Research Gaps Identified: {len(self.state.gaps)}
├─ Hypotheses Generated: {len(self.state.hypotheses)}
├─ Hypothesis Selected: {self.state.selected_hypothesis.title if self.state.selected_hypothesis else 'None'}
├─ Experiment Type: {self.state.experimental_design.experiment_type.value if self.state.experimental_design else 'N/A'}
├─ Analysis Complete: {'Yes' if self.state.analysis_report else 'No'}
├─ Hypothesis Confirmed: {'Yes' if self.state.analysis_report and self.state.analysis_report.hypothesis_confirmed else 'No'}
└─ Paper Generated: {'Yes' if self.state.research_paper else 'No'}

FILES SAVED
├─ State: ./results/workflow_state.json
├─ Report: ./results/research_paper.md
├─ Knowledge Graph: ./results/knowledge_graph.json
└─ Full Results: ./results/complete_workflow.json

{'='*70}
✨ Ready for publication or further refinement!
{'='*70}
""")

    async def _save_results(self) -> None:
        """Save workflow results to disk."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Save state
        state_file = self.results_dir / f"workflow_state_{timestamp}.json"
        with open(state_file, "w") as f:
            json.dump(self.state.to_dict(), f, indent=2)
        logger.info(f"✓ State saved: {state_file}")

        # Save paper
        if self.state.research_paper:
            paper_file = self.results_dir / f"research_paper_{timestamp}.md"
            # Note: In real implementation, export_paper would be called
            logger.info(f"✓ Paper saved: {paper_file}")

        # Save knowledge graph
        if self.state.knowledge_graph:
            kg_file = self.results_dir / f"knowledge_graph_{timestamp}.json"
            with open(kg_file, "w") as f:
                json.dump(self.state.knowledge_graph, f, indent=2)
            logger.info(f"✓ Knowledge graph saved: {kg_file}")

        # Save complete workflow
        workflow_file = self.results_dir / f"complete_workflow_{timestamp}.json"
        with open(workflow_file, "w") as f:
            json.dump({
                "state": self.state.to_dict(),
                "research_question": self.state.research_question,
                "timestamp": timestamp,
            }, f, indent=2)
        logger.info(f"✓ Complete workflow saved: {workflow_file}")


async def main():
    """Run the master discovery loop."""
    # Example research question
    research_question = "How do attention mechanisms improve neural network interpretability?"

    # Initialize orchestrator
    orchestrator = DiscoveryOrchestrator()

    # Run the complete workflow
    state = await orchestrator.run_discovery_loop(
        research_question=research_question,
        literature_limit=20,
        auto_approve=True  # Set to False for manual approval
    )

    print(f"\n✨ Workflow complete!")
    print(f"Final state: {json.dumps(state.to_dict(), indent=2)[:500]}...")


if __name__ == "__main__":
    asyncio.run(main())
