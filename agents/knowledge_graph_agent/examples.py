"""Mycobacterium tuberculosis Knowledge Graph Agent Examples."""

import asyncio
import json
from agents.knowledge_graph_agent import KnowledgeGraphAgent


async def main():
    print("\n" + "="*70)
    print("MYCOBACTERIUM TUBERCULOSIS KNOWLEDGE GRAPH AGENT EXAMPLES")
    print("="*70)

    literature = [{"title": "Targeting DprE1 in drug-resistant tuberculosis", "publication_year": 2025}]
    
    hypothesis = {
        "id": "mtb_hyp_001",
        "title": "Allosteric Inhibition of DprE1 in MDR-TB",
        "statement": "Covalent inhibitors targeting DprE1 bypass efflux resistance.",
        "molecular_targets": ["DprE1", "InhA"]
    }

    experiment_design = {
        "id": "mtb_exp_001",
        "title": "Alamar Blue Microplate Assay & Macrophage Survival",
        "experiment_type": "laboratory_experiment",
        "sample_size": 128
    }

    analysis_report = {
        "hypothesis_confirmed": True,
        "primary_finding": {
            "title": "Significant MIC Reduction in Mtb H37Rv",
            "effect_size": 0.82
        }
    }

    agent = KnowledgeGraphAgent()

    try:
        print("\n🌐 Building knowledge graph from Mtb discovery artifacts...")
        graph = await agent.update_evidence_and_links(
            literature=literature,
            hypothesis=hypothesis,
            experiment_design=experiment_design,
            analysis_report=analysis_report
        )

        print(f"✓ Knowledge Graph Updated Successfully!\n")
        print(f"  • Total Entities      : {len(graph.entities)}")
        print(f"  • Total Relationships : {len(graph.relationships)}")

        print("\nExtracted Mtb Entities:")
        for ent_id, entity in graph.entities.items():
            print(f"  • [{entity.entity_type.upper()}] {entity.label} ({ent_id})")

        print("\nEstablished Relationships:")
        for rel in graph.relationships:
            print(f"  • {rel.source_id} --({rel.relation} | conf: {rel.confidence})--> {rel.target_id}")

        json_ld = await agent.export_graph("json_ld")
        print(f"\n✓ Exported JSON-LD Graph Length: {len(json_ld)} characters\n")

    finally:
        await agent.close()

    print("="*70)
    print("✅ MTB KNOWLEDGE GRAPH EXAMPLES COMPLETED")
    print("="*70 + "\n")


if __name__ == "__main__":
    asyncio.main(main()) if hasattr(asyncio, 'main') else asyncio.run(main())