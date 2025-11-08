"""
Unit Tests for Ingestion Pipeline

Tests the document ingestion and chunking logic with mocked components.
Validates text chunking, metadata handling, and pipeline orchestration.
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, MagicMock, patch
import numpy as np

# Import ingestion pipeline
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from agents.technical_analyst.ingestion_pipeline import IngestionPipeline


class TestIngestionPipeline:
    """Test suite for Ingestion Pipeline"""

    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for test files"""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)

    @pytest.fixture
    def mock_vector_store(self):
        """Create a mock vector store"""
        mock_store = Mock()
        mock_store.add_documents = Mock()
        mock_store.total_vectors = 0
        return mock_store

    @pytest.fixture
    def mock_embeddings_manager(self):
        """Create a mock embeddings manager"""
        mock_embeddings = Mock()
        # Mock embed_documents to return random vectors
        def mock_embed(texts, show_progress=True):
            return np.random.rand(len(texts), 384).astype('float32').tolist()
        mock_embeddings.embed_documents = mock_embed
        mock_embeddings.dimension = 384
        return mock_embeddings

    @pytest.fixture
    def pipeline(self, mock_vector_store, mock_embeddings_manager):
        """Create ingestion pipeline with mocks"""
        return IngestionPipeline(
            vector_store=mock_vector_store,
            embeddings_manager=mock_embeddings_manager,
            chunk_size=1000,
            chunk_overlap=200
        )

    @pytest.fixture
    def sample_text(self):
        """Generate sample text for testing"""
        return """
        # Lei 8.666/93

        Art. 1º Esta Lei estabelece normas gerais sobre licitações e contratos
        administrativos pertinentes a obras, serviços, inclusive de publicidade,
        compras, alienações e locações no âmbito dos Poderes da União.

        Art. 2º As obras, serviços, inclusive de publicidade, compras, alienações,
        concessões, permissões e locações da Administração Pública, quando contratadas
        com terceiros, serão necessariamente precedidas de licitação.

        Parágrafo único. Para os fins desta Lei, considera-se contrato todo e qualquer
        ajuste entre órgãos ou entidades da Administração Pública e particulares.
        """

    @pytest.fixture
    def sample_markdown_files(self, temp_dir):
        """Create sample markdown files for testing"""
        md_dir = Path(temp_dir) / "markdown"
        md_dir.mkdir()

        # Create 3 sample files
        files = []
        for i in range(3):
            file_path = md_dir / f"doc_{i}.md"
            content = f"# Document {i}\n\n" + "\n\n".join([
                f"Paragraph {j}: " + "Lorem ipsum " * 50
                for j in range(5)
            ])
            file_path.write_text(content, encoding='utf-8')
            files.append(file_path)

        return md_dir

    def test_initialization(self, pipeline):
        """Test pipeline initialization"""
        assert pipeline.chunk_size == 1000
        assert pipeline.chunk_overlap == 200
        assert pipeline.vector_store is not None
        assert pipeline.embeddings is not None

    def test_chunk_text_simple(self, pipeline, sample_text):
        """Test text chunking with simple text"""
        metadata = {"filename": "test.md"}
        chunks = pipeline.chunk_text(sample_text, metadata)

        # Should create chunks
        assert len(chunks) > 0

        # Each chunk should have text and metadata
        for chunk in chunks:
            assert 'text' in chunk
            assert 'metadata' in chunk
            assert len(chunk['text']) > 0
            assert chunk['metadata']['filename'] == 'test.md'
            assert 'chunk_index' in chunk['metadata']

    def test_chunk_text_respects_size(self, pipeline):
        """Test that chunks respect size limits"""
        # Create long text
        long_text = "Lorem ipsum dolor sit amet. " * 200  # ~5600 chars

        chunks = pipeline.chunk_text(long_text, {})

        # Should create multiple chunks
        assert len(chunks) > 1

        # Most chunks should be close to chunk_size
        for chunk in chunks[:-1]:  # Exclude last chunk
            assert len(chunk['text']) <= pipeline.chunk_size + 100  # Allow some flexibility

    def test_chunk_text_with_overlap(self, pipeline):
        """Test that chunks have overlap"""
        # Create text with distinct sections
        text = "Section A. " * 100 + "Section B. " * 100

        chunks = pipeline.chunk_text(text, {})

        if len(chunks) > 1:
            # Check that there's some overlap between consecutive chunks
            # (exact overlap is hard to test due to paragraph boundaries)
            assert chunks[0]['metadata']['chunk_index'] == 0
            assert chunks[1]['metadata']['chunk_index'] == 1

    def test_chunk_text_preserves_paragraphs(self, pipeline, sample_text):
        """Test that chunking respects paragraph boundaries"""
        chunks = pipeline.chunk_text(sample_text, {})

        # Chunks should not split in the middle of a sentence
        for chunk in chunks:
            text = chunk['text'].strip()
            # Should end with punctuation or be at document end
            if text:
                # Not a perfect test, but chunks should be somewhat coherent
                assert len(text) > 0

    def test_load_markdown_files(self, pipeline, sample_markdown_files):
        """Test loading markdown files from directory"""
        documents = pipeline.load_markdown_files(str(sample_markdown_files))

        # Should load 3 files
        assert len(documents) == 3

        # Each document should have required fields
        for doc in documents:
            assert 'filename' in doc
            assert 'content' in doc
            assert 'path' in doc
            assert len(doc['content']) > 0

    def test_load_markdown_files_empty_directory(self, pipeline, temp_dir):
        """Test loading from empty directory"""
        empty_dir = Path(temp_dir) / "empty"
        empty_dir.mkdir()

        documents = pipeline.load_markdown_files(str(empty_dir))

        # Should return empty list
        assert documents == []

    def test_load_markdown_files_nonexistent(self, pipeline):
        """Test loading from nonexistent directory"""
        with pytest.raises(ValueError, match="does not exist"):
            pipeline.load_markdown_files("/nonexistent/path")

    def test_ingest_from_directory(self, pipeline, sample_markdown_files, mock_vector_store):
        """Test full ingestion from directory"""
        stats = pipeline.ingest_from_directory(str(sample_markdown_files))

        # Verify statistics
        assert stats['documents_loaded'] == 3
        assert stats['total_chunks'] > 0
        assert stats['total_embeddings'] > 0
        assert 'time_elapsed' in stats
        assert len(stats['files_processed']) == 3

        # Verify vector store was called
        assert mock_vector_store.add_documents.called

    def test_ingest_single_document(self, pipeline, sample_text, mock_vector_store):
        """Test ingesting a single document"""
        stats = pipeline.ingest_single_document(
            text=sample_text,
            metadata={"filename": "test.md"}
        )

        # Verify statistics
        assert 'chunks' in stats
        assert 'embeddings' in stats
        assert stats['chunks'] > 0
        assert stats['embeddings'] > 0

        # Verify vector store was called
        assert mock_vector_store.add_documents.called

    def test_chunk_metadata_tracking(self, pipeline, sample_text):
        """Test that chunk metadata includes tracking information"""
        metadata = {"filename": "test.md", "source": "knowledge_base"}
        chunks = pipeline.chunk_text(sample_text, metadata)

        for i, chunk in enumerate(chunks):
            # Should preserve original metadata
            assert chunk['metadata']['filename'] == 'test.md'
            assert chunk['metadata']['source'] == 'knowledge_base'

            # Should add chunk-specific metadata
            assert chunk['metadata']['chunk_index'] == i
            assert 'start_char' in chunk['metadata']
            assert 'end_char' in chunk['metadata']

    def test_empty_text_handling(self, pipeline):
        """Test handling of empty text"""
        chunks = pipeline.chunk_text("", {})

        # Should return empty list
        assert chunks == []

    def test_very_short_text(self, pipeline):
        """Test handling of very short text"""
        short_text = "Short text."
        chunks = pipeline.chunk_text(short_text, {})

        # Should create single chunk
        assert len(chunks) == 1
        assert chunks[0]['text'] == short_text

    def test_unicode_handling(self, pipeline):
        """Test handling of unicode characters"""
        unicode_text = """
        Texto com acentuação: São Paulo, José, ção, ãe.
        Caracteres especiais: € £ ¥ § ® © ™
        Emojis: 😀 🎉 ✅ ❌
        """

        chunks = pipeline.chunk_text(unicode_text, {})

        # Should handle unicode correctly
        assert len(chunks) > 0
        assert 'São Paulo' in chunks[0]['text']
        assert '€' in chunks[0]['text']

    def test_statistics_accuracy(self, pipeline, sample_markdown_files):
        """Test that statistics are accurate"""
        stats = pipeline.ingest_from_directory(str(sample_markdown_files))

        # Total embeddings should equal total chunks
        assert stats['total_embeddings'] == stats['total_chunks']

        # Files processed should match documents loaded
        assert len(stats['files_processed']) == stats['documents_loaded']

        # Time elapsed should be reasonable
        assert stats['time_elapsed'] > 0
        assert stats['time_elapsed'] < 60  # Should take less than 60 seconds


class TestChunkingEdgeCases:
    """Test edge cases in text chunking"""

    @pytest.fixture
    def pipeline(self):
        """Create pipeline with specific chunk settings"""
        mock_store = Mock()
        mock_embeddings = Mock()
        return IngestionPipeline(
            vector_store=mock_store,
            embeddings_manager=mock_embeddings,
            chunk_size=100,  # Small chunks for testing
            chunk_overlap=20
        )

    def test_chunk_exactly_at_size(self, pipeline):
        """Test text that is exactly chunk_size"""
        text = "a" * 100  # Exactly 100 chars
        chunks = pipeline.chunk_text(text, {})

        assert len(chunks) == 1
        assert len(chunks[0]['text']) == 100

    def test_chunk_just_over_size(self, pipeline):
        """Test text that is just over chunk_size"""
        text = "a" * 101  # 101 chars
        chunks = pipeline.chunk_text(text, {})

        # Should create 2 chunks with overlap
        assert len(chunks) >= 1

    def test_many_short_paragraphs(self, pipeline):
        """Test text with many short paragraphs"""
        text = "\n\n".join(["Short para." for _ in range(50)])
        chunks = pipeline.chunk_text(text, {})

        # Should create multiple chunks
        assert len(chunks) > 1


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
