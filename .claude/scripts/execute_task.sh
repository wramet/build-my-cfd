#!/bin/bash
#
# execute_task.sh - Execute a task from the R410A implementation task list
#
# Usage: ./execute_task.sh TASK_001
#

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Task file
TASK_FILE="$(dirname "$0")/../tasks/r410a_implementation.yaml"

# Check if task ID provided
if [ -z "$1" ]; then
    echo -e "${RED}❌ Error: Task ID required${NC}"
    echo "Usage: $0 TASK_001"
    exit 1
fi

TASK_ID="$1"

# Change to project root
cd "$(dirname "$0")/../.."

# Show task details
echo -e "${BLUE}📋 Task Details: $TASK_ID${NC}"
echo "================================"

# Use Python to extract task info
python3 - <<EOF
import sys
import yaml

try:
    with open('.claude/tasks/r410a_implementation.yaml', 'r') as f:
        data = yaml.safe_load(f)

    # Find the task
    for phase in data['phases']:
        for task in phase.get('tasks', []):
            if task.get('id') == '$TASK_ID':
                print(f"\nName: {task.get('name', 'Unnamed')}")
                print(f"Priority: {task.get('priority', 'medium')}")
                print(f"Effort: {task.get('effort', 'Not specified')}")
                print(f"Phase: {phase['name']}")

                if 'description' in task:
                    desc = task['description']
                    if isinstance(desc, str) and '\\n' in desc:
                        print(f"\nDescription:")
                        for line in desc.strip().split('\\n'):
                            print(f"  {line}")
                    else:
                        print(f"\nDescription: {desc}")

                if 'command' in task:
                    print(f"\n${GREEN}Command to execute:${NC}")
                    print(f"  {task['command']}")

                if 'verification' in task:
                    print(f"\n${YELLOW}Verification:${NC}")
                    verification = task['verification']
                    if isinstance(verification, str) and '\\n' in verification:
                        for line in verification.strip().split('\\n'):
                            print(f"  {line}")
                    else:
                        print(f"  {verification}")

                if 'checklist' in task:
                    print(f"\n${BLUE}Checklist:${NC}")
                    for item in task['checklist']:
                        print(f"  - [ ] {item}")

                sys.exit(0)

    print(f"${RED}Task not found: $TASK_ID${NC}", file=sys.stderr)
    sys.exit(1)

except Exception as e:
    print(f"${RED}Error: {e}${NC}", file=sys.stderr)
    sys.exit(1)
EOF

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Failed to load task${NC}"
    exit 1
fi

echo ""
echo "================================"

# Check if task has a command
TASK_COMMAND=$(python3 - <<EOF
import yaml
with open('.claude/tasks/r410a_implementation.yaml', 'r') as f:
    data = yaml.safe_load(f)
for phase in data['phases']:
    for task in phase.get('tasks', []):
        if task.get('id') == '$TASK_ID':
            print(task.get('command', ''))
            break
EOF
)

# Ask if user wants to execute
echo ""
echo -e "${YELLOW}Options:${NC}"
echo "  1) Execute command (if available)"
echo "  2) Mark as complete (skip command)"
echo "  3) Cancel"
echo ""
read -p "Choose option [1-3]: " choice

case $choice in
    1)
        if [ -n "$TASK_COMMAND" ]; then
            echo ""
            echo -e "${BLUE}Executing command...${NC}"
            echo "$ $TASK_COMMAND"
            echo ""

            # Execute the command
            eval "$TASK_COMMAND"

            if [ $? -eq 0 ]; then
                echo ""
                echo -e "${GREEN}✅ Command executed successfully${NC}"

                # Ask to mark as complete
                read -p "Mark task as complete? [y/N]: " mark_complete
                if [[ $mark_complete =~ ^[Yy]$ ]]; then
                    python3 .claude/scripts/task_manager.py complete "$TASK_ID"
                fi
            else
                echo ""
                echo -e "${RED}❌ Command failed${NC}"
                exit 1
            fi
        else
            echo -e "${YELLOW}⚠️  No command defined for this task${NC}"
            echo "You can mark it complete manually:"
            echo "  python3 .claude/scripts/task_manager.py complete $TASK_ID"
        fi
        ;;
    2)
        python3 .claude/scripts/task_manager.py complete "$TASK_ID"
        ;;
    3)
        echo -e "${YELLOW}Cancelled${NC}"
        exit 0
        ;;
    *)
        echo -e "${RED}Invalid option${NC}"
        exit 1
        ;;
esac

echo ""
echo -e "${GREEN}✅ Done!${NC}"
echo "Next steps:"
echo "  - View remaining tasks: python3 .claude/scripts/task_manager.py pending"
echo "  - Show next task: python3 .claude/scripts/task_manager.py show TASK_XXX"
