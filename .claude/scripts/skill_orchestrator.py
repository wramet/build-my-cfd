#!/usr/bin/env python3
"""
Skill Orchestrator - Main orchestration script

This is the main entry point for skill orchestration, providing a unified
interface for all skill operations.

Usage:
    python3 skill_orchestrator.py list
    python3 skill_orchestrator.py execute <skill_id> [--params JSON]
    python3 skill_orchestrator.py workflow <name> [--context JSON]
    python3 skill_orchestrator.py verify <file_path>
"""

import json
import sys
from pathlib import Path

# Add skills directory to path
skills_dir = Path(__file__).parent.parent / "skills"
sys.path.insert(0, str(skills_dir))

from orchestrator import SkillRegistry, SkillExecutor, SkillChain
from integration import ScriptSkillAPI, VerificationAssistant


def print_header(title: str):
    """Print a formatted header"""
    print(f"\n{'=' * 60}")
    print(f"  {title}")
    print('=' * 60)


def list_skills(args):
    """List all available skills"""
    registry = SkillRegistry()
    registry.discover_skills()

    print_header("Skill Registry")

    # Group by type
    from orchestrator.skill_registry import SkillType

    for skill_type in SkillType:
        skills = registry.get_skills_by_type(skill_type)
        if skills:
            print(f"\n### {skill_type.value.title()} Skills ({len(skills)})")
            for skill in sorted(skills, key=lambda s: s.skill_id):
                print(f"\n  {skill.skill_id}")
                print(f"    Name: {skill.name}")
                print(f"    Description: {skill.description}")
                if skill.invocation:
                    print(f"    Usage: {skill.invocation}")
                if skill.dependencies:
                    print(f"    Dependencies: {', '.join(skill.dependencies)}")

    print(f"\nTotal skills: {len(registry.skills)}")


def execute_skill(args):
    """Execute a single skill"""
    import json

    api = ScriptSkillAPI()

    params = json.loads(args.params) if args.params else {}
    result = api.execute_skill(args.skill_id, params)

    print_header(f"Skill Execution: {args.skill_id}")

    status_icon = "✅" if result.success else "❌"
    print(f"\nStatus: {status_icon}")
    print(f"Cached: {result.cached}")
    print(f"Execution Time: {result.execution_time:.3f}s")

    if result.success:
        if result.output:
            print(f"\nOutput:\n{result.output}")
    else:
        print(f"\nError: {result.error}")


def execute_workflow(args):
    """Execute a predefined workflow"""
    import json

    api = ScriptSkillAPI()
    context = json.loads(args.context) if args.context else {}

    print_header(f"Workflow: {args.workflow}")

    results = api.execute_workflow(args.workflow, context)

    if args.workflow == "verification":
        print(results.get("report", ""))
    else:
        print(json.dumps(results, indent=2))


def run_verification(args):
    """Run verification gates on a file"""
    assistant = VerificationAssistant()

    context = {
        "file_path": args.file,
        "content": Path(args.file).read_text()
    }

    print_header("Verification Gates")

    results = assistant.execute_all_gates(context, stop_on_failure=False)
    report = assistant.generate_report(results)

    print(report)

    # Save report
    if args.output:
        Path(args.output).write_text(report)
        print(f"\nReport saved to: {args.output}")


def show_stats(args):
    """Show execution statistics"""
    api = ScriptSkillAPI()

    print_header("Skill Orchestration Statistics")

    # Cache stats
    cache_stats = api.get_cache_stats()
    print("\n📦 Cache Statistics:")
    print(json.dumps(cache_stats, indent=2))

    # Execution metrics
    metrics = api.get_metrics()
    print("\n📊 Execution Metrics:")
    if metrics:
        for skill_id, skill_metrics in metrics.items():
            print(f"\n  {skill_id}:")
            print(f"    Total: {skill_metrics['total_executions']}")
            print(f"    Success Rate: {skill_metrics['success_rate']:.1%}")
            print(f"    Avg Time: {skill_metrics['avg_time']:.3f}s")


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Skill Orchestrator - Unified skill management interface",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # List all skills
  python3 skill_orchestrator.py list

  # Execute a skill
  python3 skill_orchestrator.py execute source-first --params '{"action": "extract"}'

  # Run a workflow
  python3 skill_orchestrator.py workflow content_creation --context '{"topic": "heat_transfer"}'

  # Verify a file
  python3 skill_orchestrator.py verify daily_learning/01.md

  # Show statistics
  python3 skill_orchestrator.py stats
        """
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # List command
    subparsers.add_parser("list", help="List all available skills")

    # Execute command
    exec_parser = subparsers.add_parser("execute", help="Execute a single skill")
    exec_parser.add_argument("skill_id", help="ID of skill to execute")
    exec_parser.add_argument("--params", help="JSON parameters for skill")

    # Workflow command
    wf_parser = subparsers.add_parser("workflow", help="Execute a predefined workflow")
    wf_parser.add_argument("workflow", help="Workflow name (content_creation, verification, diagram)")
    wf_parser.add_argument("--context", help="JSON context for workflow")

    # Verify command
    verify_parser = subparsers.add_parser("verify", help="Run verification gates")
    verify_parser.add_argument("file", help="File to verify")
    verify_parser.add_argument("--output", "-o", help="Save report to file")

    # Stats command
    subparsers.add_parser("stats", help="Show execution statistics")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 0

    # Execute command
    commands = {
        "list": list_skills,
        "execute": execute_skill,
        "workflow": execute_workflow,
        "verify": run_verification,
        "stats": show_stats
    }

    command_func = commands.get(args.command)
    if command_func:
        try:
            command_func(args)
        except KeyboardInterrupt:
            print("\n\n⚠️  Operation cancelled by user")
            return 130
        except Exception as e:
            print(f"\n❌ Error: {e}")
            import traceback
            traceback.print_exc()
            return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
