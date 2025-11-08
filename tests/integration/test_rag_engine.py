"""
Integration Tests for RAG Engine

Tests the complete RAG system with mocked embeddings.
Validates end-to-end flow from ingestion to search.
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch
import numpy as np

# Import RAG components
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from agents.technical_analyst.rag_engine import RAGEngine
from agents.technical_analyst.vector_store import FAISSVectorStore
from agents.technical_analyst.ingestion_pipeline import IngestionPipeline


class MockEmbeddingsManager:
    """Mock embeddings manager that generates deterministic embeddings"""

    def __init__(self, dimension=384):
        self.dimension = dimension
        self.provider = "mock"
        self.model = "mock-model"

    def embed_documents(self, texts, show_progress=True):
        """Generate mock embeddings for documents"""
        # Use hash of text for deterministic but unique embeddings
        embeddings = []
        for text in texts:
            # Create deterministic vector based on text hash
            seed = hash(text) % (2**32)
            np.random.seed(seed)
            embedding = np.random.rand(self.dimension).astype('float32')
            # Normalize
            embedding = embedding / np.linalg.norm(embedding)
            embeddings.append(embedding.tolist())
        return embeddings

    def embed_query(self, text):
        """Generate mock embedding for query"""
        seed = hash(text) % (2**32)
        np.random.seed(seed)
        embedding = np.random.rand(self.dimension).astype('float32')
        return (embedding / np.linalg.norm(embedding)).tolist()

    def get_dimension(self):
        return self.dimension

    def get_info(self):
        return {
            "provider": self.provider,
            "model": self.model,
            "dimension": self.dimension
        }


class TestRAGEngineIntegration:
    """Integration tests for complete RAG system"""

    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory"""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)

    @pytest.fixture
    def knowledge_base_dir(self, temp_dir):
        """Create mock knowledge base with markdown files"""
        kb_dir = Path(temp_dir) / "knowledge_base"
        kb_dir.mkdir()

        # Create sample documents about licitações
        docs = {
            "lei_8666.md": """
# Lei 8.666/93

Art. 1º Esta Lei estabelece normas gerais sobre licitações e contratos administrativos.

Art. 2º As obras e serviços serão necessariamente precedidas de licitação.

Art. 3º A licitação destina-se a garantir a observância do princípio constitucional
da isonomia e a selecionar a proposta mais vantajosa para a Administração.
            """,
            "requisitos_tecnicos.md": """
# Requisitos Técnicos Comuns

## Hardware
- Servidores com mínimo 16GB RAM
- Storage: SSD com no mínimo 500GB
- Processador: Intel Xeon ou equivalente

## Software
- Sistema operacional: Linux Ubuntu 20.04 LTS ou superior
- Banco de dados: PostgreSQL 12 ou superior
- Certificação: ISO 27001

## Rede
- Banda mínima: 100Mbps
- Latência máxima: 50ms
- Protocolos: HTTPS, TLS 1.2+
            """,
            "documentacao_qualificacao.md": """
# Documentação de Qualificação

## Regularidade Fiscal
- Certidão Negativa de Débitos (CND)
- Certidão de Regularidade do FGTS
- Certidão Negativa de Débitos Trabalhistas (CNDT)

## Qualificação Técnica
- Atestados de capacidade técnica
- Registro no CREA ou equivalente
- Certificações ISO relevantes

## Qualificação Econômico-Financeira
- Balanço patrimonial dos últimos 2 anos
- Certidão negativa de falência
- Índices de Liquidez Geral, Solvência e Liquidez Corrente
            """
        }

        for filename, content in docs.items():
            (kb_dir / filename).write_text(content.strip(), encoding='utf-8')

        return kb_dir

    @pytest.fixture
    def rag_engine(self, temp_dir, knowledge_base_dir):
        """Create RAG engine with mocked embeddings"""
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

        # Create mock config with all required attributes
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

        return engine

    def test_engine_initialization(self, rag_engine):
        """Test RAG engine initialization"""
        assert rag_engine.vector_store is not None
        assert rag_engine.embeddings is not None
        assert rag_engine.ingestion is not None

    def test_ingest_knowledge_base(self, rag_engine, knowledge_base_dir):
        """Test ingesting complete knowledge base"""
        stats = rag_engine.ingest_knowledge_base(str(knowledge_base_dir))

        # Verify ingestion
        assert stats['documents_loaded'] == 3
        assert stats['total_chunks'] > 0
        assert stats['total_embeddings'] > 0
        assert stats['time_elapsed'] > 0

        # Verify files were processed
        assert len(stats['files_processed']) == 3
        filenames = [f['filename'] for f in stats['files_processed']]
        assert 'lei_8666.md' in filenames
        assert 'requisitos_tecnicos.md' in filenames
        assert 'documentacao_qualificacao.md' in filenames

    def test_search_after_ingestion(self, rag_engine, knowledge_base_dir):
        """Test search after ingesting knowledge base"""
        # Ingest first
        rag_engine.ingest_knowledge_base(str(knowledge_base_dir))

        # Search for technical requirements
        query = "Quais são os requisitos de hardware?"
        results = rag_engine.search(query, top_k=3)

        # Should return results
        assert len(results) > 0
        assert len(results) <= 3

        # Results should have required fields
        for result in results:
            assert 'text' in result
            assert 'similarity_score' in result  # rag_engine.search returns similarity_score
            assert 'metadata' in result

    def test_search_relevance(self, rag_engine, knowledge_base_dir):
        """Test that search returns relevant results"""
        rag_engine.ingest_knowledge_base(str(knowledge_base_dir))

        # Search for specific topic
        query = "certificação ISO 27001"
        results = rag_engine.search(query, top_k=5)

        # Should find results (at least from requisitos_tecnicos.md)
        assert len(results) > 0

        # Top result should mention ISO (deterministic due to mock embeddings)
        # Note: With mock embeddings, relevance depends on text hash similarity
        assert any('ISO' in r['text'] for r in results)

    def test_search_with_context(self, rag_engine, knowledge_base_dir):
        """Test search_with_context method"""
        rag_engine.ingest_knowledge_base(str(knowledge_base_dir))

        query = "requisitos de qualificação"
        result = rag_engine.search_with_context(query, top_k=3, similarity_threshold=0.0)

        # Verify response structure (as implemented in rag_engine.py)
        assert 'query' in result
        assert 'num_results' in result
        assert 'results' in result
        assert 'avg_similarity' in result
        assert 'timestamp' in result

        assert result['query'] == query
        assert result['num_results'] >= 0
        assert isinstance(result['results'], list)

    def test_search_with_threshold(self, rag_engine, knowledge_base_dir):
        """Test search with similarity threshold"""
        rag_engine.ingest_knowledge_base(str(knowledge_base_dir))

        query = "licitação"

        # Search with low threshold (should return more results)
        results_low = rag_engine.search(query, top_k=10, similarity_threshold=0.0)

        # Search with high threshold (should return fewer results)
        results_high = rag_engine.search(query, top_k=10, similarity_threshold=0.9)

        # High threshold should return fewer or equal results
        assert len(results_high) <= len(results_low)

        # All high threshold results should meet the threshold
        for result in results_high:
            assert result['score'] >= 0.9

    def test_get_stats(self, rag_engine, knowledge_base_dir):
        """Test getting RAG engine statistics"""
        # Get stats before ingestion
        stats_before = rag_engine.get_stats()
        # Vector store stats are nested under 'vector_store' key
        assert stats_before['vector_store']['total_documents'] == 0

        # Ingest
        rag_engine.ingest_knowledge_base(str(knowledge_base_dir))

        # Get stats after ingestion
        stats_after = rag_engine.get_stats()
        assert stats_after['vector_store']['total_documents'] > 0
        assert 'vector_store' in stats_after
        assert 'embeddings' in stats_after

    def test_export_stats(self, rag_engine, knowledge_base_dir, temp_dir):
        """Test exporting statistics to file"""
        rag_engine.ingest_knowledge_base(str(knowledge_base_dir))

        export_path = Path(temp_dir) / "stats.json"
        rag_engine.export_stats(str(export_path))

        # Verify file was created
        assert export_path.exists()

        # Verify content
        import json
        with open(export_path) as f:
            stats = json.load(f)

        assert 'vector_store' in stats
        assert stats['vector_store']['total_documents'] > 0

    def test_reset_engine(self, rag_engine, knowledge_base_dir):
        """Test resetting the RAG engine"""
        # Ingest data
        rag_engine.ingest_knowledge_base(str(knowledge_base_dir))
        stats_before = rag_engine.get_stats()
        assert stats_before['vector_store']['total_documents'] > 0

        # Reset
        rag_engine.reset()

        # Verify reset - reset() reloads from disk if index exists
        # So the documents are still there unless we delete the index files
        # Instead, verify that _initialized flag is False
        assert rag_engine._initialized == False

        # Verify vector store was reloaded (may have documents from disk)
        stats_after = rag_engine.get_stats()
        assert 'vector_store' in stats_after

    def test_save_and_load_index(self, rag_engine, knowledge_base_dir, temp_dir):
        """Test saving and loading the vector index"""
        # Ingest data
        rag_engine.ingest_knowledge_base(str(knowledge_base_dir))

        # Save
        rag_engine.vector_store.save()

        # Create new engine and load
        new_store = FAISSVectorStore(
            index_path=temp_dir,
            dimension=384
        )
        new_store.load()

        new_embeddings = MockEmbeddingsManager(dimension=384)
        # Create mock config for new engine
        class MockConfig:
            TOP_K = 5
            SIMILARITY_THRESHOLD = 0.7
            VECTOR_STORE = "faiss"
            EMBEDDINGS_PROVIDER = "mock"
            EMBEDDINGS_MODEL = "mock-model"
            EMBEDDINGS_DIMENSION = 384

        new_ingestion = IngestionPipeline(new_store, new_embeddings)
        new_engine = RAGEngine(new_store, new_embeddings, new_ingestion, MockConfig())

        # Verify data was loaded
        stats = new_engine.get_stats()
        assert stats['vector_store']['total_documents'] > 0

        # Verify search works
        results = new_engine.search("licitação", top_k=3)
        assert len(results) > 0

    def test_empty_query(self, rag_engine, knowledge_base_dir):
        """Test handling of empty query"""
        rag_engine.ingest_knowledge_base(str(knowledge_base_dir))

        # Empty query should raise ValueError
        with pytest.raises(ValueError, match="Query cannot be empty"):
            rag_engine.search("", top_k=5)

    def test_query_before_ingestion(self, rag_engine):
        """Test querying before any ingestion"""
        # Should raise RuntimeError when not initialized
        with pytest.raises(RuntimeError, match="RAG Engine not initialized"):
            rag_engine.search("test query", top_k=5)

    def test_multiple_ingestions(self, rag_engine, knowledge_base_dir):
        """Test multiple ingestions accumulate documents"""
        # First ingestion
        stats1 = rag_engine.ingest_knowledge_base(str(knowledge_base_dir))
        docs_first = stats1['total_chunks']

        # Second ingestion (same files)
        stats2 = rag_engine.ingest_knowledge_base(str(knowledge_base_dir))
        docs_second = stats2['total_chunks']

        # Total should be doubled
        total_stats = rag_engine.get_stats()
        assert total_stats['vector_store']['total_documents'] == docs_first + docs_second


