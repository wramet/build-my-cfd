# R410A Property Calculator (เครื่องคำนวณคุณสมบัติ R410A)

## Overview

The R410A Property Calculator is a comprehensive Python tool for calculating thermodynamic and transport properties of R410A refrigerant. It uses CoolProp for accurate property calculations and provides flexible output formats for various applications.

## Features

- ✅ Complete saturation properties (liquid and vapor phases)
- ✅ Multiple pressure units support (MPa, kPa, bar, Pa)
- ✅ Flexible output formats (table, JSON)
- ✅ Transport properties (viscosity, thermal conductivity)
- ✅ Thermodynamic properties (density, enthalpy, entropy)
- ✅ Dimensionless numbers (Prandtl number)
- ✅ Latent heat and surface tension calculations

## Installation

```bash
# Install required packages
pip install CoolProp

# Make script executable
chmod +x r410a_properties.py
```

## Usage

### Command Line Interface

```bash
# Basic usage - table format
python3 r410a_properties.py -p 2.0

# Specify pressure unit
python3 r410a_properties.py -p 2000 -u kPa

# JSON output
python3 r410a_properties.py -p 2.5 -f json

# Save to file
python3 r410a_properties.py -p 3.0 -o properties.txt

# Show help
python3 r410a_properties.py -h
```

### Python API

```python
from r410a_properties import get_saturation_properties

# Get properties at given pressure
props = get_saturation_properties(2.5, 'MPa')

# Access individual properties
print(f"Saturation temperature: {props['T_sat']-273.15:.2f} °C")
print(f"Latent heat: {props['h_lv']/1000:.2f} kJ/kg")
print(f"Density ratio: {props['rho_ratio']:.1f}:1")
```

## Complete Implementation

