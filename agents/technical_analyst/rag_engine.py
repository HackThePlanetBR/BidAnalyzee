"""
RAG Engine - Main orchestration for Retrieval-Augmented Generation

Orchestrates all RAG components:
- Vector Store (FAISS/Pinecone)
- Embeddings Manager (local/OpenAI)
- Ingestion Pipeline
- Query Processing

Provides high-level API for:
- Ingesting knowledge base
- Searching for relevant documents
- Managing RAG lifecycle
"""

from typing import List, Dict, Any, Optional
from pathlib import Path
import json
from datetime import datetime

from .config import RAGConfig
from .vector_store import create_vector_store
from .embeddings_manager import EmbeddingsManager
from .ingestion_pipeline import IngestionPipeline


class RAGEngine:
    """
    Main RAG orchestration engine

    Provides high-level API for:
    - Knowledge base ingestion
    - Semantic search
    - Document retrieval

    Usage:
        engine = RAGEngine.from_config()
        engine.ingest_knowledge_base()
        results = engine.search("What are the technical requirements?")
    """

    def __init__(
        self,
        vector_store,
        embeddings_manager: EmbeddingsManager,
        ingestion_pipeline: IngestionPipeline,
        config: RAGConfig
    ):
        """
        Initialize RAG Engine

        Args:
            vector_store: Vector store instance
            embeddings_manager: Embeddings manager instance
            ingestion_pipeline: Ingestion pipeline instance
            config: RAG configuration
        """
        self.vector_store = vector_store
        self.embeddings = embeddings_manager
        self.ingestion = ingestion_pipeline
        self.config = config

        self._initialized = False
        self._stats = {}

    @classmethod
    def from_config(cls, config: Optional[RAGConfig] = None) -> "RAGEngine":
        """
        Factory method to create RAGEngine from configuration

        Args:
            config: RAGConfig instance (uses default if None)

        Returns:
            Initialized RAGEngine instance
        """
        if config is None:
            config = RAGConfig()

        # Validate configuration
        if not config.validate():
            raise ValueError("Invalid RAG configuration")

        # Initialize components
        print("🔧 Initializing RAG Engine...")

        # 1. Vector Store
        print(f"   Vector Store: {config.VECTOR_STORE}")
        vector_store = create_vector_store(
            store_type=config.VECTOR_STORE,
            index_path=config.FAISS_INDEX_PATH if config.VECTOR_STORE == "faiss" else None,
            dimension=config.EMBEDDINGS_DIMENSION
        )

        # Try to load existing index
        try:
            vector_store.load()
            print(f"   ✅ Loaded existing index")
        except FileNotFoundError:
            print(f"   ⚠️  No existing index found (will create on first ingestion)")

        # 2. Embeddings Manager
        print(f"   Embeddings: {config.EMBEDDINGS_PROVIDER} ({config.EMBEDDINGS_MODEL})")
        embeddings = EmbeddingsManager(
            provider=config.EMBEDDINGS_PROVIDER,
            model=config.EMBEDDINGS_MODEL
        )

        # 3. Ingestion Pipeline
        print(f"   Ingestion Pipeline: chunk_size={config.CHUNK_SIZE}, overlap={config.CHUNK_OVERLAP}")
        ingestion = IngestionPipeline(
            vector_store=vector_store,
            embeddings_manager=embeddings,
            chunk_size=config.CHUNK_SIZE,
            chunk_overlap=config.CHUNK_OVERLAP
        )

        print("✅ RAG Engine initialized successfully\n")

        return cls(
            vector_store=vector_store,
            embeddings_manager=embeddings,
            ingestion_pipeline=ingestion,
            config=config
        )

    def ingest_knowledge_base(self, directory_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Ingest all documents from knowledge base directory

        Args:
            directory_path: Path to knowledge base (uses config default if None)

        Returns:
            Statistics dict with ingestion results
        """
        if directory_path is None:
            directory_path = self.config.KNOWLEDGE_BASE_PATH

        print(f"📚 Ingesting knowledge base from: {directory_path}")

        stats = self.ingestion.ingest_from_directory(directory_path)

        self._initialized = True
        self._stats = {
            **stats,
            "last_ingestion": datetime.now().isoformat()
        }

        return stats

    def search(
        self,
        query: str,
        top_k: Optional[int] = None,
        similarity_threshold: Optional[float] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for documents relevant to query

        Args:
            query: Search query
            top_k: Number of results to return (uses config default if None)
            similarity_threshold: Minimum similarity score (uses config default if None)

        Returns:
            List of dicts with keys: {text, metadata, similarity_score}
        """
        if not self._initialized and self.vector_store.get_stats()["total_documents"] == 0:
            raise RuntimeError(
                "RAG Engine not initialized. Call ingest_knowledge_base() first."
            )

        if not query or not query.strip():
            raise ValueError("Query cannot be empty")

        # Use config defaults if not specified
        if top_k is None:
            top_k = self.config.TOP_K
        if similarity_threshold is None:
            similarity_threshold = self.config.SIMILARITY_THRESHOLD

        # Generate query embedding
        query_embedding = self.embeddings.embed_query(query)

        # Search vector store
        results = self.vector_store.search(
            query_embedding=query_embedding,
            top_k=top_k
        )

        # Filter by similarity threshold
        # vector_store returns 'score', rename to 'similarity_score'
        filtered_results = []
        for result in results:
            if result["score"] >= similarity_threshold:
                result_copy = result.copy()
                result_copy["similarity_score"] = result_copy.pop("score")
                filtered_results.append(result_copy)

        return filtered_results

    def search_with_context(
        self,
        query: str,
        top_k: Optional[int] = None,
        similarity_threshold: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Search with additional context information

        Returns both search results and query metadata for downstream processing.

        Args:
            query: Search query
            top_k: Number of results to return
            similarity_threshold: Minimum similarity score

        Returns:
            Dict with keys: {
                query,
                results: List[Dict],
                num_results,
                avg_similarity,
                timestamp
            }
        """
        results = self.search(query, top_k, similarity_threshold)

        return {
            "query": query,
            "results": results,
            "num_results": len(results),
            "avg_similarity": sum(r["similarity_score"] for r in results) / len(results) if results else 0.0,
            "timestamp": datetime.now().isoformat()
        }

    def get_stats(self) -> Dict[str, Any]:
        """
        Get RAG engine statistics

        Returns:
            Dict with keys: {
                vector_store_stats,
                embeddings_info,
                last_ingestion,
                initialized
            }
        """
        vector_stats = self.vector_store.get_stats()

        return {
            "initialized": self._initialized,
            "vector_store": {
                **vector_stats,
                "type": self.config.VECTOR_STORE
            },
            "embeddings": {
                "provider": self.config.EMBEDDINGS_PROVIDER,
                "model": self.config.EMBEDDINGS_MODEL,
                "dimension": self.config.EMBEDDINGS_DIMENSION
            },
            "search_config": {
                "top_k": self.config.TOP_K,
                "similarity_threshold": self.config.SIMILARITY_THRESHOLD
            },
            "last_ingestion": self._stats.get("last_ingestion", None),
            "ingestion_stats": self._stats
        }

    def export_stats(self, output_path: str):
        """
        Export statistics to JSON file

        Args:
            output_path: Path to output JSON file
        """
        stats = self.get_stats()

        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(stats, f, indent=2, ensure_ascii=False)

        print(f"📊 Stats exported to: {output_path}")

    def reset(self):
        """
        Reset RAG engine (clear vector store)

        WARNING: This will delete all indexed documents!
        """
        print("⚠️  Resetting RAG Engine (clearing all data)...")

        # Clear vector store
        self.vector_store = create_vector_store(
            store_type=self.config.VECTOR_STORE,
            index_path=self.config.FAISS_INDEX_PATH if self.config.VECTOR_STORE == "faiss" else None,
            dimension=self.config.EMBEDDINGS_DIMENSION
        )

        # Re-initialize ingestion pipeline with new vector store
        self.ingestion = IngestionPipeline(
            vector_store=self.vector_store,
            embeddings_manager=self.embeddings,
            chunk_size=self.config.CHUNK_SIZE,
            chunk_overlap=self.config.CHUNK_OVERLAP
        )

        self._initialized = False
        self._stats = {}

        print("✅ RAG Engine reset complete")


def create_rag_engine(config: Optional[RAGConfig] = None) -> RAGEngine:
    """
    Convenience factory function for creating RAG engine

    Args:
        config: RAGConfig instance (uses default if None)

    Returns:
        Initialized RAGEngine instance
    """
    return RAGEngine.from_config(config)


if __name__ == "__main__":
    # Test RAG Engine
    print("Testing RAG Engine...")
    print("=" * 60)

    try:
        from config import RAGConfig

        # Initialize engine
        print("🔧 Initializing RAG Engine...\n")
        engine = RAGEngine.from_config()

        # Check if knowledge base exists
        kb_path = Path(RAGConfig.KNOWLEDGE_BASE_PATH)
        if not kb_path.exists():
            print(f"❌ Knowledge base not found: {RAGConfig.KNOWLEDGE_BASE_PATH}")
            print("   Run ingestion pipeline first to create knowledge base.")
            exit(1)

        # Ingest knowledge base
        print("\n📚 Ingesting knowledge base...\n")
        stats = engine.ingest_knowledge_base()

        print(f"\n✅ Ingestion complete!")
        print(f"   Documents: {stats['documents_loaded']}")
        print(f"   Chunks: {stats['total_chunks']}")
        print(f"   Time: {stats['time_elapsed']:.2f}s")

        # Test search
        print("\n" + "=" * 60)
        print("🔍 Testing search functionality...")
        print("=" * 60)

        test_queries = [
            "Quais são os requisitos técnicos para sistema de CFTV?",
            "Como deve ser feita a qualificação técnica?",
            "Quais são os prazos de entrega?",
        ]

        for query in test_queries:
            print(f"\n📝 Query: {query}")
            results = engine.search(query, top_k=3)

            print(f"   Found {len(results)} results:")
            for i, result in enumerate(results, 1):
                print(f"\n   [{i}] Similarity: {result['similarity_score']:.3f}")
                print(f"       Source: {result['metadata'].get('filename', 'unknown')}")
                print(f"       Chunk: {result['metadata'].get('chunk_index', 'unknown')}")
                print(f"       Text: {result['text'][:150]}...")

        # Print final stats
        print("\n" + "=" * 60)
        print("📊 Final Statistics")
        print("=" * 60)

        final_stats = engine.get_stats()
        print(f"Vector Store: {final_stats['vector_store']['type']}")
        print(f"Total Documents: {final_stats['vector_store']['total_documents']}")
        print(f"Embeddings Model: {final_stats['embeddings']['model']}")
        print(f"Dimension: {final_stats['embeddings']['dimension']}")

        # Export stats
        print("\n📊 Exporting stats...")
        engine.export_stats("data/rag_stats.json")

        print("\n" + "=" * 60)
        print("✅ All tests passed!")
        print("=" * 60)

    except ImportError as e:
        print(f"\n⚠️  Dependencies not installed yet: {e}")
        print("   Run: pip install -r requirements.txt")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
