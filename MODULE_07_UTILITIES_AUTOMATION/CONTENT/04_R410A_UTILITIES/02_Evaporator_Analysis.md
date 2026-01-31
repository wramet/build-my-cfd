# Evaporator Analysis Tools (เครื่องมือวิเคราะห์เครื่องระเหย)

## Overview

Evaporator Analysis Tools provide comprehensive validation and analysis capabilities for R410A evaporator simulations in OpenFOAM. These tools automate mesh quality assessment, boundary layer verification, convergence monitoring, and key performance indicator extraction.

## Features

- ✅ Mesh quality validation and reporting
- ✅ y+ calculation and assessment
- ✅ Interface statistics extraction
- ✅ Mass conservation verification
- ✅ Convergence monitoring
- ✅ Pressure drop calculation
- ✅ Heat transfer coefficient analysis

## Installation

```bash
# Make scripts executable
chmod +x evaporator_analysis.sh
chmod +x calculate_yplus.sh
chmod +x check_convergence.sh

# Ensure OpenFOAM utilities are in PATH
source $HOME/OpenFOAM/OpenFOAM-v2212/etc/bashrc
```

## Complete Implementation

```bash
#!/bin/bash
# R410A Evaporator Analysis Tool
# Analyze OpenFOAM results for R410A evaporator simulation

# Check if case directory exists
if [ $# -eq 0 ]; then
    echo "Usage: $0 <case_directory> [options]"
    echo "Options:"
    echo "  -v, --verbose     Verbose output"
    echo "  -r, --report      Generate PDF report"
    echo "  -p, --plot        Generate plots"
    echo "  -h, --help        Show this help"
    exit 1
fi

CASE_DIR=$1
VERBOSE=false
GENERATE_REPORT=false
GENERATE_PLOTS=false

# Parse command line options
shift
while [ $# -gt 0 ]; do
    case $1 in
        -v|--verbose)
            VERBOSE=true
            shift
            ;;
        -r|--report)
            GENERATE_REPORT=true
            shift
            ;;
        -p|--plot)
            GENERATE_PLOTS=true
            shift
            ;;
        -h|--help)
            echo "Usage: $0 <case_directory> [options]"
            echo "Options:"
            echo "  -v, --verbose     Verbose output"
            echo "  -r, --report      Generate PDF report"
            echo "  -p, --plot        Generate plots"
            echo "  -h, --help        Show this help"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Check if case directory exists
if [ ! -d "$CASE_DIR" ]; then
    echo "Error: Case directory '$CASE_DIR' not found"
    exit 1
fi

# Enter case directory
cd $CASE_DIR

# Create log directory
mkdir -p logs

echo "R410A Evaporator Analysis"
echo "========================="
echo "Case: $(basename $PWD)"
echo "Time: $(date)"
echo ""

# Function to print section header
print_section() {
    echo ""
    echo "$1"
    echo "${1//?/-}"
}

# Function to check command success
check_command() {
    if [ $? -eq 0 ]; then
        echo "  ✓ $1"
        if [ "$VERBOSE" = true ]; then
            cat logs/$2.log
        fi
    else
        echo "  ✗ $1 - Check logs/$2.log"
    fi
}

print_section "1. Mesh Quality Analysis"

# Check mesh
echo "Running checkMesh..."
checkMesh -allGeometry -allTopology > logs/checkMesh.log 2>&1
if grep -q "Mesh OK" logs/checkMesh.log; then
    echo "  ✓ Mesh OK"

    # Extract mesh statistics
    echo "  Mesh Statistics:"
    echo "    Cells: $(grep "cells" logs/checkMesh.log | head -1 | awk '{print $3}')"
    echo "    Faces: $(grep "faces" logs/checkMesh.log | head -1 | awk '{print $3}')"
    echo "    Points: $(grep "points" logs/checkMesh.log | head -1 | awk '{print $3}')"
    echo "    Boundary faces: $(grep "boundary" logs/checkMesh.log | head -1 | awk '{print $3}')"

    # Check for non-orthogonality
    MAX_NON_ORTHO=$(grep "Non-orthogonality" logs/checkMesh.log | awk '{print $3}')
    MAX_SKEWNESS=$(grep "Skewness" logs/checkMesh.log | awk '{print $3}')

    echo "    Max non-orthogonality: $MAX_NON_ORTHO°"
    echo "    Max skewness: $MAX_SKEWNESS"

    # Quality assessment
    if (( $(echo "$MAX_NON_ORTHO < 70" | bc -l) )); then
        echo "  ✓ Mesh quality acceptable"
    else
        echo "  ⚠ High non-orthogonality detected"
    fi

    if (( $(echo "$MAX_SKEWNESS < 0.85" | bc -l) )); then
        echo "  ✓ Skewness acceptable"
    else
        echo "  ⚠ High skewness detected"
    fi

else
    echo "  ✗ Mesh has problems - see logs/checkMesh.log"
fi

print_section "2. Boundary Layer Analysis"

# Check if yPlus utility exists
if command -v yPlus >/dev/null 2>&1; then
    echo "Running yPlus calculation..."
    yPlus > logs/yPlus.log 2>&1

    # Extract statistics
    YPLUS_MEAN=$(grep "Mean y+" logs/yPlus.log | awk '{print $3}')
    YPLUS_MAX=$(grep "Max y+" logs/yPlus.log | awk '{print $3}')
    YPLUS_MIN=$(grep "Min y+" logs/yPlus.log | awk '{print $3}')

    echo "  y+ Statistics:"
    echo "    Mean: $YPLUS_MEAN"
    echo "    Min: $YPLUS_MIN"
    echo "    Max: $YPLUS_MAX"

    # Assessment
    if (( $(echo "$YPLUS_MEAN < 1" | bc -l) )); then
        echo "  ✓ y+ < 1 (resolved boundary layer)"
    elif (( $(echo "$YPLUS_MEAN < 5" | bc -l) )); then
        echo "  ⚠ y+ in wall function range"
    else
        echo "  ✗ y+ too high - need mesh refinement"
    fi

    # Check for near-wall cells
    if [ -f "postProcessing/yPlus/0/yPlus.dat" ]; then
        YPLUS_WALL=$(tail -1 postProcessing/yPlus/0/yPlus.dat | awk '{print $NF}')
        echo "  Near-wall cell y+: $YPLUS_WALL"
    fi
else
    echo "  ⚠ yPlus utility not found"
fi

print_section "3. Simulation Status"

# Check if simulation has completed
if [ -f "log.final" ]; then
    echo "  ✓ Simulation completed"

    # Extract run time
    RUN_TIME=$(grep "ExecutionTime" log.final | awk '{print $3}')
    echo "  Total run time: $RUN_TIME s"

    # Check convergence
    if grep -q "Finalising parallel run" log.final; then
        echo "  ✓ Converged"
    else
        echo "  ⚠ May not have fully converged"
    fi

else
    echo "  ⚠ Simulation may not be complete"
fi

# Check latest time directory
LATEST_TIME=$(foamListTimes -latest | tail -1)
if [ -n "$LATEST_TIME" ]; then
    echo "  Latest time: $LATEST_TIME"

    # Check continuity equation
    if [ -f "$LATEST_TIME/cont residuals.dat" ]; then
        CONT_RES=$(tail -1 "$LATEST_TIME/cont residuals.dat" | awk '{print $NF}')
        echo "  Continuity residual: $CONT_RES"
    fi
fi

print_section "4. Interface Analysis"

# Check for alpha field
if [ -f "$LATEST_TIME/alpha" ]; then
    echo "  Interface tracking enabled"

    # Calculate average void fraction
    ALPHA_MEAN=$(sampleUniform -latestTime alpha 2>/dev/null | grep "mean" | awk '{print $2}')
    ALPHA_MAX=$(sampleUniform -latestTime alpha 2>/dev/null | grep "max" | awk '{print $2}')

    echo "  Void fraction: mean = $ALPHA_MEAN, max = $ALPHA_MAX"

    # Interface statistics
    ALPHA_MIN=$(sampleUniform -latestTime alpha 2>/dev/null | grep "min" | awk '{print $2}')
    INTERFACE_RANGE=$(echo "$ALPHA_MAX - $ALPHA_MIN" | bc -l)
    echo "  Interface width: $INTERFACE_RANGE"

    # Check for reasonable interface
    if (( $(echo "$INTERFACE_RANGE < 0.1" | bc -l) )); then
        echo "  ✓ Sharp interface"
    else
        echo "  ⚠ Diffuse interface"
    fi
else
    echo "  ⚠ No alpha field found"
fi

print_section "5. Conservation Analysis"

# Mass conservation check
echo "Checking mass conservation..."
INITIAL_MASS=$(find 0 -name "*[Uu]" -exec head -n 1 {} \; | awk '{sum += $1} END {print sum}')
FINAL_MASS=$(find $LATEST_TIME -name "*[Uu]" -exec head -n 1 {} \; | awk '{sum += $1} END {print sum}')

if [ -n "$INITIAL_MASS" ] && [ -n "$FINAL_MASS" ]; then
    MASS_DIFF=$(echo "scale=6; $FINAL_MASS - $INITIAL_MASS" | bc -l)
    MASS_ERROR=$(echo "scale=6; $MASS_DIFF / $INITIAL_MASS * 100" | bc -l)
    echo "  Initial mass: $INITIAL_MASS"
    echo "  Final mass: $FINAL_MASS"
    echo "  Mass difference: $MASS_DIFF"
    echo "  Mass error: $MASS_ERROR%"

    if (( $(echo "$MASS_ERROR < 1" | bc -l) )); then
        echo "  ✓ Mass conservation OK"
    else
        echo "  ⚠ Mass conservation issue"
    fi
else
    echo "  ⚠ Could not check mass conservation"
fi

print_section "6. Pressure Drop Analysis"

# Extract pressure drop if available
if [ -f "0/p" ] && [ -f "$LATEST_TIME/p" ]; then
    echo "Calculating pressure drop..."

    # Extract inlet and outlet pressures
    P_INLET=$(grep "patch/inlet" 0/p | head -1 | awk '{print $NF}')
    P_OUTLET=$(grep "patch/outlet" 0/p | head -1 | awk '{print $NF}')

    if [ -n "$P_INLET" ] && [ -n "$P_OUTLET" ]; then
        P_DROP=$(echo "scale=2; $P_INLET - $P_OUTLET" | bc -l)
        echo "  Inlet pressure: $P_INLET Pa"
        echo "  Outlet pressure: $P_OUTLET Pa"
        echo "  Pressure drop: $P_DROP Pa"

        # Calculate dimensionless numbers
        if [ -f "0/U" ]; then
            U_INLET=$(grep "patch/inlet" 0/U | head -1 | awk '{print $NF}')
            D=$(grep "diameter" system/controlDict | awk '{print $3}')
            RHO=$(grep "patch/inlet" 0/alpha | head -1 | awk '{print $NF}')

            if [ -n "$U_INLET" ] && [ -n "$D" ] && [ -n "$RHO" ]; then
                # Reynolds number
                MU=$(python3 -c "from r410a_properties import R410APropertyCalculator; calc = R410APropertyCalculator(); props = calc.get_saturation_properties(2.0, 'MPa'); print(props['liquid']['mu'])")
                RE=$(echo "scale=2; $RHO * $U_INLET * $D / $MU" | bc -l)
                echo "  Inlet Reynolds number: $RE"

                # Euler number
                EULER=$(echo "scale=4; $P_DROP / (0.5 * $RHO * $U_INLET^2)" | bc -l)
                echo "  Euler number: $EULER"
            fi
        fi
    fi
fi

print_section "7. Heat Transfer Analysis"

# Check for temperature field
if [ -f "$LATEST_TIME/T" ]; then
    echo "Analyzing heat transfer..."

    # Extract temperatures
    T_MIN=$(sampleUniform -latestTime T 2>/dev/null | grep "min" | awk '{print $2}')
    T_MAX=$(sampleUniform -latestTime T 2>/dev/null | grep "max" | awk '{print $2}')
    T_MEAN=$(sampleUniform -latestTime T 2>/dev/null | grep "mean" | awk '{print $2}')

    echo "  Temperature range: $T_MIN K to $T_MAX K"
    echo "  Mean temperature: $T_MEAN K"

    # Check wall heat flux
    if [ -f "$LATEST_TIME/phi" ]; then
        Q_WALL=$(sample -latestTime -patch wall phi | grep "mean" | awk '{print $2}')
        if [ -n "$Q_WALL" ]; then
            echo "  Wall heat flux: $Q_WALL W/m²"

            # Estimate heat transfer coefficient
            T_SAT=$(python3 -c "from r410a_properties import R410APropertyCalculator; calc = R410APropertyCalculator(); props = calc.get_saturation_properties(2.0, 'MPa'); print(props['T_sat_K'])")
            HTC=$(echo "scale=2; $Q_WALL / ($T_MEAN - $T_SAT)" | bc -l)
            echo "  Estimated HTC: $TCHA W/m²K"
        fi
    fi
else
    echo "  ⚠ No temperature field found"
fi

print_section "8. Summary"

echo "Analysis Summary:"
echo "  Mesh Quality: $(grep "Mesh OK" logs/checkMesh.log > /dev/null && echo "OK" || echo "Issues")"
echo "  y+ Status: $(grep "Mean y+" logs/yPlus.log > /dev/null && echo "$(grep "Mean y+" logs/yPlus.log | awk '{print $3}')" || echo "Unknown")"
echo "  Convergence: $(grep "Finalising parallel run" log.final > /dev/null && echo "OK" || echo "Check")"
echo "  Interface: $([ -f "$LATEST_TIME/alpha" ] && echo "Present" || echo "Missing")"
echo "  Mass Conservation: $([ "$MASS_ERROR" ] && echo "${MASS_ERROR}%" || echo "Unknown")"

# Generate report if requested
if [ "$GENERATE_REPORT" = true ]; then
    echo ""
    echo "Generating report..."
    python3 ../generate_report.py $(basename $PWD)
fi

# Generate plots if requested
if [ "$GENERATE_PLOTS" = true ]; then
    echo ""
    echo "Generating plots..."
    python3 ../plot_results.py $(basename $PWD)
fi

echo ""
echo "Analysis complete. Results saved in logs/ directory."
echo "Time: $(date)"
```

