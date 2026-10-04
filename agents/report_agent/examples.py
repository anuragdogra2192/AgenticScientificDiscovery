"""Mycobacterium tuberculosis Report Agent Examples."""

import asyncio
from agents.report_agent import ReportAgent, OutputFormat


async def main():
    print("\n" + "="*70)
    print("MYCOBACTERIUM TUBERCULOSIS REPORT AGENT EXAMPLES")
    print("="*70)

    agent = ReportAgent()

    try:
        hypothesis = {
            "title": "Allosteric Inhibition of DprE1 in MDR-TB",
            "statement": "Covalent inhibitors targeting DprE1 bypass efflux resistance.",
            "background": "DprE1 is vital for cell wall arabinogalactan biosynthesis in Mtb."
        }

        design = {
            "experiment_type": "laboratory_experiment",
            "sample_size": 128
        }

        analysis = {
            "interpretation": {"hypothesis_confirmed": True},
            "primary_finding": {"effect_size": 0.82}
        }

        print("\n✍️ Generating publication-ready Mtb research paper...\n")
        paper = await agent.generate_paper(hypothesis, [], analysis, design)

        print(f"✓ Paper Generated Successfully!\n")
        print(f"  • Title      : {paper.title}")
        print(f"  • Word Count : {paper.word_count}")
        print(f"  • Figures    : {len(paper.figures)}")
        print(f"  • Tables     : {len(paper.tables)}")

        markdown = await agent.export_paper(paper, OutputFormat.MARKDOWN)
        print(f"\n✓ Exported Markdown Preview (First 400 chars):\n{markdown[:400]}...\n")

    finally:
        await agent.close()

    print("="*70)
    print("✅ MTB REPORT EXAMPLES COMPLETED")
    print("="*70 + "\n")


if __name__ == "__main__":
    asyncio.run(main())