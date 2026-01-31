#!/usr/bin/env python3
"""
Skill Chain - Orchestration of multiple skills with workflow control

This module provides advanced orchestration capabilities including:
- Sequential skill execution
- Conditional branching based on results
- Parallel execution where possible
- Rollback on failure
"""

import json
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum

from .skill_registry import SkillRegistry, SkillMetadata
from .skill_executor import SkillExecutor, ExecutionResult


class ChainStatus(Enum):
    """Status of a skill chain execution"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"


@dataclass
class ChainStep:
    """A single step in a skill chain"""
    step_id: str
    skill_id: str
    parameters: dict = field(default_factory=dict)
    condition: Optional[str] = None  # Conditional expression
    on_failure: str = "stop"  # stop, continue, rollback
    timeout: Optional[int] = None


@dataclass
class ChainResult:
    """Result of executing a skill chain"""
    chain_id: str
    status: ChainStatus
    steps_completed: int
    steps_total: int
    results: List[ExecutionResult] = field(default_factory=list)
    error: Optional[str] = None
    execution_time: float = 0.0

    def to_dict(self) -> dict:
        return {
            "chain_id": self.chain_id,
            "status": self.status.value,
            "steps_completed": self.steps_completed,
            "steps_total": self.steps_total,
            "results": [r.to_dict() for r in self.results],
            "error": self.error,
            "execution_time": self.execution_time
        }


class SkillChain:
    """
    Orchestrates execution of multiple skills in a controlled workflow.

    Supports:
    - Dependency-aware execution order
    - Conditional execution based on previous results
    - Error handling strategies (stop/continue/rollback)
    - Parallel execution for independent skills
    """

    def __init__(self, registry: Optional[SkillRegistry] = None,
                 executor: Optional[SkillExecutor] = None):
        """
        Initialize skill chain.

        Args:
            registry: SkillRegistry instance
            executor: SkillExecutor instance
        """
        self.registry = registry or SkillRegistry()
        self.executor = executor or SkillExecutor(self.registry)

    def execute_chain(self, chain_id: str,
                     steps: List[ChainStep],
                     context: Optional[dict] = None) -> ChainResult:
        """
        Execute a skill chain with the given steps.

        Args:
            chain_id: Unique identifier for this chain execution
            steps: List of ChainStep to execute in order
            context: Optional context dictionary for conditional evaluation

        Returns:
            ChainResult with execution details
        """
        import time

        start_time = time.time()
        context = context or {}
        results = []
        steps_completed = 0

        try:
            for step in steps:
                # Check conditional
                if step.condition and not self._evaluate_condition(
                    step.condition, context, results
                ):
                    continue  # Skip this step

                # Execute step
                result = self.executor.execute(
                    step.skill_id,
                    step.parameters,
                    timeout=step.timeout
                )
                results.append(result)
                steps_completed += 1

                # Update context with result
                context[f"{step.step_id}_result"] = result

                # Handle failure
                if not result.success:
                    if step.on_failure == "stop":
                        return ChainResult(
                            chain_id=chain_id,
                            status=ChainStatus.FAILED,
                            steps_completed=steps_completed,
                            steps_total=len(steps),
                            results=results,
                            error=f"Step {step.step_id} failed: {result.error}",
                            execution_time=time.time() - start_time
                        )
                    elif step.on_failure == "rollback":
                        self._rollback(results)
                        return ChainResult(
                            chain_id=chain_id,
                            status=ChainStatus.ROLLED_BACK,
                            steps_completed=steps_completed,
                            steps_total=len(steps),
                            results=results,
                            error=f"Step {step.step_id} failed, rolled back",
                            execution_time=time.time() - start_time
                        )
                    # else: continue to next step

            return ChainResult(
                chain_id=chain_id,
                status=ChainStatus.COMPLETED,
                steps_completed=steps_completed,
                steps_total=len(steps),
                results=results,
                execution_time=time.time() - start_time
            )

        except Exception as e:
            return ChainResult(
                chain_id=chain_id,
                status=ChainStatus.FAILED,
                steps_completed=steps_completed,
                steps_total=len(steps),
                results=results,
                error=str(e),
                execution_time=time.time() - start_time
            )

    def _evaluate_condition(self, condition: str,
                           context: dict,
                           results: List[ExecutionResult]) -> bool:
        """
        Evaluate a conditional expression.

        Supports simple expressions like:
        - "previous.success"  # True if previous step succeeded
        - "results[0].output.contains('verified')"  # Check output content
        """
        # Add results to context
        context["results"] = results
        context["previous"] = results[-1] if results else None

        try:
            # Safe evaluation - only allow specific operations
            if "." in condition:
                parts = condition.split(".")
                if len(parts) == 2 and parts[0] in context:
                    obj = context[parts[0]]
                    attr = parts[1]
                    if hasattr(obj, attr):
                        return getattr(obj, attr)
            return bool(eval(condition, {"__builtins__": {}}, context))
        except Exception:
            return False

    def _rollback(self, results: List[ExecutionResult]):
        """
        Rollback executed steps (placeholder).

        In production, this would:
        1. Call cleanup methods for each executed skill
        2. Revert any state changes
        3. Restore original state
        """
        # Placeholder: Log rollback
        print(f"Rolling back {len(results)} executed steps")

    def execute_parallel(self, skill_ids: List[str],
                        parameters_dict: Dict[str, dict]) -> Dict[str, ExecutionResult]:
        """
        Execute multiple skills in parallel (where independent).

        Args:
            skill_ids: List of skill IDs to execute
            parameters_dict: Parameters for each skill

        Returns:
            Dictionary mapping skill_id to ExecutionResult
        """
        import concurrent.futures

        results = {}

        # Filter to only independent skills (no dependencies)
        independent = [
            sid for sid in skill_ids
            if not self.registry.get_skill(sid).dependencies
        ]

        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
            futures = {
                executor.submit(
                    self.executor.execute,
                    skill_id,
                    parameters_dict.get(skill_id, {})
                ): skill_id
                for skill_id in independent
            }

            for future in concurrent.futures.as_completed(futures):
                skill_id = futures[future]
                try:
                    results[skill_id] = future.result()
                except Exception as e:
                    results[skill_id] = ExecutionResult(
                        skill_id=skill_id,
                        success=False,
                        error=str(e)
                    )

        return results

    def load_chain_from_config(self, config_path: str) -> tuple:
        """
        Load a skill chain from a configuration file.

        Args:
            config_path: Path to JSON/YAML config file

        Returns:
            Tuple of (chain_id, steps_list)
        """
        path = config_path.lower()

        if path.endswith('.json'):
            with open(config_path) as f:
                config = json.load(f)
        elif path.endswith(('.yaml', '.yml')):
            import yaml
            with open(config_path) as f:
                config = yaml.safe_load(f)
        else:
            raise ValueError("Config file must be JSON or YAML")

        chain_id = config.get("chain_id", "unnamed")
        steps_data = config.get("steps", [])

        steps = [
            ChainStep(
                step_id=step["step_id"],
                skill_id=step["skill_id"],
                parameters=step.get("parameters", {}),
                condition=step.get("condition"),
                on_failure=step.get("on_failure", "stop"),
                timeout=step.get("timeout")
            )
            for step in steps_data
        ]

        return chain_id, steps


def main():
    """CLI for skill chain operations"""
    import argparse

    parser = argparse.ArgumentParser(description="Skill Chain CLI")
    parser.add_argument("--config", metavar="FILE",
                       help="Execute chain from config file")
    parser.add_argument("--chain-id", default="cli-chain",
                       help="Chain ID for execution")
    parser.add_argument("--steps", type=json.loads,
                       help="JSON array of chain steps")
    parser.add_argument("--parallel", nargs="+", metavar="SKILL",
                       help="Execute skills in parallel")

    args = parser.parse_args()

    chain = SkillChain()

    if args.config:
        chain_id, steps = chain.load_chain_from_config(args.config)
        result = chain.execute_chain(chain_id, steps)
        print(json.dumps(result.to_dict(), indent=2))

    elif args.steps:
        steps = [
            ChainStep(**step_data)
            for step_data in args.steps
        ]
        result = chain.execute_chain(args.chain_id, steps)
        print(json.dumps(result.to_dict(), indent=2))

    elif args.parallel:
        results = chain.execute_parallel(args.parallel, {})
        print(json.dumps({
            k: v.to_dict() for k, v in results.items()
        }, indent=2))


if __name__ == "__main__":
    main()
