"""
Ingestion Pipeline for RAG system

Loads documents from knowledge base, chunks them, generates embeddings,
and stores in vector store.

Supports:
- Markdown files (.md)
- Text chunking with overlap
- Batch processing
- Progress tracking
"""

from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
import time
import re


class IngestionPipeline:
    """
    Pipeline for ingesting documents into vector store

    Process:
    1. Load markdown files from directory
    2. Split into chunks (with overlap for context)
    3. Generate embeddings for each chunk
    4. Store in vector store with metadata
    """

    def __init__(self, vector_store, embeddings_manager, chunk_size: int = 1000, chunk_overlap: int = 200):
        """
        Initialize ingestion pipeline

        Args:
            vector_store: VectorStoreInterface implementation
            embeddings_manager: EmbeddingsManager instance
            chunk_size: Maximum characters per chunk
            chunk_overlap: Characters to overlap between chunks
        """
        self.vector_store = vector_store
        self.embeddings = embeddings_manager
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def _extract_frontmatter(self, content: str) -> tuple[Dict[str, str], str]:
        """
        Extract YAML frontmatter from markdown content

        Frontmatter format:
        ---
        title: "Document Title"
        url: "https://example.com/doc"
        source: "Source Name"
        date: "2025-11-16"
        ---

        # Document content...

        Args:
            content: Raw markdown content

        Returns:
            Tuple of (metadata_dict, content_without_frontmatter)
        """
        frontmatter_pattern = re.compile(r'^---\s*\n(.*?)\n---\s*\n', re.DOTALL)
        match = frontmatter_pattern.match(content)

        if not match:
            # No frontmatter found
            return {}, content

        frontmatter_text = match.group(1)
        content_without_frontmatter = content[match.end():]

        # Simple YAML parsing (key: value format)
        metadata = {}
        for line in frontmatter_text.split('\n'):
            if ':' in line:
                key, value = line.split(':', 1)
                key = key.strip()
                value = value.strip().strip('"').strip("'")
                metadata[key] = value

        return metadata, content_without_frontmatter

    def load_markdown_files(self, directory_path: str) -> List[Dict[str, str]]:
        """
        Load all markdown files from a directory

        Args:
            directory_path: Path to directory containing .md files

        Returns:
            List of dicts with keys: {filename, content, title, url, source, path}
        """
        directory = Path(directory_path)

        if not directory.exists():
            raise ValueError(f"Directory does not exist: {directory_path}")

        markdown_files = list(directory.glob("*.md"))

        if not markdown_files:
            print(f"⚠️  No markdown files found in {directory_path}")
            return []

        documents = []
        for file_path in sorted(markdown_files):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    raw_content = f.read()

                # Extract frontmatter metadata (title, url, etc.)
                frontmatter, content = self._extract_frontmatter(raw_content)

                doc = {
                    "filename": file_path.name,
                    "content": content,  # Content without frontmatter
                    "path": str(file_path),
                    "title": frontmatter.get("title", file_path.stem),  # Use filename if no title
                    "url": frontmatter.get("url", ""),  # Empty if no URL
                    "source": frontmatter.get("source", ""),
                    "date": frontmatter.get("date", "")
                }

                documents.append(doc)

                # Display info
                title_display = doc['title'][:50] + '...' if len(doc['title']) > 50 else doc['title']
                url_display = f" | {doc['url']}" if doc['url'] else ""
                print(f"✅ Loaded: {title_display}{url_display}")
                print(f"   File: {file_path.name} ({len(content)} chars)")

            except Exception as e:
                print(f"❌ Error loading {file_path.name}: {e}")

        print(f"\n📚 Loaded {len(documents)} documents")
        return documents

    def chunk_text(self, text: str, metadata: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Split text into overlapping chunks

        Uses simple character-based chunking with overlap.
        For production, could use langchain's RecursiveCharacterTextSplitter
        with smart splitting on paragraphs/sentences.

        Args:
            text: Text to chunk
            metadata: Metadata to attach to each chunk

        Returns:
            List of dicts with keys: {text, metadata}
        """
        if not text:
            return []

        chunks = []
        start = 0

        while start < len(text):
            end = start + self.chunk_size

            # Try to break at paragraph or sentence boundary
            if end < len(text):
                # Look for paragraph break (double newline)
                para_break = text.rfind('\n\n', start, end)
                if para_break > start:
                    end = para_break + 2

                # If no paragraph, look for sentence break
                elif '.' in text[start:end]:
                    sentence_break = text.rfind('.', start, end)
                    if sentence_break > start:
                        end = sentence_break + 1

            chunk_text = text[start:end].strip()

            if chunk_text:
                chunk_metadata = {
                    **metadata,
                    "chunk_index": len(chunks),
                    "start_char": start,
                    "end_char": end
                }

                chunks.append({
                    "text": chunk_text,
                    "metadata": chunk_metadata
                })

            # Move start position (with overlap)
            start = end - self.chunk_overlap if end < len(text) else end

        return chunks

    def ingest_from_directory(self, directory_path: str) -> Dict[str, Any]:
        """
        Ingest all markdown files from a directory

        Full pipeline:
        1. Load markdown files
        2. Chunk each document
        3. Generate embeddings for all chunks
        4. Store in vector store
        5. Save vector store to disk

        Args:
            directory_path: Path to directory with markdown files

        Returns:
            Statistics dict with keys: {
                documents_loaded,
                total_chunks,
                total_embeddings,
                time_elapsed,
                files_processed
            }
        """
        start_time = time.time()

        print("=" * 60)
        print("RAG INGESTION PIPELINE")
        print("=" * 60)

        # Step 1: Load documents
        print("\n📚 Step 1: Loading markdown files...")
        documents = self.load_markdown_files(directory_path)

        if not documents:
            return {
                "documents_loaded": 0,
                "total_chunks": 0,
                "total_embeddings": 0,
                "time_elapsed": 0,
                "files_processed": []
            }

        # Step 2: Chunk documents
        print(f"\n✂️  Step 2: Chunking documents (size={self.chunk_size}, overlap={self.chunk_overlap})...")
        all_chunks = []
        files_processed = []

        for doc in documents:
            metadata = {
                "filename": doc["filename"],
                "source_path": doc["path"],
                "title": doc["title"],
                "url": doc["url"],
                "source": doc.get("source", ""),
                "date": doc.get("date", "")
            }

            chunks = self.chunk_text(doc["content"], metadata)
            all_chunks.extend(chunks)

            files_processed.append({
                "filename": doc["filename"],
                "chunks": len(chunks),
                "chars": len(doc["content"])
            })

            print(f"   {doc['filename']}: {len(chunks)} chunks")

        print(f"\n✅ Total chunks: {len(all_chunks)}")

        # Step 3: Generate embeddings
        print(f"\n🔮 Step 3: Generating embeddings...")
        texts = [chunk["text"] for chunk in all_chunks]
        embeddings = self.embeddings.embed_documents(texts, show_progress=True)

        print(f"✅ Generated {len(embeddings)} embeddings")

        # Step 4: Store in vector store
        print(f"\n💾 Step 4: Storing in vector store...")
        metadatas = [chunk["metadata"] for chunk in all_chunks]
        self.vector_store.add_documents(texts, embeddings, metadatas)

        # Step 5: Save vector store
        print(f"\n💾 Step 5: Saving vector store to disk...")
        self.vector_store.save()

        # Calculate stats
        elapsed_time = time.time() - start_time

        stats = {
            "documents_loaded": len(documents),
            "total_chunks": len(all_chunks),
            "total_embeddings": len(embeddings),
            "time_elapsed": elapsed_time,
            "files_processed": files_processed,
            "timestamp": datetime.now().isoformat()
        }

        # Print summary
        print("\n" + "=" * 60)
        print("INGESTION COMPLETE")
        print("=" * 60)
        print(f"📚 Documents: {stats['documents_loaded']}")
        print(f"✂️  Chunks: {stats['total_chunks']}")
        print(f"🔮 Embeddings: {stats['total_embeddings']}")
        print(f"⏱️  Time: {stats['time_elapsed']:.2f} seconds")
        print(f"📊 Avg time per document: {stats['time_elapsed'] / max(stats['documents_loaded'], 1):.2f}s")
        print("=" * 60)

        return stats

    def ingest_single_document(
        self,
        text: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Ingest a single document (useful for adding new docs incrementally)

        Args:
            text: Document text
            metadata: Optional metadata

        Returns:
            Statistics dict
        """
        if not text:
            raise ValueError("Document text cannot be empty")

        if metadata is None:
            metadata = {}

        print(f"📄 Ingesting single document ({len(text)} chars)...")

        # Chunk
        chunks = self.chunk_text(text, metadata)
        print(f"   Chunks: {len(chunks)}")

        # Generate embeddings
        texts = [chunk["text"] for chunk in chunks]
        embeddings = self.embeddings.embed_documents(texts, show_progress=False)

        # Store
        metadatas = [chunk["metadata"] for chunk in chunks]
        self.vector_store.add_documents(texts, embeddings, metadatas)

        # Save
        self.vector_store.save()

        print(f"✅ Document ingested successfully")

        return {
            "chunks": len(chunks),
            "embeddings": len(embeddings)
        }


if __name__ == "__main__":
    # Test ingestion pipeline
    print("Testing Ingestion Pipeline...")
    print("=" * 60)

    try:
        from config import RAGConfig
        from vector_store import create_vector_store
        from embeddings_manager import EmbeddingsManager

        # Initialize components
        print("🔧 Initializing components...")

        vector_store = create_vector_store(
            store_type=RAGConfig.VECTOR_STORE,
            index_path=RAGConfig.FAISS_INDEX_PATH,
            dimension=RAGConfig.EMBEDDINGS_DIMENSION
        )

        embeddings = EmbeddingsManager(
            provider=RAGConfig.EMBEDDINGS_PROVIDER,
            model=RAGConfig.EMBEDDINGS_MODEL
        )

        pipeline = IngestionPipeline(
            vector_store=vector_store,
            embeddings_manager=embeddings,
            chunk_size=RAGConfig.CHUNK_SIZE,
            chunk_overlap=RAGConfig.CHUNK_OVERLAP
        )

        # Run ingestion
        print("\n🚀 Running ingestion...")
        stats = pipeline.ingest_from_directory(RAGConfig.KNOWLEDGE_BASE_PATH)

        print("\n📊 Final Stats:")
        print(f"   Documents: {stats['documents_loaded']}")
        print(f"   Chunks: {stats['total_chunks']}")
        print(f"   Time: {stats['time_elapsed']:.2f}s")

        # Test vector store
        print("\n🔍 Testing vector store...")
        store_stats = vector_store.get_stats()
        print(f"   Total in index: {store_stats['total_documents']}")

        print("\n✅ All tests passed!")

    except ImportError as e:
        print(f"\n⚠️  Dependencies not installed yet: {e}")
        print("   This is normal during initial setup.")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
