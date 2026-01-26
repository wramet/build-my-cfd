#!/usr/bin/env python3
"""
Verify that claimed class hierarchy matches actual OpenFOAM source code.

This script extracts actual class inheritance from header files and compares
them with the hierarchy claimed in AI-generated analysis to catch hallucinations.

Usage:
    python verify_class_hierarchy.py \
        --actual-hierarchy /tmp/actual_hierarchy.txt \
        --claimed-analysis daily_learning/drafts/day03_research_headers.md \
        --output daily_learning/drafts/day03_verification_report.md
"""

import argparse
import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple


def extract_actual_hierarchy(hierarchy_file: str) -> Dict[str, str]:
    """
    Extract actual class inheritance from grep output.

    Input format (from grep):
        === /path/to/file.H ===
        class className : public baseClass

    Returns:
        Dict mapping {className: baseClass}
    """
    hierarchy = {}
    current_file = None

    content = Path(hierarchy_file).read_text()

    for line in content.split('\n'):
        line = line.strip()
        if not line:
            continue

        # File separator
        if line.startswith('===') and line.endswith('==='):
            current_file = line.strip('=').strip()
            continue

        # Class inheritance: class className : public baseClass
        # Handle both single-line and template classes
        match = re.search(r'class\s+(\w+)\s*:\s*public\s+(\w+)', line)
        if match:
            child, parent = match.groups()
            hierarchy[child] = {
                'parent': parent,
                'file': current_file
            }

    return hierarchy


def extract_claimed_hierarchy(markdown_file: str) -> Dict[str, str]:
    """
    Extract claimed class hierarchy from markdown analysis.

    Looks for patterns like:
        - upwind : public surfaceInterpolationScheme
        - class upwind : public surfaceInterpolationScheme

    Returns:
        Dict mapping {className: baseClass}
    """
    hierarchy = {}

    content = Path(markdown_file).read_text()

    # Pattern 1: "className : public baseClass" (in code blocks or text)
    pattern1 = r'(\w+)\s*:\s*public\s+(\w+)'
    matches = re.findall(pattern1, content)

    for child, parent in matches:
        # Filter out common non-class terms
        if child not in ['return', 'const', 'virtual', 'tmp', 'void']:
            hierarchy[child] = parent

    # Pattern 2: Mermaid diagram syntax: Child --> Parent
    pattern2 = r'(\w+)\s+-->\s+(\w+)'
    matches2 = re.findall(pattern2, content)

    for child, parent in matches2:
        if child not in hierarchy:  # Don't override if already found
            hierarchy[child] = parent

    return hierarchy


def compare_hierarchies(actual: Dict, claimed: Dict) -> List[dict]:
    """
    Compare actual vs claimed hierarchies.

    Returns:
        List of discrepancy dicts with keys: class, claimed, actual, status
    """
    discrepancies = []

    for class_name, claimed_parent in claimed.items():
        if class_name in actual:
            actual_parent = actual[class_name]['parent']
            actual_file = actual[class_name]['file']

            if actual_parent != claimed_parent:
                discrepancies.append({
                    'class': class_name,
                    'claimed_parent': claimed_parent,
                    'actual_parent': actual_parent,
                    'source_file': actual_file,
                    'status': '❌ MISMATCH'
                })
            else:
                discrepancies.append({
                    'class': class_name,
                    'claimed_parent': claimed_parent,
                    'actual_parent': actual_parent,
                    'source_file': actual_file,
                    'status': '✅ VERIFIED'
                })
        else:
            discrepancies.append({
                'class': class_name,
                'claimed_parent': claimed_parent,
                'actual_parent': 'NOT FOUND',
                'source_file': 'N/A',
                'status': '⚠️  CLASS NOT FOUND IN SOURCE'
            })

    return discrepancies