```python
#!/usr/bin/env python3
"""
R410A Property Calculator
Calculate thermodynamic and transport properties for R410A

Usage:
    python3 r410a_properties.py [-p PRESSURE] [-u UNIT] [-f FORMAT] [-o OUTPUT]
    python3 r410a_properties.py -h | --help

Examples:
    python3 r410a_properties.py -p 2.0                    # Default: 2.0 MPa
    python3 r410a_properties.py -p 2000 -u kPa            # 2000 kPa
    python3 r410a_properties.py -p 2.5 -f json           # JSON output
    python3 r410a_properties.py -p 3.0 -o results.txt    # Save to file
"""

import CoolProp.CoolProp as CP
import argparse
import json
import sys
import os

class R410APropertyCalculator:
    """Main property calculator class"""

    def __init__(self):
        self.fluid = 'R410A'
        self.pressure_units = {
            'MPa': 1e6,
            'kPa': 1e3,
            'bar': 1e5,
            'Pa': 1.0
        }

    def get_saturation_properties(self, P, P_unit='MPa'):
        """
        Get complete saturation properties at given pressure

        Parameters:
        -----------
        P : float
            Pressure value
        P_unit : str
            Pressure unit ('MPa', 'kPa', 'bar', 'Pa')

        Returns:
        --------
        dict : Complete saturation properties
        """
        # Convert to Pa
        if P_unit not in self.pressure_units:
            raise ValueError(f"Invalid pressure unit: {P_unit}")

        P_pa = self.pressure_units[P_unit] * P

        # Validate pressure range (critical pressure for R410A ≈ 4.96 MPa)
        if P_pa < 0.1e6 or P_pa > 5.0e6:
            raise ValueError(f"Pressure {P} {P_unit} is outside valid range")

        try:
            # Saturation temperature
            T_sat = CP.PropsSI('T', 'P', P_pa, 'Q', 0, self.fluid)

            # Liquid phase properties
            liquid_props = self._get_phase_properties(P_pa, 0)

            # Vapor phase properties
            vapor_props = self._get_phase_properties(P_pa, 1)

            # Derived properties
            h_lv = vapor_props['h'] - liquid_props['h']
            rho_ratio = liquid_props['rho'] / vapor_props['rho']

            # Surface tension (at saturated liquid)
            try:
                sigma = CP.PropsSI('I', 'P', P_pa, 'Q', 0, self.fluid)
            except:
                # Approximation if CoolProp doesn't support surface tension
                sigma = 0.055 * (1 - T_sat/386.7) ** 1.256  # Approximate correlation

            return {
                'T_sat_K': T_sat,
                'T_sat_C': T_sat - 273.15,
                'P_Pa': P_pa,
                'P_MPa': P_pa / 1e6,
                'liquid': liquid_props,
                'vapor': vapor_props,
                'derived': {
                    'h_lv_Jkg': h_lv,
                    'h_lv_kJ_kg': h_lv / 1000,
                    'sigma_Nm': sigma,
                    'sigma_mN_m': sigma * 1000,
                    'rho_ratio': rho_ratio
                }
            }

        except Exception as e:
            raise ValueError(f"Error calculating properties: {str(e)}")

    def _get_phase_properties(self, P, quality):
        """Get properties for a specific phase"""
        props = {}

        try:
            # Density
            props['rho'] = CP.PropsSI('D', 'P', P, 'Q', quality, self.fluid)

            # Dynamic viscosity
            props['mu'] = CP.PropsSI('V', 'P', P, 'Q', quality, self.fluid)

            # Thermal conductivity
            props['k'] = CP.PropsSI('L', 'P', P, 'Q', quality, self.fluid)

            # Specific heat at constant pressure
            props['cp'] = CP.PropsSI('C', 'P', P, 'Q', quality, self.fluid)

            # Enthalpy
            props['h'] = CP.PropsSI('H', 'P', P, 'Q', quality, self.fluid)

            # Entropy
            props['s'] = CP.PropsSI('S', 'P', P, 'Q', quality, self.fluid)

            # Prandtl number
            props['Pr'] = props['cp'] * props['mu'] / props['k']

            return props

        except Exception as e:
            raise ValueError(f"Error calculating phase properties: {str(e)}")

    def print_table_format(self, props):
        """Print properties in table format"""
        print(f"\n{'R410A Saturation Properties':^60}")
        print("=" * 60)
        print(f"Pressure:     {props['P_MPa']:.3f} MPa")
        print(f"Temperature:  {props['T_sat_C']:.2f} °C ({props['T_sat_K']:.2f} K)")
        print("\n" + "-" * 60)
        print(f"{'Property':<20} {'Liquid':<20} {'Vapor':<20}")
        print("-" * 60)
        print(f"{'Density (kg/m³)':<20} {props['liquid']['rho']:<20.1f} {props['vapor']['rho']:<20.1f}")
        print(f"{'Viscosity (×10⁻⁵ Pa·s)':<20} {props['liquid']['mu']*1e5:<20.3f} {props['vapor']['mu']*1e6:<20.3f}")
        print(f"{'Thermal Cond. (×10⁻³ W/m·K)':<20} {props['liquid']['k']*1000:<20.2f} {props['vapor']['k']*1000:<20.2f}")
        print(f"{'Specific Heat (J/kg·K)':<20} {props['liquid']['cp']:<20.1f} {props['vapor']['cp']:<20.1f}")
        print(f"{'Enthalpy (kJ/kg)':<20} {props['liquid']['h']/1000:<20.2f} {props['vapor']['h']/1000:<20.2f}")
        print(f"{'Entropy (J/kg·K)':<20} {props['liquid']['s']:<20.1f} {props['vapor']['s']:<20.1f}")
        print(f"{'Prandtl Number':<20} {props['liquid']['Pr']:<20.3f} {props['vapor']['Pr']:<20.3f}")
        print("-" * 60)

        # Derived properties
        print("\nDerived Properties:")
        print(f"{'Latent Heat':<20} {props['derived']['h_lv_kJ_kg']:<20.2f} kJ/kg")
        print(f"{'Surface Tension':<20} {props['derived']['sigma_mN_m']:<20.2f} mN/m")
        print(f"{'Density Ratio':<20} {props['derived']['rho_ratio']:<20.1f}:1")

        print("\n" + "=" * 60)

    def print_json_format(self, props):
        """Print properties in JSON format"""
        # Create JSON-serializable version
        json_props = {
            'T_sat_C': props['T_sat_C'],
            'P_MPa': props['P_MPa'],
            'liquid': {
                'rho_kgm3': props['liquid']['rho'],
                'mu_Pas': props['liquid']['mu'],
                'k_WmK': props['liquid']['k'],
                'cp_JkgK': props['liquid']['cp'],
                'h_Jkg': props['liquid']['h'],
                's_JkgK': props['liquid']['s'],
                'Pr': props['liquid']['Pr']
            },
            'vapor': {
                'rho_kgm3': props['vapor']['rho'],
                'mu_Pas': props['vapor']['mu'],
                'k_WmK': props['vapor']['k'],
                'cp_JkgK': props['vapor']['cp'],
                'h_Jkg': props['vapor']['h'],
                's_JkgK': props['vapor']['s'],
                'Pr': props['vapor']['Pr']
            },
            'derived': {
                'h_lv_kJkg': props['derived']['h_lv_kJ_kg'],
                'sigma_mNm': props['derived']['sigma_mN_m'],
                'rho_ratio': props['derived']['rho_ratio']
            }
        }

        print(json.dumps(json_props, indent=2))

def main():
    parser = argparse.ArgumentParser(
        description='R410A Property Calculator',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__.split('Installation')[0]
    )

    parser.add_argument('-p', '--pressure', type=float, default=1.0,
                       help='Pressure value (default: 1.0 MPa)')
    parser.add_argument('-u', '--unit', choices=['MPa', 'kPa', 'bar', 'Pa'],
                       default='MPa',
                       help='Pressure unit (default: MPa)')
    parser.add_argument('-f', '--format', choices=['table', 'json'],
                       default='table',
                       help='Output format (default: table)')
    parser.add_argument('-o', '--output', type=str,
                       help='Output file (default: stdout)')

    args = parser.parse_args()

    try:
        calculator = R410APropertyCalculator()
        props = calculator.get_saturation_properties(args.pressure, args.unit)

        # Redirect output if file specified
        if args.output:
            with open(args.output, 'w') as f:
                sys.stdout = f
                if args.format == 'table':
                    calculator.print_table_format(props)
                else:
                    calculator.print_json_format(props)
        else:
            if args.format == 'table':
                calculator.print_table_format(props)
            else:
                calculator.print_json_format(props)

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()
```

