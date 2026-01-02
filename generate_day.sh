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

# Format rules summary for AI prompts
FORMAT_RULES="CRITICAL FORMAT RULES:
1. Use ASCII-only anchors (no Thai in anchor IDs)
2. Math: Use \$inline\$ and \$\$block\$\$ with NO spaces after \$
3. Code blocks: Always specify language (cpp, bash, foam)
4. Mermaid: Use graph TD for flowcharts, classDiagram for classes
5. Tables: Always include header row
6. Callouts: Use > [!INFO], > [!WARNING], > [!TIP]
7. Thai explanations in parentheses or blockquotes
8. Keep technical terms (class names, functions) in English"

cat > "$TARGET_FILE" <<EOF
---
tags: [openfoam, cfd, hardcore, day-${DATE##*-}]
date: $DATE
aliases: [$TOPIC]
difficulty: hardcore
topic: $TOPIC
---

# $TOPIC
## HARDCORE Level - $DATE

---

## Table of Contents
- [1. Theory](#1-theory-core-equations--physics)
- [2. Class Hierarchy](#2-openfoam-class-hierarchy--implementation)
- [3. Code Walkthrough](#3-code-walkthrough)
- [4. Dictionary Analysis](#4-dictionary-analysis--configuration)
- [5. Practical Tasks](#5-hands-on-practical-tasks--coding)
- [6. Concept Checks](#6-concept-checks)

---

## 1. Theory: Core Equations & Physics {#1-theory-core-equations--physics}

<!-- PLACEHOLDER_THEORY -->

---

## 2. OpenFOAM Class Hierarchy & Implementation {#2-openfoam-class-hierarchy--implementation}

<!-- PLACEHOLDER_CLASS -->

---

## 3. Code Walkthrough {#3-code-walkthrough}

<!-- PLACEHOLDER_CODE -->

---

## 4. Dictionary Analysis & Configuration {#4-dictionary-analysis--configuration}

<!-- PLACEHOLDER_DICT -->

---

## 5. Hands-on: Practical Tasks & Coding {#5-hands-on-practical-tasks--coding}

<!-- PLACEHOLDER_TASKS -->

---

## 6. Concept Checks {#6-concept-checks}

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
            --yes --no-auto-commits --file "$TARGET_FILE" --map-tokens 4096 \
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
- Show governing equations in vector form using \$\$ block math.
- Explain key terms clearly in English.
- DO NOT touch other sections.
$FORMAT_RULES"

# ========================================
# Stage 2: Class Hierarchy
# ========================================
run_stage 2 "Stage 2: Class Hierarchy" "Focus ONLY on '<!-- PLACEHOLDER_CLASS -->'.
Replace that placeholder with:
- Key C++ classes for '$TOPIC'.
- ASCII art or Mermaid classDiagram for inheritance.
- Reference \$FOAM_SRC files.
$FORMAT_RULES"

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
    
    # Phase 2: Execute - Run mini-stage for each file (using placeholder chaining)
    SUBSTAGE_NUM=1
    TOTAL_FILES=${#FILES[@]}
    for FILE in "${FILES[@]}"; do
        IS_LAST=$( [ $SUBSTAGE_NUM -eq $TOTAL_FILES ] && echo "true" || echo "false" )
        
        if [ $SUBSTAGE_NUM -eq 1 ]; then
            # First file: Replace PLACEHOLDER_CODE and add PLACEHOLDER_CODE_NEXT
            run_stage "3.$SUBSTAGE_NUM" "Stage 3.$SUBSTAGE_NUM: $FILE" "Replace '<!-- PLACEHOLDER_CODE -->' with a code walkthrough for '$FILE'.
Include:
- Heading '### 3.$SUBSTAGE_NUM $FILE'
- Key code snippets (max 30 lines).
- Brief explanation in English.
- At the END of your added content, ADD the line: <!-- PLACEHOLDER_CODE_NEXT -->
DO NOT touch other sections."
        else
            # Subsequent files: Replace PLACEHOLDER_CODE_NEXT
            if [ "$IS_LAST" = "true" ]; then
                # Last file: No new placeholder needed
                run_stage "3.$SUBSTAGE_NUM" "Stage 3.$SUBSTAGE_NUM: $FILE" "Replace '<!-- PLACEHOLDER_CODE_NEXT -->' with a code walkthrough for '$FILE'.
Include:
- Heading '### 3.$SUBSTAGE_NUM $FILE'
- Key code snippets (max 30 lines).
- Brief explanation in English.
DO NOT add any new placeholders. DO NOT touch other sections."
            else
                # Middle file: Replace and add new placeholder
                run_stage "3.$SUBSTAGE_NUM" "Stage 3.$SUBSTAGE_NUM: $FILE" "Replace '<!-- PLACEHOLDER_CODE_NEXT -->' with a code walkthrough for '$FILE'.
Include:
- Heading '### 3.$SUBSTAGE_NUM $FILE'
- Key code snippets (max 30 lines).
- Brief explanation in English.
- At the END of your added content, ADD the line: <!-- PLACEHOLDER_CODE_NEXT -->
DO NOT touch other sections."
            fi
        fi
        SUBSTAGE_NUM=$((SUBSTAGE_NUM + 1))
    done
else
    log "WARN" "Survey returned no files, using fallback"
    echo "${YELLOW}⚠️  Survey failed, using fallback (single file)${NC}"
    
    # Fallback: Just do one simple code walkthrough
    run_stage 3 "Stage 3: Code Walkthrough" "Replace '<!-- PLACEHOLDER_CODE -->'.
Add a brief code walkthrough for the main solver file related to '$TOPIC'.
Keep it concise. English explanations."
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
- Brief explanation in English.
- ADD '<!-- PLACEHOLDER_FVSOLUTION -->' at the end of this subsection.
DO NOT touch other sections."

# Stage 4.1b: fvSolution Analysis
run_stage "4.1b" "Stage 4.1b: fvSolution" "Replace '<!-- PLACEHOLDER_FVSOLUTION -->' with:
### 4.2 fvSolution Analysis
- Analysis of solvers and relaxation factors.
- Brief explanation in English.
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
- Answers in English.
DO NOT touch other sections."

# ========================================
# ENHANCEMENT STAGES (Process existing content)
# ========================================
echo "${CYAN}=== Enhancement Stages (Iterative Refinement) ===${NC}"
log "INFO" "Starting enhancement stages"

# ----------------------------------------
# Stage 5: Deep Dive - Memory & Source Paths
# ----------------------------------------
# ----------------------------------------
# Stage 5: Deep Dive - Memory & Source Paths (Split)
# ----------------------------------------

# Stage 5a: Source Paths
run_stage "5a" "Stage 5a: Source Paths" "Read Section 3 (Code Walkthrough) and ENHANCE it:
- For each code file mentioned, add '\$FOAM_SRC/path/to/file.H' reference.
- Add it as a bullet point or small note.
DO NOT remove existing content. Only ADD."

# Stage 5b: Memory Layout
run_stage "5b" "Stage 5b: Memory Layout" "Read Section 3 (Code Walkthrough) and ENHANCE it:
- Add a '#### Memory Layout' subsection for the MAIN class (e.g. fvMesh or fvMatrix).
- Add an ASCII diagram showing the data structure (e.g. pointers, arrays).
DO NOT remove existing content. Only ADD."

# ----------------------------------------
# Stage 6: Diagrams (Split into 6a/6b)
# ----------------------------------------

# Stage 6a: Class Diagram for Section 2
run_stage "6a" "Stage 6a: Class Diagram" "Focus ONLY on Section 2 (OpenFOAM Class Hierarchy).
Add ONE Mermaid classDiagram showing the main class relationships.
Use \`\`\`mermaid code blocks.
KEEP LABELS SHORT (max 15 chars per node).
Limit to 6-8 classes for readability.
DO NOT touch other sections."

# Stage 6b: Flowchart for Section 3
run_stage "6b" "Stage 6b: Flowchart" "Focus ONLY on Section 3 (Code Walkthrough).
Add ONE Mermaid flowchart (graph TD) showing the algorithm flow.
Use \`\`\`mermaid code blocks.
KEEP LABELS SHORT (1-3 words per node).
Limit to 6-8 nodes for readability.
DO NOT touch other sections."

# ----------------------------------------
# Stage 7: Polish (Summaries only - TOC is in template)
# ----------------------------------------

# Stage 7: Section Summaries
run_stage 7 "Stage 7: Summaries" "Add a brief 'Summary' paragraph at the END of each major section (1-6).
Each summary should be 2-3 sentences in English.
Format: > **Summary:** [summary text]
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

# Validate Links (Internal & External)
validate_links() {
    log "INFO" "Validating links..."
    echo "${BLUE}🔍 Validating links...${NC}"
    
    python3 -c "
import sys
import re
import urllib.request
from urllib.parse import unquote

file_path = '$TARGET_FILE'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Find headers for anchor checking
headers = set()
for line in content.splitlines():
    if line.startswith('#'):
        # Check for explicit anchor {#...}
        match = re.search(r'\{#([^\}]+)\}$', line)
        if match:
            slug = match.group(1)
            headers.add(slug)
            continue

        # Default: Convert header to anchor
        text = line.lstrip('#').strip().lower()
        slug = re.sub(r'[^\w\- ]', '', text).replace(' ', '-')
        headers.add(slug)

# Find links: [text](url)
links = re.findall(r'\[([^\]]+)\]\(([^)]+)\)', content)
errors = []

print(f'Checking {len(links)} links...')

for text, url in links:
    if url.startswith('#'):
        # Internal anchor
        anchor = url.lstrip('#')
        if anchor not in headers:
            # Try loosely matching (sometimes LLM guesses wrong)
            if anchor not in [h.replace('-', '') for h in headers]:
                errors.append(f'❌ Broken Internal Link: [{text}]({url}) - Anchor not found')
    elif url.startswith('http'):
        # External URL (Optional: Check connectivity)
        try:
            req = urllib.request.Request(url, method='HEAD')
            # Set User-Agent to avoid 403s
            req.add_header('User-Agent', 'Mozilla/5.0')
            with urllib.request.urlopen(req, timeout=5) as response:
                if response.status >= 400:
                    errors.append(f'❌ Broken External Link: [{text}]({url}) - Status {response.status}')
        except Exception as e:
            # Don't fail the build for external links, just warn
            print(f'⚠️  Warning External Link: [{text}]({url}) - {e}')
    else:
        # Local file
        import os
        if not os.path.exists(url):
             errors.append(f'❌ Broken File Link: [{text}]({url}) - File not found')

if errors:
    print('\n'.join(errors))
    sys.exit(1)
else:
    print('✅ All links validated!')
" || echo "${YELLOW}⚠️ Link validation found issues (check log)${NC}"
}

validate_links

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
