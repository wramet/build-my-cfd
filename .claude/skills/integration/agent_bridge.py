#!/usr/bin/env python3
"""
Agent-Skill Bridge - Interface between agents and skill execution

This module enables agents to request and execute skills as part of their workflows.
"""

import os
import json
from typing import Dict, List, Optional, Any
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "orchestrator"))

from orchestrator.skill_registry import SkillRegistry, SkillType, SkillMetadata
from orchestrator.skill_executor import SkillExecutor, ExecutionResult


class AgentSkillBridge:
    """
    Bridge interface between agents and the skill orchestration system.

    Enables agents to:
    - Request appropriate skills for their task
    - Execute skills with parameters
    - Get results and handle errors
    """

    def __init__(self, registry: Optional[SkillRegistry] = None,
                 executor: Optional[SkillExecutor] = None):
        self.registry = registry or SkillRegistry()
        self.executor = executor or SkillExecutor(self.registry)

    def request_skills(self, task_type: str,
                      context: Optional[dict] = None) -> List[SkillMetadata]:
        """
        Get appropriate skills for a given task type.

        Task types:
        - "content_creation": Skills for generating content
        - "verification": Skills for verification tasks
        - "diagram": Skills for creating diagrams
        - "coding": Skills for C++ implementation
        - "debugging": Skills for debugging workflows
        - "git": Skills for git operations

        Args:
            task_type: Type of task being performed
            context: Additional context for skill selection

        Returns:
            List of appropriate skill metadata
        """
        task_skill_map = {
            "content_creation": ["content-creation", "create-module", "walkthrough"],
            "verification": ["source-first", "systematic_debugging"],
            "diagram": ["mermaid_expert"],
            "coding": ["cpp_pro"],
            "debugging": ["systematic_debugging"],
            "git": ["git-operations"],
            "qa": ["qa"],
            "scientific": ["scientific_skills"],
            "claude_code": ["claude_code_guide"]
        }

        skill_ids = task_skill_map.get(task_type, [])
        skills = []

        for skill_id in skill_ids:
            skill = self.registry.get_skill(skill_id)
            if skill:
                skills.append(skill)

        return skills

    def execute_skill(self, skill_id: str,
                     parameters: dict,
                     timeout: Optional[int] = None) -> ExecutionResult:
        """
        Execute a skill and return the result.

        Args:
            skill_id: ID of skill to execute
            parameters: Parameters to pass to skill
            timeout: Optional timeout override

        Returns:
            ExecutionResult
        """
        return self.executor.execute(skill_id, parameters, timeout=timeout)

    def execute_task_workflow(self, task_type: str,
                             task_data: dict,
                             context: Optional[dict] = None) -> Dict[str, ExecutionResult]:
        """
        Execute a complete workflow for a task type.

        Automatically selects and executes appropriate skills in order.

        Args:
            task_type: Type of task (content_creation, verification, etc.)
            task_data: Task-specific data
            context: Additional context

        Returns:
            Dictionary mapping skill_id to ExecutionResult
        """
        skills = self.request_skills(task_type, context)
        results = {}

        # Resolve dependencies and execute in order
        skill_ids = [s.skill_id for s in skills]
        ordered = self.registry.resolve_dependencies(skill_ids)

        for skill_id in ordered:
            # Get skill-specific parameters from task_data
            skill_params = task_data.get(skill_id, {})

            # Add common context
            skill_params.update({
                "task_type": task_type,
                "context": context or {}
            })

            result = self.execute_skill(skill_id, skill_params)
            results[skill_id] = result

            # Stop on failure for critical skills
            if not result.success:
                skill = self.registry.get_skill(skill_id)
                if skill and skill.requires_source_first:
                    break

        return results

    def get_skill_help(self, skill_id: str) -> Optional[str]:
        """
        Get help text for a specific skill.

        Args:
            skill_id: ID of skill

        Returns:
            Help text or None if skill not found
        """
        skill = self.registry.get_skill(skill_id)
        if not skill:
            return None

        help_text = f"""
# {skill.name}

**Type:** {skill.skill_type.value}
**ID:** {skill_id}

{skill.description}

"""
        if skill.invocation:
            help_text += f"**Usage:** `{skill.invocation}`\n\n"

        if skill.dependencies:
            help_text += f"**Dependencies:** {', '.join(skill.dependencies)}\n\n"

        if skill.tags:
            help_text += f"**Tags:** {', '.join(skill.tags)}\n\n"

        return help_text


def main():
    """CLI for agent-skill bridge operations"""
    import argparse

    parser = argparse.ArgumentParser(description="Agent-Skill Bridge CLI")
    parser.add_argument("--request", metavar="TASK_TYPE",
                       help="Request skills for a task type")
    parser.add_argument("--execute", metavar="SKILL_ID",
                       help="Execute a specific skill")
    parser.add_argument("--params", type=json.loads,
                       help="Parameters for skill execution")
    parser.add_argument("--workflow", metavar="TASK_TYPE",
                       help="Execute complete workflow for task type")
    parser.add_argument("--task-data", type=json.loads,
                       help="Task data for workflow execution")
    parser.add_argument("--help-skill", metavar="SKILL_ID",
                       help="Get help for a skill")

    args = parser.parse_args()

    bridge = AgentSkillBridge()

    if args.request:
        skills = bridge.request_skills(args.request)
        print(f"\nSkills for task '{args.request}':")
        for skill in skills:
            print(f"  - {skill.skill_id}: {skill.name}")

    if args.execute:
        params = args.params or {}
        result = bridge.execute_skill(args.execute, params)
        print(f"\nExecution Result:")
        print(f"  Success: {result.success}")
        if result.success:
            print(f"  Output: {result.output}")
        else:
            print(f"  Error: {result.error}")
        print(f"  Time: {result.execution_time:.3f}s")

    if args.workflow:
        task_data = args.task_data or {}
        results = bridge.execute_task_workflow(args.workflow, task_data)

        print(f"\nWorkflow Results for '{args.workflow}':")
        for skill_id, result in results.items():
            status = "✅" if result.success else "❌"
            print(f"  {status} {skill_id} ({result.execution_time:.3f}s)")

    if args.help_skill:
        help_text = bridge.get_skill_help(args.help_skill)
        if help_text:
            print(help_text)
        else:
            print(f"Skill not found: {args.help_skill}")


if __name__ == "__main__":
    main()
