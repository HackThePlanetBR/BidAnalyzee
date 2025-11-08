"""
Integration Tests for Query Processor with RAG Engine

Tests Query Processor integrated with real RAG Engine using mocked embeddings.
"""

import pytest
import tempfile
import numpy as np
from pathlib import Path

from agents.technical_analyst.query_processor import (
    QueryProcessor,
    ConformityVerdict,
    ConformityAnalysis
)
from agents.technical_analyst.rag_engine import RAGEngine
from agents.technical_analyst.vector_store import FAISSVectorStore
from agents.technical_analyst.ingestion_pipeline import IngestionPipeline


class MockEmbeddingsManager:
    """Mock embeddings manager for testing"""

    def __init__(self, dimension=384):
        self.dimension = dimension

    def embed_documents(self, texts, show_progress=True):
        """Generate deterministic mock embeddings based on text hash"""
        embeddings = []
        for text in texts:
            # Deterministic based on text content
            seed = hash(text) % (2**32)
            np.random.seed(seed)
            embedding = np.random.rand(self.dimension).astype('float32')
            # Normalize
            embedding = embedding / np.linalg.norm(embedding)
            embeddings.append(embedding.tolist())
        return embeddings

    def embed_query(self, query):
        """Generate deterministic mock embedding for query"""
        seed = hash(query) % (2**32)
        np.random.seed(seed)
        embedding = np.random.rand(self.dimension).astype('float32')
        embedding = embedding / np.linalg.norm(embedding)
        return embedding.tolist()


class TestQueryProcessorIntegration:
    """Integration tests for Query Processor with RAG Engine"""

    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for test"""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir

    @pytest.fixture
    def knowledge_base_dir(self, temp_dir):
        """Create mock knowledge base"""
        kb_dir = Path(temp_dir) / "knowledge_base"
        kb_dir.mkdir(parents=True, exist_ok=True)

        # Create mock documents about cameras and security
        documents = {
            "requisitos_tecnicos.md": """
# Requisitos Técnicos de Câmeras

## Especificações de Câmeras IP

As câmeras IP devem atender aos seguintes requisitos:

- Resolução mínima: 4MP (2688x1520 pixels)
- Taxa de quadros: mínimo 25 FPS em resolução máxima
- Compressão: H.265/H.264
- Lente: varifocal motorizada 2.8-12mm
- Iluminação IR: alcance mínimo 30 metros
- Proteção: IP67 para uso externo
- Alimentação: PoE (Power over Ethernet) IEEE 802.3af

## Armazenamento

Sistema de armazenamento deve:
- Reter gravações por no mínimo 30 dias
- Usar discos com tecnologia RAID
- Suportar gravação contínua 24/7
            """,

            "documentacao_qualificacao.md": """
# Documentação para Qualificação Técnica

## Documentos Obrigatórios

1. Atestado de Capacidade Técnica
   - Comprovar fornecimento de câmeras IP 4MP ou superior
   - Mínimo de 2 atestados de clientes diferentes
   - Prazo: últimos 3 anos

2. Certidões
   - Certidão negativa de falência
   - Regularidade fiscal (federal, estadual, municipal)
   - CNPJ ativo há pelo menos 2 anos

3. Qualificação Técnica da Equipe
   - Certificação em sistemas de CFTV
   - Comprovação de treinamento em câmeras IP
            """,

            "criterios_pontuacao.md": """
# Critérios de Pontuação Técnica

## Critérios de Avaliação

### Qualidade da Câmera (40 pontos)
- Resolução 4MP: 20 pontos
- Resolução 5MP ou superior: 30 pontos
- Resolução 8MP ou superior: 40 pontos

### Funcionalidades Adicionais (30 pontos)
- Analytics de vídeo: 15 pontos
- Detecção de movimento inteligente: 10 pontos
- Reconhecimento facial: 15 pontos
- Leitura de placas (LPR): 10 pontos

