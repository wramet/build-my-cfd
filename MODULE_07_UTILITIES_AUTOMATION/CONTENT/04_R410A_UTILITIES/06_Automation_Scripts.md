# Automation Scripts (สคริปต์การทำงานอัตโนมัติ)

## Overview

Automation Scripts provide a complete pipeline for R410A evaporator simulations, from meshing to post-processing. These scripts automate the entire workflow, including error handling, monitoring, and reporting.

## Features

- ✅ End-to-end automation pipeline
- ✅ Error handling and recovery mechanisms
- ✅ Progress monitoring and logging
- ✅ Automatic report generation
- ✅ Configuration management
- ✅ Integration with OpenFOAM utilities

## Installation

```bash
# Make scripts executable
chmod +x automated_workflow.sh
chmod +x setup_case.sh
chmod +x monitor_simulation.sh
chmod +x generate_report.sh

# Create required directories
mkdir -p workflow
mkdir -p logs
mkdir -p reports
mkdir -p templates
```

## Complete Implementation

```bash
#!/bin/bash
# R410A Evaporator Automated Workflow
# Complete pipeline from meshing to post-processing

set -e  # Exit on error

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TEMPLATES_DIR="${SCRIPT_DIR}/templates"
LOG_DIR="${SCRIPT_DIR}/logs"
REPORTS_DIR="${SCRIPT_DIR}/reports"

# Load configuration file
CONFIG_FILE="${SCRIPT_DIR}/config.ini"

if [ -f "$CONFIG_FILE" ]; then
    source "$CONFIG_FILE"
else
    echo "Warning: Configuration file not found, using defaults"
fi

# Default configuration
DEFAULT_CASE_NAME="R410A_Evaporator"
DEFAULT_TUBE_LENGTH=1.0
DEFAULT_TUBE_DIAMETER=0.005
DEFAULT_MESH_RESOLUTION=50
DEFAULT_MASS_FLUX=200
DEFAULT_HEAT_FLUX=3000
DEFAULT_TIME_STEP="0.001"
DEFAULT_TOTAL_TIME="1.0"
DEFAULT_MAX_ITERATIONS="500"

# Use configuration or defaults
CASE_NAME="${CASE_NAME:-$DEFAULT_CASE_NAME}"
TUBE_LENGTH="${TUBE_LENGTH:-$DEFAULT_TUBE_LENGTH}"
TUBE_DIAMETER="${TUBE_DIAMETER:-$DEFAULT_TUBE_DIAMETER}"
MESH_RESOLUTION="${MESH_RESOLUTION:-$DEFAULT_MESH_RESOLUTION}"
MASS_FLUX="${MASS_FLUX:-$DEFAULT_MASS_FLUX}"
HEAT_FLUX="${HEAT_FLUX:-$DEFAULT_HEAT_FLUX}"
TIME_STEP="${TIME_STEP:-$DEFAULT_TIME_STEP}"
TOTAL_TIME="${TOTAL_TIME:-$DEFAULT_TOTAL_TIME}"
MAX_ITERATIONS="${MAX_ITERATIONS:-$DEFAULT_MAX_ITERATIONS}"

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    local status=$1
    local message=$2
    case $status in
        "info")    echo -e "${BLUE}[INFO]${NC} $message" ;;
        "success") echo -e "${GREEN}[SUCCESS]${NC} $message" ;;
        "warning") echo -e "${YELLOW}[WARNING]${NC} $message" ;;
        "error")   echo -e "${RED}[ERROR]${NC} $message" ;;
        *)         echo "[$status] $message" ;;
    esac
}

# Function to log with timestamp
log_with_timestamp() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_DIR/${CASE_NAME}_workflow.log"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check OpenFOAM environment
check_openfoam() {
    print_status "info" "Checking OpenFOAM environment..."

    if ! command_exists foamListTimes; then
        print_status "error" "OpenFOAM not properly sourced"
        exit 1
    fi

    if ! command_exists blockMesh; then
        print_status "error" "blockMesh not found"
        exit 1
    fi

    if ! command_exists checkMesh; then
        print_status "error" "checkMesh not found"
        exit 1
    fi

    print_status "success" "OpenFOAM environment OK"
}

# Function to validate configuration
validate_config() {
    print_status "info" "Validating configuration..."

    # Check required parameters
    if [ -z "$CASE_NAME" ]; then
        print_status "error" "Case name not specified"
        exit 1
    fi

    if [ "$TUBE_LENGTH" -le 0 ] || [ "$TUBE_DIAMETER" -le 0 ]; then
        print_status "error" "Invalid tube dimensions"
        exit 1
    fi

    if [ "$MASS_FLUX" -le 0 ] || [ "$HEAT_FLUX" -le 0 ]; then
        print_status "error" "Invalid flow/heat parameters"
        exit 1
    fi

    print_status "success" "Configuration valid"
}

# Function to create case directory
create_case_directory() {
    print_status "info" "Creating case directory..."

    if [ -d "$CASE_NAME" ]; then
        print_status "warning" "Case directory already exists, backing up..."
        mv "$CASE_NAME" "${CASE_NAME}_backup_$(date +%Y%m%d_%H%M%S)"
    fi

    mkdir -p "$CASE_NAME"
    mkdir -p "$CASE_NAME/constant"
    mkdir -p "$CASE_NAME/system"
    mkdir -p "$CASE_NAME/0.orig"

    print_status "success" "Case directory created"
}

# Function to generate mesh
generate_mesh() {
    print_status "info" "Generating mesh..."

    # Create blockMeshDict
    cat > "$CASE_NAME/system/blockMeshDict" << EOF
/*--------------------------------*- C++ -*----------------------------------*\\
| =========                 |                                                 |
| \\\\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox           |
|  \\\\    /   O peration     | Version:  v2212                                 |
|   \\\\  /    A nd           | Web:      www.OpenFOAM.org                      |
|    \\\\/     M anipulation  |                                                 |
\\*---------------------------------------------------------------------------*/
FoamFile
{
    version     2.0;
    format      ascii;
    class       dictionary;
    object      blockMeshDict;
}
// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

convertToMeters 1;

vertices
(
    // Inlet
    (-0.1 0 0)
    (-0.1 ${TUBE_DIAMETER/2} 0)
    (-0.1 0 ${TUBE_LENGTH})
    (-0.1 ${TUBE_DIAMETER/2} ${TUBE_LENGTH})

    // Outlet
    (0.1 0 0)
    (0.1 ${TUBE_DIAMETER/2} 0)
    (0.1 0 ${TUBE_LENGTH})
    (0.1 ${TUBE_DIAMETER/2} ${TUBE_LENGTH})
);

blocks
(
    hex (0 1 3 2 4 5 7 6) ($MESH_RESOLUTION ${MESH_RESOLUTION/5} $MESH_RESOLUTION) simpleGrading (1 1 1)
);

boundary
(
    inlet
    {
        type patch;
        faces
        (
            (0 4 5 1)
        );
    }

    outlet
    {
        type patch;
        faces
        (
            (2 6 7 3)
        );
    }

    wall
    {
        type wall;
        faces
        (
            (0 2 3 1)
            (4 5 7 6)
        );
    }

    empty
    {
        type empty;
        faces
        (
            (0 1 3 2)
            (4 6 7 5)
        );
    }
);

// ************************************************************************* //
EOF

    # Run blockMesh
    log_with_timestamp "Running blockMesh..."
    cd "$CASE_NAME"
    blockMesh > "$LOG_DIR/blockMesh.log" 2>&1

    if [ $? -eq 0 ]; then
        print_status "success" "Mesh generated successfully"
    else
        print_status "error" "Mesh generation failed"
        log_with_timestamp "blockMesh.log:"
        tail -20 "$LOG_DIR/blockMesh.log"
        exit 1
    fi

    cd ..
}

# Function to check mesh
check_mesh() {
    print_status "info" "Checking mesh quality..."

    cd "$CASE_NAME"
    checkMesh -allGeometry -allTopology > "$LOG_DIR/checkMesh.log" 2>&1

    if grep -q "Mesh OK" "$LOG_DIR/checkMesh.log"; then
        print_status "success" "Mesh OK"

        # Extract mesh statistics
        local cells=$(grep "cells" "$LOG_DIR/checkMesh.log" | head -1 | awk '{print $3}')
        local faces=$(grep "faces" "$LOG_DIR/checkMesh.log" | head -1 | awk '{print $3}')
        local points=$(grep "points" "$LOG_DIR/checkMesh.log" | head -1 | awk '{print $3}')

        log_with_timestamp "Mesh cells: $cells, faces: $faces, points: $points"
    else
        print_status "warning" "Mesh has issues, continuing anyway"
        log_with_timestamp "checkMesh.log:"
        grep "Non-orthogonality\|Skewness" "$LOG_DIR/checkMesh.log" | head -10
    fi

    cd ..
}

# Function to create field files
create_fields() {
    print_status "info" "Creating field files..."

    cd "$CASE_NAME"

    # Create 0.orig directory
    mkdir -p 0.orig

    # Create U field
    cat > 0.orig/U << EOF
/*--------------------------------*- C++ -*----------------------------------*\\
| =========                 |                                                 |
| \\\\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox           |
|  \\\\    /   O peration     | Version:  v2212                                 |
|   \\\\  /    A nd           | Web:      www.OpenFOAM.org                      |
|    \\\\/     M anipulation  |                                                 |
\\*---------------------------------------------------------------------------*/
FoamFile
{
    version     2.0;
    format      ascii;
    class       volVectorField;
    object      U;
}
// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

dimensions      [0 1 -1 0 0 0 0];

internalField   uniform (0 0 0);

boundaryField
{
    inlet
    {
        type            flowRateInletVelocity;
        volumetricFlowRate ${MASS_FLUX}*(3.14159*(${TUBE_DIAMETER}/2)^2);
        value           uniform (0 0 0);
    }

    outlet
    {
        type            outletInlet;
        outlet          uniform (0 0 1);
        value           uniform (0 0 1);
    }

    wall
    {
        type            noSlip;
    }

    empty
    {
        type            empty;
    }
}

// ************************************************************************* //
EOF

    # Create p field
    cat > 0.orig/p << EOF
/*--------------------------------*- C++ -*----------------------------------*\\
| =========                 |                                                 |
| \\\\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox           |
|  \\\\    /   O peration     | Version:  v2212                                 |
|   \\\\  /    A nd           | Web:      www.OpenFOAM.org                      |
|    \\\\/     M anipulation  |                                                 |
\\*---------------------------------------------------------------------------*/
FoamFile
{
    version     2.0;
    format      ascii;
    class       volScalarField;
    object      p;
}
// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

dimensions      [0 2 -2 0 0 0 0];

internalField   uniform 100000;

boundaryField
{
    inlet
    {
        type            fixedValue;
        value           uniform 100000;
    }

    outlet
    {
        type            fixedValue;
        value           uniform 100000;
    }

    wall
    {
        type            zeroGradient;
    }

    empty
    {
        type            empty;
    }
}

// ************************************************************************* //
EOF

    # Create alpha field
    cat > 0.orig/alpha << EOF
/*--------------------------------*- C++ -*----------------------------------*\\
| =========                 |                                                 |
| \\\\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox           |
|  \\\\    /   O peration     | Version:  v2212                                 |
|   \\\\  /    A nd           | Web:      www.OpenFOAM.org                      |
|    \\\\/     M anipulation  |                                                 |
\\*---------------------------------------------------------------------------*/
FoamFile
{
    version     2.0;
    format      ascii;
    class       volScalarField;
    object      alpha;
}
// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

dimensions      [0 0 0 0 0 0 0];

internalField   uniform 0.0;

boundaryField
{
    inlet
    {
        type            fixedValue;
        value           uniform 0.0;
    }

    outlet
    {
        type            inletOutlet;
        inletValue      uniform 0.0;
        value           uniform 0.0;
    }

    wall
    {
        type            zeroGradient;
    }

    empty
    {
        type            empty;
    }
}

// ************************************************************************* //
EOF

    # Create T field
    cat > 0.orig/T << EOF
/*--------------------------------*- C++ -*----------------------------------*\\
| =========                 |                                                 |
| \\\\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox           |
|  \\\\    /   O peration     | Version:  v2212                                 |
|   \\\\  /    A nd           | Web:      www.OpenFOAM.org                      |
|    \\\\/     M anipulation  |                                                 |
\\*---------------------------------------------------------------------------*/
FoamFile
{
    version     2.0;
    format      ascii;
    class       volScalarField;
    object      T;
}
// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

dimensions      [0 0 0 1 0 0 0];

internalField   uniform 300;

boundaryField
{
    inlet
    {
        type            fixedValue;
        value           uniform 300;
    }

    outlet
    {
        type            zeroGradient;
    }

    wall
    {
        type            fixedFluxHeat;
        q               uniform ${HEAT_FLUX};
    }

    empty
    {
        type            empty;
    }
}

// ************************************************************************* //
EOF

    # Copy to 0 directory
    cp -r 0.orig/* 0/

    print_status "success" "Field files created"
    cd ..
}

# Function to create controlDict
create_control_dict() {
    print_status "info" "Creating controlDict..."

    cat > "$CASE_NAME/system/controlDict" << EOF
/*--------------------------------*- C++ -*----------------------------------*\\
| =========                 |                                                 |
| \\\\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox           |
|  \\\\    /   O peration     | Version:  v2212                                 |
|   \\\\  /    A nd           | Web:      www.OpenFOAM.org                      |
|    \\\\/     M anipulation  |                                                 |
\\*---------------------------------------------------------------------------*/
FoamFile
{
    version     2.0;
    format      ascii;
    class       dictionary;
    object      controlDict;
}
// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

application     R410ASolver;

startFrom       latestTime;

startTime       0;

stopAt          endTime;

endTime         ${TOTAL_TIME};

deltaT          ${TIME_STEP};

writeControl    adjustable;

writeInterval   0.01;

purgeWrite      0;

writeFormat     ascii;

writePrecision  6;

writeCompression off;

timeFormat      general;

timePrecision   6;

runTimeModifiable true;

functions
{
    residuals
    {
        type            residuals;
        libs            ("libutilityFunctions.so");
        executeControl  timeStep;
        executeInterval  1;
        fields
        (
            p
            U
            alpha
        );
    }

    yPlus
    {
        type            yPlus;
        libs            ("libfieldFunctionObjects.so");
        executeControl   timeStep;
        executeInterval  10;
    }
}

// ************************************************************************* //
EOF

    print_status "success" "controlDict created"
}

# Function to set up boundary conditions
setup_bcs() {
    print_status "info" "Setting up boundary conditions..."

    # This would involve more sophisticated boundary condition setup
    # For now, we've already created the boundary fields

    print_status "success" "Boundary conditions set up"
}

# Function to run solver
run_solver() {
    print_status "info" "Running R410A solver..."

    cd "$CASE_NAME"

    # Start solver monitoring in background
    monitor_simulation &
    MONITOR_PID=$!

    # Run solver
    log_with_timestamp "Starting solver..."
    R410ASolver > "$LOG_DIR/solver.log" 2>&1

    if [ $? -eq 0 ]; then
        print_status "success" "Solver completed successfully"
        log_with_timestamp "Solver finished"
    else
        print_status "error" "Solver failed"
        log_with_timestamp "Solver error:"
        tail -20 "$LOG_DIR/solver.log"
        kill $MONITOR_PID 2>/dev/null
        exit 1
    fi

    kill $MONITOR_PID 2>/dev/null
    cd ..
}

# Function to monitor simulation
monitor_simulation() {
    print_status "info" "Starting simulation monitor..."

    local start_time=$(date +%s)
    local last_check_time=$start_time
    local converged=false

    while [ $converged = false ]; do
        # Check if solver is still running
        if ! pgrep -f "R410ASolver" > /dev/null; then
            break
        fi

        # Check convergence every minute
        current_time=$(date +%s)
        if [ $((current_time - last_check_time)) -ge 60 ]; then
            local converged_count=$(grep "Finalising parallel run" "$LOG_DIR/solver.log" | wc -l)

            if [ $converged_count -gt 0 ]; then
                print_status "success" "Simulation converged"
                converged=true
            else
                # Check residuals
                local last_residual=$(tail -1 "$LOG_DIR/solver.log" | grep "residuals" | awk '{print $NF}')
                if [ -n "$last_residual" ] && (( $(echo "$last_residual < 1e-6" | bc -l) )); then
                    print_status "success" "Residuals converged"
                    converged=true
                fi
            fi

            last_check_time=$current_time
        fi

        sleep 10
    done

    # Check if wall time exceeded
    local wall_time=$((current_time - start_time))
    if [ $wall_time -ge $((MAX_ITERATIONS * TIME_STEP)) ]; then
        print_status "warning" "Maximum iterations reached"
    fi
}

# Function to post-process
post_process() {
    print_status "info" "Post-processing results..."

    cd "$CASE_NAME"

    # Run post-processing utilities
    log_with_timestamp "Running post-processing..."

    # Calculate y+
    yPlus > "$LOG_DIR/yPlus.log" 2>&1

    # Extract results
    sample -latestTime > "$LOG_DIR/sample.log" 2>&1

    # Generate plots
    python3 "$SCRIPT_DIR/post_process.py" --all --output "$REPORTS_DIR" "$CASE_NAME"

    cd ..

    print_status "success" "Post-processing complete"
}

# Function to generate report
generate_report() {
    print_status "info" "Generating final report..."

    # Generate PDF report
    python3 "$SCRIPT_DIR/generate_report.py" "$CASE_NAME" "$REPORTS_DIR"

    print_status "success" "Report generated"
}

# Function to cleanup
cleanup() {
    print_status "info" "Cleaning up temporary files..."

    # Remove backup files older than 7 days
    find . -name "backup_*" -mtime +7 -exec rm -rf {} \;

    # Compress log files
    gzip -f "$LOG_DIR"/*.log 2>/dev/null || true

    print_status "success" "Cleanup complete"
}

# Function to show usage
show_usage() {
    echo "Usage: $0 [options]"
    echo "Options:"
    echo "  -n, --name NAME        Case name (default: $DEFAULT_CASE_NAME)"
    echo "  -l, --length L         Tube length (m, default: $DEFAULT_TUBE_LENGTH)"
    echo "  -d, --diameter D       Tube diameter (m, default: $DEFAULT_TUBE_DIAMETER)"
    echo "  -r, --resolution R     Mesh resolution (default: $DEFAULT_MESH_RESOLUTION)"
    echo "  -g, --flux G           Mass flux (kg/m²s, default: $DEFAULT_MASS_FLUX)"
    echo "  -q, --heat Q           Heat flux (W/m², default: $DEFAULT_HEAT_FLUX)"
    echo "  -t, --time T           Total time (s, default: $DEFAULT_TOTAL_TIME)"
    echo "  -s, --step S           Time step (s, default: $DEFAULT_TIME_STEP)"
    echo "  -m, --max-i I          Max iterations (default: $DEFAULT_MAX_ITERATIONS)"
    echo "  -c, --config FILE      Configuration file"
    echo "  -v, --verbose         Verbose output"
    echo "  -h, --help            Show this help"
}

# Parse command line options
while [ $# -gt 0 ]; do
    case $1 in
        -n|--name)
            CASE_NAME="$2"
            shift 2
            ;;
        -l|--length)
            TUBE_LENGTH="$2"
            shift 2
            ;;
        -d|--diameter)
            TUBE_DIAMETER="$2"
            shift 2
            ;;
        -r|--resolution)
            MESH_RESOLUTION="$2"
            shift 2
            ;;
        -g|--flux)
            MASS_FLUX="$2"
            shift 2
            ;;
        -q|--heat)
            HEAT_FLUX="$2"
            shift 2
            ;;
        -t|--time)
            TOTAL_TIME="$2"
            shift 2
            ;;
        -s|--step)
            TIME_STEP="$2"
            shift 2
            ;;
        -m|--max-i)
            MAX_ITERATIONS="$2"
            shift 2
            ;;
        -c|--config)
            CONFIG_FILE="$2"
            shift 2
            ;;
        -v|--verbose)
            set -x
            shift
            ;;
        -h|--help)
            show_usage
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            show_usage
            exit 1
            ;;
    esac
done

# Main workflow
log_with_timestamp "Starting R410A Evaporator workflow"
log_with_timestamp "Case: $CASE_NAME"
log_with_timestamp "Configuration: L=$TUBE_LENGTH, D=$TUBE_DIAMETER, G=$MASS_FLUX, Q=$HEAT_FLUX"

# Step 1: Check environment
check_openfoam

# Step 2: Validate configuration
validate_config

# Step 3: Create case directory
create_case_directory

# Step 4: Generate mesh
generate_mesh

# Step 5: Check mesh
check_mesh

# Step 6: Create field files
create_fields

# Step 7: Set up boundary conditions
setup_bcs

# Step 8: Create controlDict
create_control_dict

# Step 9: Run solver
run_solver

# Step 10: Post-process results
post_process

# Step 11: Generate report
generate_report

# Step 12: Cleanup
cleanup

log_with_timestamp "Workflow complete!"
print_status "success" "R410A Evaporator simulation complete!"
print_status "success" "Results available in: $CASE_NAME/"
print_status "success" "Report available in: $REPORTS_DIR/${CASE_NAME}_report.pdf"
```

