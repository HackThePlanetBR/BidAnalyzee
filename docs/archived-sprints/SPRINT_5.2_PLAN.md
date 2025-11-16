# Sprint 5.2 Plan - Query Processor

**Data de Início:** 08 de novembro de 2025
**Duração Estimada:** 8-10 horas
**Objetivo:** Implementar Query Processor para análise de conformidade de requisitos técnicos

---

## 🎯 Objetivo da História

Implementar o **Query Processor**, componente que:
1. Recebe requisitos técnicos extraídos pelo Document Structurer
2. Usa o RAG Engine para buscar informação relevante na base de conhecimento
3. Analisa conformidade do requisito contra a documentação encontrada
4. Gera veredicto estruturado com evidências e recomendações

---

## 📋 Critérios de Aceitação

- [ ] Classe `QueryProcessor` implementada
- [ ] Método `analyze_requirement()` funcional
- [ ] Integração com RAG Engine
- [ ] Geração de veredicto estruturado (CONFORME/NÃO_CONFORME/REVISÃO)
- [ ] Cálculo de score de confiança
- [ ] Extração de evidências da base de conhecimento
- [ ] Sistema de reasoning/justificativa
- [ ] Testes unitários (90%+ cobertura)
- [ ] Testes de integração end-to-end
- [ ] Documentação completa

---

## 🏗️ Arquitetura

### Componentes

```
┌──────────────────────────────────────────────┐
│        Technical Analyst Agent               │
│                                              │
│  ┌────────────────┐      ┌───────────────┐  │
│  │     Query      │─────▶│   RAG Engine  │  │
│  │   Processor    │      │   (Busca)     │  │
│  └────────────────┘      └───────────────┘  │
│         │                        │           │
│         ▼                        ▼           │
│  ┌────────────────┐      ┌───────────────┐  │
│  │   Conformity   │      │ Vector Store  │  │
│  │    Analyzer    │      │    (FAISS)    │  │
│  └────────────────┘      └───────────────┘  │
│         │                                    │
│         ▼                                    │
│  ┌────────────────┐                         │
│  │   Evidence     │                         │
│  │   Generator    │                         │
│  └────────────────┘                         │
└──────────────────────────────────────────────┘
```

### Input/Output

**Input:**
```python
{
    "id": "REQ-001",
    "descricao": "Câmeras IP com resolução mínima 4MP",
    "tipo": "Técnico",
    "categoria": "Hardware",
    "metadata": {...}
}
```

**Output:**
```python
{
    "requirement_id": "REQ-001",
    "conformity": "CONFORME | NAO_CONFORME | REVISAO",
    "confidence": 0.85,  # 0-1
    "evidence": [
        {
            "source": "requisitos_tecnicos_comuns.md",
            "text": "Câmeras IP devem ter resolução mínima de 4MP...",
            "relevance": 0.92
        }
    ],
    "reasoning": "O requisito está em conformidade pois...",
    "recommendations": ["Verificar compatibilidade com...", ...],
    "sources": ["requisitos_tecnicos_comuns.md", ...]
}
```

---

## 📝 Implementação Detalhada

### 1. `query_processor.py`

