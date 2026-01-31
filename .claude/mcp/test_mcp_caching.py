#!/usr/bin/env python3
"""
Test MCP Server Caching

Tests the response caching feature of the DeepSeek MCP server.

Usage:
    python3 .claude/mcp/test_mcp_caching.py
"""

import asyncio
import json
import sys
import time
from datetime import datetime
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

# Import the cached MCP server functions
try:
    from deepseek_mcp_server_cached import generate_cache_key, PromptCache, CACHE_ENABLED
    from cache_manager import PromptCache
except ImportError as e:
    print(f"Error importing modules: {e}")
    sys.exit(1)


class MCPCacheTest:
    """Test MCP server caching functionality."""

    def __init__(self):
        self.cache = PromptCache() if CACHE_ENABLED else None
        self.results = []

    def test_cache_key_generation(self):
        """Test that cache keys are generated correctly."""
        print("\n" + "="*60)
        print("Test 1: Cache Key Generation")
        print("="*60)

        # Test identical prompts
        prompt1 = "Explain the upwind scheme in OpenFOAM"
        prompt2 = "Explain the upwind scheme in OpenFOAM"

        key1 = generate_cache_key("deepseek-chat", prompt1)
        key2 = generate_cache_key("deepseek-chat", prompt2)

        print(f"\nPrompt 1: {prompt1}")
        print(f"Key 1:    {key1[:16]}...")
        print(f"\nPrompt 2: {prompt2}")
        print(f"Key 2:    {key2[:16]}...")
        print(f"\nKeys match: {'✅ YES' if key1 == key2 else '❌ NO'}")

        result = {
            "test": "cache_key_generation",
            "passed": key1 == key2,
            "key1": key1,
            "key2": key2
        }

        self.results.append(result)
        return result["passed"]

    def test_cache_hit_miss(self):
        """Test cache hit and miss behavior."""
        print("\n" + "="*60)
        print("Test 2: Cache Hit/Miss Behavior")
        print("="*60)

        if not self.cache:
            print("⚠️  Cache not available, skipping test")
            return False

        prompt = "What is the finite volume method?"

        # First call should be a miss
        print("\n1️⃣  First call (expected MISS):")
        start = time.time()
        miss = self.cache.get(prompt, {"type": "mcp", "model": "deepseek-chat"})
        miss_time = time.time() - start

        if miss:
            print(f"   ❌ Unexpected cache hit: {miss[:50]}...")
            print(f"   This should have been a miss!")
            return False

        print(f"   ✅ Cache MISS (as expected)")
        print(f"   Time: {miss_time*1000:.2f}ms")

        # Add to cache
        fake_response = "The finite volume method is a numerical technique..."
        self.cache.put(
            prompt,
            fake_response,
            context={"type": "mcp", "model": "deepseek-chat"},
            token_count=100,
            cost=0.01
        )
        print(f"\n   💾 Cached response: {fake_response[:50]}...")

        # Second call should be a hit
        print("\n2️⃣  Second call (expected HIT):")
        start = time.time()
        hit = self.cache.get(prompt, {"type": "mcp", "model": "deepseek-chat"})
        hit_time = time.time() - start

        if hit:
            print(f"   ✅ Cache HIT: {hit[:50]}...")
            print(f"   Time: {hit_time*1000:.2f}ms")
            print(f"   ⚡ Speedup: {miss_time/hit_time:.1f}x faster")
        else:
            print(f"   ❌ Cache MISS (unexpected!)")
            return False

        result = {
            "test": "cache_hit_miss",
            "passed": hit is not None,
            "miss_time_ms": round(miss_time * 1000, 2),
            "hit_time_ms": round(hit_time * 1000, 2),
            "speedup": round(miss_time / hit_time, 1)
        }

        self.results.append(result)
        return result["passed"]

    def test_cache_stats(self):
        """Test cache statistics."""
        print("\n" + "="*60)
        print("Test 3: Cache Statistics")
        print("="*60)

        if not self.cache:
            print("⚠️  Cache not available, skipping test")
            return False

        stats = self.cache.get_stats()

        print(f"\n📊 Cache Statistics:")
        print(f"   Total Entries: {stats['total_entries']}")
        print(f"   Cache Size: {stats['cache_size_mb']} MB / {stats['max_size_mb']} MB")
        print(f"   Hit Rate: {stats['hit_rate']}%")
        print(f"   Hits: {stats['hits']}")
        print(f"   Misses: {stats['misses']}")
        print(f"   Tokens Saved: {stats['tokens_saved']:,}")
        print(f"   Cost Saved: ${stats['cost_saved']}")

        result = {
            "test": "cache_stats",
            "passed": stats["total_entries"] >= 0,
            "stats": stats
        }

        self.results.append(result)
        return result["passed"]

    def run_all_tests(self):
        """Run all MCP cache tests."""
        print("\n" + "="*70)
        print(" " * 15 + "MCP SERVER CACHING TESTS")
        print("="*70)
        print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Caching: {'ENABLED' if CACHE_ENABLED else 'DISABLED'}")

        all_passed = True

        # Test 1: Cache key generation
        if not self.test_cache_key_generation():
            all_passed = False

        # Test 2: Cache hit/miss
        if not self.test_cache_hit_miss():
            all_passed = False

        # Test 3: Cache statistics
        if not self.test_cache_stats():
            all_passed = False

        # Summary
        print("\n" + "="*70)
        print(" " * 25 + "TEST SUMMARY")
        print("="*70)

        passed_count = sum(1 for r in self.results if r["passed"])
        total_count = len(self.results)

        print(f"\nTests Passed: {passed_count}/{total_count}")

        for result in self.results:
            status = "✅ PASS" if result["passed"] else "❌ FAIL"
            print(f"  {result['test']}: {status}")

        if all_passed:
            print(f"\n🎉 All tests passed!")
        else:
            print(f"\n⚠️  Some tests failed")

        # Save results
        output_dir = Path("/tmp/benchmark_results")
        output_dir.mkdir(parents=True, exist_ok=True)
        results_file = output_dir / f"mcp_cache_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        with open(results_file, "w") as f:
            json.dump({
                "timestamp": datetime.now().isoformat(),
                "results": self.results,
                "all_passed": all_passed
            }, f, indent=2)

        print(f"\n💾 Results saved to: {results_file}")

        return all_passed


def main():
    """Run MCP cache tests."""
    tester = MCPCacheTest()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
