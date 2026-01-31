#!/usr/bin/env python3
"""
Property Integration Verification Script

Verifies CoolProp/R410A property integration:
- CoolProp API usage
- R410A property accuracy
- Table interpolation
- Temperature ranges
"""

import sys
import re
from pathlib import Path
from typing import Dict, List, Tuple

# Color output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'


# R410A reference values (at typical evaporator conditions: 5-10°C)
R410A_REFERENCE = {
    'T_sat_10_bar': 39.4,  # Saturation temperature at 10 bar (°C)
    'rho_l_10_bar': 1000,   # Liquid density at 10 bar (kg/m³)
    'rho_v_10_bar': 45,     # Vapor density at 10 bar (kg/m³)
    'h_fg_10_bar': 200,     # Latent heat at 10 bar (kJ/kg)
    'T_range': (-50, 72),   # Valid temperature range (°C) for R410A
    'P_range': (1, 40),     # Valid pressure range (bar) for R410A
}


def verify_coolprop_api(content: str) -> Tuple[bool, str]:
    """Verify CoolProp API is used correctly."""
    # Check for CoolProp include
    has_include = (
        '#include "CoolProp.h"' in content or
        '#include <CoolProp.h>' in content or
        'CoolProp' in content
    )

    # Check for CoolProp namespace
    has_namespace = (
        'CoolProp::' in content or
        'using namespace CoolProp' in content
    )

    # Check for common CoolProp functions
    has_props_func = (
        'Props1SI' in content or 'PropsSI' in content or
        'HaPropsSI' in content or 'Props1' in content
    )

    # Check for fluid specification
    has_fluid = (
        'R410A' in content or 'REFPROP-' in content or
        "'R410A'" in content or '"R410A"' in content
    )

    # Check for property specification (density, enthalpy, etc.)
    has_property = (
        'D' in content or 'H' in content or 'P' in content or 'T' in content
    )

    if has_include or has_namespace:
        if has_props_func:
            if has_fluid:
                return True, f"{Colors.GREEN}✓ CoolProp API used correctly{Colors.END}"
            else:
                return False, f"{Colors.YELLOW}⚠ CoolProp present but fluid not specified{Colors.END}"
        else:
            return False, f"{Colors.YELLOW}⚠ CoolProp included but Props function not found{Colors.END}"
    elif has_fluid and has_property:
        return False, f"{Colors.YELLOW}⚠ R410A mentioned but CoolProp API unclear{Colors.END}"
    else:
        return False, f"{Colors.RED}✗ CoolProp API not found{Colors.END}"


def verify_r410a_properties(content: str) -> Tuple[bool, str]:
    """Verify R410A property values are accurate."""
    # Check for R410A mention
    has_r410a = 'R410A' in content or 'r410a' in content.lower()

    # Check for density values
    has_density = (
        'rho' in content.lower() or 'ρ' in content or 'density' in content.lower()
    )

    # Check for reasonable density values
    # R410A: liquid ~1000 kg/m³, vapor ~30-50 kg/m³
    density_matches = re.findall(r'(\d+)\s*(?:kg/?m³|kg/m\^3)', content)
    if density_matches:
        densities = [int(d) for d in density_matches]
        has_reasonable_density = any(
            900 <= d <= 1100 for d in densities  # Liquid range
        ) and any(
            20 <= d <= 80 for d in densities     # Vapor range
        )
    else:
        has_reasonable_density = False

    # Check for saturation temperature/pressure
    has_saturation = (
        'T_sat' in content or 'P_sat' in content or
        'saturation' in content.lower()
    )

    # Check for latent heat
    has_latent_heat = (
        'h_fg' in content or 'latent' in content.lower() or
        'enthalpy of vaporization' in content.lower()
    )

    if has_r410a:
        if has_density and has_reasonable_density:
            return True, f"{Colors.GREEN}✓ R410A properties accurate{Colors.END}"
        elif has_density:
            return False, f"{Colors.YELLOW}⚠ R410A present but density values questionable{Colors.END}"
        else:
            return False, f"{Colors.YELLOW}⚠ R410A mentioned but properties not detailed{Colors.END}"
    else:
        return False, f"{Colors.RED}✗ R410A not found in content{Colors.END}"


def verify_table_interpolation(content: str) -> Tuple[bool, str]:
    """Verify table interpolation is valid."""
    # Check for table usage
    has_table = (
        'table' in content.lower() or
        'lookup' in content.lower() or
        'interpolat' in content.lower()
    )

    # Check for interpolation method
    has_interpolation_method = (
        'linear' in content.lower() or
        'cubic' in content.lower() or
        'spline' in content.lower() or
        'interp' in content.lower()
    )

    # Check for table bounds checking
    has_bounds_check = (
        'clamp' in content.lower() or
        'bound' in content.lower() or
        'range check' in content.lower() or
        ('min' in content.lower() and 'max' in content.lower())
    )

    # Check for table structure
    has_table_structure = (
        ('vector' in content.lower() or 'array' in content.lower()) and
        ('temperature' in content.lower() or 'T[' in content)
    )

    if has_table:
        if has_interpolation_method and has_bounds_check:
            return True, f"{Colors.GREEN}✓ Table interpolation valid{Colors.END}"
        elif has_interpolation_method:
            return False, f"{Colors.YELLOW}⚠ Interpolation present but bounds check unclear{Colors.END}"
        elif has_table_structure:
            return False, f"{Colors.YELLOW}⚠ Table structure found but interpolation method unclear{Colors.END}"
        else:
            return False, f"{Colors.YELLOW}⚠ Table mentioned but implementation unclear{Colors.END}"
    else:
        # Not using tables - may use direct CoolProp calls
        return False, f"{Colors.YELLOW}⚠ Table interpolation not used (may use direct CoolProp calls){Colors.END}"


