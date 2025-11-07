#!/usr/bin/env python3
"""
Unit Tests for Cache Manager

Tests caching functionality including:
- Cache get/set operations
- TTL expiration
- Cache invalidation
- Size limits and eviction
- Statistics tracking
- File hash computation

Author: BidAnalyzee Team
Date: 2025-11-06
Version: 1.0.0
"""

import sys
import tempfile
import time
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from agents.document_structurer.cache_manager import (
    CacheManager,
    get_cached_text,
    cache_text
)


class TestCacheManager:
    """Test suite for Cache Manager"""

    def setup_method(self):
        """Setup test fixtures"""
        # Create temporary directories
        self.temp_dir = tempfile.mkdtemp()

        # Cache directory (subdirectory of temp_dir)
        cache_dir = Path(self.temp_dir) / "cache"
        self.cache = CacheManager(cache_dir=str(cache_dir), ttl_hours=1)

        # Test file directory (separate from cache)
        test_files_dir = Path(self.temp_dir) / "test_files"
        test_files_dir.mkdir(exist_ok=True)

        # Create temporary test file
        self.test_file = test_files_dir / "test.pdf"
        self.test_file.write_text("Test PDF content")

    def teardown_method(self):
        """Cleanup after tests"""
        import shutil
        if Path(self.temp_dir).exists():
            shutil.rmtree(self.temp_dir)

    def test_cache_initialization(self):
        """Test cache manager initialization"""
        assert self.cache.cache_dir.exists()
        assert self.cache.text_cache_dir.exists()
        assert self.cache.metadata_cache_dir.exists()
        assert self.cache.ocr_cache_dir.exists()
        assert self.cache.ttl_hours == 1

        print("✅ Cache initialization: PASS")

    def test_cache_set_and_get(self):
        """Test basic cache set and get operations"""
        test_data = "Extracted PDF text here"

        # Set cache
        self.cache.set(str(self.test_file), test_data, namespace="text")

        # Get cache
        cached = self.cache.get(str(self.test_file), namespace="text")

        assert cached is not None
        assert cached["data"] == test_data
        assert "cached_at" in cached
        assert "source_file" in cached

        print("✅ Cache set and get: PASS")

    def test_cache_miss(self):
        """Test cache miss for non-existent entry"""
        non_existent = Path(self.temp_dir) / "nonexistent.pdf"
        non_existent.write_text("Test")

        cached = self.cache.get(str(non_existent), namespace="text")
        assert cached is None

        print("✅ Cache miss: PASS")

    def test_cache_hit_statistics(self):
        """Test cache hit/miss statistics"""
        test_data = "Test data"

        # Initial stats
        stats = self.cache.get_stats()
        initial_hits = stats["hits"]
        initial_misses = stats["misses"]

        # Cache miss
        self.cache.get(str(self.test_file), namespace="text")
        stats = self.cache.get_stats()
        assert stats["misses"] == initial_misses + 1

        # Cache set
        self.cache.set(str(self.test_file), test_data, namespace="text")

        # Cache hit
        self.cache.get(str(self.test_file), namespace="text")
        stats = self.cache.get_stats()
        assert stats["hits"] == initial_hits + 1

        print("✅ Cache hit statistics: PASS")

    def test_cache_invalidation(self):
        """Test cache invalidation"""
        test_data = "Test data"

        # Set cache
        self.cache.set(str(self.test_file), test_data, namespace="text")

        # Verify it exists
        assert self.cache.get(str(self.test_file), namespace="text") is not None

        # Invalidate
        self.cache.invalidate(str(self.test_file), namespace="text")

        # Verify it's gone
        assert self.cache.get(str(self.test_file), namespace="text") is None

        print("✅ Cache invalidation: PASS")

    def test_different_namespaces(self):
        """Test caching in different namespaces"""
        text_data = "Extracted text"
        metadata_data = {"objeto": "Test", "orgao": "Test Agency"}

        # Cache in different namespaces
        self.cache.set(str(self.test_file), text_data, namespace="text")
        self.cache.set(str(self.test_file), metadata_data, namespace="metadata")

        # Retrieve from different namespaces
        cached_text = self.cache.get(str(self.test_file), namespace="text")
        cached_metadata = self.cache.get(str(self.test_file), namespace="metadata")

        assert cached_text["data"] == text_data
        assert cached_metadata["data"] == metadata_data

        print("✅ Different namespaces: PASS")

    def test_file_hash_computation(self):
        """Test file hash computation"""
        hash1 = self.cache._compute_file_hash(str(self.test_file))

        assert isinstance(hash1, str)
        assert len(hash1) == 64  # SHA256 hex digest length

        # Same file should produce same hash
        hash2 = self.cache._compute_file_hash(str(self.test_file))
        assert hash1 == hash2

        # Different file should produce different hash
        test_file2 = Path(self.temp_dir) / "test2.pdf"
        test_file2.write_text("Different content")
        hash3 = self.cache._compute_file_hash(str(test_file2))
        assert hash1 != hash3

        print("✅ File hash computation: PASS")

    def test_cache_size_calculation(self):
        """Test cache size calculation"""
        # Initially empty (or near-zero, accounting for stats file)
        initial_size = self.cache._get_cache_size()
        assert initial_size >= 0

        # Add some cache entries
        self.cache.set(str(self.test_file), "Test data 1", namespace="text")

        test_file2 = Path(self.temp_dir) / "test2.pdf"
        test_file2.write_text("Different content")
        self.cache.set(str(test_file2), "Test data 2", namespace="text")

        # Should have non-zero size now
        size = self.cache._get_cache_size()
        assert size > initial_size, f"Cache size should increase: {initial_size} -> {size}"

        stats = self.cache.get_stats()
        assert stats["cache_size_bytes"] >= size  # May include stats file
        assert stats["cache_size_mb"] >= 0

        print("✅ Cache size calculation: PASS")

    def test_stats_structure(self):
        """Test cache statistics structure"""
        stats = self.cache.get_stats()

        required_keys = [
            "total_entries",
            "cache_size_mb",
            "cache_size_bytes",
            "max_size_mb",
            "hits",
            "misses",
            "hit_rate_percent",
            "evictions",
            "ttl_hours",
            "created",
            "last_cleanup"
        ]

        for key in required_keys:
            assert key in stats, f"Missing key: {key}"

        assert isinstance(stats["total_entries"], int)
        assert isinstance(stats["cache_size_mb"], (int, float))
        assert isinstance(stats["hit_rate_percent"], (int, float))

        print("✅ Stats structure: PASS")

    def test_convenience_functions(self):
        """Test convenience functions"""
        test_text = "Extracted PDF text"

        # Cache using convenience function
        cache_text(str(self.test_file), test_text, cache_manager=self.cache)

        # Retrieve using convenience function
        cached = get_cached_text(str(self.test_file), cache_manager=self.cache)

        assert cached == test_text

        print("✅ Convenience functions: PASS")

    def test_invalidate_all(self):
        """Test invalidating all cache entries"""
        # Add entries in multiple namespaces
        self.cache.set(str(self.test_file), "text", namespace="text")
        self.cache.set(str(self.test_file), {"key": "value"}, namespace="metadata")

        # Verify they exist
        text_before = self.cache.get(str(self.test_file), namespace="text")
        meta_before = self.cache.get(str(self.test_file), namespace="metadata")
        assert text_before is not None, f"Text cache should exist before invalidate, got: {text_before}"
        assert meta_before is not None, f"Metadata cache should exist before invalidate, got: {meta_before}"

        # Invalidate all
        self.cache.invalidate_all()

        # Verify test file still exists
        assert self.test_file.exists(), f"Test file should not be deleted by cache invalidation: {self.test_file}"

        # Stats should be reset immediately after invalidate (before any get() calls)
        stats_after_invalidate = self.cache.get_stats()
        assert stats_after_invalidate["hits"] == 0, f"Hits should be 0 after invalidate, got: {stats_after_invalidate['hits']}"
        assert stats_after_invalidate["misses"] == 0, f"Misses should be 0 after invalidate, got: {stats_after_invalidate['misses']}"

        # Verify cache entries are gone
        text_after = self.cache.get(str(self.test_file), namespace="text")
        meta_after = self.cache.get(str(self.test_file), namespace="metadata")
        assert text_after is None, f"Text cache should be None after invalidate, got: {text_after}"
        assert meta_after is None, f"Metadata cache should be None after invalidate, got: {meta_after}"

        # After the get() calls, we should have 2 misses
        stats_final = self.cache.get_stats()
        assert stats_final["misses"] == 2, f"Should have 2 misses from get() calls, got: {stats_final['misses']}"

        print("✅ Invalidate all: PASS")


def run_all_tests():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("Cache Manager - Unit Tests")
    print("=" * 60 + "\n")

    test_suite = TestCacheManager()

    # Run tests
    tests = [
        test_suite.test_cache_initialization,
        test_suite.test_cache_set_and_get,
        test_suite.test_cache_miss,
        test_suite.test_cache_hit_statistics,
        test_suite.test_cache_invalidation,
        test_suite.test_different_namespaces,
        test_suite.test_file_hash_computation,
        test_suite.test_cache_size_calculation,
        test_suite.test_stats_structure,
        test_suite.test_convenience_functions,
        test_suite.test_invalidate_all,
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            test_suite.setup_method()
            test()
            test_suite.teardown_method()
            passed += 1
        except AssertionError as e:
            print(f"❌ {test.__name__}: FAILED")
            print(f"   Error: {e}")
            test_suite.teardown_method()
            failed += 1
        except Exception as e:
            print(f"❌ {test.__name__}: ERROR")
            print(f"   Error: {e}")
            test_suite.teardown_method()
            failed += 1

    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"Total: {passed + failed}")
    print("=" * 60 + "\n")

    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
