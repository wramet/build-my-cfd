#!/bin/bash
# verify_obsidian_syntax.sh
# Verify Markdown files for Obsidian MathJax/Mermaid compatibility
# Usage: bash verify_obsidian_syntax.sh <file.md>

set -e

FILE="$1"

if [ -z "$FILE" ]; then
    echo "Usage: $0 <file.md>"
    exit 1
fi

if [ ! -f "$FILE" ]; then
    echo "❌ File not found: $FILE"
    exit 1
fi

ERRORS=0
WARNINGS=0

echo "=== Obsidian Syntax Verification: $FILE ==="
echo ""

# Check 1: Code block balance
COUNT=$(awk '/```/{count++} END{print count}' "$FILE")
if [ -z "$COUNT" ]; then COUNT=0; fi
if [ $((COUNT % 2)) -ne 0 ]; then
    echo "❌ Code blocks unbalanced: $COUNT backticks (odd number)"
    ((ERRORS++))
else
    echo "✅ Code blocks balanced: $COUNT backticks"
fi

# Check 2: LaTeX-style delimiters (forbidden)
LATEX_OPEN=$(grep -c '\\\\\[' "$FILE" 2>/dev/null || true)
LATEX_CLOSE=$(grep -c '\\\\\]' "$FILE" 2>/dev/null || true)
LATEX_INLINE=$(grep -c '\\\\\(' "$FILE" 2>/dev/null || true)
LATEX_TOTAL=$((LATEX_OPEN + LATEX_CLOSE + LATEX_INLINE))
if [ "$LATEX_TOTAL" -gt 0 ]; then
    echo "❌ Found $LATEX_TOTAL LaTeX delimiter(s) - use \$ instead of \\(, and \$\$ instead of \\["
    ((ERRORS++))
else
    echo "✅ No LaTeX-style delimiters"
fi

# Check 3: Wrong vector notation (\bf instead of \mathbf{})
if grep -E '\\bf[^{]|\\bfs?{' "$FILE" > /dev/null 2>&1; then
    echo "❌ Wrong vector notation - use \\mathbf{} instead of \\bf"
    ((ERRORS++))
else
    echo "✅ Vector notation correct (using \\mathbf{})"
fi

# Check 4: File starts with day header
if head -1 "$FILE" | grep -q "^# Day [0-9]"; then
    echo "✅ File starts with day header"
elif head -3 "$FILE" | grep -q "^# Day [0-9]"; then
    echo "⚠️  File has artifacts before day header"
    ((WARNINGS++))
else
    echo "❌ File doesn't start with day header"
    ((ERRORS++))
fi

# Check 5: Mermaid pipe escaping (warn only)
MERMAID_PIPE=$(grep 'mermaid' "$FILE" -A20 2>/dev/null | grep -E '\[[^"]*\|[^"]*\]' | wc -l || echo "0")
if [ "$MERMAID_PIPE" -gt 0 ]; then
    echo "⚠️  Possible unescaped pipe in $MERMAID_PIPE Mermaid node(s)"
    ((WARNINGS++))
else
    echo "✅ Mermaid syntax clean"
fi

# Check 6: Nested LaTeX (forbidden)
if grep -E '\$\$.*\$[^$]' "$FILE" > /dev/null 2>&1; then
    echo "❌ Found nested math delimiters"
    ((ERRORS++))
else
    echo "✅ No nested math delimiters"
fi

# Check 7: Count correct math delimiters
OPEN_DOLLAR=$(grep -o '\$' "$FILE" | wc -l | tr -d ' ')
if [ $((OPEN_DOLLAR % 2)) -ne 0 ]; then
    echo "⚠️  Odd number of \$ signs - possible unclosed inline math"
    ((WARNINGS++))
fi

OPEN_DBL=$(grep -o '\$\$' "$FILE" | wc -l | tr -d ' ')
if [ $((OPEN_DBL % 2)) -ne 0 ]; then
    echo "❌ Odd number of \$\$ delimiters - unclosed block math"
    ((ERRORS++))
fi

# Summary
echo ""
echo "=== Summary ==="
if [ $ERRORS -eq 0 ] && [ $WARNINGS -eq 0 ]; then
    echo "✅ All syntax checks passed"
    exit 0
elif [ $ERRORS -eq 0 ]; then
    echo "⚠️  Passed with $WARNINGS warning(s)"
    exit 0
else
    echo "❌ Failed: $ERRORS error(s), $WARNINGS warning(s)"
    exit 1
fi
