#!/usr/bin/env python3
"""
Performance Utilities for Document Structurer

Provides utilities for optimized PDF processing:
- Chunked processing for large PDFs
- Parallel page extraction
- Progress tracking
- Memory-efficient operations

Author: BidAnalyzee Team
Date: 2025-11-06
Version: 1.0.0
"""

from typing import List, Dict, Any, Callable, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
import time


class ChunkedProcessor:
    """
    Process large PDFs in chunks to reduce memory usage.

    Instead of loading entire PDF, processes N pages at a time.
    """

    def __init__(self, chunk_size: int = 20):
        """
        Initialize chunked processor.

        Args:
            chunk_size: Number of pages to process at once (default: 20)
        """
        self.chunk_size = chunk_size

    def process_in_chunks(
        self,
        items: List[Any],
        processor_func: Callable,
        progress_callback: Optional[Callable] = None
    ) -> List[Any]:
        """
        Process items in chunks.

        Args:
            items: List of items to process
            processor_func: Function to process each chunk
            progress_callback: Optional callback for progress updates

        Returns:
            List of processed results
        """
        results = []
        total_items = len(items)

        for i in range(0, total_items, self.chunk_size):
            chunk = items[i:i + self.chunk_size]
            chunk_results = processor_func(chunk)
            results.extend(chunk_results)

            if progress_callback:
                progress = min((i + self.chunk_size) / total_items * 100, 100)
                progress_callback(progress, i + len(chunk), total_items)

        return results


class ParallelProcessor:
    """
    Process items in parallel using thread pool.

    Useful for I/O-bound operations like PDF page extraction.
    """

    def __init__(self, max_workers: int = 4):
        """
        Initialize parallel processor.

        Args:
            max_workers: Maximum number of parallel workers (default: 4)
        """
        self.max_workers = max_workers

    def process_parallel(
        self,
        items: List[Any],
        processor_func: Callable,
        progress_callback: Optional[Callable] = None
    ) -> List[Any]:
        """
        Process items in parallel.

        Args:
            items: List of items to process
            processor_func: Function to process each item
            progress_callback: Optional callback for progress updates

        Returns:
            List of processed results (order preserved)
        """
        results = [None] * len(items)

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all tasks
            future_to_index = {
                executor.submit(processor_func, item): i
                for i, item in enumerate(items)
            }

            # Collect results as they complete
            completed = 0
            for future in as_completed(future_to_index):
                index = future_to_index[future]
                results[index] = future.result()
                completed += 1

                if progress_callback:
                    progress = completed / len(items) * 100
                    progress_callback(progress, completed, len(items))

        return results


class ProgressTracker:
    """Track and display progress for long-running operations."""

    def __init__(self, total: int, description: str = "Processing"):
        """
        Initialize progress tracker.

        Args:
            total: Total number of items to process
            description: Description of the operation
        """
        self.total = total
        self.description = description
        self.current = 0
        self.start_time = time.time()

    def update(self, progress_percent: float, current: int, total: int):
        """
        Update progress.

        Args:
            progress_percent: Progress percentage (0-100)
            current: Current item number
            total: Total items
        """
        self.current = current
        elapsed = time.time() - self.start_time

        if current > 0:
            eta = (elapsed / current) * (total - current)
            eta_str = f"{int(eta)}s"
        else:
            eta_str = "?"

        print(f"\r{self.description}: {progress_percent:.1f}% ({current}/{total}) - ETA: {eta_str}", end="")

        if current >= total:
            print()  # New line when complete

    def finish(self):
        """Mark progress as finished."""
        elapsed = time.time() - self.start_time
        print(f"\n✅ {self.description} complete in {elapsed:.2f}s")


# Convenience functions

def process_pages_chunked(
    pages: List[Dict],
    processor_func: Callable,
    chunk_size: int = 20,
    show_progress: bool = True
) -> List[Any]:
    """
    Process PDF pages in chunks.

    Args:
        pages: List of page dictionaries
        processor_func: Function to process each chunk
        chunk_size: Pages per chunk
        show_progress: Whether to show progress

    Returns:
        List of processed results
    """
    chunked = ChunkedProcessor(chunk_size=chunk_size)

    if show_progress:
        tracker = ProgressTracker(len(pages), "Processing pages (chunked)")
        results = chunked.process_in_chunks(pages, processor_func, tracker.update)
        tracker.finish()
    else:
        results = chunked.process_in_chunks(pages, processor_func)

    return results


def process_pages_parallel(
    pages: List[Dict],
    processor_func: Callable,
    max_workers: int = 4,
    show_progress: bool = True
) -> List[Any]:
    """
    Process PDF pages in parallel.

    Args:
        pages: List of page dictionaries
        processor_func: Function to process each page
        max_workers: Number of parallel workers
        show_progress: Whether to show progress

    Returns:
        List of processed results (order preserved)
    """
    parallel = ParallelProcessor(max_workers=max_workers)

    if show_progress:
        tracker = ProgressTracker(len(pages), "Processing pages (parallel)")
        results = parallel.process_parallel(pages, processor_func, tracker.update)
        tracker.finish()
    else:
        results = parallel.process_parallel(pages, processor_func)

    return results


if __name__ == "__main__":
    # Example usage
    print("=" * 60)
    print("Performance Utilities - Demo")
    print("=" * 60)

    # Simulate processing 100 items
    items = list(range(100))

    def slow_processor(item):
        """Simulate slow processing"""
        time.sleep(0.01)
        return item * 2

    print("\n1. Chunked Processing (chunk_size=20):")
    chunked = ChunkedProcessor(chunk_size=20)
    tracker = ProgressTracker(len(items), "Chunked processing")
    results = chunked.process_in_chunks(items, lambda chunk: [slow_processor(x) for x in chunk], tracker.update)
    tracker.finish()
    print(f"   Processed {len(results)} items")

    print("\n2. Parallel Processing (4 workers):")
    parallel = ParallelProcessor(max_workers=4)
    tracker2 = ProgressTracker(len(items), "Parallel processing")
    results2 = parallel.process_parallel(items, slow_processor, tracker2.update)
    tracker2.finish()
    print(f"   Processed {len(results2)} items")

    print("\n" + "=" * 60)
