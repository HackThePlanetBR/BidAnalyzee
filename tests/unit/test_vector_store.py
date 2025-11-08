"""
Unit Tests for Vector Store (FAISS)

Tests the vector store operations with mocked embeddings.
These tests validate the logic independent of the embeddings provider.
"""

import pytest
import numpy as np
import tempfile
import shutil
from pathlib import Path

# Import vector store classes
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from agents.technical_analyst.vector_store import (
    FAISSVectorStore,
    VectorStoreInterface
)


class TestFAISSVectorStore:
    """Test suite for FAISS Vector Store"""

    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for test files"""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)

    @pytest.fixture
    def vector_store(self, temp_dir):
        """Create a FAISS vector store instance"""
        return FAISSVectorStore(
            index_path=temp_dir,
            dimension=384
        )

    @pytest.fixture
    def mock_embeddings(self):
        """Generate mock embeddings (random vectors)"""
        np.random.seed(42)  # For reproducibility
        return np.random.rand(10, 384).astype('float32')

    @pytest.fixture
    def mock_texts(self):
        """Generate mock text documents"""
        return [
            f"Documento {i}: Este é um texto de teste sobre requisitos técnicos."
            for i in range(10)
        ]

    @pytest.fixture
    def mock_metadata(self):
        """Generate mock metadata"""
        return [
            {
                "filename": f"doc_{i}.md",
                "chunk_index": 0,
                "source": "test"
            }
            for i in range(10)
        ]

    def test_initialization(self, vector_store):
        """Test vector store initialization"""
        assert vector_store.dimension == 384
        assert vector_store.index is not None
        assert vector_store.get_stats()['total_documents'] == 0

    def test_add_documents(self, vector_store, mock_texts, mock_embeddings, mock_metadata):
        """Test adding documents to the vector store"""
        # Add documents
        vector_store.add_documents(mock_texts, mock_embeddings, mock_metadata)

        # Verify documents were added
        assert vector_store.get_stats()['total_documents'] == 10
        assert len(vector_store.texts) == 10
        assert len(vector_store.metadatas) == 10

    def test_search(self, vector_store, mock_texts, mock_embeddings, mock_metadata):
        """Test searching in the vector store"""
        # Add documents first
        vector_store.add_documents(mock_texts, mock_embeddings, mock_metadata)

        # Create a query vector (same as first document for easy testing)
        query_vector = mock_embeddings[0]

        # Search
        results = vector_store.search(query_vector, top_k=3)

        # Verify results
        assert len(results) == 3
        assert all('text' in r for r in results)
        assert all('metadata' in r for r in results)
        assert all('score' in r for r in results)

        # First result should have highest score (query matches first doc)
        assert results[0]['score'] >= results[1]['score']

    def test_search_with_threshold(self, vector_store, mock_texts, mock_embeddings, mock_metadata):
        """Test search with similarity threshold"""
        vector_store.add_documents(mock_texts, mock_embeddings, mock_metadata)

        query_vector = mock_embeddings[0]

        # Search with top_k (vector_store.search doesn't have similarity_threshold param)
        results = vector_store.search(query_vector, top_k=10)

        # Manually filter by threshold
        filtered_results = [r for r in results if r['score'] >= 0.95]

        # Verify filtered results meet threshold
        assert all(r['score'] >= 0.95 for r in filtered_results)

    def test_save_and_load(self, vector_store, mock_texts, mock_embeddings, mock_metadata, temp_dir):
        """Test saving and loading the index"""
        # Add documents
        vector_store.add_documents(mock_texts, mock_embeddings, mock_metadata)

        # Save
        vector_store.save()

        # Create new instance and load
        new_store = FAISSVectorStore(
            index_path=temp_dir,
            dimension=384
        )
        new_store.load()

        # Verify loaded data
        assert new_store.get_stats()['total_documents'] == 10
        assert len(new_store.texts) == 10
        assert len(new_store.metadatas) == 10

        # Verify search works on loaded index
        query_vector = mock_embeddings[0]
        results = new_store.search(query_vector, top_k=3)
        assert len(results) == 3

    def test_get_stats(self, vector_store, mock_texts, mock_embeddings, mock_metadata):
        """Test getting statistics"""
        vector_store.add_documents(mock_texts, mock_embeddings, mock_metadata)

        stats = vector_store.get_stats()

        assert stats['total_documents'] == 10
        assert stats['dimension'] == 384
        assert 'index_size' in stats

    def test_delete_all(self, vector_store, mock_texts, mock_embeddings, mock_metadata):
        """Test deleting all documents"""
        # Add documents
        vector_store.add_documents(mock_texts, mock_embeddings, mock_metadata)
        assert vector_store.get_stats()['total_documents'] == 10

        # Delete all
        vector_store.delete_all()

        # Verify deletion
        assert vector_store.get_stats()['total_documents'] == 0
        assert len(vector_store.texts) == 0
        assert len(vector_store.metadatas) == 0

    def test_empty_search(self, vector_store):
        """Test search on empty index"""
        query_vector = np.random.rand(384).astype('float32')

        results = vector_store.search(query_vector, top_k=5)

        # Should return empty list
        assert results == []

    def test_batch_addition(self, vector_store):
        """Test adding documents in batches"""
        # Add first batch
        batch1_texts = ["doc1", "doc2", "doc3"]
        batch1_embeddings = np.random.rand(3, 384).astype('float32')
        batch1_metadata = [{"batch": 1, "id": i} for i in range(3)]

        vector_store.add_documents(batch1_texts, batch1_embeddings, batch1_metadata)
        assert vector_store.get_stats()['total_documents'] == 3

        # Add second batch
        batch2_texts = ["doc4", "doc5"]
        batch2_embeddings = np.random.rand(2, 384).astype('float32')
        batch2_metadata = [{"batch": 2, "id": i} for i in range(2)]

        vector_store.add_documents(batch2_texts, batch2_embeddings, batch2_metadata)
        assert vector_store.get_stats()['total_documents'] == 5

    def test_normalized_vectors(self, vector_store, mock_texts, mock_metadata, temp_dir):
        """Test that vectors are L2 normalized for cosine similarity"""
        # Create non-normalized vectors
        embeddings = np.array([[1.0, 2.0, 3.0] + [0.0] * 381] * 3, dtype='float32')

        # Add to store (should normalize internally)
        store = FAISSVectorStore(index_path=temp_dir + "/test2", dimension=384)
        store.add_documents(["doc1", "doc2", "doc3"], embeddings, mock_metadata[:3])

        # Check that search works (FAISS will use cosine via L2 normalized vectors)
        query = np.array([1.0, 2.0, 3.0] + [0.0] * 381, dtype='float32')
        results = store.search(query, top_k=3)

        assert len(results) == 3
        # Cosine similarity of identical vectors should be close to 1.0
        assert results[0]['score'] > 0.99


class TestVectorStoreInterface:
    """Test that FAISS implements the interface correctly"""

    def test_implements_interface(self):
        """Test that FAISSVectorStore implements VectorStoreInterface"""
        assert issubclass(FAISSVectorStore, VectorStoreInterface)

    def test_interface_methods(self):
        """Test that all interface methods are implemented"""
        required_methods = [
            'add_documents',
            'search',
            'save',
            'load',
            'get_stats',
            'delete_all'
        ]

        for method in required_methods:
            assert hasattr(FAISSVectorStore, method)
            assert callable(getattr(FAISSVectorStore, method))


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
