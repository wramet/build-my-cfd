#!/bin/bash
# run_content_workflow.sh
# Complete workflow for creating daily content with integrated Python wrapper

set -e

DAY_NUM=$1
DAY_TOPIC=$2

if [ -z "$DAY_NUM" ]; then
  echo "Usage: $0 <DAY_NUMBER> <TOPIC>"
  echo "Example: $0 05 'Spatial Discretization Schemes'"
  exit 1
fi

DAY_FMT=$(printf "%02d" "$DAY_NUM")

echo "======================================"
echo "📋 Daily Content Creation Workflow"
echo "======================================"
echo "Day: $DAY_FMT"
echo "Topic: $DAY_TOPIC"
echo ""

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Stage 1: Research (GLM-4.7 via Claude)
echo -e "${BLUE}[Stage 1/6]${NC} Extract Ground Truth (GLM-4.7 via Claude)"
echo "Please ask Claude to:"
echo "  1. Use WebSearch to find latest OpenFOAM documentation"
echo "  2. Extract class hierarchy from source code"
echo "  3. Extract mathematical formulas with operators"
echo "  4. Output: /tmp/verified_facts_day${DAY_FMT}.json"
echo ""
read -p "Press Enter after Claude completes Stage 1..."

# Verify ground truth exists
if [ ! -f "/tmp/verified_facts_day${DAY_FMT}.json" ]; then
  echo -e "${RED}❌ Error: /tmp/verified_facts_day${DAY_FMT}.json not found${NC}"
  exit 1
fi
echo -e "${GREEN}✅ Ground truth extracted${NC}"
echo ""

# Stage 2: Create Skeleton (GLM-4.7 via Claude)
echo -e "${BLUE}[Stage 2/6]${NC} Generate Skeleton (GLM-4.7 via Claude)"
echo "Please ask Claude to:"
echo "  1. Read roadmap.md for Day ${DAY_FMT}"
echo "  2. Create ENGLISH-ONLY skeleton from ground truth"
echo "  3. Output: daily_learning/skeletons/day${DAY_FMT}_skeleton.json"
echo ""
read -p "Press Enter after Claude completes Stage 2..."

# Verify skeleton exists
if [ ! -f "daily_learning/skeletons/day${DAY_FMT}_skeleton.json" ]; then
  echo -e "${RED}❌ Error: Skeleton not found${NC}"
  exit 1
fi
echo -e "${GREEN}✅ Skeleton created${NC}"
echo ""

# Stage 3: Verify Skeleton (DeepSeek R1 via Direct API)
echo -e "${BLUE}[Stage 3/6]${NC} Verify Skeleton (DeepSeek R1 - Direct API)"
echo ""

cat > /tmp/stage3_prompt_day${DAY_FMT}.txt << 'EOF'
Verify skeleton for Day ${DAY_FMT}: ${DAY_TOPIC}

SKELETON: $(cat daily_learning/skeletons/day${DAY_FMT}_skeleton.json)
GROUND TRUTH: $(cat /tmp/verified_facts_day${DAY_FMT}.json)

Verification tasks:
1. Class hierarchy matches ground truth exactly
2. Formulas match ground truth (check operators!)
3. No hallucinated classes or methods
4. All ⭐ facts are verified

Output format:
- PASS if all checks succeed
- FAIL with specific issues if any mismatch found

Be thorough and specific about any issues found.
EOF

echo "Calling DeepSeek R1..."
python3 .claude/scripts/deepseek_content.py deepseek-reasoner /tmp/stage3_prompt_day${DAY_FMT}.txt > /tmp/verification_report_day${DAY_FMT}.txt

if [ $? -eq 0 ]; then
  echo -e "${GREEN}✅ Verification complete${NC}"
  cat /tmp/verification_report_day${DAY_FMT}.txt
else
  echo -e "${RED}❌ Verification failed${NC}"
  exit 1
fi
echo ""

# Check if verification passed
if grep -q "FAIL\|error\|Error\|issue\|mismatch" /tmp/verification_report_day${DAY_FMT}.txt; then
  echo -e "${YELLOW}⚠️  Skeleton verification failed. Fix skeleton and re-run Stage 3.${NC}"
  exit 1
fi

# Stage 4: Generate Content (DeepSeek Chat V3 via Direct API)
echo -e "${BLUE}[Stage 4/6]${NC} Generate Content (DeepSeek Chat V3 - Direct API)"
echo ""

cat > /tmp/stage4_prompt_day${DAY_FMT}.txt << 'EOF'
Expand Day ${DAY_FMT}: ${DAY_TOPIC} - ENGLISH ONLY

SKELETON: $(cat daily_learning/skeletons/day${DAY_FMT}_skeleton.json)
BLUEPRINT: $(cat daily_learning/blueprints/day${DAY_FMT}_blueprint.json)

CRITICAL REQUIREMENTS:
- ENGLISH-ONLY content (no Thai translation)
- Follow blueprint structure EXACTLY (template: $(cat daily_learning/blueprints/day${DAY_FMT}_blueprint.json | grep -o '"template":[^,]*' | cut -d'"' -f4))
- All ⭐ facts remain unchanged

