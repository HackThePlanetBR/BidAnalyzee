#!/usr/bin/env python3
"""
Knowledge Base Indexing Script

Indexes all documents from the knowledge base directory into FAISS vector store.
Creates embeddings using sentence-transformers and stores them for RAG search.

Usage:
    python3 scripts/index_knowledge_base.py [--kb-path PATH] [--force]

Options:
    --kb-path PATH    Path to knowledge base directory (default: data/knowledge_base/mock)
    --force           Force re-indexing even if index exists
    --stats           Export statistics to JSON file

This is a prerequisite for using the Technical Analyst Agent's RAG search.
"""

import argparse
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from agents.technical_analyst import RAGEngine, RAGConfig


def main():
    parser = argparse.ArgumentParser(
        description="Index knowledge base documents into FAISS vector store"
    )
    parser.add_argument(
        "--kb-path",
        type=str,
        default=None,
        help="Path to knowledge base directory (default: from RAGConfig)"
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Force re-indexing even if index already exists"
    )
    parser.add_argument(
        "--stats",
        type=str,
        default=None,
        help="Export statistics to JSON file (e.g., data/kb_stats.json)"
    )
    parser.add_argument(
        "--verify",
        action="store_true",
        help="Verify index after creation with test queries"
    )

    args = parser.parse_args()

    try:
        print("=" * 70)
        print("📚 KNOWLEDGE BASE INDEXING")
        print("=" * 70)
        print()

        # Initialize RAG Engine
        print("🔧 Initializing RAG Engine...")
        config = RAGConfig()
        rag = RAGEngine.from_config(config)
        print()

        # Check if index already exists
        kb_path = args.kb_path or config.KNOWLEDGE_BASE_PATH
        kb_dir = Path(kb_path)

        if not kb_dir.exists():
            print(f"❌ Knowledge base directory not found: {kb_path}")
            print(f"💡 Hint: Create {kb_path} and add documents (.md, .txt files)")
            return 1

        # Count documents (recursive search)
        doc_files = list(kb_dir.glob("**/*.md")) + list(kb_dir.glob("**/*.txt"))
        print(f"📁 Knowledge Base: {kb_path}")
        print(f"📄 Documents found: {len(doc_files)}")

        if len(doc_files) == 0:
            print("⚠️  No documents found in knowledge base")
            print("💡 Add .md or .txt files to the knowledge base directory")
            return 1

        for doc in doc_files:
            print(f"   - {doc.name}")
        print()

        # Check if index exists
        stats = rag.get_stats()
        index_exists = stats['vector_store']['total_documents'] > 0

        if index_exists and not args.force:
            print(f"✅ Index already exists ({stats['vector_store']['total_documents']} documents)")
            print("💡 Use --force to re-index")
            print()
        else:
            if args.force and index_exists:
                print("⚠️  Force re-indexing (clearing existing index)...")
                rag.reset()
                print()

            # Ingest knowledge base
            print("🚀 Starting indexing process...")
            print("   This may take a few minutes depending on KB size...")
            print()

            ingest_stats = rag.ingest_knowledge_base(kb_path)

            print()
            print("=" * 70)
            print("✅ INDEXING COMPLETE")
            print("=" * 70)
            print(f"📄 Documents loaded: {ingest_stats['documents_loaded']}")
            print(f"📦 Total chunks: {ingest_stats['total_chunks']}")
            print(f"⏱️  Time elapsed: {ingest_stats['time_elapsed']:.2f}s")
            print()

        # Verify with test queries
        if args.verify:
            print("=" * 70)
            print("🔍 VERIFICATION - Testing Index")
            print("=" * 70)
            print()

            test_queries = [
                "Security Center system requirements",           # TechDocs/SCSaaS
                "ISO 27001 certification compliance",            # Compliance
                "video surveillance hardware specifications",    # TechDocs
                "cloud services managed deployment",             # SCSaaS
                "SOC 2 Type 2 audit report",                    # Compliance
                "access control integration protocols"          # TechDocs
            ]

            for query in test_queries:
                print(f"Query: \"{query}\"")
                results = rag.search(query, top_k=3, similarity_threshold=0.5)
                print(f"  ✅ Found {len(results)} results")
                if results:
                    best = results[0]
                    print(f"  📊 Best match: {best['metadata'].get('filename', 'unknown')} "
                          f"(similarity: {best['similarity_score']:.2f})")
                print()

        # Export stats if requested
        if args.stats:
            print("📊 Exporting statistics...")
            rag.export_stats(args.stats)
            print(f"✅ Stats saved to: {args.stats}")
            print()

        # Final stats
        final_stats = rag.get_stats()
        print("=" * 70)
        print("📊 FINAL STATISTICS")
        print("=" * 70)
        print(f"Vector Store Type: {final_stats['vector_store']['type']}")
        print(f"Total Documents: {final_stats['vector_store']['total_documents']}")
        print(f"Embeddings Model: {final_stats['embeddings']['model']}")
        print(f"Dimension: {final_stats['embeddings']['dimension']}")
        print(f"Index Path: {config.FAISS_INDEX_PATH}")
        print()

        print("=" * 70)
        print("🎉 Knowledge Base is ready for RAG search!")
        print("=" * 70)
        print()
        print("💡 Next steps:")
        print("   - Test search: python3 scripts/rag_search.py --requirement 'requisitos técnicos'")
        print("   - Run analysis: /analyze-edital <csv_path>")
        print()

        return 0

    except KeyboardInterrupt:
        print("\n⚠️  Indexing interrupted by user")
        return 130
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("💡 Hint: Install dependencies with: pip install -r requirements.txt")
        return 1
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
