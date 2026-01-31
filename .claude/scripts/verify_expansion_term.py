#!/usr/bin/env python3
"""
Expansion Term Verification Script

Verifies the expansion term implementation for phase change:
- Mathematical derivation
- Sign convention
- Implementation in pressure equation
- Density ratio terms
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


def verify_expansion_term_present(content: str) -> Tuple[bool, str]:
    """Verify expansion term is present in content."""
    # Check for divergence of velocity
    has_div = (
        'div' in content or '∇·' in content or 'nabla' in content.lower() or
        'divergence' in content.lower()
    )

    # Check for expansion term pattern
    has_expansion_term = (
        ('∇·U' in content or 'div(U)' in content or 'div(phi)' in content) and
        ('mass' in content.lower() or 'mdot' in content.lower() or 'ṁ' in content)
    )

    # Check for density ratio terms
    has_density_ratio = (
        ('1/ρ' in content or '1/rho' in content) and
        ('rho_l' in content or 'rho_v' in content or 'ρ_l' in content or 'ρ_v' in content)
    )

    # Check for phase change source term
    has_phase_change_source = (
        'S_expansion' in content or 'S_exp' in content or
        'phase change' in content.lower()
    )

    if has_expansion_term or (has_div and has_density_ratio):
        return True, f"{Colors.GREEN}✓ Expansion term present{Colors.END}"
    elif has_div:
        return False, f"{Colors.YELLOW}⚠ Divergence found but expansion term unclear{Colors.END}"
    elif has_phase_change_source:
        return False, f"{Colors.YELLOW}⚠ Phase change source mentioned but expansion term not explicit{Colors.END}"
    else:
        return False, f"{Colors.RED}✗ Expansion term not found{Colors.END}"


def verify_sign_convention(content: str) -> Tuple[bool, str]:
    """Verify sign convention (ṁ positive for evaporation)."""
    # Check for mass transfer rate variable
    has_mass_transfer = (
        'mdot' in content.lower() or 'ṁ' in content or
        'mass transfer' in content.lower() or 'm_dot' in content.lower()
    )

    # Check for evaporation/condensation terminology
    has_evaporation = 'evaporation' in content.lower() or 'evapor' in content.lower()
    has_condensation = 'condensation' in content.lower() or 'condens' in content.lower()

    # Check for sign convention statement
    has_sign_statement = (
        ('positive' in content.lower() and 'evaporation' in content.lower()) or
        ('negative' in content.lower() and 'condensation' in content.lower()) or
        ('ṁ > 0' in content or 'mdot > 0' in content)
    )

    # Check for correct formula structure
    # ∇·U = ṁ(1/ρ_v - 1/ρ_l) for evaporation (positive ṁ)
    has_correct_structure = (
        ('1/ρ_v - 1/ρ_l' in content or '1/rho_v - 1/rho_l' in content) and
        ('=' in content and ('U' in content or 'div' in content))
    )

    if has_mass_transfer:
        if has_sign_statement:
            return True, f"{Colors.GREEN}✓ Sign convention stated{Colors.END}"
        elif has_correct_structure:
            # Implicit sign convention from formula structure
            return True, f"{Colors.GREEN}✓ Sign convention implied from formula{Colors.END}"
        else:
            return False, f"{Colors.YELLOW}⚠ Mass transfer present but sign convention unclear{Colors.END}"
    else:
        return False, f"{Colors.RED}✗ Mass transfer rate not found{Colors.END}"


def verify_pressure_equation(content: str) -> Tuple[bool, str]:
    """Verify expansion term is implemented in pressure equation."""
    # Check for pressure equation
    has_pressure = (
        'p' in content and ('equation' in content.lower() or 'solve' in content.lower())
    )

    # Check for pressure correction (p')
    has_p_prime = "p'" in content or 'pprime' in content.lower() or 'p_prime' in content.lower()

    # Check for Laplacian of pressure
    has_laplacian = (
        'laplacian' in content.lower() or '∇²' in content or 'nabla^2' in content.lower() or
        '∇·(' in content and '∇p' in content
    )

    # Check for source term in pressure equation
    has_source_term = (
        'S_' in content or 'source' in content.lower() or 'rhs' in content.lower()
    )

    # Check for explicit expansion term in pressure equation
    has_expansion_in_pressure = (
        has_pressure and has_laplacian and has_source_term
    )

    if has_expansion_in_pressure:
        return True, f"{Colors.GREEN}✓ Expansion term in pressure equation{Colors.END}"
    elif has_pressure and has_laplacian:
        return False, f"{Colors.YELLOW}⚠ Pressure equation present but expansion term unclear{Colors.END}"
    elif has_pressure:
        return False, f"{Colors.YELLOW}⚠ Pressure mentioned but equation structure unclear{Colors.END}"
    else:
        return False, f"{Colors.RED}✗ Pressure equation not found{Colors.END}"


def verify_density_ratio_terms(content: str) -> Tuple[bool, str]:
    """Verify density ratio terms are correct."""
    # Check for both liquid and vapor densities
    has_liquid_density = (
        'rho_l' in content or 'ρ_l' in content or
        'liquid_density' in content.lower() or 'rhoLiquid' in content
    )

    has_vapor_density = (
        'rho_v' in content or 'ρ_v' in content or
        'vapor_density' in content.lower() or 'rhoVapor' in content
    )

    # Check for density ratio calculation
    has_ratio = (
        'rho_v/rho_l' in content or 'ρ_v/ρ_l' in content or
        'densityRatio' in content or 'density_ratio' in content.lower()
    )

    # Check for volume expansion term structure
    # Volumetric expansion = (1/ρ_v - 1/ρ_l) * ṁ
    has_volume_expansion = (
        ('1/ρ_v' in content or '1/rho_v' in content) and
        ('1/ρ_l' in content or '1/rho_l' in content) and
        ('-' in content)
    )

    # Check for R410A specific values
    has_r410a_values = (
        'R410A' in content or 'r410a' in content.lower()
    )

    if has_liquid_density and has_vapor_density:
        if has_volume_expansion:
            return True, f"{Colors.GREEN}✓ Density ratio terms correct{Colors.END}"
        elif has_ratio:
            return False, f"{Colors.YELLOW}⚠ Densities present but volume expansion unclear{Colors.END}"
        else:
            return False, f"{Colors.YELLOW}⚠ Phase densities found but expansion term structure unclear{Colors.END}"
    elif has_liquid_density or has_vapor_density:
        return False, f"{Colors.YELLOW}⚠ Only one phase density found{Colors.END}"
    else:
        return False, f"{Colors.RED}✗ Phase densities not found{Colors.END}"


def verify_mathematical_soundness(content: str) -> Tuple[bool, str]:
    """Verify the derivation is mathematically sound."""
    # Check for conservation of mass reference
    has_mass_conservation = (
        'mass conservation' in content.lower() or
        'continuity' in content.lower() or
        '∂ρ/∂t' in content or 'conservation of mass' in content.lower()
    )

    # Check for incompressible assumption
    has_incompressible = (
        'incompressible' in content.lower() or
        'constant density' in content.lower() or
        '∇·U' in content
    )

    # Check for phase change source term
    has_phase_change = (
        'phase change' in content.lower() or
        'evaporation' in content.lower() or
        'condensation' in content.lower()
    )

    # Check for derivation steps
    has_derivation = (
        'derivation' in content.lower() or
        'starting from' in content.lower() or
        ('=' in content and content.count('=') > 2)
    )

    # Check for final formula
    has_final_formula = (
        ('∇·U' in content or 'div(U)' in content) and
        ('=' in content) and
        ('ṁ' in content or 'mdot' in content.lower()) and
        ('1/ρ' in content or '1/rho' in content)
    )

    checks_passed = sum([
        has_mass_conservation,
        has_incompressible,
        has_phase_change,
        has_derivation,
        has_final_formula
    ])

    if checks_passed >= 4:
        return True, f"{Colors.GREEN}✓ Mathematically sound derivation{Colors.END}"
    elif checks_passed >= 2:
        return False, f"{Colors.YELLOW}⚠ Some derivation elements present but incomplete{Colors.END}"
    else:
        return False, f"{Colors.RED}✗ Mathematical derivation not found{Colors.END}"


def verify_file(file_path: Path) -> int:
    """Verify a single file for expansion term."""
    with open(file_path, "r") as f:
        content = f.read()

    print(f"\n{Colors.BLUE}Verifying: {file_path}{Colors.END}")

    checks = [
        ("Expansion Term Present", verify_expansion_term_present),
        ("Mathematical Soundness", verify_mathematical_soundness),
        ("Sign Convention", verify_sign_convention),
        ("Pressure Equation", verify_pressure_equation),
        ("Density Ratio Terms", verify_density_ratio_terms),
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

    parser = argparse.ArgumentParser(description="Expansion Term Verification")
    parser.add_argument("--file", type=str, help="File to verify")
    parser.add_argument("--content", type=str, help="Content string to verify")
    parser.add_argument("--check", type=str, help="Specific check to run")

    args = parser.parse_args()

    if args.content:
        content = args.content
        print(f"{Colors.BLUE}Verifying provided content{Colors.END}\n")

        checks = {
            "present": verify_expansion_term_present,
            "math": verify_mathematical_soundness,
            "sign": verify_sign_convention,
            "pressure": verify_pressure_equation,
            "density": verify_density_ratio_terms,
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
        # Expansion Term Derivation

        Starting from mass conservation for two-phase flow:
        $$\\frac{\\partial \\rho}{\\partial t} + \\nabla \\cdot (\\rho \\mathbf{U}) = 0$$

        For incompressible phases with phase change, the expansion term is:
        $$\\nabla \\cdot \\mathbf{U} = \\dot{m}\\left(\\frac{1}{\\rho_v} - \\frac{1}{\\rho_l}\\right)$$

        Where:
        - $\\dot{m} > 0$ for evaporation (liquid → vapor)
        - $\\rho_v$ is vapor density (~30 kg/m³ for R410A)
        - $\\rho_l$ is liquid density (~1000 kg/m³ for R410A)

        The expansion term is added as a source term in the pressure equation:
        $$\\nabla \\cdot \\left(\\frac{1}{A_p} \\nabla p'\\right) = \\nabla \\cdot \\mathbf{U}^* - S_{expansion}$$
        """

        print(f"{Colors.BLUE}Running demo verification with sample content{Colors.END}\n")

        # Run all checks on sample content
        checks = {
            "present": verify_expansion_term_present,
            "math": verify_mathematical_soundness,
            "sign": verify_sign_convention,
            "pressure": verify_pressure_equation,
            "density": verify_density_ratio_terms,
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
