#!/usr/bin/env zsh
# generate_day.sh - Production-Grade Multi-stage HARDCORE Content Generator
# 
# Features:
#   - Git checkpoint after each successful stage
#   - Auto-restore from last checkpoint on failure
#   - 3 retries per stage before giving up
#   - Dynamic sub-stage generation (Survey → Execute pattern)
#   - Detailed logging
#
# Usage: ./generate_day.sh <date> <topic>

set -e  # Exit on error

# ========================================
# Configuration
# ========================================
TIMEOUT_CMD="gtimeout"      # Use gtimeout on macOS (from coreutils)
TIMEOUT_SECONDS=600         # 10 minutes max per stage
MAX_RETRIES=3               # Maximum retries per stage
LOG_FILE="/tmp/generate_day_${1:-unknown}.log"

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

# ========================================
# Logging Function
# ========================================
log() {
    local LEVEL=$1
    shift
    local MSG="$@"
    local TIMESTAMP=$(date "+%Y-%m-%d %H:%M:%S")
    echo "[$TIMESTAMP] [$LEVEL] $MSG" | tee -a "$LOG_FILE"
}

# ========================================
# Arguments
# ========================================
DATE=$1
TOPIC=$2

if [ -z "$DATE" ] || [ -z "$TOPIC" ]; then
    echo "${RED}Usage: $0 <date> <topic>${NC}"
    exit 1
fi

TARGET_FILE="daily_learning/$DATE.md"

# Initialize log
echo "" > "$LOG_FILE"
log "INFO" "=========================================="
log "INFO" "Starting generation for $DATE: $TOPIC"
log "INFO" "=========================================="

echo "${BLUE}🚀 Starting Production-Grade HARDCORE Generation${NC}"
echo "📅 Date: $DATE"
echo "📚 Topic: $TOPIC"
echo "🎯 Target: $TARGET_FILE"
echo "📝 Log: $LOG_FILE"
echo ""

# Setup Aider
source ~/.zshrc
use-aider-glm

# ========================================
# Git Functions
# ========================================
git_checkpoint() {
    local STAGE_NAME=$1
    git add "$TARGET_FILE" 2>/dev/null || true
    git commit -m "Checkpoint: $STAGE_NAME complete for $DATE" --quiet 2>/dev/null || true
    log "INFO" "Git checkpoint created: $STAGE_NAME"
}

git_restore_from_last() {
    log "WARN" "Restoring $TARGET_FILE from last commit..."
    git checkout HEAD -- "$TARGET_FILE" 2>/dev/null || true
    log "INFO" "File restored from last checkpoint"
}

# ========================================
# STAGE 0: Create Skeleton (Template)
# ========================================
echo "${BLUE}=== Stage 0: Creating Template ===${NC}"
log "INFO" "Stage 0: Creating template"

cat > "$TARGET_FILE" <<EOF
# $TOPIC
## HARDCORE Level - $DATE

---

## 1. Theory: Core Equations & Physics

<!-- PLACEHOLDER_THEORY -->

---

## 2. OpenFOAM Class Hierarchy & Implementation

<!-- PLACEHOLDER_CLASS -->

---

## 3. Code Walkthrough

<!-- PLACEHOLDER_CODE -->

---

## 4. Dictionary Analysis & Configuration

<!-- PLACEHOLDER_DICT -->

---

## 5. Hands-on: Practical Tasks & Coding

<!-- PLACEHOLDER_TASKS -->

---

## 6. Concept Checks

<!-- PLACEHOLDER_CHECKS -->

---

## Recommended Reading

- OpenFOAM User Guide: https://www.openfoam.com/documentation/user-guide
- OpenFOAM Programmer's Guide: https://doc.openfoam.com/
- CFD Online Forum: https://www.cfd-online.com/Forums/openfoam/

EOF

echo "${GREEN}✅ Template created${NC}"
git_checkpoint "Stage 0 - Template"
echo ""

