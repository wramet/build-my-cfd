#!/usr/bin/env python3
"""
Script API - Programmatic access to skills from scripts

This module provides a clean API for scripts to execute skills
and retrieve results.
"""

import json
import sys
from typing import Dict, List, Optional, Any
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "orchestrator"))

from orchestrator.skill_registry import SkillRegistry
from orchestrator.skill_executor import SkillExecutor, ExecutionResult
from orchestrator.skill_chain import SkillChain, ChainStep


class ScriptSkillAPI:
    """
    Programmatic interface for script-skill integration.

    Provides:
    - Batch skill execution
    - Result retrieval
    - Simple workflow orchestration
    """

    def __init__(self, skills_dir: str = ".claude/skills"):
        """
        Initialize script API.

        Args:
            skills_dir: Path to skills directory
        """
        self.registry = SkillRegistry(skills_dir)
        self.executor = SkillExecutor(self.registry)
        self.chain = SkillChain(self.registry, self.executor)
        self._execution_history: List[ExecutionResult] = []

    def execute_skills(self, skill_ids: List[str],
                      parameters_dict: Optional[Dict[str, dict]] = None,
                      parallel: bool = False) -> Dict[str, ExecutionResult]:
        """
        Execute multiple skills.

        Args:
            skill_ids: List of skill IDs to execute
            parameters_dict: Optional dict mapping skill_id -> parameters
            parallel: Whether to execute independent skills in parallel

        Returns:
            Dictionary mapping skill_id to ExecutionResult
        """
        parameters_dict = parameters_dict or {}

        if parallel:
            # Execute independent skills in parallel
            results = self.chain.execute_parallel(skill_ids, parameters_dict)
        else:
            # Execute in dependency order
            results = {}
            ordered = self.registry.resolve_dependencies(skill_ids)

            for skill_id in ordered:
                params = parameters_dict.get(skill_id, {})
                result = self.executor.execute(skill_id, params)
                results[skill_id] = result
                self._execution_history.append(result)

        return results

    def execute_skill(self, skill_id: str,
                     parameters: Optional[dict] = None) -> ExecutionResult:
        """
        Execute a single skill.

        Args:
            skill_id: ID of skill to execute
            parameters: Parameters for skill execution

        Returns:
            ExecutionResult
        """
        params = parameters or {}
        result = self.executor.execute(skill_id, params)
        self._execution_history.append(result)
        return result

    def get_result(self, execution_id: Optional[str] = None,
                   index: int = -1) -> Optional[ExecutionResult]:
        """
        Get an execution result from history.

        Args:
            execution_id: Optional ID to filter by
            index: Index in history (default: last result)

        Returns:
            ExecutionResult or None
        """
        if execution_id:
            for result in self._execution_history:
                if result.skill_id == execution_id:
                    return result
            return None

        if self._execution_history:
            return self._execution_history[index]
        return None

    def list_skills(self, skill_type: Optional[str] = None) -> List[dict]:
        """
        List available skills.

        Args:
            skill_type: Optional filter by skill type

        Returns:
            List of skill metadata dictionaries
        """
        if skill_type:
            from skill_registry import SkillType
            skills = self.registry.get_skills_by_type(SkillType(skill_type))
        else:
            skills = self.registry.list_skills()

        return [s.to_dict() for s in skills]

    def get_cache_stats(self) -> dict:
        """Get cache statistics"""
        return self.executor.get_cache_stats()

    def get_metrics(self) -> dict:
        """Get execution metrics"""
        return self.executor.get_metrics()

    def clear_cache(self):
        """Clear the skill execution cache"""
        if self.executor.cache:
            self.executor.cache.clear()

    def execute_workflow(self, workflow_name: str,
                        context: Optional[dict] = None) -> Dict[str, Any]:
        """
        Execute a predefined workflow.

        Workflows:
        - "content_creation": Full content generation workflow
        - "verification": Verification gate workflow
        - "diagram": Diagram generation workflow

        Args:
            workflow_name: Name of workflow to execute
            context: Workflow context data

        Returns:
            Workflow execution results
        """
        context = context or {}
        results = {}

        if workflow_name == "content_creation":
            # Content creation workflow
            skills = ["source-first", "scientific_skills", "mermaid_expert"]
            results = self.execute_skills(skills, {
                "source-first": {"action": "extract", **context},
                "scientific_skills": {"format": "latex", **context},
                "mermaid_expert": {"validate": True, **context}
            })

        elif workflow_name == "verification":
            # Verification workflow
            from .verification_assistant import VerificationAssistant
            assistant = VerificationAssistant(self.registry, self.executor)
            gate_results = assistant.execute_all_gates(context)
            results = {
                "gates": [r.to_dict() for r in gate_results],
                "report": assistant.generate_report(gate_results)
            }

        elif workflow_name == "diagram":
            # Diagram generation workflow
            results = self.execute_skill("mermaid_expert", {
                "diagram_type": context.get("type", "flowchart"),
                "topic": context.get("topic")
            })

        return results


def main():
    """CLI for script API operations"""
    import argparse

    parser = argparse.ArgumentParser(description="Script API CLI")
    parser.add_argument("--execute", metavar="SKILL_ID",
                       help="Execute a single skill")
    parser.add_argument("--params", type=json.loads,
                       help="Parameters for skill execution")
    parser.add_argument("--batch", nargs="+", metavar="SKILL_ID",
                       help="Execute multiple skills")
    parser.add_argument("--parallel", action="store_true",
                       help="Execute independent skills in parallel")
    parser.add_argument("--workflow", metavar="NAME",
                       help="Execute a predefined workflow")
    parser.add_argument("--context", type=json.loads,
                       help="Context for workflow execution")
    parser.add_argument("--list", action="store_true",
                       help="List available skills")
    parser.add_argument("--cache-stats", action="store_true",
                       help="Show cache statistics")
    parser.add_argument("--metrics", action="store_true",
                       help="Show execution metrics")

    args = parser.parse_args()

    api = ScriptSkillAPI()

    if args.execute:
        params = args.params or {}
        result = api.execute_skill(args.execute, params)

        print(f"\nExecution Result:")
        print(f"  Skill: {result.skill_id}")
        print(f"  Success: {result.success}")
        print(f"  Time: {result.execution_time:.3f}s")
        print(f"  Cached: {result.cached}")

        if result.success:
            if result.output:
                print(f"\n  Output:\n{result.output}")
        else:
            print(f"  Error: {result.error}")

    if args.batch:
        results = api.execute_skills(args.batch, parallel=args.parallel)

        print(f"\nBatch Execution Results:")
        for skill_id, result in results.items():
            status = "✅" if result.success else "❌"
            print(f"  {status} {skill_id} ({result.execution_time:.3f}s)")

    if args.workflow:
        context = args.context or {}
        results = api.execute_workflow(args.workflow, context)

        print(f"\nWorkflow '{args.workflow}' Results:")
        print(json.dumps(results, indent=2))

    if args.list:
        skills = api.list_skills()
        print(f"\nAvailable Skills ({len(skills)}):")
        for skill in skills:
            print(f"\n  {skill['skill_id']}: {skill['name']}")
            print(f"    Type: {skill['skill_type']}")
            print(f"    Description: {skill['description']}")

    if args.cache_stats:
        stats = api.get_cache_stats()
        print(f"\nCache Statistics:")
        print(json.dumps(stats, indent=2))

    if args.metrics:
        metrics = api.get_metrics()
        print(f"\nExecution Metrics:")
        print(json.dumps(metrics, indent=2))


if __name__ == "__main__":
    main()
