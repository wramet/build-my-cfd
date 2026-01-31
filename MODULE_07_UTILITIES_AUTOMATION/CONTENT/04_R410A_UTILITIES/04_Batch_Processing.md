# Batch Processing for Parametric Studies (การประมวลผลแบบเป็นกลุ่มสำหรับศึกษาพารามิเตอร์)

## Overview

Batch Processing Tools enable automated parametric studies for R410A evaporator simulations. These tools streamline the process of running multiple cases with varying parameters, monitoring convergence, and organizing results.

## Features

- ✅ Automated case generation from templates
- ✅ Parameter sweeps (mass flux, heat flux, inlet quality)
- ✅ Convergence monitoring and error handling
- ✅ Results organization and analysis
- ✅ Parallel processing capability
- ✅ Progress tracking and logging
- ✅ Shell script implementations

## Installation

```bash
# Make scripts executable
chmod +x run_parametric.sh
chmod +x batch_manager.py
chmod +x monitor_progress.sh

# Create required directories
mkdir -p templates
mkdir -p results
mkdir -p logs
```

## Complete Implementation

```bash
#!/bin/bash
# R410A Parametric Study Runner
# Run multiple cases with varying parameters

# Configuration file
CONFIG_FILE="parametric_config.ini"

# Default values
DEFAULT_BASE_CASE="base_case"
DEFAULT_RESULTS_DIR="results"
DEFAULT_PARALLEL_JOBS=4
DEFAULT_TIME_STEP="0.001"
DEFAULT_TOTAL_TIME="0.5"

# Load configuration if exists
if [ -f "$CONFIG_FILE" ]; then
    source "$CONFIG_FILE"
else
    echo "Using default configuration"
    BASE_CASE="$DEFAULT_BASE_CASE"
    RESULTS_DIR="$DEFAULT_RESULTS_DIR"
    PARALLEL_JOBS="$DEFAULT_PARALLEL_JOBS"
    TIME_STEP="$DEFAULT_TIME_STEP"
    TOTAL_TIME="$DEFAULT_TOTAL_TIME"
fi

# Function to display usage
show_usage() {
    echo "Usage: $0 [options]"
    echo "Options:"
    echo "  -c, --config FILE     Configuration file (default: parametric_config.ini)"
    echo "  -b, --base DIR        Base case directory (default: $DEFAULT_BASE_CASE)"
    echo "  -r, --results DIR     Results directory (default: $DEFAULT_RESULTS_DIR)"
    echo "  -j, --jobs N          Number of parallel jobs (default: $DEFAULT_PARALLEL_JOBS)"
    echo "  -t, --time STEP       Time step (default: $DEFAULT_TIME_STEP)"
    echo "  -T, --total TIME      Total simulation time (default: $DEFAULT_TOTAL_TIME)"
    echo "  -v, --verbose         Verbose output"
    echo "  -h, --help            Show this help"
    echo ""
    echo "Configuration file format:"
    echo "[PARAMETRIC]"
    echo "base_case = base_case"
    echo "results_dir = results"
    echo "parallel_jobs = 4"
    echo "time_step = 0.001"
    echo "total_time = 0.5"
}

# Parse command line options
while [ $# -gt 0 ]; do
    case $1 in
        -c|--config)
            CONFIG_FILE=$2
            shift 2
            ;;
        -b|--base)
            BASE_CASE=$2
            shift 2
            ;;
        -r|--results)
            RESULTS_DIR=$2
            shift 2
            ;;
        -j|--jobs)
            PARALLEL_JOBS=$2
            shift 2
            ;;
        -t|--time)
            TIME_STEP=$2
            shift 2
            ;;
        -T|--total)
            TOTAL_TIME=$2
            shift 2
            ;;
        -v|--verbose)
            VERBOSE=true
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

# Check if base case exists
if [ ! -d "$BASE_CASE" ]; then
    echo "Error: Base case directory '$BASE_CASE' not found"
    exit 1
fi

# Create results directory
mkdir -p "$RESULTS_DIR"
mkdir -p "$RESULTS_DIR/logs"

# Display configuration
echo "R410A Parametric Study Configuration"
echo "=================================="
echo "Base case:    $BASE_CASE"
echo "Results dir:  $RESULTS_DIR"
echo "Parallel jobs: $PARALLEL_JOBS"
echo "Time step:    $TIME_STEP"
echo "Total time:   $TOTAL_TIME"
echo "Config file:  $CONFIG_FILE"
echo ""

# Read parameter ranges from stdin or file
if [ ! -t 0 ]; then
    # Read from pipe
    PARAMETER_INPUT=$(cat)
else
    # Check if parameter file is provided
    if [ -f "param_ranges.txt" ]; then
        PARAMETER_INPUT=$(cat param_ranges.txt)
    else
        # Default parameter ranges
        PARAMETER_INPUT=$(cat <<EOF
# Mass flux (kg/m²s)
100 150 200 250 300

# Heat flux (W/m²)
2000 3000 4000 5000

# Inlet quality (-)
0.0 0.1 0.2

# Inlet subcooling (K)
2 5 10
EOF
)
    fi
fi

# Parse parameter ranges
parse_parameters() {
    local input="$1"
    local mass_fluxes heat_fluxes qualities subcoolings

    # Extract parameters using awk
    mass_fluxes=$(echo "$input" | awk '/Mass flux/ {getline; print}')
    heat_fluxes=$(echo "$input" | awk '/Heat flux/ {getline; print}')
    qualities=$(echo "$input" | awk '/Inlet quality/ {getline; print}')
    subcoolings=$(echo "$input" | awk '/Inlet subcooling/ {getline; print}')

    echo "$mass_fluxes $heat_fluxes $qualities $subcoolings"
}

# Generate parameter combinations
generate_combinations() {
    local mass_fluxes heat_fluxes qualities subcoolings

    read -r mass_fluxes heat_fluxes qualities subcoolings <<< $(parse_parameters "$PARAMETER_INPUT")

    # Generate combinations
    local combinations=()

    for G in $mass_fluxes; do
        for Q in $heat_fluxes; do
            for X_IN in $qualities; do
                for DT_SUB in $subcoolings; do
                    # Skip invalid combinations
                    if (( $(echo "$X_IN + $DT_SUB/20 > 1.0" | bc -l) )); then
                        continue
                    fi

                    combinations+=("${G}_${Q}_${X_IN}_${DT_SUB}")
                done
            done
        done
    done

    echo "${combinations[@]}"
}

# Function to create case directory
create_case() {
    local case_name=$1
    local mass_flux=$2
    local heat_flux=$3
    local inlet_quality=$4
    local subcooling=$5

    local case_dir="$RESULTS_DIR/$case_name"

    echo "Creating case: $case_name"

    # Copy base case
    cp -r "$BASE_CASE" "$case_dir"

    # Modify controlDict
    sed -i "s/timeStep $TIME_STEP/timeStep $TIME_STEP/" "$case_dir/system/controlDict"
    sed -i "s/endTime 0.5/endTime $TOTAL_TIME/" "$case_dir/system/controlDict"

    # Modify boundary conditions
    # This would use Python or sed to modify the files
    # For example:
    # sed -i "s/G \([0-9.]*\)/G $mass_flux/" "$case_dir/0/U"
    # sed -i "s/Q \([0-9.]*\)/Q $heat_flux/" "$case_dir/0/T"

    # Create run script for this case
    cat > "$case_dir/run_case.sh" <<EOF
#!/bin/bash
# Case: $case_name

echo "Starting R410A simulation for $case_name"

# Run solver
R410ASolver > log.solve 2>&1

# Check convergence
if grep -q "Finalising parallel run" log.solve; then
    echo "Case $case_name: CONVERGED"
    echo "CONVERGED" > status.txt
else
    echo "Case $case_name: FAILED"
    echo "FAILED" > status.txt
fi

# Extract results
python3 ../extract_results.py $case_name

echo "Case $case_name complete"
EOF

    chmod +x "$case_dir/run_case.sh"
}

# Function to run single case
run_single_case() {
    local case_dir=$1

    cd "$case_dir"
    ./run_case.sh > "../logs/$(basename $case_dir).log" 2>&1 &
}

# Main execution
echo "Generating parameter combinations..."
combinations=($(generate_combinations))

total_cases=${#combinations[@]}
echo "Total cases to run: $total_cases"

# Generate all cases
echo "Generating case directories..."
for combination in "${combinations[@]}"; do
    IFS='_' read -r G Q X_IN DT_SUB <<< "$combination"
    create_case "$combination" "$G" "$Q" "$X_IN" "$DT_SUB"
done

# Start progress monitor
echo ""
echo "Starting simulations..."
echo "Use 'monitor_progress.sh' to track progress"
echo ""

# Run cases in parallel
current_job=0
for case_dir in "$RESULTS_DIR"/*/; do
    if [ -d "$case_dir" ] && [ -f "$case_dir/run_case.sh" ]; then
        run_single_case "$case_dir"

        # Control parallel jobs
        ((current_job++))
        if (( current_job >= PARALLEL_JOBS )); then
            wait
            current_job=0
        fi
    fi
done

# Wait for remaining jobs
wait

echo ""
echo "All simulations complete!"
echo "Results in: $RESULTS_DIR/"

# Generate summary report
python3 generate_summary.py "$RESULTS_DIR"

# Clean up temporary files
rm -f "$RESULTS_DIR"/*/run_case.sh
```

