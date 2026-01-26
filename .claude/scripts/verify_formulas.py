#!/usr/bin/env python3
"""
Verify that claimed mathematical formulas match actual OpenFOAM source code.

This script extracts actual formulas from source code (e.g., TVD limiter implementations)
and compares them with formulas derived by AI to catch mathematical hallucinations.

Usage:
    python verify_formulas.py \
        --actual-formulas /tmp/actual_formulas.txt \
        --claimed-formulas daily_learning/drafts/day03_math_derivation.md \
        --output daily_learning/drafts/day03_formula_verification.md
"""

import argparse
import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple


def extract_actual_formulas(formulas_file: str) -> Dict[str, str]:
    """
    Extract actual formulas from grep output of source files.

    Input format (from grep -A 2 "return"):
        === /path/to/limiter.H ===
        return (r + mag(r))/(1 + mag(r));

    Returns:
        Dict mapping {limiter_name: formula}
    """
    formulas = {}
    current_file = None
    current_class = None

    content = Path(formulas_file).read_text()

    for line in content.split('\n'):
        line = line.strip()
        if not line:
            continue

        # File separator
        if line.startswith('===') and line.endswith('==='):
            current_file = line.strip('=').strip()
            # Extract class name from file path
            current_class = Path(current_file).stem
            continue

        # Return statement with formula
        if 'return' in line and ('r' in line or 'phi' in line):
            # Clean up the formula
            formula = line.strip()
            # Remove leading/trailing whitespace, 'return', ';'
            formula = re.sub(r'^return\s+', '', formula)
            formula = re.sub(r';\s*$', '', formula)
            formula = formula.strip()

            if formula and current_class:
                formulas[current_class] = {
                    'formula': formula,
                    'file': current_file
                }

    return formulas


def extract_claimed_formulas(markdown_file: str) -> Dict[str, str]:
    """
    Extract claimed formulas from markdown math derivation.

    Looks for:
    - LaTeX formulas: \psi(r) = ...
    - Named limiters: van Leer, SuperBee, van Albada

    Returns:
        Dict mapping {limiter_name: formula}
    """
    formulas = {}
    content = Path(markdown_file).read_text()

    # Common limiter names
    limiter_names = ['vanLeer', 'van Leer', 'vanLeer01', 'SuperBee', 'vanAlbada', 'minmod', 'UMIST']

    for limiter in limiter_names:
        # Look for formula patterns near the limiter name
        # Pattern: limiter name followed by formula within ~500 characters
        idx = content.lower().find(limiter.lower())
        if idx != -1:
            # Extract surrounding text
            surrounding = content[max(0, idx-50):min(len(content), idx+500)]

            # Look for LaTeX formula patterns
            # Pattern 1: \psi(r) = ... or ψ(r) = ...
            latex_pattern = r'[ψ\w^\\psi]+\([^)]+\)\s*=\s*([^$\n]+)'
            matches = re.findall(latex_pattern, surrounding)

            if matches:
                # Take the first match as the main formula
                formula = matches[0].strip()
                # Clean up LaTeX
                formula = formula.replace('\\\\', '\\')
                formula = formula.replace('\\frac', '(')
                formula = re.sub(r'\{([^}]+)\}\{([^}]+)\)', r'(\1)/(\2)', formula)
                formulas[limiter] = formula

    return formulas


def formula_to_code_style(latex_formula: str) -> str:
    """
    Convert LaTeX formula to C++ code style for comparison.

    Examples:
        (r + |r|) / (1 + |r|) -> (r + mag(r))/(1 + mag(r))
        max(0, min(2r, 1)) -> max(0, min(2*r, 1))
    """
    code_style = latex_formula

    # Replace common LaTeX/math notation with C++ equivalents
    code_style = code_style.replace('|r|', 'mag(r)')
    code_style = code_style.replace('|r', 'mag(r)')
    code_style = code_style.replace('·', '*')
    code_style = code_style.replace('−', '-')  # Minus sign to hyphen

    # Add multiplication signs where needed
    code_style = re.sub(r'(\d)\(', r'\1*(', code_style)  # 2( -> 2*(
    code_style = re.sub(r'\)r', r')*r', code_style)      # )r -> )*r

    return code_style


def compare_formulas(actual: Dict, claimed: Dict) -> List[dict]:
    """
    Compare actual vs claimed formulas.

    Returns:
        List of comparison results
    """
    comparisons = []

    # Check each claimed limiter
    for limiter_name, claimed_formula in claimed.items():
        # Try to find matching actual formula
        # Normalize names (van Leer -> vanLeer)
        normalized_name = limiter_name.replace(' ', '')

        if normalized_name in actual:
            actual_entry = actual[normalized_name]
            actual_formula = actual_entry['formula']

            # Convert claimed formula to code style for comparison
            claimed_code_style = formula_to_code_style(claimed_formula)

            # Simple comparison (could be improved with AST-based comparison)
            if normalized_claimed := normalize_formula(claimed_code_style):
                if normalized_actual := normalize_formula(actual_formula):
                    if normalized_claimed == normalized_actual:
                        comparisons.append({
                            'limiter': limiter_name,
                            'claimed': claimed_formula,
                            'actual': actual_formula,
                            'source_file': actual_entry['file'],
                            'status': '✅ VERIFIED'
                        })
                    else:
                        comparisons.append({
                            'limiter': limiter_name,
                            'claimed': claimed_formula,
                            'actual': actual_formula,
                            'source_file': actual_entry['file'],
                            'status': '❌ MISMATCH',
                            'note': f'Claimed: {normalized_claimed}, Actual: {normalized_actual}'
                        })
                    continue

        # If we get here, verification failed
        comparisons.append({
            'limiter': limiter_name,
            'claimed': claimed_formula,
            'actual': actual.get(normalized_name, {}).get('formula', 'NOT FOUND'),
            'source_file': actual.get(normalized_name, {}).get('file', 'N/A'),
            'status': '⚠️  CANNOT VERIFY'
        })

    return comparisons


