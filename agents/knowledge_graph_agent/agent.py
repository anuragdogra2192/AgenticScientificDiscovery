"""Knowledge Graph Agent for building semantic representations of research discoveries."""

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
    """Represents a semantic knowledge graph of research discovery."""
    entities: Dict[str, KGEntity] = field(default_factory=dict)
    relationships: List[KGRelationship] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def add_entity(self, entity: KGEntity) -> None:
        """Add an entity to the knowledge graph."""
        self.entities[entity.id] = entity

    def add_relationship(self, relationship: KGRelationship) -> None:
        """Add a relationship to the knowledge graph."""
        self.relationships.append(relationship)

    def to_dict(self) -> dict:
        return {
            "entities": {k: v.to_dict() for k, v in self.entities.items()},
            "relationships": [r.to_dict() for r in self.relationships],
            "metadata": self.metadata,
            "created_at": self.created_at,
        }

    def to_rdf(self) -> str:
        """Export knowledge graph as RDF/XML."""
        rdf = '<?xml version="1.0" encoding="UTF-8"?>\n'
        rdf += '<rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#" '
        rdf += 'xmlns:rdfs="http://www.w3.org/2000/01/rdf-schema#">\n'

        for entity in self.entities.values():
            rdf += f'  <rdf:Description rdf:about="#{entity.id}">\n'
            rdf += f'    <rdfs:label>{entity.label}</rdfs:label>\n'
            rdf += f'    <rdf:type>{entity.entity_type.value}</rdf:type>\n'
            if entity.description:
                rdf += f'    <rdfs:comment>{entity.description}</rdfs:comment>\n'
            rdf += '  </rdf:Description>\n'

        for rel in self.relationships:
            rdf += f'  <rdf:Description rdf:about="#{rel.source_id}">\n'
            rdf += f'    <{rel.relation.value} rdf:resource="#{rel.target_id}" />\n'
            rdf += '  </rdf:Description>\n'

        rdf += '</rdf:RDF>'
        return rdf

    def to_turtle(self) -> str:
        """Export knowledge graph as Turtle/TTL."""
        ttl = "@prefix kg: <http://discovery.lab/kg/> .\n\n"

        for entity in self.entities.values():
            ttl += f'kg:{entity.id} a kg:{entity.entity_type.value} ;\n'
            ttl += f'  rdfs:label "{entity.label}" ;\n'
            if entity.description:
                ttl += f'  rdfs:comment "{entity.description}" ;\n'
            ttl += '  .\n\n'

        for rel in self.relationships:
            ttl += f'kg:{rel.source_id} kg:{rel.relation.value} kg:{rel.target_id} ;\n'
            ttl += f'  kg:confidence {rel.confidence} .\n\n'

        return ttl

    def to_json_ld(self) -> dict:
        """Export knowledge graph as JSON-LD."""
        return {
            "@context": {
                "@vocab": "http://discovery.lab/kg/",
                "entities": "@nest",
                "relationships": "@nest",
            },
            "@id": "http://discovery.lab/kg/graph",
            "@type": "KnowledgeGraph",
            "entities": [e.to_dict() for e in self.entities.values()],
            "relationships": [r.to_dict() for r in self.relationships],
            "metadata": self.metadata,
        }


