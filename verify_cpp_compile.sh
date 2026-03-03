#!/usr/bin/env bash
# ==============================================================================
# verify_cpp_compile.sh
# ==============================================================================
# Ground truth verification tool for Modern C++ CFD curriculum
#
# Purpose: Extracts C++ code blocks from markdown files and compiles them
#          to verify technical accuracy
#
# Usage:   ./verify_cpp_compile.sh <file.md>
# ==============================================================================

set -e

# Default configuration
COMPILER="g++"
STANDARD="-std=c++20"
FLAGS="-O2 -Wall -Wextra"
VERBOSE=false

# Parse arguments
while [[ $# -gt 0 ]]; do
    case "$1" in
        --strict) FLAGS="$FLAGS -Werror"; shift ;;
        --verbose) VERBOSE=true; shift ;;
        --compiler) COMPILER="$2"; shift 2 ;;
        --std) STANDARD="-std=$2"; shift 2 ;;
        -h|--help)
            echo "Usage: $0 [--strict] [--verbose] [--compiler CMD] [--std VER] <file.md>"
            exit 0
            ;;
        *) INPUT_FILE="$1"; shift ;;
    esac
done

if [[ -z "${INPUT_FILE:-}" ]]; then
    echo "Error: No input file specified"
    exit 2
fi

if [[ ! -f "$INPUT_FILE" ]]; then
    echo "Error: File not found: $INPUT_FILE"
    exit 2
fi

echo "========================================="
echo "  C++ Ground Truth Verification Tool"
echo "========================================="
echo ""
echo "Configuration:"
echo "  Compiler: $COMPILER"
echo "  Standard: $STANDARD"
echo "  Input: $INPUT_FILE"
echo ""

# Extract and compile C++ code blocks
TMPDIR=$(mktemp -d)
trap "rm -rf $TMPDIR" EXIT

block_num=0
in_block=false
current_block=()
failed=0

while IFS= read -r line; do
    # Check for code block start
    if [[ "$line" =~ ^\`\`\`(cpp|C\+\+|c\+\+|cxx)$ ]]; then
        in_block=true
        current_block=()
        continue
    fi

    # Check for code block end
    if [[ "$line" == '```' ]] && $in_block; then
        in_block=false
        block_num=$((block_num + 1))

        # Save code to file
        block_file="$TMPDIR/block_$block_num.cpp"
        printf '%s\n' "${current_block[@]}" > "$block_file"

        # Try to compile
        echo -n "  [Block $block_num] "
        if $VERBOSE; then
            echo ""
            echo "Compiling: $COMPILER $STANDARD $FLAGS $block_file -o /dev/null"
        fi

        if $COMPILER $STANDARD $FLAGS "$block_file" -o /dev/null 2>/dev/null; then
            echo "✓"
        else
            echo "✗ FAILED"
            $COMPILER $STANDARD $FLAGS "$block_file" -o /dev/null 2>&1 | head -n 5
            failed=1
        fi
        continue
    fi

    # Accumulate code lines
    if $in_block; then
        current_block+=("$line")
    fi
done < "$INPUT_FILE"

echo ""

# Summary
if [[ $block_num -eq 0 ]]; then
    echo "⚠️  No C++ code blocks found in $INPUT_FILE"
    exit 0
fi

if [[ $failed -eq 0 ]]; then
    echo "✅ Success: All $block_num C++ code block(s) compiled successfully"
    exit 0
else
    echo "❌ Failed: Some code blocks did not compile"
    exit 1
fi
