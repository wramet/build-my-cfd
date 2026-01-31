#!/usr/bin/env python3
"""
Skill Executor - Skill execution engine with caching and monitoring

This module provides the core skill execution capabilities including:
- Skill invocation with timeout handling
- Result caching for performance
- Execution metrics tracking
- Chain execution for multiple skills
"""

import os
import json
import time
import hashlib
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from datetime import datetime
from collections import OrderedDict

from .skill_registry import SkillRegistry, SkillMetadata


@dataclass
class ExecutionResult:
    """Result from a skill execution"""
    skill_id: str
    success: bool
    output: Optional[str] = None
    error: Optional[str] = None
    execution_time: float = 0.0
    cached: bool = False
    timestamp: str = ""

    def to_dict(self) -> dict:
        return {
            "skill_id": self.skill_id,
            "success": self.success,
            "output": self.output,
            "error": self.error,
            "execution_time": self.execution_time,
            "cached": self.cached,
            "timestamp": self.timestamp
        }


class SkillCache:
    """
    LRU cache for skill execution results.

    Implements size-based and time-based eviction.
    """

    def __init__(self, max_size: int = 100, ttl: int = 3600):
        """
        Initialize cache.

        Args:
            max_size: Maximum number of cached results
            ttl: Time-to-live in seconds (default: 1 hour)
        """
        self.cache: OrderedDict[str, ExecutionResult] = OrderedDict()
        self.max_size = max_size
        self.ttl = ttl

    def _generate_key(self, skill_id: str, parameters: dict) -> str:
        """Generate cache key from skill ID and parameters"""
        param_str = json.dumps(parameters, sort_keys=True)
        return f"{skill_id}:{hashlib.md5(param_str.encode()).hexdigest()}"

    def get(self, skill_id: str, parameters: dict) -> Optional[ExecutionResult]:
        """Get cached result if available and not expired"""
        key = self._generate_key(skill_id, parameters)

        if key not in self.cache:
            return None

        result = self.cache[key]

        # Check TTL
        cache_time = datetime.fromisoformat(result.timestamp)
        age = (datetime.now() - cache_time).total_seconds()

        if age > self.ttl:
            del self.cache[key]
            return None

        # Move to end (LRU)
        self.cache.move_to_end(key)
        return result

    def set(self, skill_id: str, parameters: dict, result: ExecutionResult):
        """Cache a result"""
        key = self._generate_key(skill_id, parameters)

        # Evict oldest if at capacity
        if len(self.cache) >= self.max_size and key not in self.cache:
            self.cache.popitem(last=False)

        self.cache[key] = result
        self.cache.move_to_end(key)

    def clear(self):
        """Clear all cached results"""
        self.cache.clear()

    def stats(self) -> dict:
        """Get cache statistics"""
        return {
            "size": len(self.cache),
            "max_size": self.max_size,
            "ttl": self.ttl
        }


class SkillMetrics:
    """
    Track skill execution metrics.
    """

    def __init__(self):
        self.executions: Dict[str, List[Dict]] = {}
        self.start_times: Dict[str, float] = {}

    def start_execution(self, skill_id: str):
        """Mark the start of a skill execution"""
        self.start_times[skill_id] = time.time()

    def end_execution(self, skill_id: str, success: bool, error: Optional[str] = None):
        """Record the end of a skill execution"""
        if skill_id not in self.start_times:
            return

        execution_time = time.time() - self.start_times[skill_id]
        del self.start_times[skill_id]

        if skill_id not in self.executions:
            self.executions[skill_id] = []

        self.executions[skill_id].append({
            "timestamp": datetime.now().isoformat(),
            "execution_time": execution_time,
            "success": success,
            "error": error
        })

    def get_stats(self, skill_id: str) -> dict:
        """Get statistics for a specific skill"""
        if skill_id not in self.executions:
            return {
                "total_executions": 0,
                "success_rate": 0.0,
                "avg_time": 0.0
            }

        executions = self.executions[skill_id]
        successful = sum(1 for e in executions if e["success"])
        total_time = sum(e["execution_time"] for e in executions)

        return {
            "total_executions": len(executions),
            "successful": successful,
            "failed": len(executions) - successful,
            "success_rate": successful / len(executions) if executions else 0.0,
            "avg_time": total_time / len(executions) if executions else 0.0,
            "total_time": total_time
        }

    def get_all_stats(self) -> dict:
        """Get statistics for all skills"""
        return {
            skill_id: self.get_stats(skill_id)
            for skill_id in self.executions.keys()
        }


