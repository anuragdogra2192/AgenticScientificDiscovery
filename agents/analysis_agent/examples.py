"""Example use cases for the Analysis Agent."""

import asyncio
import json
from agents.experiment_agent import ExperimentAgent
from agents.hypothesis_agent import HypothesisAgent
from agents.literature_agent import LiteratureAgent
from agents.analysis_agent import AnalysisAgent


async def example_1_basic_analysis():
    """Example 1: Basic result analysis."""
    print("\n" + "="*60)
    print("EXAMPLE 1: Basic Result Analysis")
    print("="*60)

    # Sample results
    sample_results = {
        "n": 100,
        "simulated_effect_size": 0.55,
        "missing_count": 1,
        "outlier_count": 0,
        "variables": {
            "outcome": [5.2 + i*0.01 for i in range(50)] + [6.0 + i*0.01 for i in range(50)],
            "group": [0]*50 + [1]*50,
        }
    }

    sample_design = {
        "id": "exp_001",
        "title": "Treatment vs Control",
        "experiment_type": "randomized_controlled_trial",
        "groups": ["control", "treatment"],
    }

    sample_hypothesis = {
        "id": "hyp_001",
        "title": "Treatment improves outcome",
        "statement": "Treatment group will show higher outcomes",
    }

    agent = AnalysisAgent()

    try:
        print("\n📊 Analyzing results...\n")
        report = await agent.analyze_results(sample_design, sample_hypothesis, sample_results)

        print(f"✓ Analysis complete\n")
        print(f"Hypothesis Confirmed: {report.hypothesis_confirmed}")
        print(f"Confirmation Strength: {report.confirmation_strength}")
        print(f"Direction Matches: {report.direction_matches}")
        print(f"P-value: {report.primary_analysis.p_value:.4f}")
        print(f"Effect Size: {report.primary_finding.effect_size:.3f}")

    finally:
        await agent.close()


async def example_2_statistical_tests():
    """Example 2: Multiple statistical tests."""
    print("\n" + "="*60)
    print("EXAMPLE 2: Statistical Test Comparison")
    print("="*60)

    sample_results = {
        "n": 150,
        "simulated_effect_size": 0.42,
        "missing_count": 3,
        "outlier_count": 2,
        "variables": {
            "outcome": [4.5 + i*0.02 for i in range(75)] + [5.3 + i*0.02 for i in range(75)],
        }
    }

    design = {
        "id": "exp_002",
        "title": "Multi-group comparison",
        "experiment_type": "randomized_controlled_trial",
        "groups": ["control", "treatment_low", "treatment_high"],
    }

    hypothesis = {
        "id": "hyp_002",
        "title": "Dose-response relationship",
    }

    agent = AnalysisAgent()

    try:
        print("\n🔍 Conducting multiple statistical tests...\n")
        report = await agent.analyze_results(design, hypothesis, sample_results)

        print(f"Primary Analysis:")
        print(f"  Test: {report.primary_analysis.test_name.value}")
        print(f"  Statistic: {report.primary_analysis.test_statistic:.3f}")
        print(f"  P-value: {report.primary_analysis.p_value:.4f}")
        print(f"  Significance: {report.primary_analysis.significance_level.value}")

        print(f"\nSecondary Analyses: {len(report.secondary_analyses)}")
        for i, analysis in enumerate(report.secondary_analyses, 1):
            print(f"  {i}. {analysis.test_name.value}: p={analysis.p_value:.4f}")

        print(f"\nSensitivity Analyses: {len(report.sensitivity_analyses)}")
        for i, analysis in enumerate(report.sensitivity_analyses, 1):
            print(f"  {i}. {analysis.test_name.value}: p={analysis.p_value:.4f}")

    finally:
        await agent.close()