## Configuration File

```ini
# config.ini
[R410A_Evaporator]
case_name = R410A_Evaporator
tube_length = 1.0
tube_diameter = 0.005
mesh_resolution = 50
mass_flux = 200
heat_flux = 3000
time_step = 0.001
total_time = 1.0
max_iterations = 500

[Environment]
openfoam_solver = R410ASolver
post_processor = sample
yplus_calculator = yPlus

[Monitoring]
check_interval = 60
max_wall_time = 3600
convergence_threshold = 1e-6

[Output]
report_format = pdf
plot_format = png
save_intermediate = false
```

## Supporting Scripts

### Case Setup Script

```bash
#!/bin/bash
# Setup R410A evaporator case

setup_case() {
    local case_name=$1
    local tube_length=$2
    local tube_diameter=$3

    echo "Setting up case: $case_name"

    # Create directory structure
    mkdir -p "$case_name"/{constant,system,0,0.orig}

    # Copy templates
    cp -r "$TEMPLATES_DIR"/* "$case_name/system/"

    # Generate mesh files
    python3 generate_mesh.py "$case_name" "$tube_length" "$tube_diameter"

    # Initialize fields
    python3 initialize_fields.py "$case_name" $mass_flux $heat_flux

    echo "Case setup complete: $case_name"
}
```

