# Refrigerant Database (ฐานข้อมูลน้ำเย็น)

## Overview

The Refrigerant Database creates and manages property lookup tables for R410A refrigerant, optimized for OpenFOAM integration. It generates CSV files for easy analysis and HDF5 format for efficient OpenFOAM access.

## Features

- ✅ Saturation property lookup tables
- ✅ 2D property tables for superheated/compressed regions
- ✅ Multiple output formats (CSV, HDF5, JSON)
- ✅ Property range validation
- ✅ OpenFOAM integration support
- ✅ Batch property generation
- ✅ Performance optimization

## Installation

```bash
# Install required packages
pip install CoolProp numpy pandas h5py

# Make script executable
chmod +x r410a_database.py
```

## Complete Implementation

```python
#!/usr/bin/env python3
"""
R410A Refrigerant Database
Create and manage property lookup tables for OpenFOAM

Usage:
    python3 r410a_database.py [options]

Options:
    --saturation-table          Generate saturation property table
    --2d-table                 Generate 2D property table
    --range P_MIN-P_MAX        Pressure range in MPa
    --temp-range T_MIN-T_MAX   Temperature range in K
    --n-points N               Number of points
    --output FILE              Output file
    --format FORMAT            Output format (csv, hdf5, json)
    --batch                    Generate multiple tables
    --validate                 Validate generated tables
    --help                     Show help
"""

import CoolProp.CoolProp as CP
import numpy as np
import pandas as pd
import h5py
import json
import argparse
import sys
import os
from typing import Dict, List, Tuple, Optional
import multiprocessing as mp
from functools import partial

class R410ADatabase:
    """Create and manage R410A property database"""

    def __init__(self):
        self.fluid = 'R410A'
        self.pressure_units = {
            'MPa': 1e6,
            'kPa': 1e3,
            'bar': 1e5,
            'Pa': 1.0
        }

        # Critical properties for validation
        self.T_critical = CP.PropsSI('Tcrit', '', '', '', '', 'R410A')
        self.P_critical = CP.PropsSI('Pcrit', '', '', '', '', 'R410A')
        self.rho_critical = CP.PropsSI('Dcrit', '', '', '', '', 'R410A')

    def validate_pressure(self, P: float, unit: str = 'MPa') -> bool:
        """Validate pressure against critical point"""
        P_pa = self.pressure_units[unit] * P
        return 0.1e6 <= P_pa <= 1.2 * self.P_critical

    def validate_temperature(self, T: float) -> bool:
        """Validate temperature against critical point"""
        return 200 <= T <= 1.2 * self.T_critical

    def create_saturation_table(self,
                              P_min: float = 0.5,
                              P_max: float = 5.0,
                              n_points: int = 100,
                              unit: str = 'MPa') -> pd.DataFrame:
        """
        Create saturation property table

        Parameters:
        -----------
        P_min, P_max : float
            Pressure range
        n_points : int
            Number of points
        unit : str
            Pressure unit

        Returns:
        --------
        DataFrame : Complete saturation table
        """
        if not self.validate_pressure(P_min, unit) or not self.validate_pressure(P_max, unit):
            raise ValueError("Pressure range outside valid range")

        # Create pressure array
        P_array = np.linspace(P_min, P_max, n_points)
        P_pa_array = self.pressure_units[unit] * P_array

        # Initialize arrays for properties
        properties = {
            'P_MPa': P_array,
            'T_sat_K': np.zeros(n_points),
            'T_sat_C': np.zeros(n_points),
            'rho_l_kgm3': np.zeros(n_points),
            'rho_v_kgm3': np.zeros(n_points),
            'h_l_kJkg': np.zeros(n_points),
            'h_v_kJkg': np.zeros(n_points),
            's_l_kJkgK': np.zeros(n_points),
            's_v_kJkgK': np.zeros(n_points),
            'mu_l_uPas': np.zeros(n_points),
            'mu_v_uPas': np.zeros(n_points),
            'k_l_mWmK': np.zeros(n_points),
            'k_v_mWmK': np.zeros(n_points),
            'cp_l_kJkgK': np.zeros(n_points),
            'cp_v_kJkgK': np.zeros(n_points),
            'Pr_l': np.zeros(n_points),
            'Pr_v': np.zeros(n_points),
            'h_lv_kJkg': np.zeros(n_points),
            'sigma_mNm': np.zeros(n_points)
        }

        # Calculate properties for each pressure point
        for i, P in enumerate(P_pa_array):
            try:
                # Saturation temperature
                T_sat = CP.PropsSI('T', 'P', P, 'Q', 0, self.fluid)
                properties['T_sat_K'][i] = T_sat
                properties['T_sat_C'][i] = T_sat - 273.15

                # Liquid properties
                properties['rho_l_kgm3'][i] = CP.PropsSI('D', 'P', P, 'Q', 0, self.fluid)
                properties['h_l_kJkg'][i] = CP.PropsSI('H', 'P', P, 'Q', 0, self.fluid) / 1000
                properties['s_l_kJkgK'][i] = CP.PropsSI('S', 'P', P, 'Q', 0, self.fluid) / 1000
                properties['mu_l_uPas'][i] = CP.PropsSI('V', 'P', P, 'Q', 0, self.fluid) * 1e6
                properties['k_l_mWmK'][i] = CP.PropsSI('L', 'P', P, 'Q', 0, self.fluid) * 1000
                properties['cp_l_kJkgK'][i] = CP.PropsSI('C', 'P', P, 'Q', 0, self.fluid) / 1000

                # Vapor properties
                properties['rho_v_kgm3'][i] = CP.PropsSI('D', 'P', P, 'Q', 1, self.fluid)
                properties['h_v_kJkg'][i] = CP.PropsSI('H', 'P', P, 'Q', 1, self.fluid) / 1000
                properties['s_v_kJkgK'][i] = CP.PropsSI('S', 'P', P, 'Q', 1, self.fluid) / 1000
                properties['mu_v_uPas'][i] = CP.PropsSI('V', 'P', P, 'Q', 1, self.fluid) * 1e6
                properties['k_v_mWmK'][i] = CP.PropsSI('L', 'P', P, 'Q', 1, self.fluid) * 1000
                properties['cp_v_kJkgK'][i] = CP.PropsSI('C', 'P', P, 'Q', 1, self.fluid) / 1000

                # Latent heat
                properties['h_lv_kJkg'][i] = properties['h_v_kJkg'][i] - properties['h_l_kJkg'][i]

                # Surface tension (approximation if CoolProp doesn't support)
                try:
                    sigma = CP.PropsSI('I', 'P', P, 'Q', 0, self.fluid)
                    properties['sigma_mNm'][i] = sigma * 1000
                except:
                    # Use approximation correlation
                    T_reduced = (T_sat - 273.15) / (71.0 - 273.15)
                    properties['sigma_mNm'][i] = 56.0 * (1 - T_reduced) ** 1.256

                # Prandtl numbers
                properties['Pr_l'][i] = (properties['cp_l_kJkgK'][i] * 1000 * properties['mu_l_uPas'][i] * 1e-6) / (properties['k_l_mWmK'][i] * 1e-3)
                properties['Pr_v'][i] = (properties['cp_v_kJkgK'][i] * 1000 * properties['mu_v_uPas'][i] * 1e-6) / (properties['k_v_mWmK'][i] * 1e-3)

            except Exception as e:
                print(f"Error at P = {P_array[i]} MPa: {e}")
                # Fill with NaN for failed points
                for key in properties:
                    if isinstance(properties[key], np.ndarray):
                        properties[key][i] = np.nan

        return pd.DataFrame(properties)

    def create_2d_table(self,
                      P_range: Tuple[float, float] = (0.5, 5.0),
                      T_range: Tuple[float, float] = (250, 350),
                      n_p: int = 50,
                      n_t: int = 50) -> Dict:
        """
        Create 2D property table for superheated/compressed regions

        Parameters:
        -----------
        P_range : tuple
            Pressure range (MPa)
        T_range : tuple
            Temperature range (K)
        n_p, n_t : int
            Number of points in P and T directions

        Returns:
        --------
        dict : 2D property arrays
        """
        P = np.linspace(P_range[0], P_range[1], n_p)
        T = np.linspace(T_range[0], T_range[1], n_t)

        # Create 2D grids
        P_grid, T_grid = np.meshgrid(P, T)

        # Initialize property arrays
        rho = np.full((n_t, n_p), np.nan)
        h = np.full((n_t, n_p), np.nan)
        s = np.full((n_t, n_p), np.nan)
        mu = np.full((n_t, n_p), np.nan)
        k = np.full((n_t, n_p), np.nan)

        # Calculate properties for each (P, T) point
        for i in range(n_p):
            for j in range(n_t):
                try:
                    rho[j, i] = CP.PropsSI('D', 'P', P[i]*1e6, 'T', T[j], self.fluid)
                    h[j, i] = CP.PropsSI('H', 'P', P[i]*1e6, 'T', T[j], self.fluid) / 1000
                    s[j, i] = CP.PropsSI('S', 'P', P[i]*1e6, 'T', T[j], self.fluid) / 1000
                    mu[j, i] = CP.PropsSI('V', 'P', P[i]*1e6, 'T', T[j], self.fluid) * 1e6
                    k[j, i] = CP.PropsSI('L', 'P', P[i]*1e6, 'T', T[j], self.fluid) * 1000
                except:
                    # Outside valid range
                    pass

        return {
            'P_MPa': P,
            'T_K': T,
            'rho_kgm3': rho,
            'h_kJkg': h,
            's_kJkgK': s,
            'mu_uPas': mu,
            'k_mWmK': k,
            'P_grid': P_grid,
            'T_grid': T_grid
        }

    def export_to_csv(self, df: pd.DataFrame, filename: str):
        """Export DataFrame to CSV with formatting"""
        df.to_csv(filename, index=False, float_format='%.6g')
        print(f"CSV exported to: {filename}")

    def export_to_hdf5(self, data: Dict, filename: str):
        """Export data to HDF5 format for OpenFOAM"""
        with h5py.File(filename, 'w') as f:
            # Store main arrays
            for key, value in data.items():
                if isinstance(value, np.ndarray):
                    f.create_dataset(key, data=value)
                else:
                    f.attrs[key] = value

            # Store metadata
            f.attrs['fluid'] = self.fluid
            f.attrs['created_by'] = 'R410ADatabase'
            f.attrs['date'] = pd.Timestamp.now().isoformat()

        print(f"HDF5 exported to: {filename}")

    def export_to_json(self, data: Dict, filename: str):
        """Export data to JSON format"""
        # Convert numpy arrays to lists for JSON serialization
        json_data = {}
        for key, value in data.items():
            if isinstance(value, np.ndarray):
                json_data[key] = value.tolist()
            else:
                json_data[key] = value

        with open(filename, 'w') as f:
            json.dump(json_data, f, indent=2)

        print(f"JSON exported to: {filename}")

    def generate_openfoam_table(self, df: pd.DataFrame, variable: str):
        """Generate OpenFOAM-style lookup table"""
        # Sort by pressure
        df_sorted = df.sort_values('P_MPa')

        # Create OpenFOAM format
        header = f"""/*--------------------------------*- C++ -*----------------------------------*\\
| =========                 |                                                 |
| \\\\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox           |
|  \\\\    /   O peration     | Version:  v2212                                 |
|   \\\\  /    A nd           | Web:      www.OpenFOAM.org                      |
|    \\\\/     M anipulation  |                                                 |
\\*---------------------------------------------------------------------------*/
FoamFile
{{
    version     2.0;
    format      ascii;
    class       List<scalar>;
    object      {variable};
}}
// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

(
"""

        # Generate entries
        entries = []
        for _, row in df_sorted.iterrows():
            entries.append(f"    {row[variable]}")

        footer = "\n);"

        return header + "\n".join(entries) + footer

def batch_generate_saturation_tables(P_ranges: List[Tuple[float, float]],
                                    n_points: int = 100,
                                    base_filename: str = 'R410A_saturation'):
    """Generate multiple saturation tables for different pressure ranges"""
    db = R410ADatabase()

    for i, (P_min, P_max) in enumerate(P_ranges):
        print(f"\nGenerating table {i+1}/{len(P_ranges)}: {P_min}-{P_max} MPa")

        df = db.create_saturation_table(P_min, P_max, n_points)
        filename = f"{base_filename}_range{i+1}_{P_min}_{P_max}.csv"
        db.export_to_csv(df, filename)

    print(f"\nGenerated {len(P_ranges)} saturation tables")

def create_openfoam_constant_directory():
    """Create OpenFOAM constant directory structure"""
    os.makedirs('constant/thermophysicalProperties', exist_ok=True)
    os.makedirs('constant/tables', exist_ok=True)

def main():
    parser = argparse.ArgumentParser(
        description='R410A Refrigerant Database Generator',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python3 r410a_database.py --saturation-table --range 0.5-3.0
    python3 r410a_database.py --2d-table --range 1.0-4.0 --temp-range 280-320
    python3 r410a_database.py --batch
    python3 r410a_database.py --saturation-table --format hdf5 --output R410A.h5
        """
    )

    parser.add_argument('--saturation-table', action='store_true',
                       help='Generate saturation property table')
    parser.add_argument('--2d-table', action='store_true',
                       help='Generate 2D property table')
    parser.add_argument('--range', type=str, default='0.5-5.0',
                       help='Pressure range (MPa) - format: MIN-MAX')
    parser.add_argument('--temp-range', type=str, default='250-350',
                       help='Temperature range (K) - format: MIN-MAX')
    parser.add_argument('--n-points', type=int, default=100,
                       help='Number of pressure points')
    parser.add_argument('--output', type=str,
                       help='Output filename')
    parser.add_argument('--format', choices=['csv', 'hdf5', 'json'],
                       default='csv', help='Output format')
    parser.add_argument('--batch', action='store_true',
                       help='Generate multiple tables in different ranges')
    parser.add_argument('--validate', action='store_true',
                       help='Validate generated tables')
    parser.add_argument('--openfoam', action='store_true',
                       help='Generate OpenFOAM-compatible format')

    args = parser.parse_args()

    # Parse ranges
    P_min, P_max = map(float, args.range.split('-'))
    T_min, T_max = map(float, args.temp_range.split('-'))

    # Create output filename if not specified
    if not args.output:
        if args.saturation_table:
            args.output = 'R410A_saturation'
        elif args['2d-table']:
            args.output = 'R410A_2dtable'

    # Initialize database
    db = R410ADatabase()

    try:
        if args.batch:
            # Generate multiple tables
            P_ranges = [(0.5, 1.5), (1.5, 3.0), (3.0, 5.0)]
            batch_generate_saturation_tables(P_ranges)

        elif args.saturation_table:
            # Generate saturation table
            print("Generating saturation property table...")
            df = db.create_saturation_table(P_min, P_max, args.n_points)

            # Export based on format
            if args.format == 'csv':
                db.export_to_csv(df, f"{args.output}.csv")
            elif args.format == 'hdf5':
                # Convert DataFrame to dict for HDF5
                data_dict = df.to_dict('list')
                db.export_to_hdf5(data_dict, f"{args.output}.h5")
            elif args.format == 'json':
                data_dict = df.to_dict('list')
                db.export_to_json(data_dict, f"{args.output}.json")

            # Generate OpenFOAM format if requested
            if args.openfoam:
                create_openfoam_constant_directory()
                for var in ['rho_l_kgm3', 'rho_v_kgm3', 'h_l_kJkg', 'h_v_kJkg']:
                    table_content = db.generate_openfoam_table(df, var)
                    with open(f'constant/tables/R410A_{var}', 'w') as f:
                        f.write(table_content)
                print("OpenFOAM tables created in constant/tables/")

            # Validate if requested
            if args.validate:
                validate_saturation_table(df)

        elif args['2d-table']:
            # Generate 2D table
            print("Generating 2D property table...")
            data_dict = db.create_2d_table((P_min, P_max), (T_min, T_max))

            # Export based on format
            if args.format == 'csv':
                # Convert to DataFrame
                df_2d = pd.DataFrame()
                for key, value in data_dict.items():
                    if key in ['P_MPa', 'T_K']:
                        df_2d[key] = value
                    elif isinstance(value, np.ndarray):
                        df_2d[key] = value.flatten()
                db.export_to_csv(df_2d, f"{args.output}.csv")
            else:
                db.export_to_hdf5(data_dict, f"{args.output}.h5")

            print(f"2D table generated for {P_min}-{P_max} MPa, {T_min}-{T_max} K")

        else:
            print("Please specify table type: --saturation-table or --2d-table")
            parser.print_help()
            sys.exit(1)

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

def validate_saturation_table(df: pd.DataFrame):
    """Validate generated saturation table"""
    print("\nValidating saturation table...")

    # Check for NaN values
    if df.isnull().any().any():
        print("⚠ Warning: NaN values found in table")
        print("NaN columns:", df.columns[df.isnull().any()].tolist())
    else:
        print("✓ No NaN values found")

    # Check monotonicity
    is_monotonic = df['T_sat_K'].is_monotonic_increasing
    if is_monotonic:
        print("✓ Saturation temperature increases with pressure")
    else:
        print("⚠ Non-monotonic saturation temperature")

    # Check property ranges
    if df['rho_l_kgm3'].min() > 0 and df['rho_v_kgm3'].min() > 0:
        print("✓ All densities positive")
    else:
        print("⚠ Negative or zero density found")

    # Check latent heat
    if df['h_lv_kJkg'].min() > 0:
        print(f"✓ Latent heat positive (min: {df['h_lv_kJkg'].min():.1f} kJ/kg)")
    else:
        print("⚠ Negative latent heat found")

if __name__ == '__main__':
    main()
```