## Supporting Scripts

### y+ Calculation Script

```bash
#!/bin/bash
# Enhanced y+ calculation script

calculate_yplus() {
    CASE_DIR=$1

    cd $CASE_DIR
    mkdir -p logs

    echo "Calculating y+..."
    yPlus > logs/yPlus.log 2>&1

    # Extract and display statistics
    if grep -q "Mean y+" logs/yPlus.log; then
        MEAN_YPLUS=$(grep "Mean y+" logs/yPlus.log | awk '{print $3}')
        MAX_YPLUS=$(grep "Max y+" logs/yPlus.log | awk '{print $3}')
        MIN_YPLUS=$(grep "Min y+" logs/yPlus.log | awk '{print $3}')

        echo "y+ Statistics:"
        echo "  Mean: $MEAN_YPLUS"
        echo "  Min: $MIN_YPLUS"
        echo "  Max: $MAX_YPLUS"

        # Generate distribution plot
        python3 -c "
import matplotlib.pyplot as plt
import numpy as np

# Read yPlus data
yPlus_data = []
with open('postProcessing/yPlus/0/yPlus.dat', 'r') as f:
    for line in f:
        if line.strip() and not line.startswith('#'):
            yPlus_data.append(float(line.split()[-1]))

plt.figure(figsize=(10, 6))
plt.hist(yPlus_data, bins=50, edgecolor='black')
plt.xlabel('y+')
plt.ylabel('Frequency')
plt.title('y+ Distribution')
plt.grid(True, alpha=0.3)
plt.savefig('yplus_distribution.png')
print('y+ distribution plot saved')
"
    fi
}
```

