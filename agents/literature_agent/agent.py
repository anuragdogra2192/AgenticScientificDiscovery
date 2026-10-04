"""Literature Agent for scientific discovery."""

import asyncio
import json
from dataclasses import dataclass
from typing import Optional
from datetime import datetime
import logging

import httpx
import yaml

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


# Keep legacy Paper name for backward compatibility
Paper = BiomedicalRecord


@dataclass
class ResearchGap:
    """Represents an identified research gap."""
    gap_description: str
    related_papers: list[str]
    potential_approaches: list[str]
    priority_level: str  # high, medium, low
    confidence: float  # 0.0 to 1.0


class LiteratureAgent:
    """Agent for searching and analyzing scientific literature."""

    def __init__(self, config_path: str = "agents/literature_agent/config.yaml"):
        """Initialize the Literature Agent."""
        with open(config_path, "r") as f:
            self.config = yaml.safe_load(f)

        self.papers_cache: dict[str, Paper] = {}
        self.gaps_cache: dict[str, ResearchGap] = {}
        self.client = httpx.AsyncClient(timeout=30.0)

    async def search_papers(
        self,
        query: str,
        databases: list[str] | None = None,
        year_range: tuple[int, int] | None = None,
        limit: int | None = None,
    ) -> list[Paper]:
        """Search for biomedical papers across drug discovery databases."""
        if databases is None:
            databases = ["europe_pmc", "openalex"]  # Default to biomedical sources

        if limit is None:
            limit = self.config["search"]["default_limit"]

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

        # Deduplicate by DOI or PMCID or title
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
            # Add drug discovery keywords to enhance search
            drug_keywords = self.config["search"].get("drug_discovery_keywords", [])
            enhanced_query = f"{query} ({' OR '.join(drug_keywords[:3])})"

            params = {
                "query": enhanced_query,
                "pageSize": min(limit, 100),
                "resultType": "core",
                "format": "json",
            }

            if year_range:
                params["pubYear"] = f"{year_range[0]}-{year_range[1]}"

            response = await self.client.get(
                f"{self.config['databases']['europe_pmc']['api_url']}/search",
                params=params,
            )
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
            # First search for compounds matching the query
            compound_params = {
                "q": query,
                "type": "cid",
            }

            response = await self.client.get(
                f"{self.config['databases']['pubchem']['api_url']}/compound/search/json",
                params=compound_params,
            )
            response.raise_for_status()

            data = response.json()
            papers = []
            compound_ids = data.get("IdentifierList", {}).get("CID", [])[:min(limit, 10)]

            # For each compound, get bioactivity data
            for cid in compound_ids:
                compound_papers = await self._fetch_pubchem_bioactivity(cid, query)
                papers.extend(compound_papers)

            logger.info(f"Found {len(papers)} compound-related records in PubChem for query: {query}")
            return papers

        except httpx.HTTPError as e:
            logger.error(f"PubChem search failed: {e}")
            return []

    async def _fetch_pubchem_bioactivity(self, compound_id: str, original_query: str) -> list[Paper]:
        """Fetch bioactivity data for a PubChem compound."""
        try:
            response = await self.client.get(
                f"{self.config['databases']['pubchem']['api_url']}/compound/{compound_id}/json"
            )
            response.raise_for_status()

            data = response.json()
            compound_data = data.get("PC_CompoundAssay", {})

            papers = []
            if compound_data:
                paper = self._parse_pubchem_result(compound_data, compound_id, original_query)
                if paper:
                    papers.append(paper)

            return papers

        except httpx.HTTPError as e:
            logger.warning(f"Failed to fetch PubChem bioactivity for CID {compound_id}: {e}")
            return []

    async def _search_openalex(
        self,
        query: str,
        year_range: tuple[int, int] | None = None,
        limit: int = 50,
    ) -> list[Paper]:
        """Search OpenAlex API."""
        try:
            params = {
                "search": query,
                "per_page": min(limit, 200),
                "sort": "cited_by_count:desc",
            }

            if year_range:
                params["from_publication_date"] = f"{year_range[0]}-01-01"
                params["to_publication_date"] = f"{year_range[1]}-12-31"

            response = await self.client.get(
                f"{self.config['databases']['openalex']['api_url']}/works",
                params=params,
            )
            response.raise_for_status()

            data = response.json()
            papers = []

            for result in data.get("results", []):
                paper = self._parse_openalex_result(result)
                if paper:
                    papers.append(paper)

            logger.info(f"Found {len(papers)} papers on OpenAlex for query: {query}")
            return papers

        except httpx.HTTPError as e:
            logger.error(f"OpenAlex search failed: {e}")
            return []

    async def _search_arxiv(
        self,
        query: str,
        year_range: tuple[int, int] | None = None,
        limit: int = 50,
    ) -> list[Paper]:
        """Search arXiv API."""
        try:
            # arXiv uses a different query format
            search_query = f"search_query=all:{query}"
            if year_range:
                search_query += f" AND submittedDate:[{year_range[0]}010100000000Z TO {year_range[1]}123123595999Z]"

            search_query += f"&start=0&max_results={min(limit, 2000)}&sortBy=relevance&sortOrder=descending"

            response = await self.client.get(
                f"{self.config['databases']['arxiv']['api_url']}?{search_query}",
            )
            response.raise_for_status()

            papers = []
            # Parse XML response (simplified)
            from xml.etree import ElementTree as ET
            root = ET.fromstring(response.text)

            # arXiv uses Atom namespace
            ns = {"atom": "http://www.w3.org/2005/Atom"}

            for entry in root.findall("atom:entry", ns):
                paper = self._parse_arxiv_result(entry, ns)
                if paper:
                    papers.append(paper)

            logger.info(f"Found {len(papers)} papers on arXiv for query: {query}")
            return papers

        except (httpx.HTTPError, ET.ParseError) as e:
            logger.error(f"arXiv search failed: {e}")
            return []

    @staticmethod
    def _parse_europe_pmc_result(result: dict) -> Optional[Paper]:
        """Parse a result from Europe PMC API."""
        try:
            authors = []
            author_list = result.get("authorList", {}).get("author", [])
            if isinstance(author_list, list):
                for author in author_list[:10]:
                    if isinstance(author, dict):
                        authors.append(author.get("fullName", ""))
            elif isinstance(author_list, dict):
                authors.append(author_list.get("fullName", ""))

            pub_year_str = result.get("pubYear", "0")
            try:
                pub_year = int(pub_year_str)
            except ValueError:
                pub_year = 0

            mesh_terms = []
            mesh_list = result.get("meshHeadingList", {}).get("meshHeading", [])
            if isinstance(mesh_list, list):
                for mesh in mesh_list[:10]:
                    if isinstance(mesh, dict):
                        mesh_terms.append(mesh.get("descriptorName", ""))

            disease_targets = [t for t in mesh_terms if any(
                x in t.lower() for x in ["disease", "disorder", "condition"]
            )]

            full_text_url = None
            if result.get("pmcid"):
                full_text_url = f"https://www.ncbi.nlm.nih.gov/pmc/articles/PMC{result['pmcid']}"

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
        except (KeyError, TypeError):
            return None

    @staticmethod
    def _parse_pubchem_result(compound_data: dict, compound_id: str, original_query: str) -> Optional[Paper]:
        """Parse bioactivity data from PubChem compound."""
        try:
            # Extract compound information
            assay_data = compound_data.get("PC_CompoundAssay_Assay", [])
            if not assay_data:
                return None

            assay_info = assay_data[0] if isinstance(assay_data, list) else assay_data

            assay_description = assay_info.get("description", "Compound bioactivity data from PubChem")
            target_name = assay_info.get("target", {}).get("name", "Unknown Target")

            return Paper(
                title=f"Bioactivity Study: {original_query} (CID: {compound_id})",
                authors=["PubChem Database"],
                publication_year=2024,
                journal="PubChem",
                doi=None,
                abstract=assay_description,
                citations_count=0,
                compound_cids=[compound_id],
                molecular_targets=[target_name],
                assay_types=[assay_info.get("assayType", "Unknown")],
                organism_studied=assay_info.get("organism", ""),
            )
        except (KeyError, TypeError, IndexError):
            return None

    @staticmethod
    def _parse_openalex_result(result: dict) -> Optional[Paper]:
        """Parse a result from OpenAlex API."""
        try:
            authors = []
            for author_info in result.get("authorships", []):
                if author_info.get("author", {}).get("display_name"):
                    authors.append(author_info["author"]["display_name"])

            # Get the primary location for PDF
            pdf_url = None
            for location in result.get("open_access", {}).get("oa_locations", []):
                if location.get("pdf_url"):
                    pdf_url = location["pdf_url"]
                    break

            return Paper(
                title=result.get("title", ""),
                authors=authors,
                publication_year=result.get("publication_year", 0),
                journal=result.get("primary_location", {}).get("source", {}).get("display_name"),
                doi=result.get("doi"),
                abstract=result.get("abstract", ""),
                citations_count=result.get("cited_by_count", 0),
                openalex_id=result.get("id"),
                pdf_url=pdf_url,
            )
        except (KeyError, TypeError):
            return None

    @staticmethod
    def _parse_arxiv_result(entry, ns: dict) -> Optional[Paper]:
        """Parse a result from arXiv API."""
        try:
            from xml.etree import ElementTree as ET

            title = entry.findtext("atom:title", "", ns)
            authors = []
            for author in entry.findall("atom:author", ns):
                name = author.findtext("atom:name", "", ns)
                if name:
                    authors.append(name)

            published = entry.findtext("atom:published", "", ns)
            pub_year = int(published.split("-")[0]) if published else 0

            arxiv_id = entry.findtext("atom:id", "", ns).split("/abs/")[-1]
            pdf_url = f"https://arxiv.org/pdf/{arxiv_id}.pdf"

            summary = entry.findtext("atom:summary", "", ns).strip()

            return Paper(
                title=title,
                authors=authors,
                publication_year=pub_year,
                journal="arXiv",
                doi=None,
                abstract=summary,
                citations_count=0,
                arxiv_id=arxiv_id,
                pdf_url=pdf_url,
            )
        except (KeyError, IndexError, ValueError):
            return None

    async def identify_gaps(self, papers: list[Paper]) -> list[ResearchGap]:
        """Identify research gaps from a collection of papers."""
        gaps = []

        # Extract common themes and methodologies
        abstracts = [p.abstract for p in papers if p.abstract]

        # Simple gap detection: look for words like "limited", "future", "unclear", "unexplored"
        gap_indicators = [
            "limited understanding",
            "unclear",
            "unexplored",
            "future work",
            "further investigation",
            "lacks",
            "gap",
            "need for",
            "missing",
        ]

        gap_papers = {}
        for paper in papers:
            for indicator in gap_indicators:
                if indicator.lower() in paper.abstract.lower():
                    if indicator not in gap_papers:
                        gap_papers[indicator] = []
                    gap_papers[indicator].append(paper.title)
                    break

        # Create gap entries
        for gap_type, related_paper_titles in gap_papers.items():
            confidence = min(len(related_paper_titles) / len(papers), 1.0)

            gaps.append(
                ResearchGap(
                    gap_description=f"Multiple papers highlight {gap_type}",
                    related_papers=related_paper_titles[:5],
                    potential_approaches=[
                        "Literature review synthesis",
                        "Empirical investigation",
                        "Theoretical framework development",
                        "Interdisciplinary collaboration",
                    ],
                    priority_level=self._assess_priority(confidence),
                    confidence=confidence,
                )
            )

        return gaps

    @staticmethod
    def _assess_priority(confidence: float) -> str:
        """Assess priority level based on confidence."""
        if confidence >= 0.7:
            return "high"
        elif confidence >= 0.4:
            return "medium"
        else:
            return "low"

    async def generate_report(
        self,
        query: str,
        papers: list[Paper],
        gaps: list[ResearchGap],
    ) -> dict:
        """Generate a comprehensive literature review report."""
        return {
            "query": query,
            "generated_at": datetime.now().isoformat(),
            "statistics": {
                "total_papers": len(papers),
                "year_range": (
                    min(p.publication_year for p in papers),
                    max(p.publication_year for p in papers),
                ) if papers else (None, None),
                "avg_citations": sum(p.citations_count for p in papers) / len(papers) if papers else 0,
                "identified_gaps": len(gaps),
            },
            "papers": [p.to_dict() for p in papers],
            "research_gaps": [
                {
                    "description": g.gap_description,
                    "related_papers": g.related_papers,
                    "potential_approaches": g.potential_approaches,
                    "priority": g.priority_level,
                    "confidence": g.confidence,
                }
                for g in gaps
            ],
        }

    async def close(self):
        """Close the agent and clean up resources."""
        await self.client.aclose()


