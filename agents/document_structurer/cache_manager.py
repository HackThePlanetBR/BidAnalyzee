#!/usr/bin/env python3
"""
Cache Manager for Document Structurer

Provides disk-based caching for PDF text extraction and metadata
to significantly reduce processing time for repeated analyses.

Features:
- File-based caching with automatic TTL expiration
- SHA256 hash-based cache keys (based on PDF content)
- Automatic cache invalidation on file changes
- Size limits and LRU eviction
- Statistics tracking (hit rate, size, entries)

Author: BidAnalyzee Team
Date: 2025-11-06
Version: 1.0.0
"""

import os
import json
import hashlib
import time
from typing import Any, Dict, Optional, List
from pathlib import Path
from datetime import datetime, timedelta
import shutil


class CacheManager:
    """
    Disk-based cache manager for PDF processing results.

    Cache Structure:
    .cache/
    ├── text/           # Extracted PDF text
    ├── metadata/       # Extracted metadata
    ├── ocr/           # OCR results
    └── stats.json     # Cache statistics
    """

    def __init__(
        self,
        cache_dir: str = ".cache",
        ttl_hours: int = 24,
        max_size_mb: int = 1000
    ):
        """
        Initialize cache manager.

        Args:
            cache_dir: Base directory for cache storage
            ttl_hours: Time-to-live in hours (default: 24)
            max_size_mb: Maximum cache size in MB (default: 1000)
        """
        self.cache_dir = Path(cache_dir)
        self.ttl_hours = ttl_hours
        self.max_size_bytes = max_size_mb * 1024 * 1024

        # Create cache subdirectories
        self.text_cache_dir = self.cache_dir / "text"
        self.metadata_cache_dir = self.cache_dir / "metadata"
        self.ocr_cache_dir = self.cache_dir / "ocr"
        self.stats_file = self.cache_dir / "stats.json"

        self._ensure_cache_dirs()
        self._load_stats()

    def _ensure_cache_dirs(self):
        """Create cache directories if they don't exist."""
        for dir_path in [
            self.cache_dir,
            self.text_cache_dir,
            self.metadata_cache_dir,
            self.ocr_cache_dir
        ]:
            dir_path.mkdir(parents=True, exist_ok=True)

    def _load_stats(self):
        """Load cache statistics from disk."""
        if self.stats_file.exists():
            try:
                with open(self.stats_file, 'r') as f:
                    self.stats = json.load(f)
            except (json.JSONDecodeError, IOError):
                self.stats = self._create_empty_stats()
        else:
            self.stats = self._create_empty_stats()

    def _create_empty_stats(self) -> Dict[str, Any]:
        """Create empty statistics structure."""
        return {
            "hits": 0,
            "misses": 0,
            "evictions": 0,
            "created": datetime.now().isoformat(),
            "last_cleanup": datetime.now().isoformat()
        }

    def _save_stats(self):
        """Save cache statistics to disk."""
        try:
            with open(self.stats_file, 'w') as f:
                json.dump(self.stats, f, indent=2)
        except IOError:
            pass  # Fail silently if can't write stats

    def _compute_file_hash(self, file_path: str) -> str:
        """
        Compute SHA256 hash of file content.

        Args:
            file_path: Path to file

        Returns:
            Hex digest of file hash
        """
        sha256 = hashlib.sha256()

        with open(file_path, 'rb') as f:
            # Read in chunks to handle large files
            while chunk := f.read(8192):
                sha256.update(chunk)

        return sha256.hexdigest()

    def _get_cache_key(self, file_path: str, namespace: str) -> str:
        """
        Generate cache key for a file.

        Args:
            file_path: Path to source file
            namespace: Cache namespace (text, metadata, ocr)

        Returns:
            Cache key (hash + extension)
        """
        file_hash = self._compute_file_hash(file_path)
        return f"{file_hash}.json"

    def _get_cache_path(self, file_path: str, namespace: str) -> Path:
        """
        Get cache file path for a source file.

        Args:
            file_path: Path to source file
            namespace: Cache namespace

        Returns:
            Path to cache file
        """
        cache_key = self._get_cache_key(file_path, namespace)

        if namespace == "text":
            return self.text_cache_dir / cache_key
        elif namespace == "metadata":
            return self.metadata_cache_dir / cache_key
        elif namespace == "ocr":
            return self.ocr_cache_dir / cache_key
        else:
            raise ValueError(f"Unknown namespace: {namespace}")

    def _is_expired(self, cache_path: Path) -> bool:
        """
        Check if cache entry is expired.

        Args:
            cache_path: Path to cache file

        Returns:
            True if expired, False otherwise
        """
        if not cache_path.exists():
            return True

        # Check file age
        mtime = cache_path.stat().st_mtime
        age_seconds = time.time() - mtime
        age_hours = age_seconds / 3600

        return age_hours > self.ttl_hours

    def get(self, file_path: str, namespace: str = "text") -> Optional[Any]:
        """
        Get cached data for a file.

        Args:
            file_path: Path to source file
            namespace: Cache namespace

        Returns:
            Cached data or None if not found/expired
        """
        cache_path = self._get_cache_path(file_path, namespace)

        # Check if exists and not expired
        if not cache_path.exists():
            self.stats["misses"] += 1
            self._save_stats()
            return None

        if self._is_expired(cache_path):
            # Remove expired entry
            cache_path.unlink()
            self.stats["misses"] += 1
            self._save_stats()
            return None

        # Load cached data
        try:
            with open(cache_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            self.stats["hits"] += 1
            self._save_stats()
            return data

        except (json.JSONDecodeError, IOError):
            # Corrupted cache entry
            cache_path.unlink()
            self.stats["misses"] += 1
            self._save_stats()
            return None

    def set(self, file_path: str, data: Any, namespace: str = "text"):
        """
        Cache data for a file.

        Args:
            file_path: Path to source file
            data: Data to cache (must be JSON-serializable)
            namespace: Cache namespace
        """
        cache_path = self._get_cache_path(file_path, namespace)

        # Ensure cache directory exists
        cache_path.parent.mkdir(parents=True, exist_ok=True)

        # Write cache data
        try:
            with open(cache_path, 'w', encoding='utf-8') as f:
                json.dump({
                    "data": data,
                    "cached_at": datetime.now().isoformat(),
                    "source_file": str(file_path)
                }, f, indent=2, ensure_ascii=False)

            # Check if we need to evict old entries
            self._enforce_size_limit()

        except (IOError, TypeError) as e:
            # If caching fails, just continue without cache
            pass

    def invalidate(self, file_path: str, namespace: str = "text"):
        """
        Invalidate cache entry for a file.

        Args:
            file_path: Path to source file
            namespace: Cache namespace
        """
        cache_path = self._get_cache_path(file_path, namespace)

        if cache_path.exists():
            cache_path.unlink()

    def invalidate_all(self, namespace: Optional[str] = None):
        """
        Invalidate all cache entries.

        Args:
            namespace: If provided, only clear this namespace
        """
        if namespace:
            # Clear specific namespace
            if namespace == "text":
                shutil.rmtree(self.text_cache_dir, ignore_errors=True)
                self.text_cache_dir.mkdir(exist_ok=True)
            elif namespace == "metadata":
                shutil.rmtree(self.metadata_cache_dir, ignore_errors=True)
                self.metadata_cache_dir.mkdir(exist_ok=True)
            elif namespace == "ocr":
                shutil.rmtree(self.ocr_cache_dir, ignore_errors=True)
                self.ocr_cache_dir.mkdir(exist_ok=True)
        else:
            # Clear all
            shutil.rmtree(self.cache_dir, ignore_errors=True)
            self._ensure_cache_dirs()
            self.stats = self._create_empty_stats()
            self._save_stats()

    def _get_cache_size(self) -> int:
        """
        Get total cache size in bytes.

        Returns:
            Total size in bytes
        """
        total_size = 0

        for cache_dir in [self.text_cache_dir, self.metadata_cache_dir, self.ocr_cache_dir]:
            if cache_dir.exists():
                for file_path in cache_dir.glob("*.json"):
                    total_size += file_path.stat().st_size

        return total_size

    def _enforce_size_limit(self):
        """Enforce maximum cache size by evicting oldest entries."""
        current_size = self._get_cache_size()

        if current_size <= self.max_size_bytes:
            return

        # Get all cache files sorted by modification time (oldest first)
        cache_files = []

        for cache_dir in [self.text_cache_dir, self.metadata_cache_dir, self.ocr_cache_dir]:
            if cache_dir.exists():
                for file_path in cache_dir.glob("*.json"):
                    cache_files.append((file_path, file_path.stat().st_mtime))

        cache_files.sort(key=lambda x: x[1])

        # Remove oldest files until under limit
        for file_path, _ in cache_files:
            if current_size <= self.max_size_bytes:
                break

            file_size = file_path.stat().st_size
            file_path.unlink()
            current_size -= file_size
            self.stats["evictions"] += 1

        self._save_stats()

    def cleanup_expired(self):
        """Remove all expired cache entries."""
        for cache_dir in [self.text_cache_dir, self.metadata_cache_dir, self.ocr_cache_dir]:
            if cache_dir.exists():
                for file_path in cache_dir.glob("*.json"):
                    if self._is_expired(file_path):
                        file_path.unlink()

        self.stats["last_cleanup"] = datetime.now().isoformat()
        self._save_stats()

    def get_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.

        Returns:
            Dictionary with cache statistics
        """
        total_entries = sum(
            1 for cache_dir in [self.text_cache_dir, self.metadata_cache_dir, self.ocr_cache_dir]
            if cache_dir.exists()
            for _ in cache_dir.glob("*.json")
        )

        cache_size_bytes = self._get_cache_size()
        cache_size_mb = cache_size_bytes / (1024 * 1024)

        total_requests = self.stats["hits"] + self.stats["misses"]
        hit_rate = (self.stats["hits"] / total_requests * 100) if total_requests > 0 else 0.0

        return {
            "total_entries": total_entries,
            "cache_size_mb": round(cache_size_mb, 2),
            "cache_size_bytes": cache_size_bytes,
            "max_size_mb": self.max_size_bytes / (1024 * 1024),
            "hits": self.stats["hits"],
            "misses": self.stats["misses"],
            "hit_rate_percent": round(hit_rate, 1),
            "evictions": self.stats["evictions"],
            "ttl_hours": self.ttl_hours,
            "created": self.stats["created"],
            "last_cleanup": self.stats["last_cleanup"]
        }


# Convenience functions

def get_cached_text(file_path: str, cache_manager: Optional[CacheManager] = None) -> Optional[str]:
    """
    Get cached extracted text for a PDF file.

    Args:
        file_path: Path to PDF file
        cache_manager: Cache manager instance (creates new if None)

    Returns:
        Cached text or None if not found
    """
    if cache_manager is None:
        cache_manager = CacheManager()

    cached_data = cache_manager.get(file_path, namespace="text")
    return cached_data["data"] if cached_data else None


def cache_text(file_path: str, text: str, cache_manager: Optional[CacheManager] = None):
    """
    Cache extracted text for a PDF file.

    Args:
        file_path: Path to PDF file
        text: Extracted text to cache
        cache_manager: Cache manager instance (creates new if None)
    """
    if cache_manager is None:
        cache_manager = CacheManager()

    cache_manager.set(file_path, text, namespace="text")


if __name__ == "__main__":
    # Example usage and status check
    print("=" * 60)
    print("Cache Manager - Status Check")
    print("=" * 60)

    cache = CacheManager()
    stats = cache.get_stats()

    print(f"\nCache Statistics:")
    print(f"  Total entries: {stats['total_entries']}")
    print(f"  Cache size: {stats['cache_size_mb']:.2f} MB / {stats['max_size_mb']:.0f} MB")
    print(f"  Hits: {stats['hits']}")
    print(f"  Misses: {stats['misses']}")
    print(f"  Hit rate: {stats['hit_rate_percent']:.1f}%")
    print(f"  Evictions: {stats['evictions']}")
    print(f"  TTL: {stats['ttl_hours']} hours")
    print(f"\nCache location: {cache.cache_dir.absolute()}")
    print("=" * 60)