### Simulation Monitor Script

```bash
#!/bin/bash
# Monitor simulation progress

monitor_simulation() {
    local case_dir=$1
    local interval=${2:-60}

    echo "Monitoring simulation in $case_dir"
    echo "Press Ctrl+C to stop"

    while true; do
        # Check if solver is running
        if pgrep -f "R410ASolver" > /dev/null; then
            # Check residuals
            latest_residual=$(tail -1 "$case_dir/log.solver" 2>/dev/null | grep "residuals" | awk '{print $NF}')
            if [ -n "$latest_residual" ]; then
                echo -ne "\rLatest residual: $latest_residual"
            fi
        else
            echo -e "\nSimulation completed"
            break
        fi

        sleep $interval
    done
}
```

### Report Generator Script

```python
#!/usr/bin/env python3
"""
Generate comprehensive PDF report for R410A simulation
"""

from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
import os
import json
from datetime import datetime

def generate_report(case_name, output_dir):
    """Generate PDF report"""
    report_file = os.path.join(output_dir, f"{case_name}_report.pdf")

    # Create PDF document
    doc = SimpleDocTemplate(report_file, pagesize=A4)
    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        spaceAfter=30,
        textColor=colors.darkblue
    )

    # Content elements
    story = []

    # Title
    story.append(Paragraph(f"R410A Evaporator Simulation Report", title_style))
    story.append(Spacer(1, 20))

    # Summary
    story.append(Paragraph("Simulation Summary", styles['Heading2']))
    summary_data = [
        ['Parameter', 'Value'],
        ['Case Name', case_name],
        ['Date', datetime.now().strftime('%Y-%m-%d %H:%M:%S')],
        ['Duration', 'Calculating...'],
        ['Status', 'Completed']
    ]

    summary_table = Table(summary_data, colWidths=[3*inch, 2*inch])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 14),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))

    story.append(summary_table)
    story.append(Spacer(1, 20))

    # Results
    story.append(Paragraph("Key Results", styles['Heading2']))
    # Add results from post-processing
    # ...

    # Build PDF
    doc.build(story)
    print(f"Report generated: {report_file}")
```

