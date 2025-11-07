"""
Vector Store implementations for RAG system

Supports:
- FAISS (local, CPU-only) - current implementation
- Pinecone (cloud) - future migration

Architecture allows easy switching between implementations by changing config.
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Dict, Any, Optional
import json
import pickle


class VectorStoreInterface(ABC):
    """Abstract interface for vector stores - allows easy migration between implementations"""

    @abstractmethod
    def add_documents(
        self,
        texts: List[str],
        embeddings: List[List[float]],
        metadatas: Optional[List[Dict[str, Any]]] = None
    ) -> None:
        """
        Add documents to the vector store

        Args:
            texts: List of text chunks
            embeddings: List of embedding vectors (same length as texts)
            metadatas: Optional metadata for each document (same length as texts)
        """
        pass

    @abstractmethod
    def search(
        self,
        query_embedding: List[float],
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Search for similar documents

        Args:
            query_embedding: Query embedding vector
            top_k: Number of results to return

        Returns:
            List of dicts with keys: {text, score, metadata}
        """
        pass

    @abstractmethod
    def delete_all(self) -> None:
        """Clear all documents from the vector store"""
        pass

    @abstractmethod
    def save(self) -> None:
        """Persist vector store to disk"""
        pass

    @abstractmethod
    def load(self) -> bool:
        """
        Load vector store from disk

        Returns:
            True if loaded successfully, False otherwise
        """
        pass

    @abstractmethod
    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about the vector store"""
        pass


class FAISSVectorStore(VectorStoreInterface):
    """
    FAISS implementation - Local, fast, free

    Uses Facebook AI Similarity Search (FAISS) for efficient vector similarity search.
    Stores embeddings in memory and persists to disk.
    """

    def __init__(self, index_path: str, dimension: int = 384):
        """
        Initialize FAISS vector store

        Args:
            index_path: Directory path to store FAISS index
            dimension: Dimension of embedding vectors (default: 384 for all-MiniLM-L6-v2)
        """
        self.index_path = Path(index_path)
        self.dimension = dimension
        self.index = None
        self.texts: List[str] = []
        self.metadatas: List[Dict[str, Any]] = []

        # Create directory if it doesn't exist
        self.index_path.mkdir(parents=True, exist_ok=True)

        # Try to load existing index, otherwise create new
        if not self.load():
            self._create_index()

    def _create_index(self) -> None:
        """Create a new FAISS index"""
        try:
            import faiss

            # Use IndexFlatL2 for exact search (cosine similarity via L2 distance)
            # For large datasets, could use IndexIVFFlat for approximate search
            self.index = faiss.IndexFlatL2(self.dimension)

            print(f"✅ Created new FAISS index (dimension: {self.dimension})")
        except ImportError:
            print("❌ FAISS not installed. Run: pip install faiss-cpu")
            raise

    def add_documents(
        self,
        texts: List[str],
        embeddings: List[List[float]],
        metadatas: Optional[List[Dict[str, Any]]] = None
    ) -> None:
        """Add documents to FAISS index"""
        if not texts or not embeddings:
            return

        if len(texts) != len(embeddings):
            raise ValueError(f"Mismatch: {len(texts)} texts but {len(embeddings)} embeddings")

        if metadatas and len(metadatas) != len(texts):
            raise ValueError(f"Mismatch: {len(texts)} texts but {len(metadatas)} metadatas")

        try:
            import faiss
            import numpy as np

            # Convert embeddings to numpy array
            embeddings_array = np.array(embeddings, dtype=np.float32)

            # Normalize vectors for cosine similarity (L2 distance of normalized vectors = cosine distance)
            faiss.normalize_L2(embeddings_array)

            # Add to index
            self.index.add(embeddings_array)

            # Store texts and metadatas
            self.texts.extend(texts)

            if metadatas:
                self.metadatas.extend(metadatas)
            else:
                self.metadatas.extend([{}] * len(texts))

            print(f"✅ Added {len(texts)} documents to FAISS index (total: {len(self.texts)})")

        except ImportError:
            print("❌ FAISS or numpy not installed")
            raise

    def search(
        self,
        query_embedding: List[float],
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """Search FAISS index for similar documents"""
        if self.index.ntotal == 0:
            print("⚠️  Index is empty. No documents to search.")
            return []

        try:
            import faiss
            import numpy as np

            # Convert query to numpy array and normalize
            query_array = np.array([query_embedding], dtype=np.float32)
            faiss.normalize_L2(query_array)

            # Search
            top_k = min(top_k, self.index.ntotal)  # Don't request more than available
            distances, indices = self.index.search(query_array, top_k)

            # Convert L2 distances to similarity scores (1 - distance)
            # Normalized L2 distance ranges from 0 (identical) to 2 (opposite)
            # Convert to similarity score: 1 - (distance / 2)
            similarities = 1 - (distances[0] / 2)

            # Build results
            results = []
            for idx, score in zip(indices[0], similarities):
                if idx < len(self.texts):  # Valid index
                    results.append({
                        "text": self.texts[idx],
                        "score": float(score),  # Convert numpy float to Python float
                        "metadata": self.metadatas[idx] if idx < len(self.metadatas) else {}
                    })

            return results

        except ImportError:
            print("❌ FAISS or numpy not installed")
            raise

    def delete_all(self) -> None:
        """Clear all documents from FAISS index"""
        self._create_index()  # Create fresh index
        self.texts = []
        self.metadatas = []
        print("✅ Deleted all documents from FAISS index")

    def save(self) -> None:
        """Save FAISS index and metadata to disk"""
        try:
            import faiss

            # Save FAISS index
            index_file = self.index_path / "index.faiss"
            faiss.write_index(self.index, str(index_file))

            # Save texts and metadatas
            data = {
                "texts": self.texts,
                "metadatas": self.metadatas,
                "dimension": self.dimension
            }

            metadata_file = self.index_path / "metadata.pkl"
            with open(metadata_file, "wb") as f:
                pickle.dump(data, f)

            print(f"✅ Saved FAISS index to {self.index_path}")
            print(f"   - Index: {index_file}")
            print(f"   - Metadata: {metadata_file}")
            print(f"   - Documents: {len(self.texts)}")

        except Exception as e:
            print(f"❌ Error saving FAISS index: {e}")
            raise

    def load(self) -> bool:
        """Load FAISS index from disk"""
        index_file = self.index_path / "index.faiss"
        metadata_file = self.index_path / "metadata.pkl"

        if not index_file.exists() or not metadata_file.exists():
            return False

        try:
            import faiss

            # Load FAISS index
            self.index = faiss.read_index(str(index_file))

            # Load texts and metadatas
            with open(metadata_file, "rb") as f:
                data = pickle.load(f)

            self.texts = data["texts"]
            self.metadatas = data["metadatas"]
            self.dimension = data["dimension"]

            print(f"✅ Loaded FAISS index from {self.index_path}")
            print(f"   - Documents: {len(self.texts)}")
            print(f"   - Dimension: {self.dimension}")

            return True

        except Exception as e:
            print(f"⚠️  Could not load FAISS index: {e}")
            return False

    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about FAISS index"""
        return {
            "type": "FAISS",
            "dimension": self.dimension,
            "total_documents": len(self.texts),
            "index_size": self.index.ntotal if self.index else 0,
            "index_path": str(self.index_path),
            "is_trained": self.index.is_trained if self.index else False
        }