class SkillExecutor:
    """
    Manages skill execution with caching, timeouts, and metrics.

    This is the main execution engine for the skill orchestration system.
    """

    def __init__(self, registry: Optional[SkillRegistry] = None,
                 cache_enabled: bool = True,
                 default_timeout: int = 30):
        """
        Initialize skill executor.

        Args:
            registry: SkillRegistry instance (creates new if None)
            cache_enabled: Whether to enable result caching
            default_timeout: Default execution timeout in seconds
        """
        self.registry = registry or SkillRegistry()
        self.cache = SkillCache() if cache_enabled else None
        self.metrics = SkillMetrics()
        self.default_timeout = default_timeout

    def execute(self, skill_id: str, parameters: dict,
                timeout: Optional[int] = None,
                use_cache: bool = True) -> ExecutionResult:
        """
        Execute a single skill.

        Args:
            skill_id: ID of skill to execute
            parameters: Parameters to pass to skill
            timeout: Execution timeout (uses default if None)
            use_cache: Whether to check cache first

        Returns:
            ExecutionResult with output or error
        """
        # Get skill metadata
        skill = self.registry.get_skill(skill_id)
        if not skill:
            return ExecutionResult(
                skill_id=skill_id,
                success=False,
                error=f"Skill not found: {skill_id}",
                timestamp=datetime.now().isoformat()
            )

        # Check cache
        if use_cache and self.cache and skill.cacheable:
            cached = self.cache.get(skill_id, parameters)
            if cached:
                return ExecutionResult(
                    skill_id=skill_id,
                    success=cached.success,
                    output=cached.output,
                    error=cached.error,
                    execution_time=0.0,
                    cached=True,
                    timestamp=datetime.now().isoformat()
                )

        # Execute with timeout
        timeout = timeout or skill.execution_timeout or self.default_timeout

        self.metrics.start_execution(skill_id)
        start_time = time.time()

        try:
            # For now, return a placeholder result
            # In production, this would invoke the actual skill
            result = self._invoke_skill(skill, parameters)

            execution_time = time.time() - start_time

            exec_result = ExecutionResult(
                skill_id=skill_id,
                success=True,
                output=result,
                execution_time=execution_time,
                cached=False,
                timestamp=datetime.now().isoformat()
            )

            self.metrics.end_execution(skill_id, True)

            # Cache result
            if self.cache and skill.cacheable:
                self.cache.set(skill_id, parameters, exec_result)

            return exec_result

        except TimeoutError as e:
            execution_time = time.time() - start_time
            self.metrics.end_execution(skill_id, False, str(e))

            return ExecutionResult(
                skill_id=skill_id,
                success=False,
                error=f"Execution timeout after {timeout}s",
                execution_time=execution_time,
                cached=False,
                timestamp=datetime.now().isoformat()
            )

        except Exception as e:
            execution_time = time.time() - start_time
            self.metrics.end_execution(skill_id, False, str(e))

            return ExecutionResult(
                skill_id=skill_id,
                success=False,
                error=str(e),
                execution_time=execution_time,
                cached=False,
                timestamp=datetime.now().isoformat()
            )

    def _invoke_skill(self, skill: SkillMetadata, parameters: dict) -> str:
        """
        Invoke a skill (placeholder implementation).

        In production, this would:
        1. Load the skill's SKILL.md
        2. Parse the workflow
        3. Execute the skill logic
        4. Return the result

        For now, returns a descriptive placeholder.
        """
        # Placeholder: Simulate skill invocation
        return f"Executed {skill.name} with parameters: {json.dumps(parameters, indent=2)}"

    def execute_chain(self, skill_ids: List[str],
                     parameters_dict: Optional[Dict[str, dict]] = None,
                     stop_on_error: bool = True) -> List[ExecutionResult]:
        """
        Execute multiple skills in dependency order.

        Args:
            skill_ids: List of skill IDs to execute
            parameters_dict: Optional dict mapping skill_id -> parameters
            stop_on_error: Whether to stop on first error

        Returns:
            List of ExecutionResults in execution order
        """
        # Resolve dependencies
        ordered = self.registry.resolve_dependencies(skill_ids)
        parameters_dict = parameters_dict or {}

        results = []
        for skill_id in ordered:
            params = parameters_dict.get(skill_id, {})
            result = self.execute(skill_id, params)
            results.append(result)

            if not result.success and stop_on_error:
                break

        return results

    def get_cache_stats(self) -> dict:
        """Get cache statistics"""
        if self.cache:
            return self.cache.stats()
        return {"enabled": False}

    def get_metrics(self) -> dict:
        """Get execution metrics"""
        return self.metrics.get_all_stats()


def main():
    """CLI for skill executor operations"""
    import argparse

    parser = argparse.ArgumentParser(description="Skill Executor CLI")
    parser.add_argument("--execute", metavar="SKILL", help="Execute a skill")
    parser.add_argument("--params", type=json.loads,
                       help="JSON parameters for skill")
    parser.add_argument("--chain", nargs="+", metavar="SKILL",
                       help="Execute multiple skills in order")
    parser.add_argument("--cache-stats", action="store_true",
                       help="Show cache statistics")
    parser.add_argument("--metrics", action="store_true",
                       help="Show execution metrics")

    args = parser.parse_args()

    executor = SkillExecutor()

    if args.execute:
        params = args.params or {}
        result = executor.execute(args.execute, params)

        print(f"\nExecution Result:")
        print(f"  Skill: {result.skill_id}")
        print(f"  Success: {result.success}")
        print(f"  Cached: {result.cached}")
        print(f"  Time: {result.execution_time:.3f}s")

        if result.success:
            print(f"  Output:\n{result.output}")
        else:
            print(f"  Error: {result.error}")

    if args.chain:
        results = executor.execute_chain(args.chain)

        print(f"\nChain Execution Results:")
        for result in results:
            status = "✅" if result.success else "❌"
            print(f"  {status} {result.skill_id} ({result.execution_time:.3f}s)")

    if args.cache_stats:
        stats = executor.get_cache_stats()
        print(f"\nCache Stats: {json.dumps(stats, indent=2)}")

    if args.metrics:
        metrics = executor.get_metrics()
        print(f"\nExecution Metrics:")
        print(json.dumps(metrics, indent=2))


if __name__ == "__main__":
    main()
