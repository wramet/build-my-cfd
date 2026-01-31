#!/usr/bin/env python3
"""
Task Manager for R410A Implementation

This script manages the task list for implementing R410A integration
into the daily learning content.

Usage:
    python3 task_manager.py list              # List all tasks
    python3 task_manager.py show TASK_001     # Show task details
    python3 task_manager.py complete TASK_001 # Mark task complete
    python3 task_manager.py pending           # Show pending tasks only
    python3 task_manager.py phase PHASE_1     # Show tasks in phase
"""

import argparse
import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent
TASK_FILE = PROJECT_ROOT / ".claude" / "tasks" / "r410a_implementation.yaml"


def load_tasks():
    """Load tasks from YAML file."""
    try:
        import yaml
        with open(TASK_FILE, 'r') as f:
            return yaml.safe_load(f)
    except ImportError:
        print("❌ PyYAML not installed. Install with: pip install pyyaml")
        sys.exit(1)
    except FileNotFoundError:
        print(f"❌ Task file not found: {TASK_FILE}")
        sys.exit(1)


def save_tasks(data):
    """Save tasks to YAML file."""
    try:
        import yaml
        with open(TASK_FILE, 'w') as f:
            yaml.dump(data, f, default_flow_style=False, sort_keys=False)
        return True
    except Exception as e:
        print(f"❌ Failed to save tasks: {e}")
        return False


def format_status(status):
    """Format status with emoji."""
    status_map = {
        "pending": "⏸️",
        "in_progress": "🔄",
        "completed": "✅",
        "failed": "❌",
        "blocked": "🔒"
    }
    return status_map.get(status, "❓")


def format_priority(priority):
    """Format priority with emoji."""
    priority_map = {
        "critical": "🔴",
        "high": "🟠",
        "medium": "🟡",
        "low": "🟢"
    }
    return priority_map.get(priority, "⚪")


def list_all_tasks(data, show_all=True):
    """List all tasks with status."""
    print("\n" + "=" * 80)
    print(f"📋 R410A Implementation Task List")
    print(f"Project: {data['project']}")
    print(f"Status: {format_status(data['status'])} {data['status']}")
    print("=" * 80 + "\n")

    total_tasks = 0
    completed_tasks = 0
    pending_tasks = 0

    for phase in data['phases']:
        phase_status = format_status(phase['status'])
        phase_name = phase['name']
        phase_id = phase['id']

        # Count tasks in this phase
        phase_tasks = [t for t in phase.get('tasks', [])]
        phase_completed = sum(1 for t in phase_tasks if t.get('status') == 'completed')
        phase_total = len(phase_tasks)

        # Skip phases with no tasks if not showing all
        if not show_all and phase_total == 0:
            continue

        print(f"\n{phase_status} {phase_id}: {phase_name} ({phase_completed}/{phase_total} tasks)")
        print("-" * 80)

        for task in phase_tasks:
            task_status = task.get('status', 'pending')
            task_id = task.get('id', 'UNKNOWN')
            task_name = task.get('name', 'Unnamed task')
            task_priority = task.get('priority', 'medium')

            # Filter out completed tasks if not showing all
            if not show_all and task_status == 'completed':
                continue

            total_tasks += 1
            if task_status == 'completed':
                completed_tasks += 1
            else:
                pending_tasks += 1

            priority_emoji = format_priority(task_priority)
            status_emoji = format_status(task_status)

            print(f"  {status_emoji} {priority_emoji} {task_id}: {task_name}")

            # Show effort if available
            if 'effort' in task:
                print(f"      ⏱️  Effort: {task['effort']}")

    # Summary
    print("\n" + "=" * 80)
    print(f"📊 Summary: {completed_tasks}/{total_tasks} tasks completed ({pending_tasks} pending)")
    print("=" * 80 + "\n")

    return total_tasks, completed_tasks, pending_tasks


def show_task_details(data, task_id):
    """Show detailed information about a specific task."""
    # Find the task
    task = None
    phase = None

    for p in data['phases']:
        for t in p.get('tasks', []):
            if t.get('id') == task_id:
                task = t
                phase = p
                break
        if task:
            break

    if not task:
        print(f"❌ Task not found: {task_id}")
        return False

    # Display task details
    print("\n" + "=" * 80)
    print(f"📋 Task Details: {task_id}")
    print("=" * 80 + "\n")

    print(f"Name:        {task.get('name', 'Unnamed')}")
    print(f"Status:      {format_status(task.get('status', 'pending'))} {task.get('status', 'pending')}")
    print(f"Priority:    {format_priority(task.get('priority', 'medium'))} {task.get('priority', 'medium')}")
    print(f"Effort:      {task.get('effort', 'Not specified')}")
    print(f"Phase:       {phase['id']} - {phase['name']}")

    if 'description' in task:
        desc = task['description']
        if isinstance(desc, str) and '\n' in desc:
            print(f"\nDescription:\n{desc}")
        else:
            print(f"\nDescription: {desc}")

    if 'command' in task:
        print(f"\nCommand to execute:")
        print(f"  {task['command']}")

    if 'verification' in task:
        print(f"\nVerification:")
        verification = task['verification']
        if isinstance(verification, str) and '\n' in verification:
            for line in verification.strip().split('\n'):
                print(f"  {line}")
        else:
            print(f"  {verification}")

    if 'file' in task:
        print(f"\nFile to modify: {task['file']}")

    if 'files' in task:
        print(f"\nFiles to create:")
        for f in task['files']:
            print(f"  - {f}")

    if 'checklist' in task:
        print(f"\nChecklist:")
        for item in task['checklist']:
            print(f"  - [ ] {item}")

    print("\n" + "=" * 80 + "\n")

    return True