```python
"""
Query Processor for Technical Analyst Agent

Processes technical requirements and analyzes conformity against
knowledge base using RAG engine.
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum

from .rag_engine import RAGEngine


class ConformityVerdict(Enum):
    """Possible conformity verdicts"""
    CONFORME = "CONFORME"           # Meets all requirements
    NAO_CONFORME = "NAO_CONFORME"   # Does not meet requirements
    REVISAO = "REVISAO"              # Requires human review


@dataclass
class Evidence:
    """Evidence from knowledge base"""
    source: str
    text: str
    relevance: float
    chunk_index: int = 0


@dataclass
class ConformityAnalysis:
    """Result of conformity analysis"""
    requirement_id: str
    conformity: ConformityVerdict
    confidence: float
    evidence: List[Evidence]
    reasoning: str
    recommendations: List[str]
    sources: List[str]
    metadata: Dict[str, Any]


class QueryProcessor:
    """
    Processes queries for the Technical Analyst

    Main responsibilities:
    1. Retrieve relevant documentation using RAG
    2. Analyze conformity of requirements
    3. Generate structured verdicts with evidence
    4. Provide reasoning and recommendations
    """

    def __init__(self, rag_engine: RAGEngine, config: Optional[Dict] = None):
        """
        Initialize Query Processor

        Args:
            rag_engine: RAG engine for knowledge retrieval
            config: Optional configuration overrides
        """
        self.rag = rag_engine
        self.config = config or {}

        # Thresholds
        self.high_confidence_threshold = self.config.get('high_confidence', 0.85)
        self.low_confidence_threshold = self.config.get('low_confidence', 0.60)
        self.min_evidence_count = self.config.get('min_evidence', 2)

    def analyze_requirement(
        self,
        requirement: Dict[str, Any],
        top_k: int = 5
    ) -> ConformityAnalysis:
        """
        Analyze a requirement against knowledge base

        Args:
            requirement: Technical requirement from edital
            top_k: Number of relevant documents to retrieve

        Returns:
            ConformityAnalysis with verdict, evidence, and reasoning
        """
        # 1. Extract query from requirement
        query = self._build_query(requirement)

        # 2. Search knowledge base
        search_results = self.rag.search(query, top_k=top_k)

        # 3. Extract evidence
        evidence = self._extract_evidence(search_results)

        # 4. Analyze conformity
        verdict, confidence = self._analyze_conformity(
            requirement,
            evidence
        )

        # 5. Generate reasoning
        reasoning = self._generate_reasoning(
            requirement,
            evidence,
            verdict
        )

        # 6. Generate recommendations
        recommendations = self._generate_recommendations(
            requirement,
            evidence,
            verdict
        )

        # 7. Build result
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
                'top_k': top_k
            }
        )

    def _build_query(self, requirement: Dict[str, Any]) -> str:
        """Build search query from requirement"""
        # Combine description with category/type for better retrieval
        parts = [requirement.get('descricao', '')]

        if 'categoria' in requirement:
            parts.append(f"categoria: {requirement['categoria']}")
        if 'tipo' in requirement:
            parts.append(f"tipo: {requirement['tipo']}")

        return ' '.join(parts)

    def _extract_evidence(self, search_results: List[Dict]) -> List[Evidence]:
        """Extract evidence from search results"""
        evidence = []

        for result in search_results:
            evidence.append(Evidence(
                source=result['metadata'].get('filename', 'unknown'),
                text=result['text'],
                relevance=result.get('similarity_score', 0.0),
                chunk_index=result['metadata'].get('chunk_index', 0)
            ))

        return evidence

    def _analyze_conformity(
        self,
        requirement: Dict[str, Any],
        evidence: List[Evidence]
    ) -> tuple[ConformityVerdict, float]:
        """
        Analyze conformity based on evidence

        Returns: (verdict, confidence)
        """
        if not evidence:
            return ConformityVerdict.REVISAO, 0.0

        # Calculate average relevance
        avg_relevance = sum(e.relevance for e in evidence) / len(evidence)

        # Determine verdict based on relevance and evidence quality
        if avg_relevance >= self.high_confidence_threshold and len(evidence) >= self.min_evidence_count:
            verdict = ConformityVerdict.CONFORME
            confidence = avg_relevance
        elif avg_relevance < self.low_confidence_threshold:
            verdict = ConformityVerdict.REVISAO
            confidence = avg_relevance
        else:
            # Medium confidence - needs review
            verdict = ConformityVerdict.REVISAO
            confidence = avg_relevance

        return verdict, confidence

    def _generate_reasoning(
        self,
        requirement: Dict[str, Any],
        evidence: List[Evidence],
        verdict: ConformityVerdict
    ) -> str:
        """Generate human-readable reasoning"""
        if verdict == ConformityVerdict.CONFORME:
            return f"O requisito '{requirement.get('descricao')}' está em conformidade com a base de conhecimento. Foram encontradas {len(evidence)} evidências relevantes."
        elif verdict == ConformityVerdict.NAO_CONFORME:
            return f"O requisito '{requirement.get('descricao')}' NÃO está em conformidade. A documentação encontrada não suporta este requisito."
        else:  # REVISAO
            return f"O requisito '{requirement.get('descricao')}' requer revisão manual. Evidências insuficientes ou ambíguas ({len(evidence)} fontes encontradas)."

    def _generate_recommendations(
        self,
        requirement: Dict[str, Any],
        evidence: List[Evidence],
        verdict: ConformityVerdict
    ) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []

        if verdict == ConformityVerdict.REVISAO:
            recommendations.append("Revisar manualmente este requisito")
            recommendations.append("Consultar especialista técnico se necessário")

        if len(evidence) < self.min_evidence_count:
            recommendations.append("Base de conhecimento pode estar incompleta para este tópico")

        # Add source-specific recommendations
        sources = set(e.source for e in evidence)
        if len(sources) == 1:
            recommendations.append("Considerar buscar fontes adicionais para validação")

        return recommendations

    def analyze_batch(
        self,
        requirements: List[Dict[str, Any]],
        top_k: int = 5
    ) -> List[ConformityAnalysis]:
        """
        Analyze multiple requirements in batch

        Args:
            requirements: List of technical requirements
            top_k: Number of relevant documents per requirement

        Returns:
            List of ConformityAnalysis results
        """
        results = []

        for req in requirements:
            try:
                analysis = self.analyze_requirement(req, top_k=top_k)
                results.append(analysis)
            except Exception as e:
                # Log error but continue processing
                print(f"Error analyzing requirement {req.get('id')}: {e}")
                continue

        return results

    def get_stats(self) -> Dict[str, Any]:
        """Get processor statistics"""
        return {
            'config': self.config,
            'thresholds': {
                'high_confidence': self.high_confidence_threshold,
                'low_confidence': self.low_confidence_threshold,
                'min_evidence': self.min_evidence_count
            }
        }
```