## Usage Examples

### Basic Usage

```bash
# Generate saturation table
python3 r410a_database.py --saturation-table --range 0.5-3.0

# Generate 2D table
python3 r410a_database.py --2d-table --range 1.0-4.0 --temp-range 280-320

# Export to HDF5
python3 r410a_database.py --saturation-table --format hdf5 --output R410A.h5
```

### OpenFOAM Integration

```bash
# Generate OpenFOAM-compatible tables
python3 r410a_database.py --saturation-table --openfoam

# This creates:
# - R410A_saturation.csv (for analysis)
# - constant/tables/R410A_rho_l_kgm3 (OpenFOAM format)
# - constant/tables/R410A_rho_v_kgm3
# - constant/tables/R410A_h_l_kJkg
# - constant/tables/R410A_h_v_kJkg
```

### Batch Generation

```bash
# Generate multiple tables for different ranges
python3 r410a_database.py --batch
```

### Python API Usage

```python
from r410a_database import R410ADatabase

# Create database instance
db = R410ADatabase()

# Generate saturation table
sat_table = db.create_saturation_table(0.5, 5.0, 100)

# Access properties
print(f"Pressure range: {sat_table['P_MPa'].min()} - {sat_table['P_MPa'].max()} MPa")
print(f"Temperature range: {sat_table['T_sat_C'].min()} - {sat_table['T_sat_C'].max()} °C")

# Export to different formats
db.export_to_csv(sat_table, 'R410A_saturation.csv')
db.export_to_hdf5(sat_table.to_dict('list'), 'R410A_saturation.h5')

# Generate 2D table
table_2d = db.create_2d_table((1.0, 4.0), (280, 320))
```