class KnowledgeGraphAgent:
    """Agent for building semantic knowledge graphs from research discoveries."""

    def __init__(self, config_path: str = "agents/knowledge_graph_agent/config.yaml"):
        """Initialize the Knowledge Graph Agent."""
        if os.path.exists(config_path):
            with open(config_path, "r") as f:
                self.config = yaml.safe_load(f) or {}
        else:
            self.config = {}

        self.knowledge_graph = KnowledgeGraph()

        # Initialize Claude client if API key available
        self.use_claude = False
        self.claude_client = None
        if ANTHROPIC_AVAILABLE and os.environ.get("ANTHROPIC_API_KEY"):
            try:
                self.claude_client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
                self.use_claude = True
                logger.info("Claude Haiku API initialized for knowledge graph generation")
            except Exception as e:
                logger.warning(f"Could not initialize Claude API: {e}")
                self.use_claude = False

    async def build_knowledge_graph(
        self,
        literature: List[dict],
        hypothesis: dict,
        experiment_design: dict,
        analysis_report: dict,
    ) -> KnowledgeGraph:
        """Build a knowledge graph from research discovery artifacts."""
        logger.info("Building knowledge graph from discovery artifacts")

        # Try Claude first if available
        if self.use_claude and self.claude_client:
            try:
                logger.info("Using Claude Haiku for knowledge graph generation")
                return await self._build_with_claude(
                    literature, hypothesis, experiment_design, analysis_report
                )
            except Exception as e:
                logger.warning(f"Claude generation failed: {e}")
                self.use_claude = False

        # Fallback: Rule-based knowledge graph building
        logger.info("Using rule-based knowledge graph generation")
        return self._build_rule_based(
            literature, hypothesis, experiment_design, analysis_report
        )

    async def _build_with_claude(
        self,
        literature: List[dict],
        hypothesis: dict,
        experiment_design: dict,
        analysis_report: dict,
    ) -> KnowledgeGraph:
        """Build knowledge graph using Claude Haiku API."""
        prompt = f"""Analyze the following scientific discovery artifacts and extract structured knowledge graph entities and relationships.

HYPOTHESIS: {json.dumps(hypothesis, default=str)[:1000]}
EXPERIMENT DESIGN: {json.dumps(experiment_design, default=str)[:1000]}
ANALYSIS REPORT: {json.dumps(analysis_report, default=str)[:1000]}
LITERATURE SAMPLE: {json.dumps(literature[:3], default=str)[:1000]}

Return ONLY valid JSON with this structure:
{{
  "entities": [
    {{
      "id": "unique_id",
      "label": "Entity name",
      "type": "hypothesis|target|compound|disease|finding|methodology",
      "description": "Description",
      "properties": {{"key": "value"}}
    }}
  ],
  "relationships": [
    {{
      "source_id": "id1",
      "target_id": "id2",
      "relation": "targets|treats|inhibits|activates|associates_with|confirmed_by|contradicts|builds_on",
      "confidence": 0.85,
      "evidence": "Supporting evidence"
    }}
  ]
}}"""

        response = self.claude_client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=2048,
            messages=[{"role": "user", "content": prompt}],
        )

        response_text = response.content[0].text

        # Extract JSON from response
        json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
        if not json_match:
            raise ValueError("Claude did not return valid JSON")

        kg_data = json.loads(json_match.group())

        # Build knowledge graph from Claude response
        kg = KnowledgeGraph()

        # Add entities
        for entity_data in kg_data.get("entities", []):
            entity = KGEntity(
                id=entity_data.get("id", ""),
                label=entity_data.get("label", ""),
                entity_type=EntityType(entity_data.get("type", "finding")),
                description=entity_data.get("description"),
                properties=entity_data.get("properties", {}),
            )
            kg.add_entity(entity)

        # Add relationships
        for rel_data in kg_data.get("relationships", []):
            rel = KGRelationship(
                source_id=rel_data.get("source_id", ""),
                target_id=rel_data.get("target_id", ""),
                relation=RelationType(rel_data.get("relation", "related_to")),
                confidence=float(rel_data.get("confidence", 0.8)),
                supporting_evidence=rel_data.get("evidence"),
            )
            kg.add_relationship(rel)

        return kg

    def _build_rule_based(
        self,
        literature: List[dict],
        hypothesis: dict,
        experiment_design: dict,
        analysis_report: dict,
    ) -> KnowledgeGraph:
        """Build knowledge graph using rule-based logic."""
        kg = KnowledgeGraph()

        # Extract hypothesis entities
        hyp_id = f"hyp_{hash(hypothesis.get('title', '')) % 10000:04d}"
        kg.add_entity(
            KGEntity(
                id=hyp_id,
                label=hypothesis.get("title", "Hypothesis"),
                entity_type=EntityType.HYPOTHESIS,
                description=hypothesis.get("statement", ""),
            )
        )

        # Extract targets from hypothesis
        if "molecular_targets" in hypothesis:
            for target in hypothesis.get("molecular_targets", []):
                target_id = f"target_{hash(target) % 10000:04d}"
                kg.add_entity(
                    KGEntity(
                        id=target_id,
                        label=target,
                        entity_type=EntityType.TARGET,
                    )
                )
                kg.add_relationship(
                    KGRelationship(
                        source_id=hyp_id,
                        target_id=target_id,
                        relation=RelationType.TARGETS,
                        confidence=0.9,
                    )
                )

        # Extract disease entities
        if "disease_targets" in hypothesis:
            for disease in hypothesis.get("disease_targets", []):
                disease_id = f"disease_{hash(disease) % 10000:04d}"
                kg.add_entity(
                    KGEntity(
                        id=disease_id,
                        label=disease,
                        entity_type=EntityType.DISEASE,
                    )
                )
                kg.add_relationship(
                    KGRelationship(
                        source_id=hyp_id,
                        target_id=disease_id,
                        relation=RelationType.TREATS,
                        confidence=0.85,
                    )
                )

        # Add findings from analysis
        if analysis_report.get("primary_finding"):
            finding_id = "finding_primary"
            kg.add_entity(
                KGEntity(
                    id=finding_id,
                    label=analysis_report["primary_finding"].get("description", "Primary Finding"),
                    entity_type=EntityType.FINDING,
                    properties={
                        "effect_size": analysis_report["primary_finding"].get("effect_size"),
                        "p_value": analysis_report["primary_finding"].get("p_value"),
                    },
                )
            )
            kg.add_relationship(
                KGRelationship(
                    source_id=hyp_id,
                    target_id=finding_id,
                    relation=RelationType.CONFIRMED_BY,
                    confidence=0.9,
                )
            )

        kg.metadata = {
            "source_papers": len(literature),
            "hypothesis_tested": hypothesis.get("title"),
            "analysis_complete": analysis_report.get("hypothesis_confirmed"),
        }

        return kg

    async def close(self) -> None:
        """Clean up resources."""
        pass