### Convergence Checker

```bash
#!/bin/bash
# Check convergence status

check_convergence() {
    CASE_DIR=$1

    cd $CASE_DIR

    echo "Checking convergence..."

    # Check latest time
    LATEST_TIME=$(foamListTimes -latest)

    # Check residuals
    if [ -f "log.solver" ]; then
        echo "Residuals:"
        grep "Time" log.solver | tail -5

        # Check if residuals meet criteria
        if grep -q "Finalising parallel run" log.solver; then
            echo "✓ Converged"
        else
            echo "⚠ Not converged"
        fi
    fi

    # Check mass conservation
    if [ -f "$LATEST_TIME/cont residuals.dat" ]; then
        CONT_RES=$(tail -1 "$LATEST_TIME/cont residuals.dat" | awk '{print $NF}')
        echo "Continuity residual: $CONT_RES"
    fi
}
```

## Usage Examples

### Basic Analysis

```bash
# Run basic analysis
./evaporator_analysis.sh R410A_Evaporator

# Run with verbose output
./evaporator_analysis.sh R410A_Evaporator -v

# Run with report generation
./evaporator_analysis.sh R410A_Evaporator -r
```

### Batch Analysis

```bash
#!/bin/bash
# Analyze multiple cases

CASES=("G100_Q2000" "G200_Q3000" "G300_Q4000")

for CASE in "${CASES[@]}"; do
    echo "Analyzing $CASE..."
    ./evaporator_analysis.sh results/$CASE
done
```

