#!/bin/bash
# =============================================================================
# CFD Engine Development - Environment Setup Script
# =============================================================================
# This script sets up the development environment for the CFD engine project.
# It handles:
#   1. DeepSeek API key configuration
#   2. OpenFOAM source code symlink
# =============================================================================

set -e

echo "🚀 CFD Engine Development Setup"
echo "================================"
echo ""

# -----------------------------------------------------------------------------
# Step 1: DeepSeek API Key (Hardcoded)
# -----------------------------------------------------------------------------
export DEEPSEEK_API_KEY="sk-a8d183f6f9904326913cb4e799eaba17"
echo "✅ DEEPSEEK_API_KEY is set."

# -----------------------------------------------------------------------------
# Step 2: OpenFOAM Source Symlink
# -----------------------------------------------------------------------------
OPENFOAM_LINK="./openfoam_src"

if [ -L "$OPENFOAM_LINK" ] || [ -d "$OPENFOAM_LINK" ]; then
    echo "✅ OpenFOAM source already linked: $(readlink -f $OPENFOAM_LINK 2>/dev/null || echo $OPENFOAM_LINK)"
else
    echo ""
    echo "📁 OpenFOAM source not found."
    read -p "Do you have OpenFOAM source installed? (y/n): " has_openfoam
    
    if [ "$has_openfoam" = "y" ] || [ "$has_openfoam" = "Y" ]; then
        read -p "Enter the full path to OpenFOAM source: " openfoam_path
        
        if [ -d "$openfoam_path" ]; then
            ln -s "$openfoam_path" "$OPENFOAM_LINK"
            echo "✅ Symlink created: $OPENFOAM_LINK -> $openfoam_path"
        else
            echo "❌ Error: Directory not found: $openfoam_path"
            exit 1
        fi
    else
        echo ""
        echo "📥 Downloading OpenFOAM-dev (shallow clone)..."
        git clone --depth 1 https://github.com/OpenFOAM/OpenFOAM-dev.git openfoam_temp
        ln -s openfoam_temp "$OPENFOAM_LINK"
        echo "✅ Downloaded and linked: $OPENFOAM_LINK -> openfoam_temp"
    fi
fi

# -----------------------------------------------------------------------------
# Final Status
# -----------------------------------------------------------------------------
echo ""
echo "================================"
echo "✅ System Ready!"
echo ""
echo "Project Structure:"
echo "  📁 learning_logs/     - AI-generated lessons"
echo "  📁 openfoam_src/      - OpenFOAM source (read-only)"
echo "  📄 roadmap.md         - 90-day learning plan"
echo "  📄 quality_check.md   - QC standards"
echo ""
echo "Usage:"
echo "  Claude: /teach Day 1   - Generate Day 1 lesson"
echo "  Claude: /qc 1 12       - QC check Days 1-12"
echo "================================"