### Configuration File

```ini
# parametric_config.ini
[PARAMETRIC]
base_case = base_case
results_dir = results
parallel_jobs = 4
time_step = 0.001
total_time = 0.5

[PATHS]
openfoam_solver = R410ASolver
post_processor = sample
yplus_calculator = yPlus

[PARAMETERS]
mass_flux_range = 100,200,300,400
heat_flux_range = 2000,3000,4000,5000
inlet_quality_range = 0.0,0.1,0.2,0.3
subcooling_range = 0,5,10,15

[MONITORING]
check_interval = 60
max_wall_time = 3600
convergence_threshold = 1e-6
```

### Python Batch Manager

```python
#!/usr/bin/env python3
"""
R410A Parametric Study Manager
Advanced batch processing with progress tracking
"""

import os
import json
import subprocess
import threading
import time
import shutil
import argparse
from datetime import datetime
from typing import Dict, List, Tuple, Optional
import pandas as pd
import numpy as np

class ParametricStudy:
    """Advanced parametric study manager"""

    def __init__(self, config_file: str):
        self.config = self.load_config(config_file)
        self.cases = {}
        self.progress = {}
        self.results = {}
        self.lock = threading.Lock()

        # Initialize directories
        os.makedirs(self.config['results_dir'], exist_ok=True)
        os.makedirs(f"{self.config['results_dir']}/logs", exist_ok=True)
        os.makedirs(f"{self.config['results_dir']}/progress", exist_ok=True)

    def load_config(self, config_file: str) -> Dict:
        """Load configuration from file"""
        with open(config_file, 'r') as f:
            config = json.load(f)

        # Set defaults
        defaults = {
            'base_case': 'base_case',
            'results_dir': 'results',
            'parallel_jobs': 4,
            'time_step': '0.001',
            'total_time': '0.5',
            'check_interval': 60,
            'max_wall_time': 3600,
            'convergence_threshold': '1e-6'
        }

        for key, value in defaults.items():
            if key not in config:
                config[key] = value

        return config

    def generate_parameter_space(self) -> List[Dict]:
        """Generate all parameter combinations"""
        parameters = self.config['parameters']
        combinations = []

        # Generate combinations
        for G in parameters['mass_flux_range']:
            for Q in parameters['heat_flux_range']:
                for X_IN in parameters['inlet_quality_range']:
                    for DT_SUB in parameters['subcooling_range']:
                        # Validate combination
                        if self._validate_combination(G, Q, X_IN, DT_SUB):
                            combinations.append({
                                'mass_flux': G,
                                'heat_flux': Q,
                                'inlet_quality': X_IN,
                                'subcooling': DT_SUB
                            })

        return combinations

    def _validate_combination(self, G, Q, X_IN, DT_SUB) -> bool:
        """Validate parameter combination"""
        # Check physical limits
        if X_IN + DT_SUB/20 > 1.0:
            return False
        if X_IN < 0 or X_IN > 1.0:
            return False
        if DT_SUB < 0:
            return False
        return True

    def create_case_directories(self):
        """Create all case directories"""
        combinations = self.generate_parameter_space()

        for i, params in enumerate(combinations):
            case_name = f"case_{i:04d}_G{params['mass_flux']}_Q{params['heat_flux']}_x{params['inlet_quality']}"
            case_dir = f"{self.config['results_dir']}/{case_name}"

            # Copy base case
            if not os.path.exists(case_dir):
                shutil.copytree(self.config['base_case'], case_dir)

            # Modify files with parameters
            self._modify_case_files(case_dir, params)

            # Initialize progress tracking
            with self.lock:
                self.cases[case_name] = {
                    'directory': case_dir,
                    'parameters': params,
                    'status': 'pending',
                    'start_time': None,
                    'end_time': None,
                    'converged': False,
                    'error': None
                }

    def _modify_case_files(self, case_dir: str, params: Dict):
        """Modify case files with parameters"""
        # Update controlDict
        control_dict = f"{case_dir}/system/controlDict"
        if os.path.exists(control_dict):
            with open(control_dict, 'r') as f:
                content = f.read()

            content = content.replace(f"deltaT {self.config['time_step']}", f"deltaT {self.config['time_step']}")
            content = content.replace(f"endTime {self.config['total_time']}", f"endTime {self.config['total_time']}")

            with open(control_dict, 'w') as f:
                f.write(content)

        # Update boundary conditions
        # This would use more sophisticated modification
        boundary_files = [
            f"{case_dir}/0/U",
            f"{case_dir}/0/p",
            f"{case_dir}/0/alpha",
            f"{case_dir}/0/T"
        ]

        for file in boundary_files:
            if os.path.exists(file):
                # Store parameter information
                params_json = json.dumps(params, indent=2)
                with open(f"{file}.params", 'w') as f:
                    f.write(params_json)

    def run_study(self):
        """Run the parametric study"""
        print(f"Starting parametric study with {len(self.cases)} cases")
        print(f"Using {self.config['parallel_jobs']} parallel jobs")

        # Start progress monitor
        monitor_thread = threading.Thread(target=self.monitor_progress)
        monitor_thread.daemon = True
        monitor_thread.start()

        # Run cases in batches
        batch_size = self.config['parallel_jobs']
        case_names = list(self.cases.keys())

        for i in range(0, len(case_names), batch_size):
            batch = case_names[i:i+batch_size]
            self.run_batch(batch)

            # Wait for batch to complete
            while any(self.cases[name]['status'] == 'running' for name in batch):
                time.sleep(5)

        # Wait for monitor thread
        monitor_thread.join()

        # Generate final report
        self.generate_report()

    def run_batch(self, case_names: List[str]):
        """Run a batch of cases"""
        for case_name in case_names:
            case_info = self.cases[case_name]
            case_dir = case_info['directory']

            # Update status
            with self.lock:
                self.cases[case_name]['status'] = 'running'
                self.cases[case_name]['start_time'] = datetime.now()

            # Start case
            cmd = [self.config['openfoam_solver']]
            proc = subprocess.Popen(
                cmd,
                cwd=case_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True
            )

            # Monitor process
            threading.Thread(
                target=self.monitor_case,
                args=(case_name, proc)
            ).start()

    def monitor_case(self, case_name: str, process: subprocess.Popen):
        """Monitor individual case"""
        case_info = self.cases[case_name]

        with open(f"{case_info['directory']}/log.solve", 'w') as log_file:
            for line in process.stdout:
                log_file.write(line)

                # Check for convergence
                if "Finalising parallel run" in line:
                    with self.lock:
                        self.cases[case_name]['converged'] = True
                        self.cases[case_name]['status'] = 'completed'
                        self.cases[case_name]['end_time'] = datetime.now()
                    break

                # Check for errors
                if "error" in line.lower() or "error" in line.lower():
                    with self.lock:
                        self.cases[case_name]['error'] = line.strip()
                        self.cases[case_name]['status'] = 'failed'
                    break

        process.wait()

    def monitor_progress(self):
        """Monitor overall progress"""
        while True:
            completed = sum(1 for case in self.cases.values() if case['status'] == 'completed')
            failed = sum(1 for case in self.cases.values() if case['status'] == 'failed')
            running = sum(1 for case in self.cases.values() if case['status'] == 'running')
            pending = sum(1 for case in self.cases.values() if case['status'] == 'pending')

            progress = {
                'timestamp': datetime.now().isoformat(),
                'total': len(self.cases),
                'completed': completed,
                'failed': failed,
                'running': running,
                'pending': pending,
                'convergence_rate': completed / len(self.cases) * 100 if len(self.cases) > 0 else 0
            }

            # Save progress
            progress_file = f"{self.config['results_dir']}/progress/progress_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(progress_file, 'w') as f:
                json.dump(progress, f, indent=2)

            # Print status
            print(f"\rProgress: {completed}/{len(self.cases)} completed, {failed} failed, {running} running")

            # Check if study is complete
            if completed + failed == len(self.cases):
                break

            time.sleep(self.config['check_interval'])

    def generate_report(self):
        """Generate final report"""
        # Collect results
        results_data = []
        for case_name, case_info in self.cases.items():
            if case_info['converged']:
                results_data.append({
                    'case': case_name,
                    'mass_flux': case_info['parameters']['mass_flux'],
                    'heat_flux': case_info['parameters']['heat_flux'],
                    'inlet_quality': case_info['parameters']['inlet_quality'],
                    'subcooling': case_info['parameters']['subcooling'],
                    'runtime': (case_info['end_time'] - case_info['start_time']).total_seconds(),
                    'converged': True
                })
            else:
                results_data.append({
                    'case': case_name,
                    'mass_flux': case_info['parameters']['mass_flux'],
                    'heat_flux': case_info['parameters']['heat_flux'],
                    'inlet_quality': case_info['parameters']['inlet_quality'],
                    'subcooling': case_info['parameters']['subcooling'],
                    'runtime': None,
                    'converged': False,
                    'error': case_info['error']
                })

        # Create DataFrame
        df = pd.DataFrame(results_data)

        # Save results
        results_file = f"{self.config['results_dir']}/parametric_results.csv"
        df.to_csv(results_file, index=False)

        # Generate summary
        summary = {
            'total_cases': len(self.cases),
            'converged_cases': len([c for c in self.cases.values() if c['converged']]),
            'failed_cases': len([c for c in self.cases.values() if not c['converged']]),
            'average_runtime': df[df['converged']]['runtime'].mean(),
            'study_duration': max(case['end_time'] for case in self.cases.values() if case['end_time']) - min(case['start_time'] for case in self.cases.values() if case['start_time'])
        }

        # Save summary
        summary_file = f"{self.config['results_dir']}/study_summary.json"
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)

        print(f"\nParametric study complete!")
        print(f"Results saved to: {results_file}")
        print(f"Summary saved to: {summary_file}")

def main():
    parser = argparse.ArgumentParser(description='R410A Parametric Study Manager')
    parser.add_argument('-c', '--config', default='parametric_config.json',
                       help='Configuration file')
    parser.add_argument('-n', '--dry-run', action='store_true',
                       help='Show parameter combinations without running')

    args = parser.parse_args()

    # Create study manager
    study = ParametricStudy(args.config)

    if args.dry_run:
        # Show parameter combinations
        combinations = study.generate_parameter_space()
        print(f"Parameter combinations: {len(combinations)}")
        for i, params in enumerate(combinations[:10]):  # Show first 10
            print(f"  {i+1}. G={params['mass_flux']}, Q={params['heat_flux']}, x={params['inlet_quality']}, ΔT={params['subcooling']}")
        if len(combinations) > 10:
            print(f"  ... and {len(combinations) - 10} more")
    else:
        # Run study
        study.create_case_directories()
        study.run_study()

if __name__ == '__main__':
    main()
```

