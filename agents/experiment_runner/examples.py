"""Examples for the Experiment Runner Agent in Mycobacterium tuberculosis Research."""

import asyncio
from agents.experiment_runner.agent import ExperimentRunnerAgent


async def main():
    print("\n" + "="*70)
    print("EXPERIMENT RUNNER AGENT - Mtb ASSAY EXECUTION EXAMPLES")
    print("="*70)

    runner = ExperimentRunnerAgent()

    try:
        # Sample approved experimental design from Planner
        approved_design = {
            "title": "Advanced Intracellular Macrophage Mtb Killing & Target Engagement Assay",
            "sample_size": 128,
            "duration_weeks": 8,
            "total_budget": 48000
        }

        print(f"\n🚀 Executing approved protocol under simulated BSL-3 parameters...\n")
        
        results = await runner.run_experiment(approved_design)

        print(f"✓ Assay Execution Complete!\n")
        print(f"  • Status      : {results.get('execution_status')}")
        print(f"  • Sample Size : {results.get('sample_size')} wells/subjects")
        print(f"  • Effect Size : {results.get('simulated_effect_size')}")
        print(f"  • p-value     : {results.get('p_value')}")
        print(f"  • Execution Log: {results.get('raw_logs')}\n")

    finally:
        await runner.close()

    print("="*70)
    print("✅ EXPERIMENT RUNNER EXAMPLES COMPLETED")
    print("="*70 + "\n")


if __name__ == "__main__":
    asyncio.run(main())