## Usage Examples

### Command Line Usage

```bash
# Run complete workflow
./automated_workflow.sh

# Custom case
./automated_workflow.sh -n MyCase -l 2.0 -d 0.01 -g 300 -q 5000

# With custom configuration
./automated_workflow.sh -c my_config.ini

# Verbose output
./automated_workflow.sh -v
```

### Python API Usage

```python
from workflow import R410AWorkflow

# Create workflow
workflow = R410AWorkflow(
    case_name="MyCase",
    tube_length=2.0,
    tube_diameter=0.01,
    mass_flux=300,
    heat_flux=5000
)

# Run workflow
workflow.run()

# Access results
results = workflow.get_results()
```

## Advanced Features

### 1. Parallel Processing

```bash
#!/bin/bash
# Run multiple cases in parallel

run_parallel_cases() {
    local cases=("$@")
    local pids=()

    for case in "${cases[@]}"; do
        ./automated_workflow.sh -n "$case" &
        pids+=($!)
    done

    # Wait for all cases
    for pid in "${pids[@]}"; do
        wait $pid
    done
}

# Example usage
run_parallel_cases "Case1" "Case2" "Case3"
```

### 2. Batch Processing

```python
def batch_process(parametric_study):
    """Process parametric study"""
    results = {}

    for params in parametric_study:
        case_name = f"case_{params['id']}"

        # Create workflow
        workflow = R410AWorkflow(
            case_name=case_name,
            tube_length=params['length'],
            tube_diameter=params['diameter'],
            mass_flux=params['flux'],
            heat_flux=params['heat']
        )

        # Run workflow
        workflow.run()

        # Collect results
        results[case_name] = workflow.get_results()

    return results
```

