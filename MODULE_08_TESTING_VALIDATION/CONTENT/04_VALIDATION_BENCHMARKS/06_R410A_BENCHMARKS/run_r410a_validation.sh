#!/bin/bash

# R410A Validation Suite Runner
# Author: CFD Engine Development Team
# Date: 2026-01-28

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "================================================================"
echo "R410A Test Suite Validation Runner"
echo "================================================================"
echo

# Check if we're in the correct directory
if [ ! -f "README.md" ]; then
    echo -e "${RED}ERROR:${NC} Please run this script from the 06_R410A_BENCHMARKS directory"
    exit 1
fi

# Create results directory
mkdir -p results

# Check Python availability
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}ERROR:${NC} Python3 is not available"
    exit 1
fi

echo "Running R410A Test Suite..."
echo "Working directory: $(pwd)"
echo

# Run the Python test suite
echo -e "${YELLOW}Step 1:${NC} Running complete test suite..."
python3 run_validation_suite.py

# Check results
echo
echo -e "${YELLOW}Step 2:${NC} Checking results..."

if [ -f "results/summary.csv" ]; then
    echo "Test results:"
    cat results/summary.csv | column -t -s ','

    # Count passed tests
    PASSED=$(grep -c "PASSED\|VALIDATED" results/summary.csv || true)
    TOTAL=$(grep -c "," results/summary.csv || true)

    echo
    echo "Summary:"
    echo "- Total tests: $TOTAL"
    echo "- Passed: $PASSED"

    if [ "$PASSED" -eq "$TOTAL" ]; then
        echo -e "${GREEN}✅ All tests passed!${NC}"
        SUCCESS=true
    else
        echo -e "${RED}❌ Some tests failed!${NC}"
        SUCCESS=false
    fi
else
    echo -e "${RED}ERROR:${NC} Results not found"
    exit 1
fi

# Generate final status
echo
echo "================================================================"
if [ "$SUCCESS" = true ]; then
    echo -e "${GREEN}R410A Test Suite Validation SUCCESSFUL!${NC}"
    echo "All tests passed and ready for CFD engine integration."
else
    echo -e "${RED}R410A Test Suite Validation FAILED!${NC}"
    echo "Please check the test results and fix any issues."
    exit 1
fi
echo "================================================================"
echo "Results saved in: results/"
echo "Validation report: results/validation_report.md"
echo "Detailed results: results/results.json"
echo "CSV summary: results/summary.csv"
echo

# Clean up optional files (if requested)
if [ "$1" = "--clean" ]; then
    echo -e "${YELLOW}Cleaning up temporary files...${NC}"
    rm -f *_script.py
fi

echo "Done!"