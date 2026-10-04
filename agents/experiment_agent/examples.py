"""Example use cases for the Experiment Agent."""

import asyncio
import json
from agents.hypothesis_agent import HypothesisAgent
from agents.literature_agent import LiteratureAgent
from agents.experiment_agent import ExperimentAgent


async def example_1_basic_experiment_design():
    """Example 1: Design experiment from hypothesis."""
    print("\n" + "="*60)
    print("EXAMPLE 1: Basic Experiment Design")
    print("="*60)

    lit_agent = LiteratureAgent()
    hyp_agent = HypothesisAgent()
    exp_agent = ExperimentAgent()

    try:
        # Get literature and hypothesis
        print("\n📚 Getting literature and hypothesis...")
        papers = await lit_agent.search_papers(
            "attention mechanisms interpretability",
            limit=10
        )
        gaps = await lit_agent.identify_gaps(papers)

        hypotheses = await hyp_agent.generate_hypotheses(
            papers=papers,
            research_gaps=gaps,
            query="attention mechanisms interpretability"
        )

        if hypotheses:
            print(f"✓ Generated hypothesis: {hypotheses[0].title}\n")

            # Design experiment
            print("📐 Designing experiment...")
            hyp_dict = hypotheses[0].to_dict()
            design = await exp_agent.design_experiment(hyp_dict)

            print(f"✓ Experiment designed\n")
            print(f"Type: {design.experiment_type.value}")
            print(f"Sample Size: {design.sample_size}")
            print(f"Duration: {design.duration_weeks} weeks")
            print(f"Estimated Cost: ${design.total_cost:,.0f}")
            print(f"Success Probability: {design.success_prediction.probability_success:.1%}")

    finally:
        await lit_agent.close()
        await hyp_agent.close()
        await exp_agent.close()


async def example_2_experiment_details():
    """Example 2: Examine experiment details."""
    print("\n" + "="*60)
    print("EXAMPLE 2: Experiment Details & Protocol")
    print("="*60)

    lit_agent = LiteratureAgent()
    hyp_agent = HypothesisAgent()
    exp_agent = ExperimentAgent()

    try:
        papers = await lit_agent.search_papers(
            "neural network training efficiency",
            limit=8
        )
        gaps = await lit_agent.identify_gaps(papers)

        hypotheses = await hyp_agent.generate_hypotheses(
            papers=papers,
            research_gaps=gaps,
            query="neural network training efficiency"
        )

        if hypotheses:
            hyp_dict = hypotheses[0].to_dict()
            design = await exp_agent.design_experiment(hyp_dict)

            print(f"\n📋 Experiment: {design.title}\n")

            print("Procedures:")
            for proc in design.procedures[:3]:
                print(f"  {proc.step_number}. {proc.description}")
                print(f"     ({proc.duration_minutes} min, {proc.responsible_party})")

            print("\nPrimary Measurements:")
            for measure in design.primary_measures:
                print(f"  • {measure.name}: {measure.method}")
                print(f"    Reliability: {measure.expected_reliability:.2f}")

            print("\nPersonnel Requirements:")
            for role, hours in design.personnel_needed.items():
                print(f"  • {role}: {hours}")

            print("\nBudget Summary:")
            personnel_cost = sum(
                b.total_cost for b in design.budget
                if b.category == "Personnel"
            )
            equipment_cost = sum(
                b.total_cost for b in design.budget
                if b.category in ["Equipment", "Services"]
            )
            print(f"  Personnel: ${personnel_cost:,.0f}")
            print(f"  Equipment/Services: ${equipment_cost:,.0f}")
            print(f"  Total: ${design.total_cost:,.0f}")

    finally:
        await lit_agent.close()
        await hyp_agent.close()
        await exp_agent.close()


