#!/bin/bash
# Test Performance Monitoring Hook
# This script demonstrates how the monitoring works

echo "=========================================="
echo "Testing Performance Monitoring Hook"
echo "=========================================="
echo ""

# Create a test file
TEST_FILE="/tmp/test_monitoring_$(date +%s).md"
echo "# Test File" > "$TEST_FILE"
echo "Some content here" >> "$TEST_FILE"

echo "1. Simulating Write operation..."
python3 .claude/scripts/perf_monitor_hook.py --tool=Write --file="$TEST_FILE"

echo ""
echo "2. Simulating Edit operation..."
python3 .claude/scripts/perf_monitor_hook.py --tool=Edit --file="$TEST_FILE"

echo ""
echo "3. Simulating another Write operation..."
python3 .claude/scripts/perf_monitor_hook.py --tool=Write --file="$TEST_FILE"

echo ""
echo "=========================================="
echo "4. Showing Monitoring Statistics:"
echo "=========================================="
python3 .claude/scripts/perf_monitor_hook.py --stats

echo ""
echo "✅ Test complete!"
echo ""
echo "Next steps:"
echo "1. Add monitoring hook to hooks.json"
echo "2. Perform actual file operations"
echo "3. Check stats: python3 .claude/scripts/perf_monitor_hook.py --stats"

# Clean up
rm -f "$TEST_FILE"