async def example_3_assumption_testing():
    """Example 3: Test assumptions and data quality."""
    print("\n" + "="*60)
    print("EXAMPLE 3: Assumption Testing & Data Quality")
    print("="*60)

    sample_results = {
        "n": 80,
        "simulated_effect_size": 0.38,
        "missing_count": 5,
        "outlier_count": 3,
        "variables": {
            "outcome": [4.0 + i*0.03 for i in range(40)] + [5.0 + i*0.03 for i in range(40)],
        }
    }

    design = {
        "id": "exp_003",
        "title": "Assumption test experiment",
        "experiment_type": "quasi_experimental",
        "groups": ["comparison", "treatment"],
    }

    hypothesis = {"id": "hyp_003", "title": "Test"}

    agent = AnalysisAgent()

    try:
        print("\n✓ Checking data quality and assumptions...\n")
        report = await agent.analyze_results(design, hypothesis, sample_results)

        print("Data Quality Issues:")
        for issue in report.data_quality_issues:
            print(f"  • {issue}")

        print("\nAssumption Checks:")
        for assumption, status in report.assumptions_checked.items():
            print(f"  • {assumption}: {'✓ Met' if status else '✗ Violated'}")

        if report.violated_assumptions:
            print("\nViolated Assumptions:")
            for violation in report.violated_assumptions:
                print(f"  ⚠ {violation}")

    finally:
        await agent.close()


async def example_4_findings_extraction():
    """Example 4: Extract and prioritize findings."""
    print("\n" + "="*60)
    print("EXAMPLE 4: Finding Extraction & Prioritization")
    print("="*60)

    sample_results = {
        "n": 200,
        "simulated_effect_size": 0.68,
        "missing_count": 0,
        "outlier_count": 1,
        "variables": {
            "outcome": [4.0 + i*0.02 for i in range(100)] + [5.5 + i*0.02 for i in range(100)],
        }
    }

    design = {
        "id": "exp_004",
        "title": "Major findings experiment",
        "experiment_type": "randomized_controlled_trial",
        "groups": ["control", "treatment"],
    }

    hypothesis = {
        "id": "hyp_004",
        "title": "Strong hypothesis",
    }

    agent = AnalysisAgent()

    try:
        print("\n🎯 Extracting findings...\n")
        report = await agent.analyze_results(design, hypothesis, sample_results)

        print(f"Total Findings: {len(report.findings)}")

        print(f"\nPrimary Finding:")
        pf = report.primary_finding
        print(f"  Title: {pf.title}")
        print(f"  Type: {pf.finding_type}")
        print(f"  Effect Size: {pf.effect_size:.3f}")
        print(f"  Hypothesis Consistency: {pf.consistency_with_hypothesis}")
        print(f"  Practical Significance: {pf.practical_significance}")

        print(f"\nAll Findings:")
        for finding in report.findings:
            print(f"  • {finding.title} ({finding.finding_type})")
            print(f"    - {finding.description}")

    finally:
        await agent.close()


async def example_5_hypothesis_interpretation():
    """Example 5: Interpret hypothesis confirmation."""
    print("\n" + "="*60)
    print("EXAMPLE 5: Hypothesis Confirmation Interpretation")
    print("="*60)

    sample_results = {
        "n": 120,
        "simulated_effect_size": 0.75,
        "missing_count": 0,
        "outlier_count": 0,
        "variables": {
            "outcome": [4.0 + i*0.015 for i in range(60)] + [5.8 + i*0.015 for i in range(60)],
        }
    }

    design = {
        "id": "exp_005",
        "title": "Strong confirmation study",
        "experiment_type": "randomized_controlled_trial",
        "groups": ["control", "treatment"],
    }

    hypothesis = {
        "id": "hyp_005",
        "title": "Clear directional hypothesis",
    }

    agent = AnalysisAgent()

    try:
        print("\n💡 Interpreting hypothesis...\n")
        report = await agent.analyze_results(design, hypothesis, sample_results)

        print(f"Hypothesis Confirmed: {report.hypothesis_confirmed}")
        print(f"Confirmation Strength: {report.confirmation_strength}")
        print(f"Direction Matches: {report.direction_matches}")
        print(f"Effect Size as Predicted: {report.effect_size_as_predicted}")

        print(f"\nInterpretation:")
        print(f"  The hypothesis is {report.confirmation_strength}ly confirmed.")
        if report.hypothesis_confirmed:
            print(f"  The effect is statistically significant and practically meaningful.")
        else:
            print(f"  The evidence does not support the hypothesis.")

    finally:
        await agent.close()


