#!/usr/bin/env python3
"""
Prompt Cache Manager for CFD Engine Development Project

Implements LRU cache for prompt prefixes to reduce token costs by ~90%.
"""

import hashlib
import json
import os
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, Optional, Tuple


class PromptCache:
    """LRU cache for prompt prefixes."""

    def __init__(self, cache_dir: str = "/tmp/prompt_cache", max_size_mb: int = 100):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.max_size_bytes = max_size_mb * 1024 * 1024
        self.index_file = self.cache_dir / "cache_index.json"
        self.index = self._load_index()
        self.stats_file = self.cache_dir / "cache_stats.json"
        self.stats = self._load_stats()

    def _load_index(self) -> Dict[str, Any]:
        """Load cache index from disk."""
        if self.index_file.exists():
            with open(self.index_file, "r") as f:
                return json.load(f)
        return {"entries": {}, "last_cleanup": 0}

    def _save_index(self):
        """Save cache index to disk."""
        with open(self.index_file, "w") as f:
            json.dump(self.index, f, indent=2)

    def _load_stats(self) -> Dict[str, Any]:
        """Load cache statistics from disk."""
        if self.stats_file.exists():
            with open(self.stats_file, "r") as f:
                return json.load(f)
        return {
            "hits": 0,
            "misses": 0,
            "tokens_saved": 0,
            "cost_saved": 0.0,
            "created_at": datetime.now().isoformat()
        }

    def _save_stats(self):
        """Save cache statistics to disk."""
        with open(self.stats_file, "w") as f:
            json.dump(self.stats, f, indent=2)

    def _generate_key(self, prompt: str, context: Optional[Dict] = None) -> str:
        """Generate cache key from prompt and context."""
        key_data = prompt[:1000]  # First 1000 chars for prefix matching
        if context:
            key_data += json.dumps(context, sort_keys=True)
        return hashlib.sha256(key_data.encode()).hexdigest()

    def _get_entry_size(self, entry: Dict) -> int:
        """Calculate size of a cache entry in bytes."""
        return len(json.dumps(entry).encode())

    def _cleanup(self):
        """Remove old/low-value entries if cache is too large."""
        current_time = time.time()

        # Skip if we've cleaned up recently
        if current_time - self.index["last_cleanup"] < 300:
            return

        # Calculate total size
        total_size = sum(self._get_entry_size(e) for e in self.index["entries"].values())

        if total_size > self.max_size_bytes:
            # Sort by last_accessed and remove oldest entries
            entries = sorted(
                self.index["entries"].items(),
                key=lambda x: x[1].get("last_accessed", 0)
            )

            # Remove entries until we're under 80% of max size
            target_size = self.max_size_bytes * 0.8
            for key, entry in entries:
                if total_size <= target_size:
                    break

                # Remove entry
                entry_path = self.cache_dir / f"{key}.json"
                if entry_path.exists():
                    entry_path.unlink()

                total_size -= self._get_entry_size(entry)
                del self.index["entries"][key]

        self.index["last_cleanup"] = current_time
        self._save_index()

    def get(self, prompt: str, context: Optional[Dict] = None) -> Optional[str]:
        """Get cached response if available."""
        key = self._generate_key(prompt, context)

        if key in self.index["entries"]:
            entry = self.index["entries"][key]
            entry_path = self.cache_dir / f"{key}.json"

            if entry_path.exists():
                # Check if entry is stale (older than 24 hours)
                age = datetime.now() - datetime.fromisoformat(entry["created_at"])
                if age > timedelta(hours=24):
                    # Remove stale entry
                    entry_path.unlink()
                    del self.index["entries"][key]
                    self._save_index()
                    self.stats["misses"] += 1
                    self._save_stats()
                    return None

                # Update access time
                entry["last_accessed"] = time.time()
                entry["hit_count"] += 1
                self._save_index()

                # Update stats
                self.stats["hits"] += 1
                self.stats["tokens_saved"] += entry.get("token_count", 0)
                self.stats["cost_saved"] += entry.get("cost", 0)
                self._save_stats()

                with open(entry_path, "r") as f:
                    cached = json.load(f)
                    return cached.get("response")

        self.stats["misses"] += 1
        self._save_stats()
        return None

    def put(self, prompt: str, response: str, context: Optional[Dict] = None,
            token_count: int = 0, cost: float = 0.0):
        """Cache a response."""
        key = self._generate_key(prompt, context)

        entry = {
            "created_at": datetime.now().isoformat(),
            "last_accessed": time.time(),
            "hit_count": 0,
            "token_count": token_count,
            "cost": cost,
            "response": response
        }

        # Save to disk
        entry_path = self.cache_dir / f"{key}.json"
        with open(entry_path, "w") as f:
            json.dump(entry, f, indent=2)

        # Update index
        self.index["entries"][key] = {
            "created_at": entry["created_at"],
            "last_accessed": entry["last_accessed"],
            "hit_count": 0,
            "token_count": token_count,
            "cost": cost
        }

        # Cleanup if needed
        self._cleanup()

    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        total_requests = self.stats["hits"] + self.stats["misses"]
        hit_rate = self.stats["hits"] / total_requests if total_requests > 0 else 0

        # Calculate current cache size
        cache_size = sum(
            self.cache_dir.joinpath(f"{k}.json").stat().st_size
            for k in self.index["entries"].keys()
            if self.cache_dir.joinpath(f"{k}.json").exists()
        )

        return {
            "total_entries": len(self.index["entries"]),
            "cache_size_mb": round(cache_size / (1024 * 1024), 2),
            "max_size_mb": round(self.max_size_bytes / (1024 * 1024), 2),
            "hit_rate": round(hit_rate * 100, 1),
            "hits": self.stats["hits"],
            "misses": self.stats["misses"],
            "tokens_saved": self.stats["tokens_saved"],
            "cost_saved": round(self.stats["cost_saved"], 2),
            "created_at": self.stats["created_at"]
        }

    def clear(self):
        """Clear all cache entries."""
        for entry_file in self.cache_dir.glob("*.json"):
            if entry_file.name not in ["cache_index.json", "cache_stats.json"]:
                entry_file.unlink()

        self.index = {"entries": {}, "last_cleanup": 0}
        self._save_index()
        self.stats = {
            "hits": 0,
            "misses": 0,
            "tokens_saved": 0,
            "cost_saved": 0.0,
            "created_at": datetime.now().isoformat()
        }
        self._save_stats()


def main():
    """CLI for cache management."""
    import argparse

    parser = argparse.ArgumentParser(description="Prompt Cache Manager")
    parser.add_argument("--stats", action="store_true", help="Show cache statistics")
    parser.add_argument("--clear", action="store_true", help="Clear cache")
    parser.add_argument("--cache-dir", default="/tmp/prompt_cache", help="Cache directory")
    parser.add_argument("--max-size-mb", type=int, default=100, help="Maximum cache size in MB")

    args = parser.parse_args()

    cache = PromptCache(cache_dir=args.cache_dir, max_size_mb=args.max_size_mb)

    if args.stats:
        stats = cache.get_stats()
        print("Cache Statistics:")
        print(f"- Total Entries: {stats['total_entries']}")
        print(f"- Cache Size: {stats['cache_size_mb']} MB / {stats['max_size_mb']} MB")
        print(f"- Hit Rate: {stats['hit_rate']}%")
        print(f"- Hits: {stats['hits']}")
        print(f"- Misses: {stats['misses']}")
        print(f"- Tokens Saved: {stats['tokens_saved']:,}")
        print(f"- Cost Saved: ${stats['cost_saved']}")

    elif args.clear:
        cache.clear()
        print("Cache cleared successfully.")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
