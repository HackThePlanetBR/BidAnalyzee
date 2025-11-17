#!/usr/bin/env python3
"""
RAG Search Utility Script

Searches the knowledge base using RAG (FAISS + sentence-transformers)
and returns relevant evidence for requirement analysis.

Usage:
    python3 scripts/rag_search.py --requirement "text" --top-k 5

This script is used by the Technical Analyst Agent (Claude Code)
during conformity analysis.
"""

import argparse
import json
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from agents.technical_analyst import RAGEngine


def main():
    parser = argparse.ArgumentParser(
        description="Search knowledge base using RAG for requirement analysis"
    )
    parser.add_argument(
        "--requirement",
        type=str,
        required=True,
        help="Requirement text to search for"
    )
    parser.add_argument(
        "--top-k",
        type=int,
        default=5,
        help="Number of results to return (default: 5)"
    )
    parser.add_argument(
        "--threshold",
        type=float,
        default=0.7,
        help="Minimum similarity threshold (default: 0.7)"
    )
    parser.add_argument(
        "--output-json",
        action="store_true",
        help="Output in JSON format (default: human-readable)"
    )

    args = parser.parse_args()

    try:
        # Initialize RAG Engine
        rag = RAGEngine.from_config()

        # Search knowledge base
        results = rag.search(
            query=args.requirement,
            top_k=args.top_k,
            similarity_threshold=args.threshold
        )

        if args.output_json:
            # JSON output for programmatic use
            output = {
                "query": args.requirement,
                "top_k": args.top_k,
                "threshold": args.threshold,
                "results_count": len(results),
                "results": results
            }
            print(json.dumps(output, indent=2, ensure_ascii=False))
        else:
            # Human-readable output
            print(f"\n{'='*70}")
            print(f"RAG SEARCH RESULTS")
            print(f"{'='*70}")
            print(f"Query: {args.requirement}")
            print(f"Top-K: {args.top_k}")
            print(f"Threshold: {args.threshold}")
            print(f"Results: {len(results)}")
            print(f"{'='*70}\n")

            if not results:
                print("WARNING: No evidence found. Consider:")
                print("  - Lowering similarity threshold")
                print("  - Rephrasing query")
                print("  - Using broader search terms")
                print()
            else:
                for i, result in enumerate(results, 1):
                    metadata = result.get('metadata', {})
                    title = metadata.get('title', metadata.get('filename', 'unknown'))
                    url = metadata.get('url', '')
                    filename = metadata.get('filename', 'unknown')
                    chunk_idx = metadata.get('chunk_index', 0)
                    similarity = result.get('similarity_score', 0.0)
                    text = result.get('text', '')

                    print(f"[{i}] {title}")
                    if url:
                        print(f"    URL: {url}")
                    print(f"    File: {filename} (chunk {chunk_idx}) | Similarity: {similarity:.2f}")
                    print(f"    Text: {text[:200]}...")
                    print()

        return 0

    except FileNotFoundError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        print("HINT: Run knowledge base ingestion first", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"ERROR: Unexpected error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