async def example_6_contextualization():
    """Example 6: Contextualize findings with literature."""
    print("\n" + "="*60)
    print("EXAMPLE 6: Contextualization & Literature Comparison")
    print("="*60)

    sample_results = {
        "n": 150,
        "simulated_effect_size": 0.52,
        "missing_count": 2,
        "outlier_count": 0,
        "variables": {
            "outcome": [4.5 + i*0.015 for i in range(75)] + [5.3 + i*0.015 for i in range(75)],
        }
    }

    design = {
        "id": "exp_006",
        "title": "Context study",
        "experiment_type": "randomized_controlled_trial",
        "groups": ["control", "treatment"],
    }

    hypothesis = {
        "id": "hyp_006",
        "title": "Literature-grounded hypothesis",
    }

    agent = AnalysisAgent()

    try:
        print("\n📚 Contextualizing with literature...\n")
        report = await agent.analyze_results(design, hypothesis, sample_results)

        print("Literature Comparison:")
        print(f"  {report.literature_comparison}")

        print("\nNovel Findings:")
        for i, novel in enumerate(report.novel_findings, 1):
            print(f"  {i}. {novel}")

        print("\nBoundary Conditions:")
        for i, boundary in enumerate(report.boundary_conditions, 1):
            print(f"  {i}. {boundary}")

    finally:
        await agent.close()


async def example_7_implications():
    """Example 7: Identify implications and recommendations."""
    print("\n" + "="*60)
    print("EXAMPLE 7: Implications & Recommendations")
    print("="*60)

    sample_results = {
        "n": 180,
        "simulated_effect_size": 0.61,
        "missing_count": 1,
        "outlier_count": 1,
        "variables": {
            "outcome": [4.2 + i*0.02 for i in range(90)] + [5.4 + i*0.02 for i in range(90)],
        }
    }

    design = {
        "id": "exp_007",
        "title": "Implications study",
        "experiment_type": "randomized_controlled_trial",
        "groups": ["control", "treatment"],
    }

    hypothesis = {
        "id": "hyp_007",
        "title": "Applied research hypothesis",
    }

    agent = AnalysisAgent()

    try:
        print("\n🚀 Identifying implications...\n")
        report = await agent.analyze_results(design, hypothesis, sample_results)

        print("Practical Implications:")
        for i, impl in enumerate(report.practical_implications, 1):
            print(f"  {i}. {impl}")

        print("\nTheoretical Implications:")
        for i, impl in enumerate(report.theoretical_implications, 1):
            print(f"  {i}. {impl}")

        print("\nLimitations:")
        for i, lim in enumerate(report.limitations[:3], 1):
            print(f"  {i}. {lim}")

        print("\nRecommendations:")
        for i, rec in enumerate(report.recommendations, 1):
            print(f"  {i}. {rec}")

    finally:
        await agent.close()


