#!/usr/bin/env python3
"""
Two-Phase Flow Physics Verification Script

Verifies two-phase flow implementations for:
- Void fraction bounds
- Density ratio handling
- Surface tension
- Interface compression
"""

import sys
import json
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


def load_ground_truth() -> Dict:
    """Load ground truth from /tmp/verified_facts.json."""
    facts_file = Path("/tmp/verified_facts.json")
    if facts_file.exists():
        with open(facts_file, "r") as f:
            return json.load(f)
    return {}


def verify_void_fraction_bounds(content: str) -> Tuple[bool, str]:
    """Verify void fraction is bounded [0,1]."""
    # Check for void fraction variable (alpha)
    has_alpha = 'alpha' in content.lower() or 'α' in content

    # Check for bounds enforcement
    has_bounds_check = (
        'max(0' in content or 'min(1' in content or
        'max(min(' in content or
        ('bound' in content.lower() and 'alpha' in content.lower())
    )

    # Check for clipping or limiting
    has_clipping = (
        'clip' in content.lower() or
        'clamp' in content.lower() or
        'limit' in content.lower()
    )

    if has_alpha:
        if has_bounds_check or has_clipping:
            return True, f"{Colors.GREEN}✓ Void fraction bounds enforced{Colors.END}"
        else:
            return False, f"{Colors.YELLOW}⚠ Void fraction present but bounds not explicitly enforced{Colors.END}"
    else:
        return False, f"{Colors.RED}✗ Void fraction not found in content{Colors.END}"


def verify_density_ratio(content: str) -> Tuple[bool, str]:
    """Verify large density ratio handling."""
    # Check for density references
    has_density = 'rho' in content.lower() or 'ρ' in content or 'density' in content.lower()

    # Check for phase-specific densities
    has_phase_densities = (
        ('rho_l' in content or 'ρ_l' in content or 'liquid_density' in content.lower()) and
        ('rho_v' in content or 'ρ_v' in content or 'vapor_density' in content.lower())
    )

    # Check for density ratio handling
    has_ratio_handling = (
        'density ratio' in content.lower() or
        'rho_v/rho_l' in content or 'ρ_v/ρ_l' in content
    )

    # Check for large density ratio considerations
    has_large_ratio_consideration = (
        'large density' in content.lower() or
        'density ratio' in content.lower() and ('1/30' in content or '30:1' in content)
    )

    if has_density:
        if has_phase_densities:
            if has_ratio_handling:
                return True, f"{Colors.GREEN}✓ Density ratio handling present{Colors.END}"
            else:
                return False, f"{Colors.YELLOW}⚠ Phase densities found but ratio handling not explicit{Colors.END}"
        else:
            return False, f"{Colors.YELLOW}⚠ Density mentioned but phase-specific densities not found{Colors.END}"
    else:
        return False, f"{Colors.RED}✗ Density not mentioned in content{Colors.END}"


def verify_surface_tension(content: str) -> Tuple[bool, str]:
    """Verify surface tension is included."""
    # Check for surface tension
    has_sigma = 'sigma' in content.lower() or 'σ' in content
    has_surface_tension = 'surface tension' in content.lower()

    # Check for implementation
    has_implementation = (
        'interfaceproperties' in content.lower() or
        'surface_tension' in content.lower() or
        ('sigma' in content.lower() and ('force' in content.lower() or 'model' in content.lower()))
    )

    if has_surface_tension or has_sigma:
        if has_implementation:
            return True, f"{Colors.GREEN}✓ Surface tension included{Colors.END}"
        else:
            return False, f"{Colors.YELLOW}⚠ Surface tension mentioned but implementation unclear{Colors.END}"
    else:
        return False, f"{Colors.RED}✗ Surface tension not found in content{Colors.END}"


def verify_interface_compression(content: str) -> Tuple[bool, str]:
    """Verify interface compression is present."""
    # Check for compression term
    has_compression = (
        'compression' in content.lower() or
        'compress' in content.lower()
    )

    # Check for specific compression schemes
    has_compression_scheme = (
        'mules' in content.lower() or
        'compressive' in content.lower() or
        'interface' in content.lower() and ('sharp' in content.lower() or 'compression' in content.lower())
    )

    # Check for VOF-related terms
    has_vof = 'vof' in content.lower() or 'volume of fluid' in content.lower()

    if has_vof:
        if has_compression_scheme:
            return True, f"{Colors.GREEN}✓ Interface compression scheme present{Colors.END}"
        elif has_compression:
            return False, f"{Colors.YELLOW}⚠ Compression mentioned but scheme not explicit{Colors.END}"
        else:
            return False, f"{Colors.YELLOW}⚠ VOF present but compression scheme unclear{Colors.END}"
    else:
        return False, f"{Colors.RED}✗ Interface compression not found in content{Colors.END}"


def verify_file(file_path: Path) -> int:
    """Verify a single file for two-phase physics."""
    with open(file_path, "r") as f:
        content = f.read()

    print(f"\n{Colors.BLUE}Verifying: {file_path}{Colors.END}")

    checks = [
        ("Void Fraction Bounds", verify_void_fraction_bounds),
        ("Density Ratio Handling", verify_density_ratio),
        ("Surface Tension", verify_surface_tension),
        ("Interface Compression", verify_interface_compression),
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

    parser = argparse.ArgumentParser(description="Two-Phase Flow Physics Verification")
    parser.add_argument("--file", type=str, help="File to verify")
    parser.add_argument("--content", type=str, help="Content string to verify")
    parser.add_argument("--check", type=str, help="Specific check to run")

    args = parser.parse_args()

    if args.content:
        content = args.content
        print(f"{Colors.BLUE}Verifying provided content{Colors.END}\n")

        checks = {
            "void_fraction": verify_void_fraction_bounds,
            "density_ratio": verify_density_ratio,
            "surface_tension": verify_surface_tension,
            "interface_compression": verify_interface_compression,
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
        // Two-phase flow with VOF method
        volScalarField alpha;

        // bounded alpha
        alpha = max(min(alpha, scalar(1)), scalar(0));

        // Phase densities
        const dimensionedScalar rho_l(1000);
        const dimensionedScalar rho_v(30);

        // Density ratio
        const scalar densityRatio = rho_v / rho_l;  // ~1/30 for R410A

        // Surface tension
        const dimensionedScalar sigma(0.07);

        // Interface compression
        surfaceScalarField phiAlpha(mesh.Sf() * fvc::interpolate(alpha));
        """

        print(f"{Colors.BLUE}Running demo verification with sample content{Colors.END}\n")

        # Run all checks on sample content
        checks = {
            "void_fraction": verify_void_fraction_bounds,
            "density_ratio": verify_density_ratio,
            "surface_tension": verify_surface_tension,
            "interface_compression": verify_interface_compression,
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