def complete_task(data, task_id):
    """Mark a task as complete."""
    # Find and update the task
    for phase in data['phases']:
        for task in phase.get('tasks', []):
            if task.get('id') == task_id:
                old_status = task.get('status', 'pending')
                task['status'] = 'completed'
                print(f"✅ Marked {task_id} as complete (was: {old_status})")

                # Save the updated data
                if save_tasks(data):
                    return True
                else:
                    # Revert status if save failed
                    task['status'] = old_status
                    return False

    print(f"❌ Task not found: {task_id}")
    return False


def show_pending_only(data):
    """Show only pending tasks."""
    print("\n" + "=" * 80)
    print(f"📋 Pending Tasks Only")
    print("=" * 80 + "\n")

    pending_count = 0

    for phase in data['phases']:
        phase_tasks = [t for t in phase.get('tasks', []) if t.get('status') != 'completed']

        if not phase_tasks:
            continue

        print(f"\n{phase['id']}: {phase['name']}")

        for task in phase_tasks:
            task_id = task.get('id', 'UNKNOWN')
            task_name = task.get('name', 'Unnamed task')
            task_priority = task.get('priority', 'medium')

            pending_count += 1

            priority_emoji = format_priority(task_priority)

            print(f"  {priority_emoji} {task_id}: {task_name}")

            if 'effort' in task:
                print(f"      ⏱️  Effort: {task['effort']}")

    print("\n" + "=" * 80)
    print(f"📊 Total pending tasks: {pending_count}")
    print("=" * 80 + "\n")


def show_phase_tasks(data, phase_id):
    """Show tasks for a specific phase."""
    # Find the phase
    phase = None
    for p in data['phases']:
        if p['id'] == phase_id:
            phase = p
            break

    if not phase:
        print(f"❌ Phase not found: {phase_id}")
        return False

    print("\n" + "=" * 80)
    print(f"📋 Phase: {phase_id} - {phase['name']}")
    print(f"Status: {format_status(phase['status'])} {phase['status']}")
    print("=" * 80 + "\n")

    if 'description' in phase:
        print(f"Description: {phase['description']}\n")

    if 'depends_on' in phase:
        print(f"Depends on: {phase['depends_on']}\n")

    tasks = phase.get('tasks', [])
    completed = sum(1 for t in tasks if t.get('status') == 'completed')

    print(f"Tasks: {completed}/{len(tasks)} completed\n")

    for task in tasks:
        task_id = task.get('id', 'UNKNOWN')
        task_name = task.get('name', 'Unnamed task')
        task_status = task.get('status', 'pending')
        task_priority = task.get('priority', 'medium')

        priority_emoji = format_priority(task_priority)
        status_emoji = format_status(task_status)

        print(f"{status_emoji} {priority_emoji} {task_id}: {task_name}")

        if 'effort' in task:
            print(f"      ⏱️  {task['effort']}")

    print("\n" + "=" * 80 + "\n")

    return True


def main():
    parser = argparse.ArgumentParser(
        description="Task Manager for R410A Implementation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 task_manager.py list              # List all tasks
  python3 task_manager.py show TASK_001     # Show task details
  python3 task_manager.py complete TASK_001 # Mark task complete
  python3 task_manager.py pending           # Show pending tasks only
  python3 task_manager.py phase PHASE_1     # Show tasks in phase
        """
    )

    parser.add_argument(
        'action',
        choices=['list', 'show', 'complete', 'pending', 'phase'],
        help='Action to perform'
    )

    parser.add_argument(
        'target',
        nargs='?',
        help='Task ID or Phase ID (for show/complete/phase actions)'
    )

    parser.add_argument(
        '-a', '--all',
        action='store_true',
        help='Show all tasks including completed'
    )

    args = parser.parse_args()

    # Load task data
    data = load_tasks()

    # Execute action
    if args.action == 'list':
        list_all_tasks(data, show_all=args.all)
    elif args.action == 'show':
        if not args.target:
            print("❌ Task ID required for 'show' action")
            print("Usage: python3 task_manager.py show TASK_001")
            sys.exit(1)
        show_task_details(data, args.target)
    elif args.action == 'complete':
        if not args.target:
            print("❌ Task ID required for 'complete' action")
            print("Usage: python3 task_manager.py complete TASK_001")
            sys.exit(1)
        complete_task(data, args.target)
    elif args.action == 'pending':
        show_pending_only(data)
    elif args.action == 'phase':
        if not args.target:
            print("❌ Phase ID required for 'phase' action")
            print("Usage: python3 task_manager.py phase PHASE_1")
            sys.exit(1)
        show_phase_tasks(data, args.target)


if __name__ == '__main__':
    main()
