"""Mycobacterium tuberculosis Analysis Agent Examples."""

import asyncio
import json
from agents.analysis_agent import AnalysisAgent


async def main():
    print("\n" + "="*70)
    print("MYCOBACTERIUM TUBERCULOSIS ANALYSIS AGENT EXAMPLES")
    print("="*70)

    agent = AnalysisAgent()

    try:
        # Sample Mtb assay results (e.g. MIC reduction data)
        sample_results = {
            "n": 128,
            "simulated_effect_size": 0.82,
            "p_value": 0.0008,
            "variables": {
                "mic_reduction_ug_ml": [2.5 - (i * 0.015) for i in range(128)]
            }
        }

        sample_design = {
            "id": "mtb_exp_001",
            "title": "Advanced Intracellular Macrophage Mtb Killing & Target Engagement Assay",
            "experiment_type": "laboratory_experiment"
        }

        sample_hypothesis = {
            "id": "mtb_hyp_001",
            "title": "Allosteric Inhibition of DprE1 in MDR-TB",
            "statement": "Targeting the DprE1 enzyme via novel analogues will bypass resistance."
        }

        print("\n📊 Analyzing Mtb assay results...\n")
        report = await agent.analyze_results(sample_design, sample_hypothesis, sample_results)

        print(f"✓ Analysis Complete Successfully!\n")
        print(f"  • Hypothesis Confirmed : {report.hypothesis_confirmed}")
        print(f"  • Confirmation Strength: {report.confirmation_strength.upper()}")
        print(f"  • Statistical Test     : {report.primary_analysis.test_name.value}")
        print(f"  • p-value              : {report.primary_analysis.p_value:.4f}")
        print(f"  • Effect Size (Cohen's d): {report.primary_finding.effect_size:.2f}")
        print(f"  • Primary Finding      : {report.primary_finding.title}")
        print(f"  • Future Direction     : {report.future_research_directions[0]}\n")

    finally:
        await agent.close()

    print("="*70)
    print("✅ MTB ANALYSIS AGENT EXAMPLES COMPLETED")
    print("="*70 + "\n")


if __name__ == "__main__":
    asyncio.run(main())