### Progress Monitor Script

```bash
#!/bin/bash
# Monitor progress of parametric study

monitor_progress() {
    RESULTS_DIR=$1
    INTERVAL=${2:-60}

    echo "Monitoring progress (refresh every $INTERVAL seconds)"
    echo "Press Ctrl+C to stop monitoring"
    echo ""

    while true; do
        # Count cases by status
        total=$(find "$RESULTS_DIR" -name "status.txt" | wc -l)
        converged=$(grep -r "CONVERGED" "$RESULTS_DIR" 2>/dev/null | wc -l)
        failed=$(grep -r "FAILED" "$RESULTS_DIR" 2>/dev/null | wc -l)
        running=$(find "$RESULTS_DIR" -name "*.log" -mmin -1 2>/dev/null | wc -l)

        echo -ne "\rTotal: $total, Converged: $converged, Failed: $failed, Running: $running"

        # Check if all cases are complete
        if [ "$converged" -gt 0 ] && [ "$((converged + failed))" -eq "$total" ] && [ "$total" -gt 0 ]; then
            echo ""
            echo "All cases complete!"
            break
        fi

        sleep $INTERVAL
    done
}

# Show resource usage
show_resources() {
    echo ""
    echo "Resource Usage:"
    echo "CPU: $(top -l 1 | grep "CPU usage" | awk '{print $3}' | cut -d',' -f1)"
    echo "Memory: $(ps -cax -orss,comm | sort -nr | head -5 | awk '{print $1/1024/1024 " GB " $2}')"
    echo "Disk: $(df -h . | tail -1 | awk '{print $5 " used"}')"
}

# Main monitoring loop
while true; do
    show_resources
    monitor_progress "$1" "$2"

    # Check if we should continue monitoring
    if [ "$3" = "--continuous" ]; then
        sleep 300  # Wait 5 minutes before next check
    else
        break
    fi
done
```

