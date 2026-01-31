# Task Manager - Quick Reference

## Overview

The task manager helps track and execute the 27 tasks required for implementing R410A integration into the daily learning content.

## Commands

### List all tasks

```bash
python3 .claude/scripts/task_manager.py list
```

Shows all tasks with status, priority, and effort estimates.

### Show task details

```bash
python3 .claude/scripts/task_manager.py show TASK_001
```

Displays detailed information about a specific task including:
- Name, status, priority, effort
- Description
- Command to execute (if applicable)
- Verification steps
- Checklist items

### Show pending tasks only

```bash
python3 .claude/scripts/task_manager.py pending
```

Shows only incomplete tasks, filtering out completed ones.

### Show tasks in a phase

```bash
python3 .claude/scripts/task_manager.py phase PHASE_0
```

Shows all tasks within a specific phase.

### Mark task as complete

```bash
python3 .claude/scripts/task_manager.py complete TASK_001
```

Marks a task as completed and updates the task file.

### Interactive task execution

```bash
.claude/scripts/execute_task.sh TASK_001
```

Interactive script that:
1. Shows task details
2. Offers to execute the command (if available)
3. Offers to mark as complete

## Task Status Indicators

| Status | Emoji | Meaning |
|--------|-------|---------|
| pending | ⏸️ | Task not started |
| in_progress | 🔄 | Task currently being worked on |
| completed | ✅ | Task finished |
| failed | ❌ | Task failed |
| blocked | 🔒 | Task blocked by dependencies |

## Priority Indicators

| Priority | Emoji | Description |
|----------|-------|-------------|
| critical | 🔴 | Must be done immediately |
| high | 🟠 | Should be done soon |
| medium | 🟡 | Normal priority |
| low | 🟢 | Can be deferred |

## Phase Structure

| Phase | Name | Tasks | Effort |
|-------|------|-------|--------|
| PHASE_0 | Preparation | 2 | 35 min |
| PHASE_1 | Pipeline Fixes | 6 | 2.5 hours |
| PHASE_2 | Content Gen - Phase 1 | 4 | 4.5 hours |
| PHASE_3 | Content Gen - Phase 2 | 4 | 3.5 hours |
| PHASE_4 | Content Gen - Phase 3 | 3 | 15 hours |
| PHASE_5 | Content Gen - Phase 4 | 3 | 16 hours |
| PHASE_6 | Content Gen - Phases 5-6 | 2 | 7 hours |
| PHASE_7 | Validation & Documentation | 3 | 8 hours |

## Typical Workflow

1. **Start each session:**
   ```bash
   python3 .claude/scripts/task_manager.py pending
   ```
   See what tasks remain.

2. **Pick a task:**
   ```bash
   python3 .claude/scripts/task_manager.py show TASK_XXX
   ```
   Review task details.

3. **Execute the task:**
   ```bash
   .claude/scripts/execute_task.sh TASK_XXX
   ```
   Follow the interactive prompts.

4. **Mark as complete:**
   The execute script offers to mark complete, or you can:
   ```bash
   python3 .claude/scripts/task_manager.py complete TASK_XXX
   ```

5. **Repeat** until all tasks in current phase are done.

## Quick Start

First time using the task manager? Start here:

```bash
# 1. See all pending tasks
python3 .claude/scripts/task_manager.py pending

# 2. Review the first critical task
python3 .claude/scripts/task_manager.py show TASK_001

# 3. Execute it interactively
.claude/scripts/execute_task.sh TASK_001
```

## Files

- **Task list:** `.claude/tasks/r410a_implementation.yaml`
- **Task manager:** `.claude/scripts/task_manager.py`
- **Execution helper:** `.claude/scripts/execute_task.sh`

## Help

Show all available commands:

```bash
python3 .claude/scripts/task_manager.py --help
```

## Progress Tracking

Track overall progress:

```bash
# Show all tasks with completion status
python3 .claude/scripts/task_manager.py list

# Count completed tasks
grep -c "status: completed" .claude/tasks/r410a_implementation.yaml

# Show only pending work
python3 .claude/scripts/task_manager.py pending
```

## Tips

1. **Work sequentially through phases** - Complete all tasks in PHASE_0 before moving to PHASE_1
2. **Use execute_task.sh** - It provides the best interactive experience
3. **Check dependencies** - Some phases depend on previous phases being complete
4. **Update estimates** - If effort estimates are wrong, update them in the YAML file

## Troubleshooting

### Task not found
- Check the task ID format (TASK_001, TASK_002, etc.)
- Run `python3 .claude/scripts/task_manager.py list` to see all valid IDs

### YAML syntax error
- Run: `python3 -c "import yaml; yaml.safe_load(open('.claude/tasks/r410a_implementation.yaml'))"`
- Fix any syntax errors in the YAML file

### Permission denied on execute_task.sh
- Run: `chmod +x .claude/scripts/execute_task.sh`

---

**Last Updated:** 2026-01-30
**Total Tasks:** 27
**Estimated Effort:** ~57 hours