MANDATORY OUTPUT REQUIREMENTS:
1. Structure: Follow blueprint's progressive overload (beginner → professional)
2. MANDATORY Appendix: MUST end with "## Appendix: Complete File Listings" section
3. Code with Context: Every snippet includes file path, line numbers, line-by-line explanation
4. Theory Quality: Complete derivations, not just final formulas
5. Code Quality: Real OpenFOAM implementation with file references

APPENDIX REQUIREMENT (MANDATORY):
Every output MUST end with an Appendix section using EXACT title:
```markdown
## Appendix: Complete File Listings

> For copy-paste convenience, here are the complete, compilable files discussed above, including all necessary headers, constructors, and CMake configurations.
```

SELF-CHECK BEFORE OUTPUT:
- [ ] Blueprint structure followed exactly
- [ ] Appendix section present with exact title
- [ ] Theory has complete derivations (not just formulas)
- [ ] Code includes file paths and line numbers
- [ ] Progressive overload: simple → complex across parts

Write comprehensive technical content suitable for CFD learners.

Format:
- Use $$ for display math equations
- Use $ for inline math
- Include proper Mermaid diagrams
- All code blocks must have language tags
- Headers in English only

Output complete markdown file content.
EOF

echo "Calling DeepSeek Chat V3 (this may take 1-2 minutes)..."
python3 .claude/scripts/deepseek_content.py deepseek-chat /tmp/stage4_prompt_day${DAY_FMT}.txt > daily_learning/Phase_01_Foundation_Theory/${DAY_FMT}.md

if [ $? -eq 0 ]; then
  echo -e "${GREEN}✅ Content generated${NC}"
  LINE_COUNT=$(wc -l < "daily_learning/Phase_01_Foundation_Theory/${DAY_FMT}.md")
  echo "   Generated ${LINE_COUNT} lines"
else
  echo -e "${RED}❌ Content generation failed${NC}"
  exit 1
fi
echo ""

# Stage 5: Final Verification (DeepSeek R1 via Direct API)
echo -e "${BLUE}[Stage 5/6]${NC} Final Verification (DeepSeek R1 - Direct API)"
echo ""

cat > /tmp/stage5_prompt_day${DAY_FMT}.txt << 'EOF'
Final verification for Day ${DAY_FMT}: ${DAY_TOPIC}

CONTENT: $(cat daily_learning/Phase_01_Foundation_Theory/${DAY_FMT}.md)
GROUND TRUTH: $(cat /tmp/verified_facts_day${DAY_FMT}.json)

Verification tasks:
1. All Mermaid diagrams match ground truth
2. All formulas in LaTeX match ground truth (check operators!)
3. Code snippets are syntactically correct
4. No ⚠️ claims without explanation

Output verification report with specific issues if any found.
EOF

echo "Calling DeepSeek R1..."
python3 .claude/scripts/deepseek_content.py deepseek-reasoner /tmp/stage5_prompt_day${DAY_FMT}.txt > /tmp/final_verification_day${DAY_FMT}.txt

if [ $? -eq 0 ]; then
  echo -e "${GREEN}✅ Final verification complete${NC}"
  cat /tmp/final_verification_day${DAY_FMT}.txt
else
  echo -e "${RED}❌ Final verification failed${NC}"
  exit 1
fi
echo ""

# Check if final verification passed
if grep -q "FAIL\|error\|Error\|issue\|mismatch" /tmp/final_verification_day${DAY_FMT}.txt; then
  echo -e "${YELLOW}⚠️  Final verification failed. Review content and re-run Stage 5.${NC}"
  exit 1
fi

# Stage 6: Syntax QC
echo -e "${BLUE}[Stage 6/6]${NC} Syntax QC (Python Script)"
echo ""

if [ -f ".claude/scripts/qc_syntax_check.py" ]; then
  python3 .claude/scripts/qc_syntax_check.py --file="daily_learning/Phase_01_Foundation_Theory/${DAY_FMT}.md"

  if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Syntax QC PASSED${NC}"
  else
    echo -e "${RED}❌ Syntax QC FAILED - Fix issues before publishing${NC}"
    exit 1
  fi
else
  echo -e "${YELLOW}⚠️  QC script not found, skipping${NC}"
fi
echo ""

# Summary
echo "======================================"
echo "✅ Workflow Complete!"
echo "======================================"
echo ""
echo "Output Files:"
echo "  📋 Ground Truth: /tmp/verified_facts_day${DAY_FMT}.json"
echo "  📄 Skeleton: daily_learning/skeletons/day${DAY_FMT}_skeleton.json"
echo "  📄 Content: daily_learning/Phase_01_Foundation_Theory/${DAY_FMT}.md"
echo "  📋 Verification: /tmp/verification_report_day${DAY_FMT}.txt"
echo "  📋 Final Verify: /tmp/final_verification_day${DAY_FMT}.txt"
echo ""

# Verify Direct API (not through proxy)
echo -e "${BLUE}Verification:${NC}"
DEEPSEEK_COUNT=$(grep -c "deepseek" proxy.log 2>/dev/null || echo "0")
echo "  DeepSeek requests in proxy.log: ${DEEPSEEK_COUNT} (should be 0)"
echo "  Direct API calls: $(ls -1 /tmp/stage*_prompt_day${DAY_FMT}.txt 2>/dev/null | wc -l)"
echo ""
echo -e "${GREEN}🎉 Day ${DAY_FMT} ready for review!${NC}"