#### Shell Script Implementation

```bash
#!/bin/bash
# R410A Batch Processing Shell Script
# Automated parameter study runner

# Configuration
BASE_CASE="base_case"
RESULTS_DIR="results"
PARALLEL_JOBS=4

# Function to run single case
run_case() {
    local case_name=$1
    echo "Running case: $case_name"
    cd $case_name
    R410ASolver > log.solve 2>&1
    if grep -q "Finalising parallel run" log.solve; then
        echo "Case $case_name: SUCCESS"
        cp ../template/results_template.csv ../results/${case_name}_results.csv
    else
        echo "Case $case_name: FAILED"
    fi
    cd ..
}

# Main execution
for i in {1..10}; do
    run_case "case_$i" &
    if (( i % PARALLEL_JOBS == 0 )); then
        wait
    fi
done
```

### Usage Examples

#### Shell Script Usage
```bash
# Run parametric study with default configuration
./run_parametric.sh

# Run with custom configuration
./run_parametric.sh -b my_base_case -r my_results -j 8

# Monitor progress in another terminal
./monitor_progress.sh results
```

### Python API Usage

```python
from parametric_study import ParametricStudy

# Create study
study = ParametricStudy('parametric_config.json')

# Generate parameter combinations
combinations = study.generate_parameter_space()
print(f"Total combinations: {len(combinations)}")

# Run study
study.create_case_directories()
study.run_study()

# Access results
results = pd.read_csv('results/parametric_results.csv')
```