async def example_8_analysis_summary():
    """Example 8: Generate complete analysis summary."""
    print("\n" + "="*60)
    print("EXAMPLE 8: Complete Analysis Summary Report")
    print("="*60)

    sample_results = {
        "n": 250,
        "simulated_effect_size": 0.70,
        "missing_count": 0,
        "outlier_count": 0,
        "variables": {
            "outcome": [4.0 + i*0.015 for i in range(125)] + [5.7 + i*0.015 for i in range(125)],
        }
    }

    design = {
        "id": "exp_008",
        "title": "Final comprehensive study",
        "experiment_type": "randomized_controlled_trial",
        "groups": ["control", "treatment"],
    }

    hypothesis = {
        "id": "hyp_008",
        "title": "Comprehensive hypothesis",
    }

    agent = AnalysisAgent()

    try:
        print("\n📄 Generating comprehensive summary...\n")
        report = await agent.analyze_results(design, hypothesis, sample_results)

        # Generate summary
        summary = await agent.generate_analysis_summary(report)
        print(summary)

        # Export to JSON
        print("\n✓ Exporting to JSON...")
        report_dict = report.to_dict()
        with open("/tmp/analysis_report.json", "w") as f:
            json.dump(report_dict, f, indent=2)

        print("✓ Saved to /tmp/analysis_report.json")

    finally:
        await agent.close()


async def example_9_full_pipeline():
    """Example 9: Full end-to-end pipeline analysis."""
    print("\n" + "="*60)
    print("EXAMPLE 9: Full Pipeline - Literature to Analysis")
    print("="*60)

    lit_agent = LiteratureAgent()
    hyp_agent = HypothesisAgent()
    exp_agent = ExperimentAgent()
    ana_agent = AnalysisAgent()

    try:
        # Step 1: Literature
        print("\n1️⃣ Searching literature...")
        papers = await lit_agent.search_papers(
            "cognitive training effectiveness",
            limit=8
        )
        gaps = await lit_agent.identify_gaps(papers)

        # Step 2: Hypotheses
        print("2️⃣ Generating hypotheses...")
        hypotheses = await hyp_agent.generate_hypotheses(papers, gaps, "cognitive training")

        # Step 3: Design
        print("3️⃣ Designing experiment...")
        design = await exp_agent.design_experiment(hypotheses[0].to_dict())

        # Step 4: Analyze (simulated results)
        print("4️⃣ Analyzing results...")
        sample_results = {
            "n": design.sample_size,
            "simulated_effect_size": 0.58,
            "missing_count": 2,
            "outlier_count": 1,
            "variables": {
                "outcome": [5.0 + i*0.01 for i in range(design.sample_size//2)] +
                          [6.2 + i*0.01 for i in range(design.sample_size//2)],
            }
        }

        report = await ana_agent.analyze_results(
            design.to_dict(),
            hypotheses[0].to_dict(),
            sample_results
        )

        print("\n✅ Pipeline Complete!\n")
        print(f"Hypothesis: {hypotheses[0].title}")
        print(f"Design: {design.experiment_type.value}")
        print(f"Sample: {design.sample_size}")
        print(f"Results: Hypothesis {'CONFIRMED' if report.hypothesis_confirmed else 'NOT CONFIRMED'}")
        print(f"Strength: {report.confirmation_strength}")
        print(f"Effect Size: {report.primary_finding.effect_size:.3f}")

    finally:
        await lit_agent.close()
        await hyp_agent.close()
        await exp_agent.close()
        await ana_agent.close()


async def main():
    """Run all examples."""
    print("\n🧪 Analysis Agent - Example Use Cases\n")

    examples = [
        ("Basic Analysis", example_1_basic_analysis),
        ("Statistical Tests", example_2_statistical_tests),
        ("Assumption Testing", example_3_assumption_testing),
        ("Finding Extraction", example_4_findings_extraction),
        ("Hypothesis Interpretation", example_5_hypothesis_interpretation),
        ("Contextualization", example_6_contextualization),
        ("Implications", example_7_implications),
        ("Summary Report", example_8_analysis_summary),
        ("Full Pipeline", example_9_full_pipeline),
    ]

    for i, (name, func) in enumerate(examples, 1):
        try:
            await func()
        except Exception as e:
            print(f"\n❌ Error in {name}: {e}")
            print("   (This might be due to API limits or connectivity issues)")

    print("\n" + "="*60)
    print("✅ Examples completed!")
    print("="*60 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