---

## 🧪 Testes

### Unit Tests (`tests/unit/test_query_processor.py`)

```python
import pytest
from agents.technical_analyst.query_processor import QueryProcessor, ConformityVerdict


class TestQueryProcessor:
    """Unit tests for Query Processor"""

    def test_build_query(self, query_processor):
        """Test query building from requirement"""
        req = {
            'descricao': 'Câmera 4MP',
            'categoria': 'Hardware',
            'tipo': 'Técnico'
        }

        query = query_processor._build_query(req)

        assert 'Câmera 4MP' in query
        assert 'Hardware' in query

    def test_extract_evidence(self, query_processor, mock_search_results):
        """Test evidence extraction"""
        evidence = query_processor._extract_evidence(mock_search_results)

        assert len(evidence) > 0
        assert all(hasattr(e, 'source') for e in evidence)
        assert all(hasattr(e, 'relevance') for e in evidence)

    def test_analyze_conformity_high_confidence(self, query_processor, high_quality_evidence):
        """Test conformity analysis with high confidence evidence"""
        verdict, confidence = query_processor._analyze_conformity({}, high_quality_evidence)

        assert verdict == ConformityVerdict.CONFORME
        assert confidence > 0.85

    def test_analyze_conformity_low_confidence(self, query_processor, low_quality_evidence):
        """Test conformity analysis with low confidence evidence"""
        verdict, confidence = query_processor._analyze_conformity({}, low_quality_evidence)

        assert verdict == ConformityVerdict.REVISAO
        assert confidence < 0.60

    def test_generate_reasoning(self, query_processor):
        """Test reasoning generation"""
        req = {'descricao': 'Test requirement'}
        evidence = []

        reasoning = query_processor._generate_reasoning(
            req, evidence, ConformityVerdict.REVISAO
        )

        assert isinstance(reasoning, str)
        assert len(reasoning) > 0
```

### Integration Tests (`tests/integration/test_query_processor.py`)

```python
import pytest
from agents.technical_analyst.query_processor import QueryProcessor
from agents.technical_analyst.rag_engine import RAGEngine


class TestQueryProcessorIntegration:
    """Integration tests for Query Processor with RAG Engine"""

    def test_end_to_end_analysis(self, rag_engine, sample_requirement):
        """Test complete requirement analysis flow"""
        processor = QueryProcessor(rag_engine)

        result = processor.analyze_requirement(sample_requirement)

        assert result.requirement_id == sample_requirement['id']
        assert result.conformity in [v for v in ConformityVerdict]
        assert 0 <= result.confidence <= 1
        assert len(result.evidence) > 0
        assert len(result.reasoning) > 0

    def test_batch_analysis(self, rag_engine, sample_requirements):
        """Test batch requirement analysis"""
        processor = QueryProcessor(rag_engine)

        results = processor.analyze_batch(sample_requirements)

        assert len(results) == len(sample_requirements)
        assert all(r.conformity is not None for r in results)
```

---

## 📊 Métricas de Sucesso

| Métrica | Target | Como Medir |
|---------|--------|------------|
| Tempo de análise | < 2s por requisito | Timer no método |
| Precisão | > 80% conformidade correta | Validação manual |
| Cobertura de testes | > 90% | pytest-cov |
| Evidências por análise | ≥ 2 fontes | Contagem automática |

---

## 📅 Cronograma

### Fase 1: Implementação Core (4-5h)
- [ ] Criar `query_processor.py`
- [ ] Implementar classes e dataclasses
- [ ] Implementar método `analyze_requirement()`
- [ ] Implementar métodos auxiliares

### Fase 2: Testes (2-3h)
- [ ] Criar testes unitários
- [ ] Criar testes de integração
- [ ] Atingir 90%+ cobertura
- [ ] Validar com casos reais

### Fase 3: Documentação (2h)
- [ ] Docstrings completas
- [ ] Exemplos de uso
- [ ] Atualizar TECHNICAL_ANALYST_RAG.md
- [ ] Criar guia de análise

---

## ✅ Definition of Done

História 5.2 está completa quando:

- [ ] `QueryProcessor` classe implementada
- [ ] Todos os métodos funcionais e testados
- [ ] Integração com RAG Engine validada
- [ ] Testes unitários > 90% cobertura
- [ ] Testes de integração passando
- [ ] Documentação completa
- [ ] Código commitado e pushed
- [ ] Exemplos de uso documentados
- [ ] Performance targets atingidos

---

**Status:** 🚀 Ready to Start
**Próximo Passo:** Implementar query_processor.py
**Responsável:** Claude (Technical Analyst development)
**Data:** 08 de novembro de 2025
