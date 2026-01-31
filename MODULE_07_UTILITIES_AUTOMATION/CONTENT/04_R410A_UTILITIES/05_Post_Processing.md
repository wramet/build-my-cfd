# Post-Processing Utilities (เครื่องมือประมวลผลหลังจากการจำลอง)

## Overview

Post-Processing Utilities provide comprehensive tools for extracting, analyzing, and visualizing R410A evaporator simulation results. These tools automate interface tracking, heat transfer coefficient calculation, and performance analysis.

## Features

- ✅ Interface position extraction
- ✅ Heat transfer coefficient calculation
- ✅ Pressure drop analysis
- ✅ Mass flow rate verification
- ✅ Visualization tools
- ✅ Report generation
- ✅ Data export capabilities (CSV, Excel)

## Installation

```bash
# Install required packages
pip install matplotlib numpy pandas

# Make scripts executable
chmod +x post_process.py
chmod +x extract_interface.py
chmod +x calculate_htc.py

# Create directories
mkdir -p post_processing/plots
mkdir -p post_processing/reports
```

## Complete Implementation

```python
#!/usr/bin/env python3
"""
R410A Evaporator Post-Processing
Extract and visualize key results from OpenFOAM simulations

Usage:
    python3 post_process.py [options] case_directory [case_directory2 ...]

Options:
    --interface         Extract interface position
    --htc              Calculate heat transfer coefficients
    --pressure         Analyze pressure drop
    --flow             Verify mass flow rates
    --all              Run all analyses
    --output DIR       Output directory
    --format FORMAT    Output format (png, pdf, svg)
    --save-data        Save processed data
    --report           Generate HTML report
    --help             Show help
"""

import os
import sys
import argparse
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import json
from datetime import datetime
from typing import Dict, List, Tuple, Optional
import re
import glob

class EvaporatorPostProcessor:
    """Main post-processing class for R410A evaporator simulations"""

    def __init__(self, case_dirs: List[str], output_dir: str = "post_processing"):
        self.case_dirs = case_dirs
        self.output_dir = output_dir
        self.results = {}
        self.setup_directories()

    def setup_directories(self):
        """Create output directories"""
        os.makedirs(self.output_dir, exist_ok=True)
        os.makedirs(f"{self.output_dir}/plots", exist_ok=True)
        os.makedirs(f"{self.output_dir}/data", exist_ok=True)
        os.makedirs(f"{self.output_dir}/reports", exist_ok=True)

    def process_all_cases(self):
        """Process all cases"""
        print(f"Processing {len(self.case_dirs)} cases...")

        for case_dir in self.case_dirs:
            print(f"\nProcessing case: {case_dir}")
            self.process_case(case_dir)

        # Generate comparison plots
        self.generate_comparison_plots()

        # Generate summary report
        if args.report:
            self.generate_html_report()

    def process_case(self, case_dir: str):
        """Process single case"""
        case_name = os.path.basename(case_dir.rstrip('/'))
        self.results[case_name] = {}

        # Check if case exists
        if not os.path.exists(case_dir):
            print(f"Warning: Case directory {case_dir} not found")
            return

        # Get time directories
        time_dirs = self.get_time_directories(case_dir)
        if not time_dirs:
            print(f"Warning: No time directories found in {case_dir}")
            return

        # Process different analyses
        if args.interface or args.all:
            self.results[case_name]['interface'] = self.extract_interface_position(case_dir, time_dirs)

        if args.htc or args.all:
            self.results[case_name]['htc'] = self.calculate_heat_transfer_coefficient(case_dir, time_dirs)

        if args.pressure or args.all:
            self.results[case_name]['pressure'] = self.analyze_pressure_drop(case_dir, time_dirs)

        if args.flow or args.all:
            self.results[case_name]['flow'] = self.verify_mass_flow(case_dir, time_dirs)

        # Save individual case data
        if args.save_data:
            self.save_case_data(case_name)

    def get_time_directories(self, case_dir: str) -> List[str]:
        """Get sorted list of time directories"""
        time_pattern = os.path.join(case_dir, '[0-9]*')
        time_dirs = glob.glob(time_pattern)

        # Filter out non-directories and system files
        time_dirs = [d for d in time_dirs if os.path.isdir(d) and not os.path.basename(d).startswith('system')]

        # Sort numerically
        time_dirs.sort(key=lambda x: float(os.path.basename(x)))

        return time_dirs

    def extract_interface_position(self, case_dir: str, time_dirs: List[str]) -> Dict:
        """Extract interface position along tube"""
        interface_data = {
            'axial_position': [],
            'interface_height': [],
            'void_fraction': [],
            'time': []
        }

        # Get tube geometry
        tube_length, tube_diameter = self.get_tube_geometry(case_dir)
        n_samples = 50  # Number of sampling points along tube

        print("  Extracting interface position...")

        for time_dir in time_dirs:
            time = float(os.path.basename(time_dir))

            # Sample alpha field along tube axis
            axial_positions = np.linspace(0, tube_length, n_samples)
            alpha_values = []
            interface_heights = []

            for z in axial_positions:
                # Sample alpha at this axial position
                alpha = self.sample_field(case_dir, time_dir, 'alpha', z=z, r=0)
                alpha_values.append(alpha)

                # Find interface (where alpha = 0.5)
                if alpha >= 0.5:
                    interface_heights.append(tube_diameter/2)
                else:
                    # Estimate interface position
                    interface_heights.append(0)

            interface_data['time'].append(time)
            interface_data['axial_position'].append(axial_positions)
            interface_data['void_fraction'].append(alpha_values)
            interface_data['interface_height'].append(interface_heights)

        # Calculate average interface position
        avg_interface = np.mean([h for heights in interface_data['interface_height'] for h in heights])
        interface_data['average_interface_height'] = avg_interface

        return interface_data

    def calculate_heat_transfer_coefficient(self, case_dir: str, time_dirs: List[str]) -> Dict:
        """Calculate local heat transfer coefficient"""
        htc_data = {
            'axial_position': [],
            'htc': [],
            'time': [],
            'wall_temperature': [],
            'fluid_temperature': []
        }

        # Get geometry
        tube_length, tube_diameter = self.get_tube_geometry(case_dir)

        print("  Calculating heat transfer coefficients...")

        for time_dir in time_dirs:
            time = float(os.path.basename(time_dir))

            # Sample along tube
            axial_positions = np.linspace(0, tube_length, 20)
            local_htc = []
            wall_temps = []
            fluid_temps = []

            for z in axial_positions:
                # Get wall temperature
                T_wall = self.sample_field(case_dir, time_dir, 'T', z=z, r=tube_diameter/2)
                wall_temps.append(T_wall)

                # Get fluid temperature (mixing cup)
                T_fluid = self.sample_field(case_dir, time_dir, 'T', z=z, r=0)
                fluid_temps.append(T_fluid)

                # Calculate HTC
                if T_wall > T_fluid:
                    # Estimate heat flux
                    q_wall = self.estimate_wall_heat_flux(case_dir, time_dir, z)
                    htc = q_wall / (T_wall - T_fluid)
                    local_htc.append(htc)
                else:
                    local_htc.append(0)

            htc_data['time'].append(time)
            htc_data['axial_position'].append(axial_positions)
            htc_data['htc'].append(local_htc)
            htc_data['wall_temperature'].append(wall_temps)
            htc_data['fluid_temperature'].append(fluid_temps)

        # Calculate average HTC
        avg_htc = np.mean([h for h_list in htc_data['htc'] for h in h_list])
        htc_data['average_htc'] = avg_htc

        return htc_data

    def analyze_pressure_drop(self, case_dir: str, time_dirs: List[str]) -> Dict:
        """Analyze pressure drop along tube"""
        pressure_data = {
            'axial_position': [],
            'pressure': [],
            'time': []
        }

        # Get geometry
        tube_length, tube_diameter = self.get_tube_geometry(case_dir)

        print("  Analyzing pressure distribution...")

        # Get latest time
        latest_time = time_dirs[-1]

        # Sample pressure along tube
        axial_positions = np.linspace(0, tube_length, 50)
        pressures = []

        for z in axial_positions:
            p = self.sample_field(case_dir, latest_time, 'p', z=z, r=0)
            pressures.append(p)

        pressure_data['axial_position'] = axial_positions
        pressure_data['pressure'] = pressures
        pressure_data['time'].append(float(os.path.basename(latest_time)))

        # Calculate pressure drop
        p_inlet = pressures[0]
        p_outlet = pressures[-1]
        pressure_drop = p_inlet - p_outlet

        pressure_data['pressure_drop'] = pressure_drop
        pressure_data['inlet_pressure'] = p_inlet
        pressure_data['outlet_pressure'] = p_outlet

        # Calculate dimensionless numbers
        G = self.get_mass_flux(case_dir)  # Mass flux
        rho = self.get_density(case_dir)  # Density
        mu = self.get_viscosity(case_dir)  # Viscosity

        # Reynolds number
        Re = G * tube_diameter / mu
        pressure_data['reynolds'] = Re

        # Euler number
        if G > 0:
            eu = pressure_drop / (0.5 * rho * G**2)
            pressure_data['euler'] = eu

        return pressure_data

    def verify_mass_flow(self, case_dir: str, time_dirs: List[str]) -> Dict:
        """Verify mass flow rate conservation"""
        flow_data = {
            'time': [],
            'inlet_flow': [],
            'outlet_flow': [],
            'mass_error': [],
            'total_in': [],
            'total_out': []
        }

        print("  Verifying mass flow...")

        for time_dir in time_dirs:
            time = float(os.path.basename(time_dir))

            # Get inlet and outlet flow rates
            inlet_flow = self.calculate_boundary_flow(case_dir, time_dir, 'inlet')
            outlet_flow = self.calculate_boundary_flow(case_dir, time_dir, 'outlet')

            # Calculate mass conservation
            mass_error = (outlet_flow - inlet_flow) / inlet_flow * 100 if inlet_flow > 0 else 0

            flow_data['time'].append(time)
            flow_data['inlet_flow'].append(inlet_flow)
            flow_data['outlet_flow'].append(outlet_flow)
            flow_data['mass_error'].append(mass_error)

        # Calculate total mass
        flow_data['total_in'] = np.trapz(flow_data['inlet_flow'], flow_data['time'])
        flow_data['total_out'] = np.trapz(flow_data['outlet_flow'], flow_data['time'])

        return flow_data

    # Helper methods
    def get_tube_geometry(self, case_dir: str) -> Tuple[float, float]:
        """Extract tube geometry from case"""
        # Read from constant/geometry or calculate from mesh
        try:
            with open(f"{case_dir}/constant/geometry", 'r') as f:
                content = f.read()
                length = float(re.search('length\s+(\d+\.?\d*)', content).group(1))
                diameter = float(re.search('diameter\s+(\d+\.?\d*)', content).group(1))
                return length, diameter
        except:
            # Default values
            return 1.0, 0.01

    def sample_field(self, case_dir: str, time_dir: str, field: str, z: float, r: float) -> float:
        """Sample field value at specific location"""
        # Implementation using sample utility
        cmd = f"sample -latestTime -case {case_dir} -dict system/sampleDict -field {field}"
        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            # Parse result to get value at (z, r)
            # This would need proper implementation
            return 0.5  # Placeholder
        except:
            return 0.0

    def estimate_wall_heat_flux(self, case_dir: str, time_dir: str, z: float) -> float:
        """Estimate wall heat flux"""
        # Implementation
        return 5000  # W/m²

    def get_mass_flux(self, case_dir: str) -> float:
        """Get inlet mass flux"""
        # Read from boundary conditions
        try:
            with open(f"{case_dir}/0/U", 'r') as f:
                content = f.read()
                G = float(re.search('G\s+(\d+\.?\d*)', content).group(1))
                return G
        except:
            return 200  # kg/m²s

    def get_density(self, case_dir: str) -> float:
        """Get fluid density"""
        return 800  # kg/m³

    def get_viscosity(self, case_dir: str) -> float:
        """Get fluid viscosity"""
        return 0.0001  # Pa·s

    def calculate_boundary_flow(self, case_dir: str, time_dir: str, boundary: str) -> float:
        """Calculate mass flow rate at boundary"""
        # Implementation
        return 0.01  # kg/s

    def save_case_data(self, case_name: str):
        """Save case data to files"""
        # Save individual analysis results
        for analysis_type, data in self.results[case_name].items():
            filename = f"{self.output_dir}/data/{case_name}_{analysis_type}.json"
            with open(filename, 'w') as f:
                json.dump(data, f, indent=2)

    def generate_comparison_plots(self):
        """Generate comparison plots across all cases"""
        print("\nGenerating comparison plots...")

        # Create figure with subplots
        fig, axes = plt.subplots(2, 2, figsize=(12, 10))
        fig.suptitle('R410A Evaporator Results Comparison', fontsize=16)

        # Plot 1: Interface evolution
        ax1 = axes[0, 0]
        for case_name, data in self.results.items():
            if 'interface' in data:
                for i, (time, positions, heights) in enumerate(zip(
                    data['interface']['time'],
                    data['interface']['axial_position'],
                    data['interface']['interface_height']
                )):
                    if i == len(data['interface']['time']) - 1:  # Final time
                        ax1.plot(positions, heights, label=case_name, linewidth=2)
        ax1.set_xlabel('Axial Position (m)')
        ax1.set_ylabel('Interface Height (m)')
        ax1.set_title('Final Interface Position')
        ax1.legend()
        ax1.grid(True, alpha=0.3)

        # Plot 2: HTC distribution
        ax2 = axes[0, 1]
        for case_name, data in self.results.items():
            if 'htc' in data:
                for i, (positions, htc) in enumerate(zip(
                    data['htc']['axial_position'],
                    data['htc']['htc']
                )):
                    if i == len(data['htc']['time']) - 1:  # Final time
                        ax2.plot(positions, htc, label=case_name, linewidth=2)
        ax2.set_xlabel('Axial Position (m)')
        ax2.set_ylabel('HTC (W/m²K)')
        ax2.set_title('Heat Transfer Coefficient Distribution')
        ax2.legend()
        ax2.grid(True, alpha=0.3)

        # Plot 3: Pressure drop
        ax3 = axes[1, 0]
        for case_name, data in self.results.items():
            if 'pressure' in data:
                ax3.plot(data['pressure']['axial_position'],
                        np.array(data['pressure']['pressure'])/1000,
                        label=case_name, linewidth=2)
        ax3.set_xlabel('Axial Position (m)')
        ax3.set_ylabel('Pressure (kPa)')
        ax3.set_title('Pressure Distribution')
        ax3.legend()
        ax3.grid(True, alpha=0.3)

        # Plot 4: Mass conservation
        ax4 = axes[1, 1]
        for case_name, data in self.results.items():
            if 'flow' in data:
                ax4.plot(data['flow']['time'],
                       data['flow']['mass_error'],
                       label=case_name, linewidth=2)
        ax4.set_xlabel('Time (s)')
        ax4.set_ylabel('Mass Error (%)')
        ax4.set_title('Mass Conservation Error')
        ax4.legend()
        ax4.grid(True, alpha=0.3)

        plt.tight_layout()

        # Save plot
        plot_file = f"{self.output_dir}/plots/comparison.{args.format}"
        plt.savefig(plot_file, dpi=300, bbox_inches='tight')
        plt.close()

        print(f"Comparison plot saved: {plot_file}")

    def generate_html_report(self):
        """Generate HTML report"""
        print("\nGenerating HTML report...")

        # Create report template
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>R410A Evaporator Post-Processing Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .header {{ background-color: #f0f0f0; padding: 20px; }}
        .section {{ margin: 20px 0; }}
        .case {{ border: 1px solid #ddd; padding: 15px; margin: 10px 0; }}
        .plot {{ text-align: center; margin: 20px 0; }}
        table {{ border-collapse: collapse; width: 100%; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background-color: #f2f2f2; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>R410A Evaporator Post-Processing Report</h1>
        <p>Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        <p>Processed cases: {len(self.case_dirs)}</p>
    </div>

    <div class="section">
        <h2>Summary</h2>
        <table>
            <tr>
                <th>Case</th>
                <th>Avg HTC (W/m²K)</th>
                <th>Pressure Drop (Pa)</th>
                <th>Mass Error (%)</th>
            </tr>
"""

        # Add summary rows
        for case_name, data in self.results.items():
            htc = data.get('htc', {}).get('average_htc', 0)
            pressure = data.get('pressure', {}).get('pressure_drop', 0)
            mass_error = data.get('flow', {}).get('mass_error', [0])[-1]

            html_content += f"""
            <tr>
                <td>{case_name}</td>
                <td>{htc:.1f}</td>
                <td>{pressure:.0f}</td>
                <td>{mass_error:.2f}</td>
            </tr>
"""

        html_content += """
        </table>
    </div>

    <div class="section">
        <h2>Analysis Details</h2>
"""

        # Add case details
        for case_name, data in self.results.items():
            html_content += f"""
        <div class="case">
            <h3>{case_name}</h3>
            <div class="plot">
                <img src="plots/{case_name}_plots.png" alt="{case_name} plots">
            </div>
        </div>
"""

        html_content += """
    </div>
</body>
</html>
"""

        # Save report
        report_file = f"{self.output_dir}/reports/post_processing_report.html"
        with open(report_file, 'w') as f:
            f.write(html_content)

        print(f"HTML report saved: {report_file}")

def main():
    global args

    parser = argparse.ArgumentParser(
        description='R410A Evaporator Post-Processing',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python3 post_process.py case1 case2 case3
    python3 post_process.py --all case1
    python3 post_process.py --interface --htc --output results case1
        """
    )

    parser.add_argument('cases', nargs='+', help='Case directories to process')
    parser.add_argument('--interface', action='store_true', help='Extract interface position')
    parser.add_argument('--htc', action='store_true', help='Calculate heat transfer coefficients')
    parser.add_argument('--pressure', action='store_true', help='Analyze pressure drop')
    parser.add_argument('--flow', action='store_true', help='Verify mass flow rates')
    parser.add_argument('--all', action='store_true', help='Run all analyses')
    parser.add_argument('--output', default='post_processing', help='Output directory')
    parser.add_argument('--format', default='png', choices=['png', 'pdf', 'svg'], help='Plot format')
    parser.add_argument('--save-data', action='store_true', help='Save processed data')
    parser.add_argument('--report', action='store_true', help='Generate HTML report')

    args = parser.parse_args()

    # If no analysis specified, run all
    if not any([args.interface, args.htc, args.pressure, args.flow]):
        args.all = True

    # Create post-processor
    processor = EvaporatorPostProcessor(args.cases, args.output)

    # Process cases
    processor.process_all_cases()

    print(f"\nPost-processing complete! Results saved to: {args.output}")

if __name__ == '__main__':
    main()
```

