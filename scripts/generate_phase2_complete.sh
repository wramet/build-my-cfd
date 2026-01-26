#!/bin/bash

echo "🚀 Starting Phase 2 Batch Generation..."

# 1. Generate Skeletons
echo "--- Step 1: Generating Skeletons ---"
./scripts/batch_generate_phase2_skeletons.sh

# 2. Generate Content
# Check if skeletons exist before running content generation (basic check)
if [ -f "daily_learning/skeletons/day19_skeleton.json" ]; then
    echo "--- Step 2: Generating Content ---"
    ./scripts/batch_generate_phase2_content.sh
else
    echo "❌ Usage Warning: Skeletons might not have finished correctly. Attempting content generation anyway..."
    ./scripts/batch_generate_phase2_content.sh
fi

echo "✅ Phase 2 Batch Generation Complete!"