async def example_3_design_comparison():
    """Example 3: Compare different experiment designs."""
    print("\n" + "="*60)
    print("EXAMPLE 3: Design Comparison & Trade-offs")
    print("="*60)

    lit_agent = LiteratureAgent()
    hyp_agent = HypothesisAgent()
    exp_agent = ExperimentAgent()

    try:
        papers = await lit_agent.search_papers(
            "machine learning fairness bias",
            limit=8
        )
        gaps = await lit_agent.identify_gaps(papers)

        hypotheses = await hyp_agent.generate_hypotheses(
            papers=papers,
            research_gaps=gaps,
            query="machine learning fairness bias"
        )

        if hypotheses:
            hyp_dict = hypotheses[0].to_dict()
            design = await exp_agent.design_experiment(hyp_dict)

            print(f"\n📊 Design Characteristics:\n")
            print(f"Experiment Type: {design.experiment_type.value.replace('_', ' ').title()}")
            print(f"Rigor Level: {design.rigor_level.value.upper()}")
            print(f"Sample Size: {design.sample_size} participants")
            print(f"Duration: {design.duration_weeks} weeks")
            print(f"Groups: {', '.join(design.groups)}")

            print(f"\nInternal Validity Strategies:")
            for strategy in design.internal_validity_strategies:
                print(f"  • {strategy}")

            print(f"\nExternal Validity Considerations:")
            for consideration in design.external_validity_considerations:
                print(f"  • {consideration}")

            print(f"\nAnalysis Plan:")
            print(f"  Primary: {design.primary_analysis}")
            print(f"  Secondary:")
            for analysis in design.secondary_analyses:
                print(f"    - {analysis}")

    finally:
        await lit_agent.close()
        await hyp_agent.close()
        await exp_agent.close()


async def example_4_dataset_identification():
    """Example 4: Identify datasets needed."""
    print("\n" + "="*60)
    print("EXAMPLE 4: Dataset & Resource Identification")
    print("="*60)

    lit_agent = LiteratureAgent()
    hyp_agent = HypothesisAgent()
    exp_agent = ExperimentAgent()

    try:
        papers = await lit_agent.search_papers(
            "graph neural networks node classification",
            limit=8
        )
        gaps = await lit_agent.identify_gaps(papers)

        hypotheses = await hyp_agent.generate_hypotheses(
            papers=papers,
            research_gaps=gaps,
            query="graph neural networks node classification"
        )

        if hypotheses:
            hyp_dict = hypotheses[0].to_dict()
            design = await exp_agent.design_experiment(hyp_dict)

            print(f"\n📊 Data & Resource Requirements:\n")

            print("Datasets Required:")
            for dataset in design.datasets_required:
                print(f"  • {dataset.name}")
                print(f"    Size: {dataset.size_gb:.1f} GB")
                print(f"    Sample Size: {dataset.sample_size}")
                print(f"    Access Level: {dataset.access_level}")
                print(f"    Preprocessing: {dataset.preprocessing_required}")

            print("\nEquipment Needed:")
            for equipment in design.equipment_needed:
                print(f"  • {equipment}")

            print("\nBudget Breakdown:")
            for item in design.budget[:5]:
                print(f"  • {item.item}: ${item.total_cost:,.0f}")
                print(f"    ({item.quantity:.1f} {item.unit} @ ${item.unit_cost:.2f})")

    finally:
        await lit_agent.close()
        await hyp_agent.close()
        await exp_agent.close()


async def example_5_protocol_generation():
    """Example 5: Generate detailed protocol document."""
    print("\n" + "="*60)
    print("EXAMPLE 5: Protocol Document Generation")
    print("="*60)

    lit_agent = LiteratureAgent()
    hyp_agent = HypothesisAgent()
    exp_agent = ExperimentAgent()

    try:
        papers = await lit_agent.search_papers(
            "reinforcement learning reward shaping",
            limit=8
        )
        gaps = await lit_agent.identify_gaps(papers)

        hypotheses = await hyp_agent.generate_hypotheses(
            papers=papers,
            research_gaps=gaps,
            query="reinforcement learning reward shaping"
        )

        if hypotheses:
            hyp_dict = hypotheses[0].to_dict()
            design = await exp_agent.design_experiment(hyp_dict)

            print(f"\n📄 Generating protocol document...")
            protocol = await exp_agent.generate_protocol_document(design)

            print("\nProtocol (first 1500 characters):\n")
            print(protocol[:1500])
            print("\n... [truncated] ...")

    finally:
        await lit_agent.close()
        await hyp_agent.close()
        await exp_agent.close()


async def example_6_risk_assessment():
    """Example 6: Risk assessment and mitigation."""
    print("\n" + "="*60)
    print("EXAMPLE 6: Risk Assessment & Mitigation")
    print("="*60)

    lit_agent = LiteratureAgent()
    hyp_agent = HypothesisAgent()
    exp_agent = ExperimentAgent()

    try:
        papers = await lit_agent.search_papers(
            "federated learning privacy preservation",
            limit=8
        )
        gaps = await lit_agent.identify_gaps(papers)

        hypotheses = await hyp_agent.generate_hypotheses(
            papers=papers,
            research_gaps=gaps,
            query="federated learning privacy preservation"
        )

        if hypotheses:
            hyp_dict = hypotheses[0].to_dict()
            design = await exp_agent.design_experiment(hyp_dict)

            print(f"\n⚠️ Risk Assessment:\n")

            print("Potential Risks:")
            for i, risk in enumerate(design.potential_risks, 1):
                print(f"  {i}. {risk}")

            print("\nMitigation Strategies:")
            for i, strategy in enumerate(design.mitigation_strategies, 1):
                print(f"  {i}. {strategy}")

            print(f"\nSuccess Factors:")
            for factor in design.success_prediction.success_factors[:3]:
                print(f"  ✓ {factor}")

            print(f"\nFailure Factors:")
            for factor in design.success_prediction.failure_factors[:3]:
                print(f"  ✗ {factor}")

    finally:
        await lit_agent.close()
        await hyp_agent.close()
        await exp_agent.close()


