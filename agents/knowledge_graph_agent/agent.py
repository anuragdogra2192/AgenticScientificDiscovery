"""Knowledge Graph Agent for building semantic representations of Mycobacterium tuberculosis research discoveries."""

import asyncio
import json
import logging
import os
import re
from dataclasses import dataclass, asdict, field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

import yaml

try:
    from anthropic import Anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False

logger = logging.getLogger(__name__)


class EntityType(str, Enum):
    """Types of entities in knowledge graph."""
    HYPOTHESIS = "hypothesis"
    TARGET = "target"
    COMPOUND = "compound"
    DISEASE = "disease"
    FINDING = "finding"
    METHODOLOGY = "methodology"
    AUTHOR = "author"
    PUBLICATION = "publication"
    EVIDENCE = "evidence"


class RelationType(str, Enum):
    """Types of relationships in knowledge graph."""
    TARGETS = "targets"
    TREATS = "treats"
    INHIBITS = "inhibits"
    ACTIVATES = "activates"
    ASSOCIATES_WITH = "associates_with"
    CONFIRMED_BY = "confirmed_by"
    CONTRADICTS = "contradicts"
    BUILDS_ON = "builds_on"
    RELATED_TO = "related_to"
    VALIDATES = "validates"
    TESTED_BY = "tested_by"


@dataclass
class KGEntity:
    """Represents an entity in the knowledge graph."""
    id: str
    label: str
    entity_type: EntityType
    description: Optional[str] = None
    properties: Dict[str, Any] = field(default_factory=dict)
    source_papers: List[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "label": self.label,
            "entity_type": self.entity_type.value,
            "description": self.description,
            "properties": self.properties,
            "source_papers": self.source_papers,
        }


@dataclass
class KGRelationship:
    """Represents a relationship between entities."""
    source_id: str
    target_id: str
    relation: RelationType
    confidence: float = 0.8
    supporting_evidence: Optional[str] = None
    properties: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "source_id": self.source_id,
            "target_id": self.target_id,
            "relation": self.relation.value,
            "confidence": self.confidence,
            "supporting_evidence": self.supporting_evidence,
            "properties": self.properties,
        }


@dataclass
class KnowledgeGraph:
    """Represents a semantic knowledge graph of Mtb research discovery."""
    entities: Dict[str, KGEntity] = field(default_factory=dict)
    relationships: List[KGRelationship] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def add_entity(self, entity: KGEntity) -> None:
        self.entities[entity.id] = entity

    def add_relationship(self, relationship: KGRelationship) -> None:
        self.relationships.append(relationship)

    def to_dict(self) -> dict:
        return {
            "entities": {k: v.to_dict() for k, v in self.entities.items()},
            "relationships": [r.to_dict() for r in self.relationships],
            "metadata": self.metadata,
            "created_at": self.created_at,
        }

    def to_json_ld(self) -> dict:
        return {
            "@context": {"@vocab": "http://discovery.lab/kg/"},
            "@id": "http://discovery.lab/kg/mtb_graph",
            "@type": "KnowledgeGraph",
            "entities": [e.to_dict() for e in self.entities.values()],
            "relationships": [r.to_dict() for r in self.relationships],
            "metadata": self.metadata,
        }