class PineconeVectorStore(VectorStoreInterface):
    """
    Pinecone implementation - Cloud, scalable (future)

    This is a stub for future migration to Pinecone cloud.
    Will be implemented when migrating from local to cloud.
    """

    def __init__(self, api_key: str, environment: str, index_name: str):
        """Initialize Pinecone vector store (stub)"""
        self.api_key = api_key
        self.environment = environment
        self.index_name = index_name

        raise NotImplementedError(
            "Pinecone implementation is not yet available. "
            "Use FAISSVectorStore for local development. "
            "To migrate to Pinecone: "
            "1. Set RAG_VECTOR_STORE=pinecone in .env "
            "2. Configure Pinecone credentials "
            "3. Implement this class"
        )

    def add_documents(self, texts, embeddings, metadatas=None):
        raise NotImplementedError("Pinecone not implemented yet")

    def search(self, query_embedding, top_k=5):
        raise NotImplementedError("Pinecone not implemented yet")

    def delete_all(self):
        raise NotImplementedError("Pinecone not implemented yet")

    def save(self):
        raise NotImplementedError("Pinecone not implemented yet")

    def load(self):
        raise NotImplementedError("Pinecone not implemented yet")

    def get_stats(self):
        raise NotImplementedError("Pinecone not implemented yet")


# Factory function for creating vector stores
def create_vector_store(
    store_type: str,
    **kwargs
) -> VectorStoreInterface:
    """
    Factory function to create vector store instances

    Args:
        store_type: Type of vector store ("faiss" or "pinecone")
        **kwargs: Additional arguments for the vector store

    Returns:
        VectorStoreInterface implementation

    Example:
        >>> store = create_vector_store("faiss", index_path="data/vector_store/faiss", dimension=384)
        >>> store = create_vector_store("pinecone", api_key="...", environment="...", index_name="...")
    """
    if store_type == "faiss":
        return FAISSVectorStore(**kwargs)
    elif store_type == "pinecone":
        return PineconeVectorStore(**kwargs)
    else:
        raise ValueError(f"Unknown vector store type: {store_type}. Use 'faiss' or 'pinecone'")


if __name__ == "__main__":
    # Test FAISS vector store
    print("Testing FAISS Vector Store...")
    print("=" * 60)

    # This will fail if dependencies not installed yet, but that's OK for now
    try:
        store = create_vector_store("faiss", index_path="data/vector_store/faiss_test", dimension=384)
        print(store.get_stats())
    except ImportError as e:
        print(f"⚠️  Dependencies not installed yet: {e}")
        print("   This is normal during initial setup.")
