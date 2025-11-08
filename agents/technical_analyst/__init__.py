"""
Technical Analyst Agent - Sprint 5

RAG-based agent for analyzing technical requirements against knowledge base.

Components:
- RAG Engine: Main orchestration
- Query Processor: Requirement analysis and conformity checking
- Analysis Pipeline: End-to-end integration (NEW in v0.3.0)
- Report Generator: Multi-format conformity reports (NEW in v0.3.0)
- Vector Store: FAISS (local) or Pinecone (cloud)
- Embeddings Manager: sentence-transformers (local) or OpenAI (cloud)
- Ingestion Pipeline: Document ingestion and indexing
"""

__version__ = "0.3.0"
__author__ = "BidAnalyzee Team"

from .config import RAGConfig
from .rag_engine import RAGEngine
from .query_processor import (
    QueryProcessor,
    ConformityVerdict,
    ConformityAnalysis,
    Evidence
)
from .vector_store import (
    VectorStoreInterface,
    FAISSVectorStore,
    create_vector_store
)
from .embeddings_manager import EmbeddingsManager
from .ingestion_pipeline import IngestionPipeline
from .pipeline import AnalysisPipeline
from .report import ConformityReport, ReportExporter


__all__ = [
    # Configuration
    'RAGConfig',

    # Core RAG
    'RAGEngine',

    # Query Processing (v0.2.0)
    'QueryProcessor',
    'ConformityVerdict',
    'ConformityAnalysis',
    'Evidence',

    # Analysis Pipeline (NEW in v0.3.0)
    'AnalysisPipeline',
    'ConformityReport',
    'ReportExporter',

    # Vector Store
    'VectorStoreInterface',
    'FAISSVectorStore',
    'create_vector_store',

    # Components
    'EmbeddingsManager',
    'IngestionPipeline',
]