## Advanced Features

### 1. Database Management

```python
class R410ADatabaseManager:
    """Advanced database with caching and validation"""

    def __init__(self):
        self.db = R410ADatabase()
        self.cache = {}
        self.metadata = {}

    def get_or_calculate(self, P_min, P_max, n_points):
        """Get from cache or calculate"""
        key = f"{P_min}_{P_max}_{n_points}"
        if key not in self.cache:
            self.cache[key] = self.db.create_saturation_table(P_min, P_max, n_points)
            self.metadata[key] = {
                'created': pd.Timestamp.now(),
                'n_points': n_points,
                'P_range': (P_min, P_max)
            }
        return self.cache[key]
```

### 2. Property Interpolation

```python
def interpolate_property(df, P_target, property_name):
    """Interpolate property at target pressure"""
    from scipy.interpolate import interp1d

    # Sort by pressure
    df_sorted = df.sort_values('P_MPa')

    # Create interpolator
    f = interp1d(df_sorted['P_MPa'], df_sorted[property_name],
                 bounds_error=False, fill_value='extrapolate')

    return float(f(P_target))
```

### 3. OpenFOAM Dictionary Generation

```python
def create_thermophysical_properties():
    """Create OpenFOAM thermophysicalProperties dictionary"""

    content = """/*--------------------------------*- C++ -*----------------------------------*\\
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
    object      thermophysicalProperties;
}
// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

thermoType
{
    type            heRhoThermo;
    mixture         R410A;
    transport       sutherland;
    thermodynamics  janaf;
    energy          sensibleEnthalpy;
}

mixture
{
    species
    (
        R410A
    );

    thermodynamics
    {
        rho           table
        (
            (100 0.5 5.0)
            (
                100
                $(R410A_rho)
            )
        );
    };
}

// ************************************************************************* //
"""

    with open('constant/thermophysicalProperties', 'w') as f:
        f.write(content)
```