class KnowledgeGraphAgent:
    """Agent for building semantic knowledge graphs from Mtb discoveries."""

    def __init__(self, config_path: str = "agents/knowledge_graph_agent/knowledge_graph_agent.yaml"):
        if not os.path.exists(config_path):
            config_path = "knowledge_graph_agent.yaml"

        if os.path.exists(config_path):
            with open(config_path, "r") as f:
                self.config = yaml.safe_load(f) or {}
        else:
            self.config = {}

        self.knowledge_graph = KnowledgeGraph()

        self.use_claude = False
        self.claude_client = None
        if ANTHROPIC_AVAILABLE and os.environ.get("ANTHROPIC_API_KEY"):
            try:
                self.claude_client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
                self.use_claude = True
                logger.info("Claude Haiku API initialized for Mtb knowledge graph generation")
            except Exception as e:
                logger.warning(f"Could not initialize Claude API: {e}")

    async def update_evidence_and_links(
        self,
        literature: List[dict],
        hypothesis: dict,
        experiment_design: dict,
        analysis_report: dict,
    ) -> KnowledgeGraph:
        """Wrapper method to update evidence and links from pipeline artifacts."""
        kg = await self.build_knowledge_graph(literature, hypothesis, experiment_design, analysis_report)
        self.knowledge_graph = kg
        return kg

    async def export_graph(self, format_type: str = "json_ld") -> Any:
        """Export knowledge graph in specified format."""
        if format_type == "json_ld":
            return json.dumps(self.knowledge_graph.to_json_ld(), indent=2)
        elif format_type == "dict":
            return self.knowledge_graph.to_dict()
        return json.dumps(self.knowledge_graph.to_dict(), indent=2)

    async def build_knowledge_graph(
        self,
        literature: List[dict],
        hypothesis: dict,
        experiment_design: dict,
        analysis_report: dict,
    ) -> KnowledgeGraph:
        """Build a knowledge graph from Mtb research discovery artifacts."""
        logger.info("Building knowledge graph from Mtb discovery artifacts")

        if self.use_claude and self.claude_client:
            try:
                return await self._build_with_claude(literature, hypothesis, experiment_design, analysis_report)
            except Exception as e:
                logger.warning(f"Claude KG generation failed: {e}. Falling back to rule-based.")

        return self._build_rule_based(literature, hypothesis, experiment_design, analysis_report)

    async def _build_with_claude(
        self,
        literature: List[dict],
        hypothesis: dict,
        experiment_design: dict,
        analysis_report: dict,
    ) -> KnowledgeGraph:
        prompt = f"""Extract Mtb knowledge graph entities and relationships from these artifacts:
HYPOTHESIS: {json.dumps(hypothesis, default=str)[:800]}
EXPERIMENT: {json.dumps(experiment_design, default=str)[:800]}
ANALYSIS: {json.dumps(analysis_report, default=str)[:800]}

Return ONLY valid JSON with structure:
{{
  "entities": {{"id1": {{"id": "id1", "label": "DprE1", "entity_type": "target"}}}},
  "relationships": [{{"source_id": "hyp_1", "target_id": "id1", "relation": "targets", "confidence": 0.9}}]
}}"""

        response = self.claude_client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=2048,
            messages=[{"role": "user", "content": prompt}],
        )

        match = re.search(r'\{.*\}', response.content[0].text, re.DOTALL)
        if not match:
            raise ValueError("Invalid JSON from Claude")

        data = json.loads(match.group())
        kg = KnowledgeGraph()

        for e_id, e_data in data.get("entities", {}).items():
            kg.add_entity(KGEntity(
                id=e_data.get("id", e_id),
                label=e_data.get("label", ""),
                entity_type=EntityType(e_data.get("entity_type", "target")),
                description=e_data.get("description"),
                properties=e_data.get("properties", {})
            ))

        for r_data in data.get("relationships", []):
            kg.add_relationship(KGRelationship(
                source_id=r_data.get("source_id", ""),
                target_id=r_data.get("target_id", ""),
                relation=RelationType(r_data.get("relation", "targets")),
                confidence=float(r_data.get("confidence", 0.85)),
                supporting_evidence=r_data.get("evidence_source")
            ))

        return kg

    def _build_rule_based(
        self,
        literature: List[dict],
        hypothesis: dict,
        experiment_design: dict,
        analysis_report: dict,
    ) -> KnowledgeGraph:
        kg = KnowledgeGraph()

        hyp_id = hypothesis.get("id", "mtb_hyp_001")
        kg.add_entity(KGEntity(
            id=hyp_id,
            label=hypothesis.get("title", "Mtb Hypothesis"),
            entity_type=EntityType.HYPOTHESIS,
            description=hypothesis.get("statement", "")
        ))

        # Add Mtb targets
        for target in hypothesis.get("molecular_targets", ["DprE1", "InhA"]):
            target_id = f"target_{target.lower()}"
            kg.add_entity(KGEntity(id=target_id, label=target, entity_type=EntityType.TARGET, description="Mtb cell wall target"))
            kg.add_relationship(KGRelationship(source_id=hyp_id, target_id=target_id, relation=RelationType.TARGETS, confidence=0.92))

        # Add findings
        if analysis_report.get("primary_finding"):
            finding_id = "mtb_finding_primary"
            kg.add_entity(KGEntity(
                id=finding_id,
                label=analysis_report["primary_finding"].get("title", "MIC Reduction Finding"),
                entity_type=EntityType.FINDING,
                properties={"effect_size": analysis_report["primary_finding"].get("effect_size", 0.82)}
            ))
            kg.add_relationship(KGRelationship(source_id=hyp_id, target_id=finding_id, relation=RelationType.CONFIRMED_BY, confidence=0.95))

        kg.metadata = {"organism": "Mycobacterium tuberculosis", "sources": len(literature)}
        return kg

    async def close(self) -> None:
        pass