### Advanced Configuration

```python
# Custom parameter generation
def generate_custom_space():
    """Generate non-uniform parameter space"""
    import numpy as np

    # Log-spaced mass fluxes
    mass_fluxes = np.logspace(2, 3, 5)  # 100 to 1000 kg/m²s

    # Linear heat fluxes
    heat_fluxes = np.linspace(2000, 5000, 4)

    # Quality at saturation for different pressures
    qualities = [0.0, 0.05, 0.1, 0.15]

    return combinations
```

## Integration with Analysis Tools

### Results Processing

```python
def process_parametric_results(results_dir):
    """Process parametric study results"""
    # Load results
    df = pd.read_csv(f"{results_dir}/parametric_results.csv")

    # Create analysis
    analysis = {
        'convergence_analysis': analyze_convergence(df),
        'sensitivity_analysis': perform_sensitivity_analysis(df),
        'optimal_conditions': find_optimal_conditions(df)
    }

    # Save analysis
    with open(f"{results_dir}/analysis_report.json", 'w') as f:
        json.dump(analysis, f, indent=2)
```

### Visualization

```python
def plot_results(results_df):
    """Create visualization of parametric study results"""
    import matplotlib.pyplot as plt

    # Create plots
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))

    # Plot 1: Convergence by mass flux
    ax1 = axes[0, 0]
    convergence_by_flux = results_df.groupby('mass_flux')['converged'].mean() * 100
    ax1.bar(convergence_by_flux.index, convergence_by_flux.values)
    ax1.set_xlabel('Mass Flux (kg/m²s)')
    ax1.set_ylabel('Convergence Rate (%)')

    # Plot 2: Runtime distribution
    ax2 = axes[0, 1]
    ax2.hist(results_df['runtime'], bins=20)
    ax2.set_xlabel('Runtime (s)')
    ax2.set_ylabel('Frequency')

    # Plot 3: Parameter sensitivity
    ax3 = axes[1, 0]
    # Create sensitivity matrix
    ...

    # Plot 4: Optimal operating conditions
    ax4 = axes[1, 1]
    # Plot Pareto front
    ...

    plt.tight_layout()
    plt.savefig(f"{results_dir}/parametric_analysis.png")
```