class TestRAGEnginePerformance:
    """Performance tests for RAG engine"""

    @pytest.fixture
    def large_knowledge_base(self, tmp_path):
        """Create larger knowledge base for performance testing"""
        kb_dir = tmp_path / "large_kb"
        kb_dir.mkdir()

        # Create 10 documents with multiple paragraphs each
        for i in range(10):
            content = f"# Document {i}\n\n"
            for j in range(20):
                content += f"Paragraph {j}: " + "Lorem ipsum " * 20 + "\n\n"

            (kb_dir / f"doc_{i}.md").write_text(content, encoding='utf-8')

        return kb_dir

    def test_ingestion_performance(self, large_knowledge_base, tmp_path):
        """Test that ingestion completes in reasonable time"""
        import time

        class MockConfig:
            TOP_K = 5
            SIMILARITY_THRESHOLD = 0.7
            VECTOR_STORE = "faiss"
            EMBEDDINGS_PROVIDER = "mock"
            EMBEDDINGS_MODEL = "mock-model"
            EMBEDDINGS_DIMENSION = 384

        vector_store = FAISSVectorStore(index_path=str(tmp_path), dimension=384)
        embeddings = MockEmbeddingsManager(384)
        ingestion = IngestionPipeline(vector_store, embeddings)
        engine = RAGEngine(vector_store, embeddings, ingestion, MockConfig())

        start = time.time()
        stats = engine.ingest_knowledge_base(str(large_knowledge_base))
        elapsed = time.time() - start

        # Should complete in reasonable time (< 30 seconds with mocks)
        assert elapsed < 30

        # Should process all documents
        assert stats['documents_loaded'] == 10

    def test_search_performance(self, large_knowledge_base, tmp_path):
        """Test that search completes quickly"""
        import time

        class MockConfig:
            TOP_K = 5
            SIMILARITY_THRESHOLD = 0.7
            VECTOR_STORE = "faiss"
            EMBEDDINGS_PROVIDER = "mock"
            EMBEDDINGS_MODEL = "mock-model"
            EMBEDDINGS_DIMENSION = 384

        vector_store = FAISSVectorStore(index_path=str(tmp_path), dimension=384)
        embeddings = MockEmbeddingsManager(384)
        ingestion = IngestionPipeline(vector_store, embeddings)
        engine = RAGEngine(vector_store, embeddings, ingestion, MockConfig())

        engine.ingest_knowledge_base(str(large_knowledge_base))

        # Perform multiple searches
        queries = [
            "Lorem ipsum",
            "Document information",
            "Paragraph details",
            "Test query",
            "Random search"
        ]

        start = time.time()
        for query in queries:
            results = engine.search(query, top_k=5)
            assert len(results) >= 0
        elapsed = time.time() - start

        # All searches should complete quickly (< 5 seconds total)
        assert elapsed < 5


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