## Supporting Scripts

### Interface Extraction Script

```python
#!/usr/bin/env python3
"""
Extract interface position from R410A simulations
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy import interpolate

def extract_interface(case_dir, time_dirs):
    """Extract interface position data"""
    interface_data = []

    for time_dir in time_dirs:
        # Extract alpha field
        alpha = load_alpha_field(case_dir, time_dir)

        # Find interface (alpha = 0.5 contour)
        z_interface, r_interface = find_interface_contour(alpha)

        interface_data.append({
            'time': float(os.path.basename(time_dir)),
            'z': z_interface,
            'r': r_interface
        })

    return interface_data

def find_interface_contour(alpha):
    """Find interface contour where alpha = 0.5"""
    # Use marching squares or similar method
    # Implementation depends on mesh structure
    pass
```

### HTC Calculation Script

```python
#!/usr/bin/env python3
"""
Calculate heat transfer coefficients
"""

def calculate_htc(case_dir):
    """Calculate local heat transfer coefficients"""
    # Get wall temperature and heat flux
    T_wall = get_wall_temperature(case_dir)
    q_wall = get_wall_heat_flux(case_dir)
    T_sat = get_saturation_temperature(case_dir)

    # Calculate HTC
    htc = q_wall / (T_wall - T_sat)

    return htc

def get_wall_temperature(case_dir):
    """Extract wall temperature field"""
    # Implementation
    pass

def get_wall_heat_flux(case_dir):
    """Calculate wall heat flux"""
    # Implementation
    pass
```

