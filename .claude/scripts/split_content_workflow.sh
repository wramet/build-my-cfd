#!/bin/bash
# split_content_workflow.sh - Master workflow for split content generation
#
# Complete workflow with context chaining, syntax repair, and seam healing
#
# Usage: bash split_content_workflow.sh <day> "<topic>"
# Example: bash split_content_workflow.sh 01 "Governing Equations"

set -e

DAY_NUM=$1
DAY_TOPIC=$2
OUTPUT_DIR="daily_learning"

if [ -z "$DAY_NUM" ]; then
  echo "Usage: $0 <day> <topic>"
  echo "Example: $0 01 'Governing Equations'"
  exit 1
fi

DAY_FMT=$(printf "%02d" "$DAY_NUM")

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo "======================================"
echo "🚀 Split Content Generation Workflow"
echo "======================================"
echo "Day: $DAY_FMT"
echo "Topic: $DAY_TOPIC"
echo ""

PARTS_DIR="$OUTPUT_DIR/parts_day${DAY_FMT}"
FINAL_OUTPUT="$OUTPUT_DIR/Phase_01_Foundation_Theory/${DAY_FMT}.md"

# Stage 1: Generate Parts with Context Chaining
echo -e "${BLUE}[Stage 1/4]${NC} Generating 6 Parts with Context Chaining"
echo ""

python3 .claude/scripts/split_content_generation.py "$DAY_NUM" "$DAY_TOPIC" "$OUTPUT_DIR"

if [ $? -eq 0 ]; then
  echo -e "${GREEN}✅ Part generation complete${NC}"
else
  echo -e "${RED}❌ Part generation failed${NC}"
  exit 1
fi

# Stage 2: Raw Merge
echo -e "${BLUE}[Stage 2/4]${NC} Raw Merge of All Parts"
echo ""

cd "$PARTS_DIR"
bash merge.sh
cd - > /dev/null

echo -e "${GREEN}✅ Raw merge complete${NC}"
RAW_MERGED="$FINAL_OUTPUT"

# Stage 3: Syntax Repair
echo -e "${BLUE}[Stage 3/4]${NC} Syntax Repair"
echo ""

python3 .claude/scripts/repair_syntax.py "$RAW_MERGED" "${RAW_MERGED}.repaired"

if [ $? -eq 0 ]; then
  echo -e "${GREEN}✅ Syntax repair complete${NC}"
else
  echo -e "${YELLOW}⚠️  Syntax repair had issues, continuing...${NC}"
fi

REPAIRED_FILE="${RAW_MERGED}.repaired"

# Stage 4: Seam Healing (Dual-Mode)
echo -e "${BLUE}[Stage 4/4]${NC} Intelligent Seam Healing"
echo ""

python3 .claude/scripts/heal_seams.py "$REPAIRED_FILE" "$FINAL_OUTPUT"

if [ $? -eq 0 ]; then
  echo -e "${GREEN}✅ Seam healing complete${NC}"
else
  echo -e "${YELLOW}⚠️  Seam healing had issues, using repaired file${NC}"
  cp "$REPAIRED_FILE" "$FINAL_OUTPUT"
fi

# Cleanup intermediate files
echo ""
echo "Cleaning up intermediate files..."
rm -f "${RAW_MERGED}.repaired"
# rm -rf "$PARTS_DIR"  # Uncomment to delete parts directory

# Final Summary
echo ""
echo "======================================"
echo "✅ Workflow Complete!"
echo "======================================"
echo ""
echo "Output: $FINAL_OUTPUT"
echo "Line count: $(wc -l < $FINAL_OUTPUT)"
echo ""
echo "Intermediate files:"
echo "  Parts directory: $PARTS_DIR"
echo "  State report: ${REPAIRED_FILE}.state.json"
echo "  Healing report: ${FINAL_OUTPUT}.heal_report.json"
echo ""

# Verification
LINE_COUNT=$(wc -l < $FINAL_OUTPUT)
if [ "$LINE_COUNT" -ge 1900 ]; then
  echo -e "${GREEN}🎉 Target achieved: $LINE_COUNT lines (target: ≥1900)${NC}"
elif [ "$LINE_COUNT" -ge 1500 ]; then
  echo -e "${YELLOW}⚠️  Minimum met: $LINE_COUNT lines (target: ≥1900, min: ≥1500)${NC}"
else
  echo -e "${RED}❌ Below minimum: $LINE_COUNT lines (target: ≥1900, min: ≥1500)${NC}"
fi
