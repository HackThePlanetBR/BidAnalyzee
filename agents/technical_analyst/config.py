"""
Configuration loader for Technical Analyst Agent (RAG)

Loads configuration from environment variables (.env file).
Provides centralized access to all RAG-related settings.
"""

import os
from pathlib import Path
from typing import Literal

# Try to load dotenv, but don't fail if not available yet
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("Warning: python-dotenv not installed. Using system environment variables only.")


class RAGConfig:
    """Configuration for RAG system"""

    # Vector Store Configuration
    VECTOR_STORE: Literal["faiss", "pinecone"] = os.getenv("RAG_VECTOR_STORE", "faiss")

    # FAISS Configuration (Local)
    FAISS_INDEX_PATH: str = os.getenv("RAG_FAISS_INDEX_PATH", "data/vector_store/faiss")

    # Pinecone Configuration (Future - Cloud)
    PINECONE_API_KEY: str = os.getenv("PINECONE_API_KEY", "")
    PINECONE_ENVIRONMENT: str = os.getenv("PINECONE_ENVIRONMENT", "")
    PINECONE_INDEX_NAME: str = os.getenv("PINECONE_INDEX_NAME", "bidanalyzee-knowledge-base")
    PINECONE_DIMENSION: int = int(os.getenv("PINECONE_DIMENSION", "1536"))
    PINECONE_METRIC: str = os.getenv("PINECONE_METRIC", "cosine")

    # Embeddings Configuration
    EMBEDDINGS_PROVIDER: Literal["local", "openai"] = os.getenv("RAG_EMBEDDINGS_PROVIDER", "local")
    EMBEDDINGS_MODEL: str = os.getenv("RAG_EMBEDDINGS_MODEL", "all-MiniLM-L6-v2")
    EMBEDDINGS_DIMENSION: int = int(os.getenv("RAG_EMBEDDINGS_DIMENSION", "384"))

    # OpenAI Configuration (Future)
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_EMBEDDINGS_MODEL: str = os.getenv("OPENAI_EMBEDDINGS_MODEL", "text-embedding-3-small")
    OPENAI_EMBEDDINGS_DIMENSION: int = int(os.getenv("OPENAI_EMBEDDINGS_DIMENSION", "1536"))

    # Knowledge Base Configuration
    KNOWLEDGE_BASE_PATH: str = os.getenv("RAG_KNOWLEDGE_BASE_PATH", "data/knowledge_base/mock")
    CHUNK_SIZE: int = int(os.getenv("RAG_CHUNK_SIZE", "1000"))
    CHUNK_OVERLAP: int = int(os.getenv("RAG_CHUNK_OVERLAP", "200"))

    # Search Configuration
    TOP_K: int = int(os.getenv("RAG_TOP_K", "5"))
    SIMILARITY_THRESHOLD: float = float(os.getenv("RAG_SIMILARITY_THRESHOLD", "0.7"))

    # n8n Configuration (Future)
    N8N_BASE_URL: str = os.getenv("N8N_BASE_URL", "")
    N8N_INGESTION_WEBHOOK_URL: str = os.getenv("N8N_INGESTION_WEBHOOK_URL", "")
    N8N_API_KEY: str = os.getenv("N8N_API_KEY", "")

    @classmethod
    def validate(cls) -> bool:
        """Validate configuration"""
        errors = []

        # Check vector store configuration
        if cls.VECTOR_STORE == "faiss":
            if not cls.FAISS_INDEX_PATH:
                errors.append("FAISS_INDEX_PATH is required when using FAISS vector store")
        elif cls.VECTOR_STORE == "pinecone":
            if not cls.PINECONE_API_KEY:
                errors.append("PINECONE_API_KEY is required when using Pinecone")
            if not cls.PINECONE_ENVIRONMENT:
                errors.append("PINECONE_ENVIRONMENT is required when using Pinecone")

        # Check embeddings configuration
        if cls.EMBEDDINGS_PROVIDER == "openai":
            if not cls.OPENAI_API_KEY:
                errors.append("OPENAI_API_KEY is required when using OpenAI embeddings")

        # Check knowledge base path exists
        kb_path = Path(cls.KNOWLEDGE_BASE_PATH)
        if not kb_path.exists():
            errors.append(f"Knowledge base path does not exist: {cls.KNOWLEDGE_BASE_PATH}")

        if errors:
            for error in errors:
                print(f"❌ Configuration Error: {error}")
            return False

        return True

    @classmethod
    def print_config(cls):
        """Print current configuration (for debugging)"""
        print("=" * 60)
        print("RAG Configuration")
        print("=" * 60)
        print(f"Vector Store: {cls.VECTOR_STORE}")

        if cls.VECTOR_STORE == "faiss":
            print(f"  FAISS Index Path: {cls.FAISS_INDEX_PATH}")

        print(f"Embeddings Provider: {cls.EMBEDDINGS_PROVIDER}")
        print(f"  Model: {cls.EMBEDDINGS_MODEL}")
        print(f"  Dimension: {cls.EMBEDDINGS_DIMENSION}")

        print(f"Knowledge Base: {cls.KNOWLEDGE_BASE_PATH}")
        print(f"  Chunk Size: {cls.CHUNK_SIZE}")
        print(f"  Chunk Overlap: {cls.CHUNK_OVERLAP}")

        print(f"Search Configuration:")
        print(f"  Top K: {cls.TOP_K}")
        print(f"  Similarity Threshold: {cls.SIMILARITY_THRESHOLD}")
        print("=" * 60)


# Create singleton instance
config = RAGConfig()


if __name__ == "__main__":
    # Test configuration
    config.print_config()

    if config.validate():
        print("✅ Configuration is valid")
    else:
        print("❌ Configuration has errors")