async def main():
    """Example usage of the Literature Agent for drug discovery."""
    agent = LiteratureAgent()

    try:
        # Drug discovery search example
        print("🔍 Searching for drug discovery literature on cancer immunotherapy...")
        papers = await agent.search_papers(
            "cancer immunotherapy PD-1 checkpoint inhibitor",
            databases=["europe_pmc", "openalex"],
            year_range=(2020, 2026),
            limit=15,
        )

        print(f"Found {len(papers)} biomedical records")
        for i, paper in enumerate(papers[:5], 1):
            print(f"\n{i}. {paper.title}")
            print(f"   Authors: {', '.join(paper.authors[:2])}")
            print(f"   Year: {paper.publication_year}")
            print(f"   Citations: {paper.citations_count}")
            if paper.pmcid:
                print(f"   PMCID: {paper.pmcid}")
            if paper.mesh_terms:
                print(f"   MeSH Terms: {', '.join(paper.mesh_terms[:2])}")
            if paper.disease_targets:
                print(f"   Disease Targets: {', '.join(paper.disease_targets[:2])}")
            if paper.compound_cids:
                print(f"   PubChem IDs: {', '.join(paper.compound_cids)}")

        # Identify gaps in drug discovery
        print("\n\n🔎 Analyzing drug discovery research gaps...")
        gaps = await agent.identify_gaps(papers)

        print(f"Identified {len(gaps)} research gaps")
        for gap in gaps[:3]:
            print(f"\n- {gap.gap_description}")
            print(f"  Priority: {gap.priority_level} (confidence: {gap.confidence:.2f})")

        # Generate report
        print("\n\n📊 Generating biomedical literature report...")
        report = await agent.generate_report(
            "cancer immunotherapy drug discovery",
            papers,
            gaps,
        )

        print(f"\nReport Summary:")
        print(f"Total papers: {report['statistics']['total_papers']}")
        print(f"Year range: {report['statistics']['year_range']}")
        print(f"Avg citations: {report['statistics']['avg_citations']:.1f}")
        print(f"Identified gaps: {report['statistics']['identified_gaps']}")

    finally:
        await agent.close()


if __name__ == "__main__":
    asyncio.run(main())