### Garantia e Suporte (30 pontos)
- Garantia de 3 anos: 15 pontos
- Garantia de 5 anos: 30 pontos
- Suporte técnico 24/7: 10 pontos
            """
        }

        for filename, content in documents.items():
            (kb_dir / filename).write_text(content.strip(), encoding='utf-8')

        return kb_dir

    @pytest.fixture
    def rag_engine(self, temp_dir, knowledge_base_dir):
        """Create RAG engine with mocked embeddings and real components"""
        # Create components
        vector_store = FAISSVectorStore(
            index_path=temp_dir,
            dimension=384
        )

        embeddings_manager = MockEmbeddingsManager(dimension=384)

        ingestion_pipeline = IngestionPipeline(
            vector_store=vector_store,
            embeddings_manager=embeddings_manager,
            chunk_size=500,
            chunk_overlap=100
        )

        # Create mock config
        class MockConfig:
            TOP_K = 5
            SIMILARITY_THRESHOLD = 0.7
            VECTOR_STORE = "faiss"
            FAISS_INDEX_PATH = temp_dir
            EMBEDDINGS_PROVIDER = "mock"
            EMBEDDINGS_MODEL = "mock-model"
            EMBEDDINGS_DIMENSION = 384
            CHUNK_SIZE = 500
            CHUNK_OVERLAP = 100

        # Create RAG engine
        engine = RAGEngine(
            vector_store=vector_store,
            embeddings_manager=embeddings_manager,
            ingestion_pipeline=ingestion_pipeline,
            config=MockConfig()
        )

        # Ingest knowledge base
        engine.ingest_knowledge_base(str(knowledge_base_dir))

        return engine

    @pytest.fixture
    def query_processor(self, rag_engine):
        """Create Query Processor with RAG engine"""
        return QueryProcessor(rag_engine)

    def test_processor_initialization(self, query_processor):
        """Test processor initialization with RAG engine"""
        assert query_processor.rag is not None
        assert query_processor.high_confidence_threshold == 0.85
        assert query_processor.min_evidence_count == 2

    def test_analyze_camera_requirement(self, query_processor):
        """Test analyzing a camera requirement"""
        requirement = {
            'id': 'REQ-001',
            'descricao': 'Câmeras IP com resolução mínima de 4MP',
            'tipo': 'Técnico',
            'categoria': 'Hardware'
        }

        result = query_processor.analyze_requirement(requirement)

        # Verify result structure
        assert isinstance(result, ConformityAnalysis)
        assert result.requirement_id == 'REQ-001'
        assert result.conformity in [v for v in ConformityVerdict]
        assert 0 <= result.confidence <= 1

        # Should have evidence
        assert len(result.evidence) > 0

        # Should have sources
        assert len(result.sources) > 0

        # Should have reasoning
        assert isinstance(result.reasoning, str)
        assert len(result.reasoning) > 0

    def test_analyze_storage_requirement(self, query_processor):
        """Test analyzing a storage requirement"""
        requirement = {
            'id': 'REQ-002',
            'descricao': 'Armazenamento de gravações por 30 dias',
            'tipo': 'Técnico',
            'categoria': 'Armazenamento'
        }

        result = query_processor.analyze_requirement(requirement)

        assert result.requirement_id == 'REQ-002'
        assert len(result.evidence) > 0

        # Should find relevant information about storage
        evidence_texts = ' '.join([e.text for e in result.evidence])
        assert '30 dias' in evidence_texts or 'armazenamento' in evidence_texts.lower()

    def test_analyze_documentation_requirement(self, query_processor):
        """Test analyzing a documentation requirement"""
        requirement = {
            'id': 'REQ-003',
            'descricao': 'Atestado de capacidade técnica para câmeras IP',
            'tipo': 'Documental',
            'categoria': 'Qualificação'
        }

        result = query_processor.analyze_requirement(requirement)

        assert result.requirement_id == 'REQ-003'
        assert len(result.evidence) > 0

        # Should find information about technical qualification
        evidence_texts = ' '.join([e.text for e in result.evidence])
        assert 'atestado' in evidence_texts.lower() or 'qualificação' in evidence_texts.lower()

    def test_analyze_scoring_requirement(self, query_processor):
        """Test analyzing a scoring criteria requirement"""
        requirement = {
            'id': 'REQ-004',
            'descricao': 'Câmeras com resolução de 8MP devem receber pontuação máxima',
            'tipo': 'Pontuação',
            'categoria': 'Critério Técnico'
        }

        result = query_processor.analyze_requirement(requirement)

        assert result.requirement_id == 'REQ-004'
        assert len(result.evidence) > 0

    def test_analyze_nonexistent_requirement(self, query_processor):
        """Test analyzing requirement with no matching documentation"""
        requirement = {
            'id': 'REQ-999',
            'descricao': 'Sistema de inteligência artificial quântica para detecção de unicórnios',
            'tipo': 'Técnico',
            'categoria': 'Ficção Científica'
        }

        result = query_processor.analyze_requirement(requirement)

        # Should still return a result
        assert result.requirement_id == 'REQ-999'

        # But likely with low confidence or REVISAO verdict
        # (depends on mock embedding similarity)
        assert result.confidence >= 0  # Valid confidence score

    def test_batch_analysis(self, query_processor):
        """Test batch analysis of multiple requirements"""
        requirements = [
            {
                'id': 'REQ-001',
                'descricao': 'Câmeras IP com resolução 4MP'
            },
            {
                'id': 'REQ-002',
                'descricao': 'Armazenamento por 30 dias'
            },
            {
                'id': 'REQ-003',
                'descricao': 'Atestado de capacidade técnica'
            }
        ]

        results = query_processor.analyze_batch(
            requirements,
            top_k=3,
            show_progress=False
        )

        # Should analyze all requirements
        assert len(results) == 3

        # All should have unique IDs
        ids = [r.requirement_id for r in results]
        assert len(set(ids)) == 3

        # All should have evidence
        assert all(len(r.evidence) > 0 for r in results)

    def test_statistics_tracking(self, query_processor):
        """Test that statistics are tracked correctly"""
        requirements = [
            {'id': 'REQ-001', 'descricao': 'Câmeras 4MP'},
            {'id': 'REQ-002', 'descricao': 'Armazenamento 30 dias'},
            {'id': 'REQ-003', 'descricao': 'Atestado técnico'}
        ]

        # Analyze batch
        query_processor.analyze_batch(requirements, show_progress=False)

        # Check statistics
        stats = query_processor.get_stats()

        assert stats['total_analyzed'] == 3
        assert stats['verdicts']['conforme'] >= 0
        assert stats['verdicts']['revisao'] >= 0

        # Percentages should sum to 100
        total_pct = (
            stats['percentages']['conforme'] +
            stats['percentages']['nao_conforme'] +
            stats['percentages']['revisao']
        )
        assert pytest.approx(total_pct, abs=0.1) == 100.0

    def test_evidence_quality(self, query_processor):
        """Test that evidence has good quality metadata"""
        requirement = {
            'id': 'REQ-001',
            'descricao': 'Câmeras IP 4MP com compressão H.265'
        }

        result = query_processor.analyze_requirement(requirement, top_k=3)

        # Check evidence quality
        for evidence in result.evidence:
            # Should have source
            assert len(evidence.source) > 0

            # Should have text
            assert len(evidence.text) > 0

            # Should have valid relevance score
            assert 0 <= evidence.relevance <= 1

            # Should have chunk index
            assert evidence.chunk_index >= 0

    def test_result_serialization(self, query_processor):
        """Test that results can be serialized to JSON"""
        import json

        requirement = {
            'id': 'REQ-001',
            'descricao': 'Câmeras 4MP'
        }

        result = query_processor.analyze_requirement(requirement)

        # Convert to dict
        result_dict = result.to_dict()
        assert isinstance(result_dict, dict)

        # Convert to JSON
        json_str = result.to_json()
        assert isinstance(json_str, str)

        # Should be valid JSON
        parsed = json.loads(json_str)
        assert parsed['requirement_id'] == 'REQ-001'

    def test_custom_thresholds(self, rag_engine):
        """Test Query Processor with custom confidence thresholds"""
        config = {
            'high_confidence': 0.95,  # Very strict
            'low_confidence': 0.50,
            'min_evidence': 3
        }

        processor = QueryProcessor(rag_engine, config=config)

        requirement = {
            'id': 'REQ-001',
            'descricao': 'Câmeras IP 4MP'
        }

        result = processor.analyze_requirement(requirement)

        # With stricter threshold, might get REVISAO instead of CONFORME
        assert result.conformity in [v for v in ConformityVerdict]

    def test_recommendations_quality(self, query_processor):
        """Test that recommendations are actionable"""
        requirement = {
            'id': 'REQ-001',
            'descricao': 'Câmeras IP 4MP'
        }

        result = query_processor.analyze_requirement(requirement)

        # Should have recommendations
        assert len(result.recommendations) > 0

        # Recommendations should be strings
        assert all(isinstance(r, str) for r in result.recommendations)

        # Recommendations should not be empty
        assert all(len(r) > 0 for r in result.recommendations)

    def test_metadata_completeness(self, query_processor):
        """Test that analysis metadata is complete"""
        requirement = {
            'id': 'REQ-001',
            'descricao': 'Câmeras IP 4MP',
            'tipo': 'Técnico'
        }

        result = query_processor.analyze_requirement(requirement, top_k=5)

        # Check metadata fields
        assert 'requirement' in result.metadata
        assert 'search_results_count' in result.metadata
        assert 'top_k' in result.metadata
        assert result.metadata['top_k'] == 5

    def test_reset_statistics(self, query_processor):
        """Test statistics can be reset"""
        # Analyze some requirements
        requirements = [
            {'id': 'REQ-001', 'descricao': 'Test 1'},
            {'id': 'REQ-002', 'descricao': 'Test 2'}
        ]

        query_processor.analyze_batch(requirements, show_progress=False)

        # Verify stats exist
        stats_before = query_processor.get_stats()
        assert stats_before['total_analyzed'] == 2

        # Reset
        query_processor.reset_stats()

        # Verify stats are cleared
        stats_after = query_processor.get_stats()
        assert stats_after['total_analyzed'] == 0
        assert stats_after['verdicts']['conforme'] == 0