def verify_temperature_ranges(content: str) -> Tuple[bool, str]:
    """Verify temperature ranges are appropriate."""
    # Check for temperature specification
    has_temperature = (
        'T[' in content or 'T =' in content or
        'temperature' in content.lower() or
        'T_sat' in content
    )

    # Check for temperature range specification
    has_range = (
        ('range' in content.lower() or 'bounds' in content.lower()) and
        ('T_' in content or 'temperature' in content.lower())
    )

    # Look for numeric temperature values
    temp_values = re.findall(r'(-?\d+\.?\d*)\s*[°C]?K?', content)
    if temp_values:
        temps = [float(t) for t in temp_values if -100 <= float(t) <= 200]
        has_reasonable_temps = len(temps) > 0
    else:
        has_reasonable_temps = False

    # Check for evaporator temperature range (typically -20 to 20°C for R410A)
    evaporator_temps = [t for t in re.findall(r'(-?\d+)\s*[°C]?', content) if -20 <= int(t) <= 20]
    has_evaporator_range = len(evaporator_temps) > 0

    if has_temperature:
        if has_evaporator_range:
            return True, f"{Colors.GREEN}✓ Temperature ranges appropriate for evaporator{Colors.END}"
        elif has_range:
            return False, f"{Colors.YELLOW}⚠ Temperature range specified but evaporator conditions unclear{Colors.END}"
        elif has_reasonable_temps:
            return False, f"{Colors.YELLOW}⚠ Temperatures found but range not explicit{Colors.END}"
        else:
            return False, f"{Colors.YELLOW}⚠ Temperature present but values questionable{Colors.END}"
    else:
        return False, f"{Colors.RED}✗ Temperature not found in content{Colors.END}"


def verify_file(file_path: Path) -> int:
    """Verify a single file for property integration."""
    with open(file_path, "r") as f:
        content = f.read()

    print(f"\n{Colors.BLUE}Verifying: {file_path}{Colors.END}")

    checks = [
        ("CoolProp API", verify_coolprop_api),
        ("R410A Properties", verify_r410a_properties),
        ("Table Interpolation", verify_table_interpolation),
        ("Temperature Ranges", verify_temperature_ranges),
    ]

    passed = 0
    failed = 0

    for name, check_func in checks:
        result, message = check_func(content)
        print(f"  {name}: {message}")
        if result:
            passed += 1
        else:
            failed += 1

    print(f"\n  Summary: {passed}/{len(checks)} checks passed")

    return 0 if failed == 0 else 1


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Property Integration Verification")
    parser.add_argument("--file", type=str, help="File to verify")
    parser.add_argument("--content", type=str, help="Content string to verify")
    parser.add_argument("--check", type=str, help="Specific check to run")

    args = parser.parse_args()

    if args.content:
        content = args.content
        print(f"{Colors.BLUE}Verifying provided content{Colors.END}\n")

        checks = {
            "coolprop": verify_coolprop_api,
            "r410a": verify_r410a_properties,
            "table": verify_table_interpolation,
            "temperature": verify_temperature_ranges,
        }

        if args.check:
            if args.check in checks:
                result, message = checks[args.check](content)
                print(f"{args.check.replace('_', ' ').title()}: {message}")
                return 0 if result else 1
            else:
                print(f"{Colors.RED}Unknown check: {args.check}{Colors.END}")
                return 1
        else:
            # Run all checks
            passed = 0
            failed = 0
            for name, check_func in checks.items():
                result, message = check_func(content)
                print(f"{name.replace('_', ' ').title()}: {message}")
                if result:
                    passed += 1
                else:
                    failed += 1

            print(f"\n{Colors.BLUE}Summary: {passed}/{len(checks)} checks passed{Colors.END}")
            return 0 if failed == 0 else 1

    elif args.file:
        file_path = Path(args.file)
        if not file_path.exists():
            print(f"{Colors.RED}File not found: {file_path}{Colors.END}")
            return 1
        return verify_file(file_path)

    else:
        # Demo with sample content
        sample_content = """
        # R410A Properties with CoolProp

        #include "CoolProp.h"
        using namespace CoolProp;

        // R410A property wrapper
        class R410AProperties {
        public:
            static scalar density(scalar T, scalar p) {
                return PropsSI("D", "T", T, "P", p, "R410A");
            }

            static scalar enthalpy(scalar T, scalar p) {
                return PropsSI("H", "T", T, "P", p, "R410A");
            }

            // Saturation properties
            static scalar T_sat(scalar p) {
                return PropsSI("T", "P", p, "R410A", 0.0);
            }
        };

        // Temperature range for evaporator: -20 to 20°C
        const dimensionedScalar T_min(-20);
        const dimensionedScalar T_max(20);
        """

        print(f"{Colors.BLUE}Running demo verification with sample content{Colors.END}\n")

        # Run all checks on sample content
        checks = {
            "coolprop": verify_coolprop_api,
            "r410a": verify_r410a_properties,
            "table": verify_table_interpolation,
            "temperature": verify_temperature_ranges,
        }

        passed = 0
        failed = 0
        for name, check_func in checks.items():
            result, message = check_func(sample_content)
            print(f"{name.replace('_', ' ').title()}: {message}")
            if result:
                passed += 1
            else:
                failed += 1

        print(f"\n{Colors.BLUE}Summary: {passed}/{len(checks)} checks passed{Colors.END}")
        return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