## Quality Assurance

### Validation Functions

```python
def validate_database_integrity(df):
    """Validate database integrity"""
    issues = []

    # Check for missing values
    if df.isnull().any().any():
        issues.append("NaN values found")

    # Check monotonicity
    if not df['T_sat_K'].is_monotonic_increasing:
        issues.append("Non-monotonic saturation temperature")

    # Check physical consistency
    if (df['rho_l_kgm3'] < df['rho_v_kgm3']).any():
        issues.append("Liquid density less than vapor density")

    # Check energy balance
    h_diff = df['h_v_kJkg'] - df['h_l_kJkg']
    if (h_diff < 0).any():
        issues.append("Negative latent heat")

    return issues
```

### Performance Optimization

```python
def parallel_property_calculation(n_points=100):
    """Calculate properties in parallel"""
    from multiprocessing import Pool

    db = R410ADatabase()
    P_array = np.linspace(0.5, 5.0, n_points)

    # Create pool of workers
    with Pool() as pool:
        func = partial(calculate_saturation_properties_at_P, db)
        results = pool.map(func, P_array)

    return pd.DataFrame(results)

def calculate_saturation_properties_at_P(db, P):
    """Calculate properties at single pressure point"""
    P_pa = db.pressure_units['MPa'] * P
    # Implementation...
    return properties_dict
```