# ========================================
# Core Stage Runner with Retry Logic
# ========================================
run_stage() {
    local STAGE_NUM=$1
    local STAGE_NAME=$2
    local INSTRUCTION=$3
    
    local RETRY_COUNT=0
    local SUCCESS=false
    
    log "INFO" "Starting $STAGE_NAME (max $MAX_RETRIES retries)"
    
    while [ $RETRY_COUNT -lt $MAX_RETRIES ] && [ "$SUCCESS" = "false" ]; do
        RETRY_COUNT=$((RETRY_COUNT + 1))
        local BEFORE_LINES=$(wc -l < "$TARGET_FILE")
        
        echo "${BLUE}=== $STAGE_NAME (Attempt $RETRY_COUNT/$MAX_RETRIES) ===${NC}"
        log "INFO" "$STAGE_NAME attempt $RETRY_COUNT/$MAX_RETRIES (lines: $BEFORE_LINES)"
        
        # Run aider with timeout
        if $TIMEOUT_CMD $TIMEOUT_SECONDS aider --model anthropic/claude-3-opus-20240229 \
            --yes --file "$TARGET_FILE" --map-tokens 4096 \
            --message "$INSTRUCTION" > /dev/null 2>&1; then
            
            local AFTER_LINES=$(wc -l < "$TARGET_FILE")
            
            # Check for partial diffs (Aider failure indicator)
            if grep -q "<<<<<<< SEARCH" "$TARGET_FILE"; then
                log "WARN" "Detected partial diff in output, treating as failure"
                git_restore_from_last
                echo "${YELLOW}⚠️  Partial diff detected, restoring and retrying...${NC}"
            elif [ $AFTER_LINES -gt $BEFORE_LINES ]; then
                # Success! Lines increased and no corruption
                SUCCESS=true
                echo "${GREEN}✅ $STAGE_NAME complete! (Lines: $BEFORE_LINES → $AFTER_LINES)${NC}"
                log "INFO" "$STAGE_NAME SUCCESS (lines: $BEFORE_LINES → $AFTER_LINES)"
                git_checkpoint "$STAGE_NAME"
            else
                log "WARN" "$STAGE_NAME: No content added (lines unchanged)"
                git_restore_from_last
                echo "${YELLOW}⚠️  No content added, restoring and retrying...${NC}"
            fi
        else
            log "WARN" "$STAGE_NAME: Timeout or execution error"
            git_restore_from_last
            echo "${YELLOW}⚠️  Timeout/Error, restoring and retrying...${NC}"
        fi
        
        # Small delay between retries
        if [ "$SUCCESS" = "false" ] && [ $RETRY_COUNT -lt $MAX_RETRIES ]; then
            echo "  ⏳ Waiting 5s before retry..."
            sleep 5
        fi
    done
    
    # Check final result
    if [ "$SUCCESS" = "false" ]; then
        log "ERROR" "$STAGE_NAME FAILED after $MAX_RETRIES attempts"
        echo "${RED}❌ $STAGE_NAME FAILED after $MAX_RETRIES attempts!${NC}"
        echo "${RED}⛔ Stopping workflow. Check log: $LOG_FILE${NC}"
        afplay /System/Library/Sounds/Basso.aiff 2>/dev/null || true
        exit 1
    fi
    
    echo ""
}

# ========================================
# Stage 1: Theory
# ========================================
run_stage 1 "Stage 1: Theory" "Focus ONLY on '<!-- PLACEHOLDER_THEORY -->'.
Replace that placeholder with mathematical theory for '$TOPIC'.
- Show governing equations in vector form.
- Explain key terms in Thai.
- DO NOT touch other sections."

# ========================================
# Stage 2: Class Hierarchy
# ========================================
run_stage 2 "Stage 2: Class Hierarchy" "Focus ONLY on '<!-- PLACEHOLDER_CLASS -->'.
Replace that placeholder with:
- Key C++ classes for '$TOPIC'.
- ASCII art inheritance diagrams.
- Reference \$FOAM_SRC files."

# ========================================
# Stage 3: Code Walkthrough (Dynamic Sub-Stages)
# ========================================
echo "${CYAN}=== Stage 3: Code Walkthrough (Survey → Execute) ===${NC}"
log "INFO" "Stage 3: Starting Survey phase"

# Phase 1: Survey - Ask Aider to write files list to a temp file
echo "${CYAN}--- Phase 1: Surveying relevant source files ---${NC}"
SURVEY_FILE="/tmp/survey_${DATE}.txt"