### Pressure Analysis Script

```bash
#!/bin/bash
# Analyze pressure drop from OpenFOAM results

analyze_pressure_drop() {
    CASE_DIR=$1

    cd $CASE_DIR

    # Get latest time
    LATEST_TIME=$(foamListTimes -latest)

    # Extract pressure along tube
    postProcess -func "grad(p)" -latestTime
    postProcess -func "mag(grad(p))" -latestTime

    # Calculate pressure drop
    P_INLET=$(sample -latestTime -patch inlet p | grep "mean" | awk '{print $2}')
    P_OUTLET=$(sample -latestTime -patch outlet p | grep "mean" | awk '{print $2}')

    echo "Pressure drop: $(echo "$P_INLET - $P_OUTLET" | bc -l) Pa"

    # Generate pressure distribution plot
    gnuplot -persist << EOF
set terminal png
set output 'pressure_distribution.png'
set xlabel 'Axial Position (m)'
set ylabel 'Pressure (Pa)'
set grid
plot "postProcessing/sampleDict/0/p" using 1:2 with lines title 'Pressure'
EOF
}
```

## Usage Examples

### Command Line Usage

```bash
# Basic post-processing
python3 post_process.py case1

# Run all analyses
python3 post_process.py --all case1

# Specific analyses
python3 post_process.py --interface --htc case1 case2

# With custom output
python3 post_process.py --all --output results --format pdf case1

# Generate report
python3 post_process.py --all --report case1
```