## Integration with OpenFOAM

### 1. Property Table Loading

```python
def load_openfoam_table(filename):
    """Load OpenFOAM table format"""
    data = []
    with open(filename, 'r') as f:
        for line in f:
            if line.strip() and not line.startswith('//'):
                try:
                    data.append(float(line.strip()))
                except:
                    pass
    return np.array(data)
```

### 2. Boundary Condition Setup

```bash
#!/bin/bash
# Set up boundary conditions using generated tables

setup_bcs() {
    CASE_DIR=$1

    cd $CASE_DIR

    # Copy tables to constant directory
    cp ../constant/tables/ constant/tables/

    # Update boundary conditions
    sed -i 's|constant/tables/R410A|constant/tables|' 0/*

    # Set saturation temperature at wall
    T_SAT=$(awk 'NR==2 {print $2}' constant/tables/R410A_rho_l_kgm3)
    sed -i "s/T \"$T_SAT\"/T \"$T_SAT\"/" 0/T
}
```

### 3. Solver Configuration

```python
def configure_solver_with_tables():
    """Configure R410ASolver to use property tables"""

    config = """
R410ASolverFoam {
    solver           R410ASolver;

    thermophysical {
        tablesDirectory   "constant/tables";
        saturationTable  "R410A_saturation";
        useTables        true;
    };
}
"""

    with open('system/R410ASolver', 'w') as f:
        f.write(config)
```

## Troubleshooting

### Common Issues

1. **CoolProp errors**
   - Solution: Check if CoolProp is properly installed
   - Verify fluid name is correct

2. **Memory issues with large tables**
   - Solution: Reduce number of points
   - Use HDF5 format instead of CSV

3. **OpenFOAM integration errors**
   - Solution: Check file paths in dictionaries
   - Verify table format is correct

### Debug Mode

```python
import logging

logging.basicConfig(level=logging.DEBUG)

# Enable debug output
db = R410ADatabase()
db.create_saturation_table(0.5, 2.0, 10)  # Small table for testing
```

---

**Note**: For production use, consider implementing unit tests, caching mechanisms, and automated validation checks.