### 3. Error Recovery

```bash
# Error recovery mechanism
error_recovery() {
    local case_dir=$1

    # Check if simulation failed
    if [ ! -f "$case_dir/log.final" ]; then
        print_status "warning" "Simulation failed, attempting recovery..."

        # Reduce time step
        sed -i "s/deltaT .*/deltaT 0.0005/" "$case_dir/system/controlDict"

        # Retry
        print_status "info" "Retrying with smaller time step..."
        run_solver "$case_dir"
    fi
}
```

## Integration with Monitoring

### Real-time Monitoring

```python
import time
import threading

class WorkflowMonitor:
    def __init__(self, workflow):
        self.workflow = workflow
        self.running = False
        self.thread = None

    def start(self):
        """Start monitoring"""
        self.running = True
        self.thread = threading.Thread(target=self._monitor)
        self.thread.start()

    def stop(self):
        """Stop monitoring"""
        self.running = False
        if self.thread:
            self.thread.join()

    def _monitor(self):
        """Monitor workflow progress"""
        while self.running:
            # Check current step
            status = self.workflow.get_status()
            print(f"Current status: {status}")

            # Check resources
            self._check_resources()

            time.sleep(60)

    def _check_resources(self):
        """Check system resources"""
        import psutil

        # Memory usage
        memory = psutil.virtual_memory()
        if memory.percent > 90:
            print("WARNING: High memory usage")

        # CPU usage
        cpu = psutil.cpu_percent()
        if cpu > 95:
            print("WARNING: High CPU usage")
```

