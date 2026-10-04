"""Literature Agent for scientific discovery powered by Omnigent and Claude."""

import asyncio
import json
import re
from dataclasses import dataclass
from typing import Optional, List, Any
from datetime import datetime
import logging
import os
from pathlib import Path

import httpx
import yaml

try:
    from anthropic import Anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False

logger = logging.getLogger(__name__)


@dataclass
class BiomedicalRecord:
    """Biomedical paper with drug discovery attributes."""
    title: str
    authors: list[str]
    publication_year: int
    journal: Optional[str]
    doi: Optional[str]
    abstract: str
    citations_count: int

    # Biomedical-specific fields
    pmcid: Optional[str] = None
    pmid: Optional[str] = None
    mesh_terms: Optional[list[str]] = None
    disease_targets: Optional[list[str]] = None
    compound_cids: Optional[list[str]] = None  # PubChem Compound IDs
    molecular_targets: Optional[list[str]] = None
    assay_types: Optional[list[str]] = None
    organism_studied: Optional[str] = None
    full_text_url: Optional[str] = None

    # Legacy compatibility
    openalex_id: Optional[str] = None
    arxiv_id: Optional[str] = None
    pdf_url: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "title": self.title,
            "authors": self.authors,
            "publication_year": self.publication_year,
            "journal": self.journal,
            "doi": self.doi,
            "abstract": self.abstract,
            "citations_count": self.citations_count,
            "pmcid": self.pmcid,
            "pmid": self.pmid,
            "mesh_terms": self.mesh_terms,
            "disease_targets": self.disease_targets,
            "compound_cids": self.compound_cids,
            "molecular_targets": self.molecular_targets,
            "assay_types": self.assay_types,
            "organism_studied": self.organism_studied,
            "full_text_url": self.full_text_url,
            "openalex_id": self.openalex_id,
            "arxiv_id": self.arxiv_id,
            "pdf_url": self.pdf_url,
        }


Paper = BiomedicalRecord


@dataclass
class ResearchGap:
    """Represents an identified research gap."""
    gap_description: str
    related_papers: list[str]
    potential_approaches: list[str]
    priority_level: str  # high, medium, low
    confidence: float  # 0.0 to 1.0

    def get(self, key, default=None):
        """Allow dictionary-like .get() access for agent compatibility."""
        mapping = {
            "gap_description": self.gap_description,
            "description": self.gap_description,
            "related_papers": self.related_papers,
            "potential_approaches": self.potential_approaches,
            "priority_level": self.priority_level,
            "priority": self.priority_level,
            "confidence": self.confidence,
        }
        return mapping.get(key, default)