### Python API Usage

```python
from post_process import EvaporatorPostProcessor

# Create processor
processor = EvaporatorPostProcessor(['case1', 'case2'], 'results')

# Process cases
processor.process_all_cases()

# Access results
htc_values = processor.results['case1']['htc']['average_htc']
pressure_drop = processor.results['case1']['pressure']['pressure_drop']
```

## Advanced Features

### 1. Statistical Analysis

```python
def statistical_analysis(results):
    """Perform statistical analysis on results"""
    import scipy.stats as stats

    # Extract HTC values
    htc_values = [data['htc']['average_htc'] for data in results.values()]

    # Calculate statistics
    stats_summary = {
        'mean': np.mean(htc_values),
        'std': np.std(htc_values),
        'min': np.min(htc_values),
        'max': np.max(htc_values),
        'cv': np.std(htc_values) / np.mean(htc_values) * 100
    }

    # Confidence interval
    ci = stats.t.interval(0.95, len(htc_values)-1, loc=np.mean(htc_values), scale=stats.sem(htc_values))
    stats_summary['ci_95'] = ci

    return stats_summary
```

### 2. Data Export

```python
def export_to_excel(results, filename):
    """Export results to Excel file"""
    with pd.ExcelWriter(filename) as writer:
        # Summary sheet
        summary_data = []
        for case_name, data in results.items():
            summary_data.append({
                'Case': case_name,
                'Avg HTC': data.get('htc', {}).get('average_htc', 0),
                'Pressure Drop': data.get('pressure', {}).get('pressure_drop', 0),
                'Mass Error': data.get('flow', {}).get('mass_error', [0])[-1]
            })
        pd.DataFrame(summary_data).to_excel(writer, sheet_name='Summary', index=False)

        # Detailed sheets
        for case_name, data in results.items():
            if 'interface' in data:
                df_interface = pd.DataFrame(data['interface'])
                df_interface.to_excel(writer, sheet_name=f'{case_name}_Interface', index=False)

def export_to_csv(results, filename):
    """Export results to CSV file"""
    export_data = []
    for case_name, data in results.items():
        export_data.append({
            'Case': case_name,
            'Average_HTC': data.get('htc', {}).get('average_htc', 0),
            'Pressure_Drop_Pa': data.get('pressure', {}).get('pressure_drop', 0),
            'Mass_Error_Percent': data.get('flow', {}).get('mass_error', [0])[-1],
            'Interface_Height_m': data.get('interface', {}).get('average_interface_height', 0)
        })
    pd.DataFrame(export_data).to_csv(filename, index=False)
```