async def example_7_validation_and_export():
    """Example 7: Validate design and export results."""
    print("\n" + "="*60)
    print("EXAMPLE 7: Design Validation & Export")
    print("="*60)

    lit_agent = LiteratureAgent()
    hyp_agent = HypothesisAgent()
    exp_agent = ExperimentAgent()

    try:
        papers = await lit_agent.search_papers(
            "transfer learning domain adaptation",
            limit=8
        )
        gaps = await lit_agent.identify_gaps(papers)

        hypotheses = await hyp_agent.generate_hypotheses(
            papers=papers,
            research_gaps=gaps,
            query="transfer learning domain adaptation"
        )

        if hypotheses:
            hyp_dict = hypotheses[0].to_dict()
            design = await exp_agent.design_experiment(hyp_dict)

            # Validate
            print(f"\n✓ Validating experimental design...\n")
            validation = await exp_agent.validate_design(design)

            print(f"Valid: {validation['valid']}")
            if validation['issues']:
                print("Issues:")
                for issue in validation['issues']:
                    print(f"  • {issue}")
            if validation['warnings']:
                print("Warnings:")
                for warning in validation['warnings']:
                    print(f"  • {warning}")

            # Export to JSON
            print(f"\n✓ Exporting design to JSON...\n")
            design_dict = design.to_dict()

            # Save
            filename = "/tmp/experiment_design.json"
            with open(filename, "w") as f:
                json.dump(design_dict, f, indent=2)

            print(f"✓ Saved to {filename}")
            print(f"\nDesign Summary:")
            print(f"  ID: {design.id}")
            print(f"  Type: {design.experiment_type.value}")
            print(f"  Status: {design.validation_status}")
            print(f"  Total Cost: ${design.total_cost:,.0f}")
            print(f"  Duration: {design.duration_weeks} weeks")
            print(f"  Success Probability: {design.success_prediction.probability_success:.1%}")

    finally:
        await lit_agent.close()
        await hyp_agent.close()
        await exp_agent.close()


async def example_8_timeline_planning():
    """Example 8: Project timeline and critical path."""
    print("\n" + "="*60)
    print("EXAMPLE 8: Timeline & Critical Path")
    print("="*60)

    lit_agent = LiteratureAgent()
    hyp_agent = HypothesisAgent()
    exp_agent = ExperimentAgent()

    try:
        papers = await lit_agent.search_papers(
            "meta-learning few-shot learning",
            limit=8
        )
        gaps = await lit_agent.identify_gaps(papers)

        hypotheses = await hyp_agent.generate_hypotheses(
            papers=papers,
            research_gaps=gaps,
            query="meta-learning few-shot learning"
        )

        if hypotheses:
            hyp_dict = hypotheses[0].to_dict()
            design = await exp_agent.design_experiment(hyp_dict)

            print(f"\n📅 Project Timeline:\n")

            print("Milestones:")
            for milestone in design.timeline_milestones:
                print(f"  Week {milestone['week']}: {milestone['milestone']}")
                print(f"    → {milestone['deliverable']}")

            print(f"\nCritical Path Items (Must Complete On Time):")
            for i, item in enumerate(design.critical_path, 1):
                print(f"  {i}. {item}")

            print(f"\nTotal Duration: {design.duration_weeks} weeks")

    finally:
        await lit_agent.close()
        await hyp_agent.close()
        await exp_agent.close()


async def main():
    """Run all examples."""
    print("\n🧪 Experiment Agent - Example Use Cases\n")

    examples = [
        ("Basic Design", example_1_basic_experiment_design),
        ("Design Details", example_2_experiment_details),
        ("Design Comparison", example_3_design_comparison),
        ("Dataset Identification", example_4_dataset_identification),
        ("Protocol Generation", example_5_protocol_generation),
        ("Risk Assessment", example_6_risk_assessment),
        ("Validation & Export", example_7_validation_and_export),
        ("Timeline Planning", example_8_timeline_planning),
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
