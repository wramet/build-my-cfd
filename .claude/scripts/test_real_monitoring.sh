#!/bin/bash
# Test Real Monitoring with Hooks
# This simulates what happens when you use Edit/Write tools

echo "=========================================="
echo "Testing Real Monitoring with Hooks"
echo "=========================================="
echo ""

# Create test directory
TEST_DIR="/tmp/monitoring_test_$(date +%s)"
mkdir -p "$TEST_DIR"

echo "📁 Test directory: $TEST_DIR"
echo ""

# Test 1: Write operation (triggers PostToolUse hook)
echo "1. Testing Write operation (PostToolUse hook)..."
TEST_FILE="$TEST_DIR/test.md"
cat > "$TEST_FILE" << 'EOF'
# Test Document

This is a test file for monitoring.

## Theory
Some equations here.

## Code
```cpp
int x = 5;
```
EOF

# The hook will be called automatically by Claude Code
# For this test, we call it manually
python3 .claude/scripts/perf_monitor_hook.py --tool=Write --file="$TEST_FILE" --action=post
echo ""

# Test 2: Edit operation (triggers PreToolUse hook)
echo "2. Testing Edit operation (PreToolUse hook)..."
# Modify the file
sed -i '' 's/int x = 5/int x = 10/' "$TEST_FILE"
python3 .claude/scripts/perf_monitor_hook.py --tool=Edit --file="$TEST_FILE" --action=pre
echo ""

# Test 3: Show statistics
echo "3. Showing monitoring statistics..."
python3 .claude/scripts/perf_monitor_hook.py --stats --limit=20
echo ""

# Show the events file
echo "4. Raw events log:"
if [ -f "/tmp/performance_monitor/events.jsonl" ]; then
    echo "Last 5 events:"
    tail -5 /tmp/performance_monitor/events.jsonl | python3 -m json.tool 2>/dev/null || tail -5 /tmp/performance_monitor/events.jsonl
else
    echo "No events logged yet"
fi

echo ""
echo "✅ Test complete!"
echo ""
echo "Summary:"
echo "  → Monitoring hooks are active"
echo "  → Every Edit/Write will be tracked"
echo "  → Check stats: python3 .claude/scripts/perf_monitor_hook.py --stats"

# Cleanup
rm -rf "$TEST_DIR"