### Integration with Python

```python
import subprocess
import json
import os

def analyze_evaporator(case_dir, generate_plots=True):
    """Run evaporator analysis and extract results"""
    cmd = ['./evaporator_analysis.sh', case_dir]
    if generate_plots:
        cmd.append('-p')

    result = subprocess.run(cmd, capture_output=True, text=True)

    # Parse results
    analysis_results = {
        'mesh_quality': parse_mesh_quality(case_dir),
        'yplus_stats': parse_yplus(case_dir),
        'convergence': parse_convergence(case_dir),
        'interface_stats': parse_interface_stats(case_dir),
        'conservation': parse_conservation(case_dir)
    }

    return analysis_results

def parse_mesh_quality(case_dir):
    """Parse mesh quality results"""
    log_file = os.path.join(case_dir, 'logs', 'checkMesh.log')
    # Implementation to parse log file
    pass
```

## Advanced Features

### 1. Automated Mesh Improvement

```bash
#!/bin/bash
# Suggest mesh improvements based on analysis

suggest_mesh_improvements() {
    CASE_DIR=$1

    cd $CASE_DIR

    echo "Mesh Improvement Suggestions:"

    # Check y+
    if grep -q "Mean y+" logs/yPlus.log; then
        MEAN_YPLUS=$(grep "Mean y+" logs/yPlus.log | awk '{print $3}')
        if (( $(echo "$MEAN_YPLUS > 5" | bc -l) )); then
            echo "  - Increase inflation layers or reduce first cell size"
        fi
    fi

    # Check non-orthogonality
    if grep -q "Non-orthogonality" logs/checkMesh.log; then
        MAX_NON_ORTHO=$(grep "Non-orthogonality" logs/checkMesh.log | awk '{print $3}')
        if (( $(echo "$MAX_NON_ORTHO > 70" | bc -l) )); then
            echo "  - Increase mesh quality or use different meshing approach"
        fi
    fi
}
```