## Advanced Features

### 1. Adaptive Mesh Refinement

```python
def adaptive_mesh_refinement(case_dir, params):
    """Adaptively refine mesh based on parameters"""
    # Estimate required y+ based on mass flux
    target_yplus = 1.0  # Target y+ for resolved boundary layer

    # Calculate required first cell size
    U = params['mass_flux'] / rho_l  # Estimate velocity
    nu = get_viscosity(params['heat_flux'])  # Get viscosity
    delta_y = target_yplus * nu / U

    # Update mesh
    update_mesh_spacing(case_dir, delta_y)
```

### 2. Dynamic Time Step Control

```python
def dynamic_time_step(case_dir, params):
    """Adjust time step based on CFL condition"""
    # Estimate velocity scale
    U_scale = params['mass_flux'] / rho_l

    # Calculate CFL-limited time step
    delta_x = get_mesh_spacing(case_dir)
    cfl = 0.5
    dt_cfl = cfl * delta_x / U_scale

    # Update controlDict
    update_time_step(case_dir, dt_cfl)
```

### 3. Fault Tolerance

```python
def fault_tolerance_mechanism(case_dir):
    """Handle solver failures"""
    if check_solver_failed(case_dir):
        # Try reducing time step
        reduce_time_step(case_dir)

        # Retry
        if retry_solver(case_dir):
            return True
        else:
            # Try different solver settings
            adjust_solver_settings(case_dir)
            retry_solver(case_dir)

    return False
```

## Troubleshooting

### Common Issues

1. **Memory errors**
   - Solution: Reduce parallel jobs or case complexity
   - Use memory monitoring

2. **Convergence problems**
   - Solution: Adjust time step or solver settings
   - Implement adaptive time stepping

3. **Disk space issues**
   - Solution: Implement cleanup of temporary files
   - Use compression for large result files

### Debug Mode

```bash
# Run with debug output
./run_parametric.sh -v

# Dry run to check parameter generation
./run_parametric.sh --dry-run

# Monitor specific case
tail -f results/case_0001/log.solve
```

---

**Note**: For production use, consider implementing checkpointing, result caching, and integration with HPC systems.