def generate_report(discrepancies: List[dict], output_file: str) -> bool:
    """
    Generate verification report in markdown format.

    Returns:
        True if all verified, False if any mismatches found
    """
    has_errors = any(d['status'] in ['❌ MISMATCH', '⚠️  CLASS NOT FOUND'] for d in discrepancies)

    with open(output_file, 'w') as f:
        f.write("# 🔒 Class Hierarchy Verification Report\n\n")
        f.write(f"**Generated:** Verification of AI-generated content against actual OpenFOAM source code\n\n")

        # Summary
        verified_count = sum(1 for d in discrepancies if d['status'] == '✅ VERIFIED')
        error_count = sum(1 for d in discrepancies if d['status'] == '❌ MISMATCH')
        not_found_count = sum(1 for d in discrepancies if 'NOT FOUND' in d['status'])

        f.write("## Summary\n\n")
        f.write(f"| Status | Count |\n")
        f.write(f"|--------|-------|\n")
        f.write(f"| ✅ Verified | {verified_count} |\n")
        f.write(f"| ❌ Mismatch | {error_count} |\n")
        f.write(f"| ⚠️  Not Found | {not_found_count} |\n")
        f.write(f"| **Total** | **{len(discrepancies)}** |\n\n")

        if has_errors:
            f.write("## ⚠️  CRITICAL ISSUES FOUND\n\n")
            f.write("The following discrepancies were detected. **Content generation must be halted** until these are resolved.\n\n")
        else:
            f.write("## ✅ All Classes Verified\n\n")
            f.write("All claimed class hierarchies match the actual OpenFOAM source code.\n\n")

        # Detailed results
        f.write("## Detailed Results\n\n")

        for d in discrepancies:
            f.write(f"### {d['class']}\n\n")
            f.write(f"- **Claimed:** `{d['class']} : public {d['claimed_parent']}`\n")
            f.write(f"- **Actual:** `{d['class']} : public {d['actual_parent']}`\n")
            f.write(f"- **Status:** {d['status']}\n")
            if d['source_file'] != 'N/A':
                f.write(f"- **Source:** `{d['source_file']}`\n")
            f.write("\n")

        # Recommendations
        if has_errors:
            f.write("## 🛠️  Required Actions\n\n")
            f.write("1. **Do NOT use** the current draft content\n")
            f.write("2. **Fix the skeleton** if it contained incorrect hierarchy\n")
            f.write("3. **Re-run** the GLM analysis with corrected information\n")
            f.write("4. **Re-verify** before proceeding to content synthesis\n\n")
            f.write("### For Common Mistakes:\n\n")
            f.write("| Wrong | Correct |\n")
            f.write("|-------|----------|\n")
            f.write("| `upwind : public surfaceInterpolationScheme` | `upwind : public limitedSurfaceInterpolationScheme` |\n")
            f.write("| `linear : public surfaceInterpolationScheme` | `linear : public surfaceInterpolationScheme` (correct) |\n")
            f.write("| `vanLeer : public limitedSurfaceInterpolationScheme` | `vanLeer` is a limiter, not a scheme class |\n\n")

    return not has_errors


def main():
    parser = argparse.ArgumentParser(
        description='Verify claimed class hierarchy against actual source code'
    )
    parser.add_argument(
        '--actual-hierarchy',
        required=True,
        help='File containing grep output of actual class inheritance'
    )
    parser.add_argument(
        '--claimed-analysis',
        required=True,
        help='Markdown file containing AI-generated class analysis'
    )
    parser.add_argument(
        '--output',
        required=True,
        help='Output file for verification report'
    )

    args = parser.parse_args()

    # Extract hierarchies
    print(f"🔍 Extracting actual hierarchy from {args.actual_hierarchy}...")
    actual = extract_actual_hierarchy(args.actual_hierarchy)
    print(f"   Found {len(actual)} classes in source code")

    print(f"🔍 Extracting claimed hierarchy from {args.claimed_analysis}...")
    claimed = extract_claimed_hierarchy(args.claimed_analysis)
    print(f"   Found {len(claimed)} classes in analysis")

    # Compare
    print("🔍 Comparing hierarchies...")
    discrepancies = compare_hierarchies(actual, claimed)

    # Generate report
    print(f"📝 Generating report: {args.output}")
    all_verified = generate_report(discrepancies, args.output)

    if all_verified:
        print("✅ All class hierarchies verified successfully!")
        return 0
    else:
        print("❌ Verification failed. Please review the report.")
        return 1


if __name__ == '__main__':
    sys.exit(main())