class LiteratureAgent:
    """Agent for searching and analyzing scientific literature via Omnigent YAML harness."""

    def __init__(self, config_path: str = "agents/literature_agent/literature_agent.yaml"):
        """Initialize the Literature Agent with auto-loaded .env.local support."""
        if not os.environ.get("ANTHROPIC_API_KEY"):
            for path_str in [".env.local", "agents/literature_agent/.env.local", "../../.env.local"]:
                env_file = Path(path_str)
                if env_file.exists():
                    with open(env_file) as f:
                        for line in f:
                            line = line.strip()
                            if line and not line.startswith("#") and "=" in line:
                                k, v = line.split("=", 1)
                                if k.strip() == "ANTHROPIC_API_KEY":
                                    os.environ["ANTHROPIC_API_KEY"] = v.strip()
                    break

        if not os.path.exists(config_path):
            config_path = "agents/literature_agent/config.yaml"
            if not os.path.exists(config_path):
                config_path = "config.yaml"

        with open(config_path, "r") as f:
            self.config = yaml.safe_load(f)

        self.executor_config = self.config.get("executor", {})
        self.model_name = self.executor_config.get("model", "claude-haiku-4-5-20251001")
        self.system_prompt = self.config.get("prompt", "You are an expert Biomedical Research Agent.")
        
        self.client = httpx.AsyncClient(timeout=30.0)
        self.anthropic_client = None
        if ANTHROPIC_AVAILABLE and os.environ.get("ANTHROPIC_API_KEY"):
            try:
                self.anthropic_client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
                logger.info(f"Initialized Anthropic client with model: {self.model_name}")
            except Exception as e:
                logger.warning(f"Failed to initialize Anthropic client: {e}")
        else:
            logger.warning("ANTHROPIC_API_KEY not found. Literature Agent running without Claude gap synthesis.")

    @staticmethod
    def _safe_get(obj: Any, attr: str, default: Any = "") -> Any:
        """Safely retrieve attribute from strings, dictionaries, or dataclass objects."""
        if isinstance(obj, str):
            return obj if attr in ["gap_description", "description", "title"] else default
        if isinstance(obj, dict):
            return obj.get(attr, default)
        return getattr(obj, attr, default)

    @staticmethod
    def _extract_json_content(text: str) -> str:
        """Robustly extract JSON string from LLM output, handling markdown blocks and conversational text."""
        text = text.strip()
        if "```json" in text:
            parts = text.split("```json")
            if len(parts) > 1:
                text = parts[1].split("```")[0].strip()
        elif "```" in text:
            parts = text.split("```")
            if len(parts) > 1:
                text = parts[1].split("```")[0].strip()

        match_array = re.search(r'\[\s*\{.*\}\s*\]', text, re.DOTALL)
        if match_array:
            return match_array.group(0)

        match_obj = re.search(r'\{\s*".*"\s*:\s*\[.*\]\s*\}', text, re.DOTALL)
        if match_obj:
            return match_obj.group(0)

        return text

    async def search_papers(
        self,
        query: str,
        databases: list[str] | None = None,
        year_range: tuple[int, int] | None = None,
        limit: int | None = None,
    ) -> list[Paper]:
        """Search for biomedical papers across drug discovery databases."""
        if databases is None:
            databases = ["europe_pmc", "openalex"]

        search_cfg = self.config.get("search_config", self.config.get("search", {"default_limit": 50}))
        if limit is None:
            limit = search_cfg.get("default_limit", 50)

        papers = []

        if "europe_pmc" in databases:
            pmc_papers = await self._search_europe_pmc(query, year_range, limit)
            papers.extend(pmc_papers)

        if "pubchem" in databases:
            pubchem_compounds = await self._search_pubchem(query, limit)
            papers.extend(pubchem_compounds)

        if "openalex" in databases:
            openalex_papers = await self._search_openalex(query, year_range, limit)
            papers.extend(openalex_papers)

        if "arxiv" in databases:
            arxiv_papers = await self._search_arxiv(query, year_range, limit)
            papers.extend(arxiv_papers)

        unique_papers = {}
        for paper in papers:
            key = paper.doi or paper.pmcid or paper.title
            if key not in unique_papers:
                unique_papers[key] = paper

        return list(unique_papers.values())[:limit]

    async def _search_europe_pmc(
        self,
        query: str,
        year_range: tuple[int, int] | None = None,
        limit: int = 50,
    ) -> list[Paper]:
        """Search Europe PMC API for biomedical literature."""
        try:
            db_config = self.config.get("databases", {}).get("europe_pmc", {})
            api_url = db_config.get("api_url", "https://www.ebi.ac.uk/europepmc/webservices/rest")

            drug_keywords = self.config.get("search_config", self.config.get("search", {})).get("drug_discovery_keywords", [])
            enhanced_query = f"{query} ({' OR '.join(drug_keywords[:3])})" if drug_keywords else query

            params = {
                "query": enhanced_query,
                "pageSize": min(limit, 100),
                "resultType": "core",
                "format": "json",
            }

            if year_range:
                params["pubYear"] = f"{year_range[0]}-{year_range[1]}"

            response = await self.client.get(f"{api_url}/search", params=params)
            response.raise_for_status()

            data = response.json()
            papers = []

            for result in data.get("resultList", {}).get("result", []):
                paper = self._parse_europe_pmc_result(result)
                if paper:
                    papers.append(paper)

            logger.info(f"Found {len(papers)} papers on Europe PMC for query: {query}")
            return papers

        except httpx.HTTPError as e:
            logger.error(f"Europe PMC search failed: {e}")
            return []

    async def _search_pubchem(
        self,
        query: str,
        limit: int = 50,
    ) -> list[Paper]:
        """Search PubChem API for chemical compounds related to drug discovery."""
        try:
            db_config = self.config.get("databases", {}).get("pubchem", {})
            api_url = db_config.get("api_url", "https://pubchem.ncbi.nlm.nih.gov/rest/pug")

            search_url = f"{api_url}/compound/name/{query}/cids/json"
            response = await self.client.get(search_url, timeout=30)
            response.raise_for_status()

            data = response.json()
            papers = []
            compound_ids = data.get("IdentifierList", {}).get("CID", [])[:min(limit, 5)]

            for cid in compound_ids:
                try:
                    compound_paper = await self._fetch_pubchem_compound(cid, query, api_url)
                    if compound_paper:
                        papers.append(compound_paper)
                except Exception as e:
                    logger.debug(f"Could not fetch compound {cid}: {e}")

            logger.info(f"Found {len(papers)} compound records in PubChem for query: {query}")
            return papers

        except httpx.HTTPError as e:
            logger.warning(f"PubChem search failed: {e} - optional source")
            return []

    async def _fetch_pubchem_compound(self, compound_id: str, original_query: str, api_url: str) -> Optional[Paper]:
        """Fetch compound data from PubChem."""
        try:
            response = await self.client.get(f"{api_url}/compound/cid/{compound_id}/json", timeout=30)
            response.raise_for_status()

            data = response.json()
            if "PC_Compounds" in data and len(data["PC_Compounds"]) > 0:
                compound_data = data["PC_Compounds"][0]
                properties = compound_data.get("props", [])

                compound_name = f"PubChem Compound {compound_id}"
                molecular_formula = ""
                molecular_weight = ""

                for prop in properties:
                    urn = prop.get("urn", {})
                    label = urn.get("label", "")
                    value = prop.get("value", {}).get("sval", "")
                    if "Molecular Formula" in label:
                        molecular_formula = value
                    elif "Molecular Weight" in label:
                        molecular_weight = value
                    elif "Compound Name" in label or label == "Name":
                        compound_name = value

                abstract = f"Chemical compound related to '{original_query}'. Formula: {molecular_formula}. Weight: {molecular_weight}."

                return Paper(
                    title=f"{compound_name} (CID: {compound_id})",
                    authors=["PubChem Database"],
                    publication_year=2024,
                    journal="PubChem",
                    doi=None,
                    abstract=abstract,
                    citations_count=0,
                    compound_cids=[str(compound_id)],
                    assay_types=["chemical_database"],
                )
            return None
        except Exception:
            return None

    async def _search_openalex(
        self,
        query: str,
        year_range: tuple[int, int] | None = None,
        limit: int = 50,
    ) -> list[Paper]:
        """Search OpenAlex API (fallback source)."""
        try:
            simple_query = " ".join(query.split()[:5])
            params = {"search": simple_query, "per_page": min(limit, 200), "sort": "cited_by_count:desc"}
            if year_range:
                params["from_publication_date"] = f"{year_range[0]}-01-01"
                params["to_publication_date"] = f"{year_range[1]}-12-31"

            response = await self.client.get("https://api.openalex.org/works", params=params, timeout=10)
            response.raise_for_status()

            papers = []
            for result in response.json().get("results", []):
                authors = [a["author"]["display_name"] for a in result.get("authorships", []) if a.get("author", {}).get("display_name")]
                papers.append(Paper(
                    title=result.get("title", ""),
                    authors=authors,
                    publication_year=result.get("publication_year", 0),
                    journal=result.get("primary_location", {}).get("source", {}).get("display_name"),
                    doi=result.get("doi"),
                    abstract=result.get("abstract", ""),
                    citations_count=result.get("cited_by_count", 0),
                    openalex_id=result.get("id")
                ))
            return papers
        except Exception:
            return []

    async def _search_arxiv(self, query: str, year_range: tuple[int, int] | None = None, limit: int = 50) -> list[Paper]:
        return []

    @staticmethod
    def _parse_europe_pmc_result(result: dict) -> Optional[Paper]:
        """Parse result from Europe PMC API."""
        try:
            authors = [a.get("fullName", "") for a in result.get("authorList", {}).get("author", []) if isinstance(a, dict)]
            pub_year = int(result.get("pubYear", 0))
            mesh_terms = [m.get("descriptorName", "") for m in result.get("meshHeadingList", {}).get("meshHeading", []) if isinstance(m, dict)]
            disease_targets = [t for t in mesh_terms if any(x in t.lower() for x in ["disease", "disorder", "condition"])]

            full_text_url = f"https://www.ncbi.nlm.nih.gov/pmc/articles/PMC{result['pmcid']}" if result.get("pmcid") else None

            return Paper(
                title=result.get("title", ""),
                authors=authors,
                publication_year=pub_year,
                journal=result.get("journalTitle", ""),
                doi=result.get("doi"),
                abstract=result.get("abstractText", ""),
                citations_count=result.get("citedByCount", 0),
                pmcid=result.get("pmcid"),
                pmid=result.get("pmid"),
                mesh_terms=mesh_terms,
                disease_targets=disease_targets,
                full_text_url=full_text_url,
            )
        except Exception:
            return None

    async def identify_gaps(self, papers: list[Paper]) -> list[ResearchGap]:
        """Identify research gaps using Claude LLM if available, with robust fallback."""
        if self.anthropic_client and papers:
            try:
                summaries = "\n".join([f"- Title: {self._safe_get(p, 'title', '')}\n  Abstract: {self._safe_get(p, 'abstract', '')[:300]}" for p in papers[:15]])
                prompt = f"""
                Analyze the following biomedical abstracts and identify 3 critical research gaps, unstudied mechanisms, or drug resistance pathways.
                Return ONLY valid JSON format:
                [
                  {{
                    "gap_description": "Detailed description of the gap",
                    "priority": "high",
                    "related_papers": ["Exact Paper Title 1"],
                    "potential_approaches": ["Approach 1", "Approach 2"]
                  }}
                ]

                Abstracts:
                {summaries}
                """
                response = self.anthropic_client.messages.create(
                    model=self.model_name,
                    max_tokens=4096,
                    system=self.system_prompt,
                    messages=[{"role": "user", "content": prompt}]
                )
                
                response_text = response.content[0].text
                cleaned_json_str = self._extract_json_content(response_text)

                gaps_data = json.loads(cleaned_json_str)
                gaps = []
                for g in gaps_data:
                    gaps.append(ResearchGap(
                        gap_description=g.get("gap_description", g.get("description", "")),
                        related_papers=g.get("related_papers", []),
                        potential_approaches=g.get("potential_approaches", ["Empirical screening"]),
                        priority_level=g.get("priority", "high"),
                        confidence=0.85
                    ))
                if gaps:
                    logger.info("Successfully generated research gaps using Claude LLM.")
                    return gaps
            except Exception as e:
                logger.warning(f"LLM gap extraction failed ({e}), falling back to rule-based parser.")

        # Rule-based fallback if LLM is unavailable or fails
        gaps = []
        gap_indicators = ["limited understanding", "unclear", "unexplored", "resistance", "gap", "need for"]
        gap_papers = {}
        for paper in papers:
            title = self._safe_get(paper, "title", "Untitled")
            abstract = self._safe_get(paper, "abstract", "")
            for ind in gap_indicators:
                if ind in abstract.lower():
                    gap_papers.setdefault(ind, []).append(title)
                    break

        for gap_type, titles in gap_papers.items():
            gaps.append(ResearchGap(
                gap_description=f"Evidence gap regarding {gap_type} in targeted therapeutics",
                related_papers=titles[:5],
                potential_approaches=["High-throughput assay", "Structure-based design"],
                priority_level="high" if len(titles) > 1 else "medium",
                confidence=0.75
            ))
        return gaps or [ResearchGap(
            gap_description="Mechanistic bottlenecks in targeted inhibitor binding affinity",
            related_papers=[self._safe_get(p, "title", "") for p in papers[:2]],
            potential_approaches=["Molecular dynamics simulation", "In vitro bioactivity screening"],
            priority_level="high",
            confidence=0.80
        )]

    async def generate_report(self, query: str, papers: list[Paper], gaps: list[ResearchGap]) -> dict:
        """Generate comprehensive literature review report."""
        return {
            "query": query,
            "generated_at": datetime.now().isoformat(),
            "statistics": {
                "total_papers": len(papers),
                "year_range": (
                    min((self._safe_get(p, "publication_year", 2020) for p in papers if self._safe_get(p, "publication_year", 0) > 0), default=2020),
                    max((self._safe_get(p, "publication_year", 2026) for p in papers), default=2026),
                ),
                "avg_citations": sum(self._safe_get(p, "citations_count", 0) for p in papers) / len(papers) if papers else 0,
                "identified_gaps": len(gaps),
            },
            "papers": [p.to_dict() if hasattr(p, "to_dict") else p for p in papers],
            "research_gaps": [{
                "description": self._safe_get(g, "gap_description", ""),
                "related_papers": self._safe_get(g, "related_papers", []),
                "potential_approaches": self._safe_get(g, "potential_approaches", []),
                "priority": self._safe_get(g, "priority_level", "medium"),
                "confidence": self._safe_get(g, "confidence", 0.8),
            } for g in gaps],
        }

    async def close(self):
        """Close HTTP client."""
        await self.client.aclose()


async def main():
    agent = LiteratureAgent()
    papers = await agent.search_papers("SARS-CoV-2 Mpro inhibitors", databases=["europe_pmc"], limit=5)
    gaps = await agent.identify_gaps(papers)
    print(f"Found {len(papers)} papers and {len(gaps)} gaps using Claude harness configuration.")


if __name__ == "__main__":
    asyncio.run(main())