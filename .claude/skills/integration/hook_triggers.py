#!/usr/bin/env python3
"""
Hook-Skill Triggers - Event-based skill execution from hooks

This module enables hooks to trigger skills automatically at specific checkpoints.
"""

import os
import json
from typing import Dict, List, Optional, Any
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "orchestrator"))

from orchestrator.skill_registry import SkillRegistry
from orchestrator.skill_executor import SkillExecutor, ExecutionResult


class HookSkillTriggers:
    """
    Manages skill execution triggered by hook events.

    Hooks can trigger skills at specific checkpoints:
    - pre_edit: Before editing a file
    - post_write: After writing a file
    - pre_tool: Before using a tool
    - post_tool: After using a tool
    """

    def __init__(self, registry: Optional[SkillRegistry] = None,
                 executor: Optional[SkillExecutor] = None,
                 triggers_config: Optional[str] = None):
        """
        Initialize hook-skill triggers.

        Args:
            registry: SkillRegistry instance
            executor: SkillExecutor instance
            triggers_config: Path to triggers configuration file
        """
        self.registry = registry or SkillRegistry()
        self.executor = executor or SkillExecutor(self.registry)
        self.triggers: Dict[str, List[dict]] = {}

        if triggers_config and Path(triggers_config).exists():
            self.load_triggers(triggers_config)

    def load_triggers(self, config_path: str):
        """
        Load trigger configuration from JSON file.

        Args:
            config_path: Path to triggers JSON file
        """
        with open(config_path) as f:
            config = json.load(f)

        self.triggers = config.get("triggers", {})

    def handle_hook_event(self, hook_name: str, context: dict) -> List[ExecutionResult]:
        """
        Execute skills triggered by a hook event.

        Args:
            hook_name: Name of the hook event (pre_edit, post_write, etc.)
            context: Context dictionary with event data

        Returns:
            List of execution results
        """
        if hook_name not in self.triggers:
            return []

        trigger_configs = self.triggers[hook_name]
        results = []

        for trigger in trigger_configs:
            # Evaluate conditions
            if not self._evaluate_conditions(trigger.get("conditions", {}), context):
                continue

            # Execute the skill
            skill_id = trigger.get("skill")
            if not skill_id:
                continue

            # Build parameters from template
            parameters = self._build_parameters(
                trigger.get("parameters", {}),
                context
            )

            result = self.executor.execute(skill_id, parameters)
            results.append(result)

            # Check if we should stop on failure
            if not result.success and trigger.get("stop_on_failure", True):
                break

        return results

    def _evaluate_conditions(self, conditions: dict, context: dict) -> bool:
        """
        Evaluate trigger conditions.

        Supported conditions:
        - file_extension: Match file extension
        - file_pattern: Regex pattern on file path
        - has_context_key: Check if key exists in context
        - context_value_equals: Check if context value matches

        Args:
            conditions: Dictionary of conditions to evaluate
            context: Event context

        Returns:
            True if all conditions pass
        """
        for condition_type, condition_value in conditions.items():
            if condition_type == "file_extension":
                file_path = context.get("file_path", "")
                if not file_path.endswith(condition_value):
                    return False

            elif condition_type == "file_pattern":
                import re
                file_path = context.get("file_path", "")
                if not re.search(condition_value, file_path):
                    return False

            elif condition_type == "has_context_key":
                if condition_value not in context:
                    return False

            elif condition_type == "context_value_equals":
                key, value = condition_value
                if context.get(key) != value:
                    return False

        return True

    def _build_parameters(self, param_template: dict, context: dict) -> dict:
        """
        Build skill parameters from template using context.

        Supports variable substitution: {{variable_name}}

        Args:
            param_template: Parameter template with variables
            context: Event context

        Returns:
            Resolved parameters
        """
        import re

        def resolve_value(value):
            if isinstance(value, str):
                # Substitute {{var}} with context values
                def replacer(match):
                    var = match.group(1)
                    return str(context.get(var, match.group(0)))

                return re.sub(r'\{\{(\w+)\}\}', replacer, value)
            elif isinstance(value, dict):
                return {k: resolve_value(v) for k, v in value.items()}
            elif isinstance(value, list):
                return [resolve_value(v) for v in value]
            return value

        return resolve_value(param_template)

    def register_trigger(self, hook_name: str, skill_id: str,
                         parameters: dict = None,
                         conditions: dict = None,
                         stop_on_failure: bool = True):
        """
        Register a new trigger.

        Args:
            hook_name: Hook event name
            skill_id: Skill to execute
            parameters: Parameters for skill
            conditions: Conditions for triggering
            stop_on_failure: Whether to stop on skill failure
        """
        if hook_name not in self.triggers:
            self.triggers[hook_name] = []

        self.triggers[hook_name].append({
            "skill": skill_id,
            "parameters": parameters or {},
            "conditions": conditions or {},
            "stop_on_failure": stop_on_failure
        })

    def save_triggers(self, config_path: str):
        """
        Save triggers to configuration file.

        Args:
            config_path: Path to save configuration
        """
        config = {"triggers": self.triggers}

        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)


def main():
    """CLI for hook-skill trigger operations"""
    import argparse

    parser = argparse.ArgumentParser(description="Hook-Skill Triggers CLI")
    parser.add_argument("--trigger", nargs=2, metavar=("HOOK", "SKILL"),
                       help="Register a trigger for a hook event")
    parser.add_argument("--list", action="store_true",
                       help="List all registered triggers")
    parser.add_argument("--handle", metavar="HOOK",
                       help="Simulate handling a hook event")
    parser.add_argument("--context", type=json.loads,
                       help="Context data for event simulation")

    args = parser.parse_args()

    triggers = HookSkillTriggers()

    if args.trigger:
        hook, skill = args.trigger
        triggers.register_trigger(hook, skill)
        print(f"Registered trigger: {hook} -> {skill}")

    if args.list:
        print("\nRegistered Triggers:")
        for hook_name, trigger_list in triggers.triggers.items():
            print(f"\n  {hook_name}:")
            for trigger in trigger_list:
                print(f"    - {trigger['skill']}")

    if args.handle:
        context = args.context or {}
        results = triggers.handle_hook_event(args.handle, context)

        print(f"\nHandled hook event: {args.handle}")
        for result in results:
            status = "✅" if result.success else "❌"
            print(f"  {status} {result.skill_id} ({result.execution_time:.3f}s)")


if __name__ == "__main__":
    main()
