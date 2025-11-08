"""
Query Processor for Technical Analyst Agent

Processes technical requirements and analyzes conformity against
knowledge base using RAG engine.

This module provides the Query Processor component that:
1. Receives technical requirements from Document Structurer
2. Uses RAG Engine to search knowledge base
3. Analyzes conformity against documentation
4. Generates structured verdicts with evidence

Example:
    >>> from agents.technical_analyst import QueryProcessor, RAGEngine
    >>> rag_engine = RAGEngine.from_config()
    >>> processor = QueryProcessor(rag_engine)
    >>>
    >>> requirement = {
    ...     'id': 'REQ-001',
    ...     'descricao': 'Câmeras IP com resolução mínima 4MP',
    ...     'tipo': 'Técnico',
    ...     'categoria': 'Hardware'
    ... }
    >>>
    >>> result = processor.analyze_requirement(requirement)
    >>> print(f"Verdict: {result.conformity}")
    >>> print(f"Confidence: {result.confidence:.2f}")
    >>> print(f"Evidence: {len(result.evidence)} sources")
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from enum import Enum
import json
from pathlib import Path

from .rag_engine import RAGEngine


class ConformityVerdict(Enum):
    """
    Possible conformity verdicts for requirement analysis

    Attributes:
        CONFORME: Requirement meets all documentation/legal requirements
        NAO_CONFORME: Requirement does not meet requirements
        REVISAO: Requires human review (insufficient/ambiguous evidence)
    """
    CONFORME = "CONFORME"
    NAO_CONFORME = "NAO_CONFORME"
    REVISAO = "REVISAO"


@dataclass
class Evidence:
    """
    Evidence extracted from knowledge base

    Attributes:
        source: Source document filename
        text: Relevant text excerpt
        relevance: Similarity score (0-1)
        chunk_index: Index of chunk in source document
    """
    source: str
    text: str
    relevance: float
    chunk_index: int = 0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)


@dataclass
class ConformityAnalysis:
    """
    Result of conformity analysis for a requirement

    Attributes:
        requirement_id: Unique identifier of requirement
        conformity: Conformity verdict (CONFORME/NAO_CONFORME/REVISAO)
        confidence: Confidence score (0-1)
        evidence: List of evidence from knowledge base
        reasoning: Human-readable explanation
        recommendations: List of actionable recommendations
        sources: List of source documents used
        metadata: Additional metadata about the analysis
    """
    requirement_id: str
    conformity: ConformityVerdict
    confidence: float
    evidence: List[Evidence]
    reasoning: str
    recommendations: List[str]
    sources: List[str]
    metadata: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary with serializable values"""
        return {
            'requirement_id': self.requirement_id,
            'conformity': self.conformity.value,
            'confidence': self.confidence,
            'evidence': [e.to_dict() for e in self.evidence],
            'reasoning': self.reasoning,
            'recommendations': self.recommendations,
            'sources': self.sources,
            'metadata': self.metadata
        }

    def to_json(self, indent: int = 2) -> str:
        """Convert to JSON string"""
        return json.dumps(self.to_dict(), indent=indent, ensure_ascii=False)

    def save(self, filepath: str) -> None:
        """Save analysis to JSON file"""
        output_path = Path(filepath)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(self.to_json())


