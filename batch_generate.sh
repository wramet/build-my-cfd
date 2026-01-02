#!/usr/bin/env zsh
# batch_generate.sh - Run multiple days of HARDCORE content generation sequentially
# Usage: ./batch_generate.sh

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

echo "${BLUE}🌙 Starting Overnight Batch Generation...${NC}"
echo "----------------------------------------"

# Function to run a day
run_day() {
    DATE=$1
    TOPIC=$2
    echo "${GREEN}🚀 Starting: $DATE - $TOPIC${NC}"
    
    # Run the generator and log specific batch output
    # Note: generate_day.sh already logs to /tmp/stage*.log
    ./generate_day.sh "$DATE" "$TOPIC"
    
    if [ $? -eq 0 ]; then
        echo "${GREEN}✅ Finished: $DATE${NC}"
    else
        echo "${RED}❌ Failed: $DATE${NC}"
        # Decide if we want to stop or continue. 
        # For overnight batch, maybe continue to try the next one?
        # But for now let's exit to avoid cascading errors if API is down.
        echo "Stopping batch due to error."
        exit 1
    fi
    
    echo "----------------------------------------"
    echo "💤 Resting for 30 seconds to be nice to API..."
    sleep 30
}

# --- 2-DAY TEST SCHEDULE (Day 1 & 2) ---

# Day 1: Governing Equations
run_day "2026-01-01" "Governing Equations & OpenFOAM Implementation"

# Day 2: The Core of FVM
run_day "2026-01-02" "Finite Volume Method & Discretization"

# Future Days (Commented out for testing)
# run_day "2026-01-03" "Boundary Conditions & Field Operations"
# run_day "2026-01-04" "Turbulence Modeling & Transport Hierarchy"
# run_day "2026-01-05" "Solver Algorithms (PIMPLE/PISO) & Time Stepping"

echo "${GREEN}✨ All 5 Days of HARDCORE Content Generated! Time to wake up! ☀️${NC}"