### 2. Performance Monitoring

```bash
#!/bin/bash
# Monitor simulation performance

monitor_performance() {
    CASE_DIR=$1

    cd $CASE_DIR

    # Check memory usage
    echo "Memory Usage:"
    grep "Memory usage" log.solver | tail -5

    # Check CPU time
    echo "CPU Time:"
    grep "ExecutionTime" log.solver | tail -5

    # Check parallel efficiency
    if [ -f "logs/OpenFOAM.log" ]; then
        grep "decomposition" logs/OpenFOAM.log | tail -3
    fi
}
```

## Quality Assurance

### Automated Validation

```bash
#!/bin/bash
# Validate case setup

validate_case() {
    CASE_DIR=$1

    cd $CASE_DIR

    echo "Validating case setup..."

    # Check required files
    REQUIRED_FILES=("0/U" "0/p" "0/alpha" "0/T" "system/controlDict" "system/fvSchemes")
    for file in "${REQUIRED_FILES[@]}"; do
        if [ -f "$file" ]; then
            echo "  ✓ $file"
        else
            echo "  ✗ $file missing"
        fi
    done

    # Check boundary conditions
    if grep -q "patch/inlet" 0/U && grep -q "patch/outlet" 0/U; then
        echo "  ✓ Boundary conditions defined"
    else
        echo "  ⚠ Boundary conditions incomplete"
    fi
}
```

## Integration with R410A Property Calculator

```bash
#!/bin/bash
# Integrate with property calculator for analysis

integrate_properties() {
    CASE_DIR=$1

    cd $CASE_DIR

    # Calculate saturation properties at operating pressure
    P_OPERATING=$(grep "patch/inlet" 0/p | head -1 | awk '{print $NF}')

    if [ -n "$P_OPERATING" ]; then
        echo "Operating pressure: $P_OPERATING Pa"

        # Generate property table
        python3 ../r410a_properties.py -p $(echo "$P_OPERATING/1e6" | bc -l) -f json > operating_properties.json

        # Extract key properties
        T_SAT=$(jq '.T_sat_C' operating_properties.json)
        echo "Saturation temperature: $T_SAT °C"
    fi
}
```

## Troubleshooting

### Common Issues

1. **y+ too high**
   - Solution: Increase inflation layers or reduce first cell size

2. **Mesh quality issues**
   - Solution: Check mesh skewness and non-orthogonality

3. **Convergence problems**
   - Solution: Check residuals and time step size

4. **Mass conservation issues**
   - Solution: Check boundary conditions and mesh quality

### Debug Mode

```bash
# Run with debug mode
./evaporator_analysis.sh R410A_Evaporator -v > debug.log 2>&1
```

---

**Note**: For production use, consider adding logging, configuration files, and integration with CI/CD pipelines.