class QueryProcessor:
    """
    Processes queries for the Technical Analyst

    Main responsibilities:
    1. Retrieve relevant documentation using RAG
    2. Analyze conformity of requirements
    3. Generate structured verdicts with evidence
    4. Provide reasoning and recommendations

    Example:
        >>> processor = QueryProcessor(rag_engine)
        >>> analysis = processor.analyze_requirement(requirement)
        >>> print(f"Conformity: {analysis.conformity}")
        >>> print(f"Confidence: {analysis.confidence:.2%}")
        >>>
        >>> # Batch processing
        >>> results = processor.analyze_batch(requirements_list)
        >>> print(f"Analyzed {len(results)} requirements")
    """

    def __init__(
        self,
        rag_engine: RAGEngine,
        config: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize Query Processor

        Args:
            rag_engine: RAG engine for knowledge retrieval
            config: Optional configuration overrides
                - high_confidence (float): Threshold for CONFORME verdict (default: 0.85)
                - low_confidence (float): Threshold for NAO_CONFORME (default: 0.60)
                - min_evidence (int): Minimum evidence sources required (default: 2)
        """
        self.rag = rag_engine
        self.config = config or {}

        # Thresholds for conformity analysis
        self.high_confidence_threshold = self.config.get('high_confidence', 0.85)
        self.low_confidence_threshold = self.config.get('low_confidence', 0.60)
        self.min_evidence_count = self.config.get('min_evidence', 2)

        # Statistics
        self._stats = {
            'total_analyzed': 0,
            'conforme_count': 0,
            'nao_conforme_count': 0,
            'revisao_count': 0
        }

    def analyze_requirement(
        self,
        requirement: Dict[str, Any],
        top_k: int = 5,
        similarity_threshold: Optional[float] = None
    ) -> ConformityAnalysis:
        """
        Analyze a requirement against knowledge base

        Args:
            requirement: Technical requirement dict with keys:
                - id: Requirement identifier
                - descricao: Requirement description
                - tipo: Type (Técnico, Legal, etc.)
                - categoria: Category (Hardware, Software, etc.)
            top_k: Number of relevant documents to retrieve
            similarity_threshold: Minimum similarity score (uses RAG default if None)

        Returns:
            ConformityAnalysis with verdict, evidence, and reasoning

        Example:
            >>> req = {
            ...     'id': 'REQ-001',
            ...     'descricao': 'Câmeras IP com resolução 4MP',
            ...     'tipo': 'Técnico',
            ...     'categoria': 'Hardware'
            ... }
            >>> analysis = processor.analyze_requirement(req)
            >>> print(f"Verdict: {analysis.conformity}")
        """
        # 1. Extract query from requirement
        query = self._build_query(requirement)

        # 2. Search knowledge base using RAG
        search_params = {'top_k': top_k}
        if similarity_threshold is not None:
            search_params['similarity_threshold'] = similarity_threshold

        search_results = self.rag.search(query, **search_params)

        # 3. Extract evidence from search results
        evidence = self._extract_evidence(search_results)

        # 4. Analyze conformity based on evidence
        verdict, confidence = self._analyze_conformity(requirement, evidence)

        # 5. Generate human-readable reasoning
        reasoning = self._generate_reasoning(requirement, evidence, verdict)

        # 6. Generate actionable recommendations
        recommendations = self._generate_recommendations(
            requirement,
            evidence,
            verdict
        )

        # 7. Update statistics
        self._update_stats(verdict)

        # 8. Build and return analysis result
        return ConformityAnalysis(
            requirement_id=requirement.get('id', 'UNKNOWN'),
            conformity=verdict,
            confidence=confidence,
            evidence=evidence,
            reasoning=reasoning,
            recommendations=recommendations,
            sources=list(set([e.source for e in evidence])),
            metadata={
                'requirement': requirement,
                'search_results_count': len(search_results),
                'top_k': top_k,
                'query': query
            }
        )

    def _build_query(self, requirement: Dict[str, Any]) -> str:
        """
        Build search query from requirement

        Combines description with category/type for better retrieval

        Args:
            requirement: Requirement dictionary

        Returns:
            Query string optimized for RAG search
        """
        parts = []

        # Primary: description
        desc = requirement.get('descricao', '')
        if desc:
            parts.append(desc)

        # Secondary: category and type for context
        categoria = requirement.get('categoria', '')
        if categoria:
            parts.append(f"categoria: {categoria}")

        tipo = requirement.get('tipo', '')
        if tipo:
            parts.append(f"tipo: {tipo}")

        return ' '.join(parts)

    def _extract_evidence(
        self,
        search_results: List[Dict[str, Any]]
    ) -> List[Evidence]:
        """
        Extract evidence objects from RAG search results

        Args:
            search_results: Results from RAG engine search

        Returns:
            List of Evidence objects
        """
        evidence = []

        for result in search_results:
            metadata = result.get('metadata', {})

            evidence.append(Evidence(
                source=metadata.get('filename', 'unknown'),
                text=result.get('text', ''),
                relevance=result.get('similarity_score', 0.0),
                chunk_index=metadata.get('chunk_index', 0)
            ))

        return evidence

    def _analyze_conformity(
        self,
        requirement: Dict[str, Any],
        evidence: List[Evidence]
    ) -> tuple[ConformityVerdict, float]:
        """
        Analyze conformity based on evidence quality

        Decision logic:
        - High confidence + sufficient evidence → CONFORME
        - Low confidence → REVISAO
        - Medium confidence → REVISAO (requires human review)

        Args:
            requirement: Requirement being analyzed
            evidence: Evidence from knowledge base

        Returns:
            Tuple of (verdict, confidence_score)
        """
        # No evidence → needs review
        if not evidence:
            return ConformityVerdict.REVISAO, 0.0

        # Calculate average relevance score
        avg_relevance = sum(e.relevance for e in evidence) / len(evidence)

        # Get highest relevance (best match)
        max_relevance = max(e.relevance for e in evidence)

        # Weighted score: 70% average, 30% max
        confidence = (0.7 * avg_relevance) + (0.3 * max_relevance)

        # Determine verdict based on confidence and evidence count
        has_sufficient_evidence = len(evidence) >= self.min_evidence_count

        if confidence >= self.high_confidence_threshold and has_sufficient_evidence:
            verdict = ConformityVerdict.CONFORME
        elif confidence < self.low_confidence_threshold:
            # Low confidence → needs review (might be non-conformant)
            verdict = ConformityVerdict.REVISAO
        else:
            # Medium confidence → needs review
            verdict = ConformityVerdict.REVISAO

        return verdict, confidence

    def _generate_reasoning(
        self,
        requirement: Dict[str, Any],
        evidence: List[Evidence],
        verdict: ConformityVerdict
    ) -> str:
        """
        Generate human-readable reasoning for the verdict

        Args:
            requirement: Requirement being analyzed
            evidence: Evidence supporting the verdict
            verdict: Conformity verdict

        Returns:
            Explanation string
        """
        desc = requirement.get('descricao', 'requisito')
        evidence_count = len(evidence)

        if verdict == ConformityVerdict.CONFORME:
            avg_relevance = sum(e.relevance for e in evidence) / evidence_count if evidence_count > 0 else 0
            return (
                f"O requisito '{desc}' está em conformidade com a base de conhecimento. "
                f"Foram encontradas {evidence_count} evidências relevantes "
                f"(similaridade média: {avg_relevance:.1%})."
            )

        elif verdict == ConformityVerdict.NAO_CONFORME:
            return (
                f"O requisito '{desc}' NÃO está em conformidade. "
                f"A documentação encontrada não suporta este requisito "
                f"({evidence_count} fontes consultadas)."
            )

        else:  # REVISAO
            if evidence_count == 0:
                return (
                    f"O requisito '{desc}' requer revisão manual. "
                    f"Nenhuma evidência relevante foi encontrada na base de conhecimento."
                )
            else:
                avg_relevance = sum(e.relevance for e in evidence) / evidence_count
                return (
                    f"O requisito '{desc}' requer revisão manual. "
                    f"Evidências insuficientes ou ambíguas ({evidence_count} fontes, "
                    f"similaridade média: {avg_relevance:.1%})."
                )

    def _generate_recommendations(
        self,
        requirement: Dict[str, Any],
        evidence: List[Evidence],
        verdict: ConformityVerdict
    ) -> List[str]:
        """
        Generate actionable recommendations

        Args:
            requirement: Requirement being analyzed
            evidence: Evidence from knowledge base
            verdict: Conformity verdict

        Returns:
            List of recommendation strings
        """
        recommendations = []

        # Verdict-specific recommendations
        if verdict == ConformityVerdict.REVISAO:
            recommendations.append("✋ Revisar manualmente este requisito")
            recommendations.append("👤 Consultar especialista técnico se necessário")

        elif verdict == ConformityVerdict.CONFORME:
            recommendations.append("✅ Requisito validado automaticamente")
            recommendations.append("📋 Incluir evidências no relatório de conformidade")

        # Evidence quality recommendations
        if len(evidence) < self.min_evidence_count:
            recommendations.append(
                f"⚠️ Base de conhecimento pode estar incompleta "
                f"(apenas {len(evidence)} fontes encontradas)"
            )

        # Source diversity recommendations
        sources = set(e.source for e in evidence)
        if len(sources) == 1 and len(evidence) > 0:
            recommendations.append(
                "🔍 Considerar buscar fontes adicionais para validação cruzada"
            )

        # Low relevance warning
        if evidence:
            max_relevance = max(e.relevance for e in evidence)
            if max_relevance < 0.75:
                recommendations.append(
                    f"⚠️ Relevância moderada detectada (máx: {max_relevance:.1%}) - "
                    "validação adicional recomendada"
                )

        return recommendations

    def analyze_batch(
        self,
        requirements: List[Dict[str, Any]],
        top_k: int = 5,
        show_progress: bool = True
    ) -> List[ConformityAnalysis]:
        """
        Analyze multiple requirements in batch

        Args:
            requirements: List of technical requirements
            top_k: Number of relevant documents per requirement
            show_progress: Whether to show progress messages

        Returns:
            List of ConformityAnalysis results

        Example:
            >>> requirements = [
            ...     {'id': 'REQ-001', 'descricao': 'Câmera 4MP'},
            ...     {'id': 'REQ-002', 'descricao': 'Armazenamento 30 dias'}
            ... ]
            >>> results = processor.analyze_batch(requirements)
            >>> print(f"Analyzed: {len(results)}/{len(requirements)}")
        """
        results = []
        total = len(requirements)

        if show_progress:
            print(f"\n🔍 Analyzing {total} requirements...")
            print("=" * 60)

        for i, req in enumerate(requirements, 1):
            try:
                if show_progress:
                    req_id = req.get('id', 'UNKNOWN')
                    print(f"[{i}/{total}] Analyzing {req_id}...", end=' ')

                analysis = self.analyze_requirement(req, top_k=top_k)
                results.append(analysis)

                if show_progress:
                    print(f"✅ {analysis.conformity.value} ({analysis.confidence:.0%})")

            except Exception as e:
                req_id = req.get('id', 'UNKNOWN')
                print(f"\n❌ Error analyzing {req_id}: {e}")
                continue

        if show_progress:
            print("=" * 60)
            print(f"✅ Batch analysis complete: {len(results)}/{total} successful\n")

        return results

    def _update_stats(self, verdict: ConformityVerdict) -> None:
        """Update internal statistics"""
        self._stats['total_analyzed'] += 1

        if verdict == ConformityVerdict.CONFORME:
            self._stats['conforme_count'] += 1
        elif verdict == ConformityVerdict.NAO_CONFORME:
            self._stats['nao_conforme_count'] += 1
        else:
            self._stats['revisao_count'] += 1

    def get_stats(self) -> Dict[str, Any]:
        """
        Get processor statistics

        Returns:
            Dictionary with statistics and configuration
        """
        total = self._stats['total_analyzed']

        return {
            'total_analyzed': total,
            'verdicts': {
                'conforme': self._stats['conforme_count'],
                'nao_conforme': self._stats['nao_conforme_count'],
                'revisao': self._stats['revisao_count']
            },
            'percentages': {
                'conforme': (self._stats['conforme_count'] / total * 100) if total > 0 else 0,
                'nao_conforme': (self._stats['nao_conforme_count'] / total * 100) if total > 0 else 0,
                'revisao': (self._stats['revisao_count'] / total * 100) if total > 0 else 0
            },
            'config': {
                'high_confidence_threshold': self.high_confidence_threshold,
                'low_confidence_threshold': self.low_confidence_threshold,
                'min_evidence_count': self.min_evidence_count
            }
        }

    def reset_stats(self) -> None:
        """Reset statistics counters"""
        self._stats = {
            'total_analyzed': 0,
            'conforme_count': 0,
            'nao_conforme_count': 0,
            'revisao_count': 0
        }