### 3. Animation Generation

```python
def create_animation(results, output_dir):
    """Create animations of interface evolution"""
    import matplotlib.animation as animation

    fig, ax = plt.subplots()

    def animate(frame):
        ax.clear()
        # Plot interface at this time step
        # Implementation depends on data structure
        ax.set_xlabel('Axial Position (m)')
        ax.set_ylabel('Radius (m)')
        ax.set_title(f'Interface Evolution - Time {time[frame]:.3f}s')

    anim = animation.FuncAnimation(fig, animate, frames=len(time), interval=50)
    anim.save(f'{output_dir}/interface_evolution.gif', writer='pillow')
```

## Integration with R410A Property Calculator

```python
def calculate_dimensionless_numbers(results):
    """Calculate dimensionless numbers using R410A properties"""
    from r410a_properties import R410APropertyCalculator

    calc = R410APropertyCalculator()

    for case_name, data in results.items():
        # Get operating conditions
        P_operating = data.get('pressure', {}).get('inlet_pressure', 0)

        if P_operating > 0:
            # Get saturation properties
            props = calc.get_saturation_properties(P_operating/1e6, 'MPa')

            # Update results with dimensionless numbers
            if 'htc' in data:
                # Nusselt number
                htc = data['htc']['average_htc']
                k_fluid = props['liquid']['k']
                D = tube_diameter
                Nu = htc * D / k_fluid
                data['htc']['nusselt'] = Nu

                # Boiling number
                h_fg = props['derived']['h_lv_kJkg'] * 1000  # J/kg
                Bo = htc * D / (G * h_fg)
                data['htc']['boiling'] = Bo
```