def normalize_formula(formula: str) -> str:
    """
    Normalize formula for comparison by removing whitespace and standardizing.

    Examples:
        (r + mag(r))/(1 + mag(r)) -> r+mag(r)/1+mag(r)
        max(0, min(2*r, 1)) -> max(0,min(2*r,1))
    """
    normalized = formula
    normalized = re.sub(r'\s+', '', normalized)  # Remove all whitespace
    normalized = normalized.lower()  # Case insensitive
    return normalized


def generate_report(comparisons: List[dict], output_file: str) -> bool:
    """
    Generate formula verification report.

    Returns:
        True if all verified, False if any issues found
    """
    has_errors = any(c['status'] in ['❌ MISMATCH', '⚠️  CANNOT VERIFY'] for c in comparisons)

    with open(output_file, 'w') as f:
        f.write("# 🔒 Mathematical Formula Verification Report\n\n")
        f.write(f"**Generated:** Verification of AI-derived formulas against actual OpenFOAM implementations\n\n")

        # Summary
        verified_count = sum(1 for c in comparisons if c['status'] == '✅ VERIFIED')
        mismatch_count = sum(1 for c in comparisons if c['status'] == '❌ MISMATCH')
        unverified_count = sum(1 for c in comparisons if 'CANNOT VERIFY' in c['status'])

        f.write("## Summary\n\n")
        f.write(f"| Status | Count |\n")
        f.write(f"|--------|-------|\n")
        f.write(f"| ✅ Verified | {verified_count} |\n")
        f.write(f"| ❌ Mismatch | {mismatch_count} |\n")
        f.write(f"| ⚠️  Cannot Verify | {unverified_count} |\n")
        f.write(f"| **Total** | **{len(comparisons)}** |\n\n")

        if has_errors:
            f.write("## ⚠️  FORMULA ISSUES FOUND\n\n")
            f.write("The following formula discrepancies were detected.\n\n")
        else:
            f.write("## ✅ All Formulas Verified\n\n")

        # Detailed results
        f.write("## Detailed Results\n\n")

        for c in comparisons:
            f.write(f"### {c['limiter']} Limiter\n\n")
            f.write(f"- **Claimed Formula:** ${c['claimed']}$\n")
            f.write(f"- **Actual Code:** `{c['actual']}`\n")
            f.write(f"- **Status:** {c['status']}\n")
            if c['source_file'] != 'N/A':
                f.write(f"- **Source:** `{c['source_file']}`\n")
            if 'note' in c:
                f.write(f"- **Note:** {c['note']}\n")
            f.write("\n")

        # Common corrections
        if mismatch_count > 0:
            f.write("## 🛠️  Common Formula Corrections\n\n")
            f.write("| Limiter | Wrong | Correct |\n")
            f.write("|---------|-------|----------|\n")
            f.write("| van Leer | `ψ(r) = (r + |r|)/(1 + r)` | `ψ(r) = (r + |r|)/(1 + |r|)` |\n")
            f.write("| SuperBee | `max[0, min(2r, 1)]` | `max(0, min(2*r, 1), min(r, 2))` |\n\n")

    return not has_errors


def main():
    parser = argparse.ArgumentParser(
        description='Verify claimed formulas against actual source code'
    )
    parser.add_argument(
        '--actual-formulas',
        required=True,
        help='File containing grep output of actual formulas'
    )
    parser.add_argument(
        '--claimed-formulas',
        required=True,
        help='Markdown file containing AI-derived formulas'
    )
    parser.add_argument(
        '--output',
        required=True,
        help='Output file for verification report'
    )

    args = parser.parse_args()

    # Extract formulas
    print(f"🔍 Extracting actual formulas from {args.actual_formulas}...")
    actual = extract_actual_formulas(args.actual_formulas)
    print(f"   Found {len(actual)} formulas in source code")

    print(f"🔍 Extracting claimed formulas from {args.claimed_formulas}...")
    claimed = extract_claimed_formulas(args.claimed_formulas)
    print(f"   Found {len(claimed)} formulas in derivation")

    # Compare
    print("🔍 Comparing formulas...")
    comparisons = compare_formulas(actual, claimed)

    # Generate report
    print(f"📝 Generating report: {args.output}")
    all_verified = generate_report(comparisons, args.output)

    if all_verified:
        print("✅ All formulas verified successfully!")
        return 0
    else:
        print("⚠️  Some formulas could not be verified. Please review the report.")
        return 1


if __name__ == '__main__':
    sys.exit(main())