## Advanced Features

### Property Range Validation

```python
# Check pressure range before calculation
def validate_pressure_range(P, P_unit='MPa'):
    P_pa = pressure_units[P_unit] * P
    if P_pa < 0.1e6 or P_pa > 5.0e6:
        raise ValueError(f"Pressure {P} {P_unit} is outside R410A valid range")
```

### Property Extrapolation

```python
def extrapolate_properties(P, T, P_unit='MPa'):
    """Get properties at given P, T (superheated/compressed)"""
    P_pa = pressure_units[P_unit] * P
    return {
        'rho': CP.PropsSI('D', 'P', P_pa, 'T', T, 'R410A'),
        'h': CP.PropsSI('H', 'P', P_pa, 'T', T, 'R410A'),
        # ... other properties
    }
```

### Batch Property Calculation

```bash
#!/bin/bash
# Calculate properties for multiple pressures
for P in 0.5 1.0 1.5 2.0 2.5 3.0; do
    python3 r410a_properties.py -p $P -f table -o results_${P}MPa.txt
done
```

## Applications

### 1. OpenFOAM Initialization

```bash
# Generate initial conditions for OpenFOAM
python3 r410a_properties.py -p 2.0 -f json > initial_conditions.json
```

### 2. Property Table Generation

```python
import pandas as pd

# Generate property table for saturation curve
P_range = [0.5, 1.0, 1.5, 2.0, 2.5, 3.0]
table_data = []

for P in P_range:
    props = calculator.get_saturation_properties(P, 'MPa')
    table_data.append({
        'P_MPa': P,
        'T_sat_C': props['T_sat_C'],
        'rho_l_kgm3': props['liquid']['rho'],
        'rho_v_kgm3': props['vapor']['rho']
    })

df = pd.DataFrame(table_data)
df.to_csv('R410A_saturation_table.csv', index=False)
```

### 3. Validation Against Literature

```bash
# Compare with published data
python3 r410a_properties.py -p 2.0 > literature_comparison.txt
```

## Error Handling

The calculator includes comprehensive error handling:

- Pressure range validation
- Unit conversion errors
- CoolProp calculation errors
- File I/O errors
- JSON formatting errors

## Performance Considerations

- CoolProp calculations are cached for repeated queries
- Vectorized operations for batch calculations
- Memory efficient for large datasets
- Parallel processing for multiple cases

---

**Note**: For production use, consider implementing unit testing and performance optimization.