## Quality Assurance

### Automated Testing

```bash
#!/bin/bash
# Test automated workflow

test_workflow() {
    echo "Running automated workflow tests..."

    # Test case setup
    ./setup_case.sh test_case 1.0 0.005
    if [ $? -eq 0 ]; then
        echo "✓ Case setup test passed"
    else
        echo "✗ Case setup test failed"
        return 1
    fi

    # Test mesh generation
    cd test_case
    blockMesh > test.log 2>&1
    if grep -q "Built mesh in" test.log; then
        echo "✓ Mesh generation test passed"
    else
        echo "✗ Mesh generation test failed"
        return 1
    fi

    # Cleanup
    cd ..
    rm -rf test_case

    echo "All tests passed"
}
```

### Validation Checks

```python
def validate_workflow_results(workflow):
    """Validate workflow results"""
    issues = []

    # Check convergence
    if not workflow.check_convergence():
        issues.append("Simulation did not converge")

    # Check mass conservation
    mass_error = workflow.get_mass_error()
    if mass_error > 5:
        issues.append(f"High mass error: {mass_error}%")

    # Check physical validity
    if not workflow.check_physical_validity():
        issues.append("Results violate physical laws")

    return issues
```

## Troubleshooting

### Common Issues

1. **OpenFOAM not found**
   - Solution: Ensure OpenFOAM is properly sourced
   - Check `which foamListTimes`

2. **Mesh generation fails**
   - Solution: Check blockMeshDict syntax
   - Verify geometry parameters

3. **Solver diverges**
   - Solution: Reduce time step
   - Check initial conditions

### Debug Mode

```bash
# Run with debug output
./automated_workflow.sh -v -n debug_case

# Check logs
tail -f logs/debug_case_workflow.log

# Check individual step
cd debug_case
cat log.solver | grep residuals
```

---

**Note**: For production use, consider implementing checkpointing, version control, and integration with HPC batch systems.