# Create a temp file for Aider to write the survey results
cat > "$SURVEY_FILE" <<EOF
# Survey Results for $TOPIC
# List the 2-3 most important OpenFOAM source files to analyze for this topic.
# Format: one filename per line (e.g., UEqn.H)

EOF

# Ask Aider to populate the survey file
$TIMEOUT_CMD 120 aider --model anthropic/claude-3-opus-20240229 \
    --yes --file "$SURVEY_FILE" --map-tokens 2048 \
    --message "Edit this file to list the 2-3 most important OpenFOAM source files for '$TOPIC'.
Write ONLY filenames, one per line (e.g., UEqn.H, pEqn.H, createFields.H).
Remove the comments and keep the file simple." > /dev/null 2>&1 || true

# Parse the survey results (extract filenames ending in .H or .C)
FILES=()
if [ -f "$SURVEY_FILE" ]; then
    while IFS= read -r line; do
        # Skip comments and empty lines
        [[ "$line" =~ ^#.*$ ]] && continue
        [[ -z "$line" ]] && continue
        
        # Extract filename (anything that looks like a .H or .C file)
        FILE=$(echo "$line" | grep -oE '[A-Za-z0-9_]+\.[HC]' | head -1)
        if [ -n "$FILE" ]; then
            FILES+=("$FILE")
        fi
    done < "$SURVEY_FILE"
fi

# Check if we got any files
if [ ${#FILES[@]} -gt 0 ]; then
    echo "${GREEN}✅ Survey completed: ${#FILES[@]} files found${NC}"
    printf '   - %s\n' "${FILES[@]}"
    log "INFO" "Survey results: ${FILES[*]}"
    
    echo ""
    echo "${CYAN}--- Phase 2: Executing ${#FILES[@]} sub-stages ---${NC}"
    log "INFO" "Phase 2: Will analyze ${#FILES[@]} files"
    
    # Phase 2: Execute - Run mini-stage for each file
    SUBSTAGE_NUM=1
    for FILE in "${FILES[@]}"; do
        if [ $SUBSTAGE_NUM -eq 1 ]; then
            # First file: Replace the PLACEHOLDER_CODE marker
            run_stage "3.$SUBSTAGE_NUM" "Stage 3.$SUBSTAGE_NUM: $FILE" "Replace '<!-- PLACEHOLDER_CODE -->' with a code walkthrough for '$FILE'.
Include:
- Heading '### 3.$SUBSTAGE_NUM $FILE'
- Key code snippets (max 30 lines).
- Brief Thai explanation.
DO NOT touch other sections."
        else
            # Subsequent files: Append after existing content in Section 3
            run_stage "3.$SUBSTAGE_NUM" "Stage 3.$SUBSTAGE_NUM: $FILE" "Add another subsection at the END of '## 3. Code Walkthrough' for file '$FILE'.
Add AFTER the existing content in Section 3:
- Heading '### 3.$SUBSTAGE_NUM $FILE'
- Key code snippets (max 30 lines).
- Brief Thai explanation.
DO NOT remove or modify existing content."
        fi
        SUBSTAGE_NUM=$((SUBSTAGE_NUM + 1))
    done
else
    log "WARN" "Survey returned no files, using fallback"
    echo "${YELLOW}⚠️  Survey failed, using fallback (single file)${NC}"
    
    # Fallback: Just do one simple code walkthrough
    run_stage 3 "Stage 3: Code Walkthrough" "Replace '<!-- PLACEHOLDER_CODE -->'.
Add a brief code walkthrough for the main solver file related to '$TOPIC'.
Keep it concise. Thai explanations."
fi

# ========================================
# Stage 4: Dictionary, Tasks & Checks (Split into 3 sub-stages)
# ========================================
echo "${CYAN}=== Stage 4: Practice Section (3 sub-stages) ===${NC}"
log "INFO" "Stage 4: Starting practice content generation"

# Stage 4.1a: fvSchemes Analysis
run_stage "4.1a" "Stage 4.1a: fvSchemes" "Replace '<!-- PLACEHOLDER_DICT -->' with:
### 4.1 fvSchemes Analysis
- Analysis of ddtSchemes, gradSchemes, divSchemes, laplacianSchemes.
- Brief Thai explanation.
- ADD '<!-- PLACEHOLDER_FVSOLUTION -->' at the end of this subsection.
DO NOT touch other sections."

# Stage 4.1b: fvSolution Analysis
run_stage "4.1b" "Stage 4.1b: fvSolution" "Replace '<!-- PLACEHOLDER_FVSOLUTION -->' with:
### 4.2 fvSolution Analysis
- Analysis of solvers and relaxation factors.
- Brief Thai explanation.
DO NOT touch other sections."

# Stage 4.2: Coding Tasks
run_stage "4.2" "Stage 4.2: Tasks" "Replace '<!-- PLACEHOLDER_TASKS -->' with:
- 2-3 practical coding exercises related to '$TOPIC'.
- Each task should have a clear objective and solution.
- Use code blocks for C++ code.
DO NOT touch other sections."

# Stage 4.3: Concept Checks
run_stage "4.3" "Stage 4.3: Checks" "Replace '<!-- PLACEHOLDER_CHECKS -->' with:
- 3-5 concept check questions about '$TOPIC'.
- After each question, provide the answer in a blockquote (> **Answer:** ...).
- Answers in Thai.
DO NOT touch other sections."

# ========================================
# ENHANCEMENT STAGES (Process existing content)
# ========================================
echo "${CYAN}=== Enhancement Stages (Iterative Refinement) ===${NC}"
log "INFO" "Starting enhancement stages"

# ----------------------------------------
# Stage 5: Deep Dive - Memory & Source Paths
# ----------------------------------------
run_stage 5 "Stage 5: Deep Dive" "Read Section 3 (Code Walkthrough) and ENHANCE it by adding:
1. For each code file mentioned, add '\$FOAM_SRC/path/to/file.H' reference.
2. Add a '#### Memory Layout' subsection with ASCII diagram showing data structures.
3. Add '#### Call Stack' showing which functions call which.
DO NOT remove existing content. Only ADD to it."

# ----------------------------------------
# Stage 6: Diagram Enrich - Mermaid diagrams
# ----------------------------------------
run_stage 6 "Stage 6: Diagrams" "Read the entire document and ADD Mermaid diagrams where helpful:
1. In Section 2 (Class Hierarchy), add a Mermaid class diagram.
2. In Section 3 (Code Walkthrough), add a Mermaid flowchart for algorithm steps.
Use \`\`\`mermaid code blocks. DO NOT remove existing content."

# ----------------------------------------
# Stage 7: Polish & Cross-References
# ----------------------------------------
run_stage 7 "Stage 7: Polish" "Final polish of the document:
1. Add internal links between sections (e.g., 'See Section 2.3 for details').
2. Ensure all Thai explanations are clear and grammatically correct.
3. Add a 'Summary' paragraph at the end of each major section.
4. Check for any incomplete sentences and fix them.
DO NOT remove existing content."

# ========================================
# Final Cleanup (Script-based, no AI)
# ========================================
echo "${BLUE}=== Final Cleanup ===${NC}"
log "INFO" "Running final cleanup"

# Remove any remaining placeholders
sed -i '' 's/<!-- PLACEHOLDER_[A-Z]* -->//g' "$TARGET_FILE"

# Remove any stray diff markers (safety)
sed -i '' '/^<<<<<<< SEARCH/,$d' "$TARGET_FILE" 2>/dev/null || true

# Final commit
git_checkpoint "Final - All stages complete"

# Stats
FINAL_LINES=$(wc -l < "$TARGET_FILE")
FINAL_SIZE=$(ls -lh "$TARGET_FILE" | awk '{print $5}')

echo "${GREEN}═══════════════════════════════════════════════════${NC}"
echo "${GREEN}🎉 Generation Complete!${NC}"
echo "${GREEN}═══════════════════════════════════════════════════${NC}"
echo "📄 File: $TARGET_FILE"
echo "📏 Lines: $FINAL_LINES"
echo "💾 Size: $FINAL_SIZE"
echo "📝 Log: $LOG_FILE"
echo ""

log "INFO" "Generation complete: $FINAL_LINES lines, $FINAL_SIZE"
log "INFO" "=========================================="

# Play success sound on macOS
afplay /System/Library/Sounds/Glass.aiff 2>/dev/null || true
echo "Done! 🚀"