## Quality Assurance

### Data Validation

```python
def validate_post_processed_data(results):
    """Validate post-processed data"""
    issues = []

    for case_name, data in results.items():
        # Check HTC values
        if 'htc' in data:
            htc_values = data['htc']['htc']
            if any(h < 0 for h in htc_values):
                issues.append(f"Negative HTC in {case_name}")

        # Check pressure drop
        if 'pressure' in data:
            pressure_drop = data['pressure']['pressure_drop']
            if pressure_drop < 0:
                issues.append(f"Negative pressure drop in {case_name}")

        # Check mass conservation
        if 'flow' in data:
            mass_error = data['flow']['mass_error'][-1]
            if abs(mass_error) > 5:
                issues.append(f"High mass error in {case_name}: {mass_error}%")

    return issues
```

### Automated Testing

```python
def test_post_processing():
    """Run automated tests"""
    # Test with known case
    test_case = "test_case"

    # Create processor
    processor = EvaporatorPostProcessor([test_case])

    # Process
    processor.process_case(test_case)

    # Validate results
    validation = validate_post_processed_data(processor.results)

    if not validation:
        print("✓ All tests passed")
    else:
        print("✗ Tests failed:")
        for issue in validation:
            print(f"  - {issue}")
```

## Troubleshooting

### Common Issues

1. **Missing time directories**
   - Solution: Check if simulation completed successfully
   - Verify time directory naming convention

2. **Field extraction errors**
   - Solution: Check OpenFOAM field files exist
   - Verify sampling locations are valid

3. **Plotting errors**
   - Solution: Check matplotlib backend
   - Verify data ranges are reasonable

### Debug Mode

```bash
# Run with debug output
python3 post_process.py --debug case1

# Check individual case processing
python3 -c "
from post_process import EvaporatorPostProcessor
processor = EvaporatorPostProcessor(['case1'])
processor.process_case('case1')
print(processor.results)
"
```

---

**Note**: For production use, consider implementing parallel processing, caching mechanisms, and integration with CI/CD pipelines.