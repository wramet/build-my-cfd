#!/usr/bin/env python3
"""
Verify skeleton against ground truth facts.

This script checks that AI-generated skeleton content matches
the actual ground truth extracted from OpenFOAM source code.

Usage:
    python verify_skeleton.py --ground-truth verified_facts.json \
                          --skeleton day03_skeleton.json \
                          --output verification_report.md
"""

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Any

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.workflow_logger import get_logger, log_phase, log_verification



def load_ground_truth(gt_file: str) -> Dict[str, Any]:
    """Load verified ground truth from JSON file."""
    with open(gt_file) as f:
        return json.load(f)


def load_skeleton(skeleton_file: str) -> Dict[str, Any]:
    """Load skeleton JSON file."""
    with open(skeleton_file) as f:
        return json.load(f)


def verify_class_hierarchy(
    ground_truth: Dict,
    skeleton: Dict
) -> List[Dict[str, str]]:
    """
    Verify class hierarchy in skeleton matches ground truth.

    Returns:
        List of verification results
    """
    results = []
    gt_hierarchy = ground_truth.get('class_hierarchy', {})

    # Check OpenFOAM analysis section
    openfoam_analysis = skeleton.get('openfoam_analysis', [])

    for class_info in openfoam_analysis:
        class_name = class_info.get('class', '')

        # Extract claimed base class from inheritance_hierarchy or similar
        claimed_base = None
        if 'inheritance_hierarchy' in class_info:
            hierarchy = class_info['inheritance_hierarchy']
            # Parse hierarchy to find base class
            for item in hierarchy:
                if f'↑ {class_name}' in item or f'class {class_name}' in item:
                    # Try to extract base class name
                    match = re.search(r'→\s*(\w+)', item)
                    if match and match.group(1) not in ['class', 'Type']:
                        claimed_base = match.group(1)
                        break

        # Check if class exists in ground truth
        if class_name in gt_hierarchy:
            actual_base = gt_hierarchy[class_name]['base_class']

            result = {
                'class': class_name,
                'type': 'class_hierarchy',
                'claimed_base': claimed_base,
                'actual_base': actual_base,
                'status': '✅ VERIFIED' if claimed_base == actual_base else '❌ MISMATCH',
                'ground_truth_source': gt_hierarchy[class_name]['file']
            }
        else:
            result = {
                'class': class_name,
                'type': 'class_hierarchy',
                'claimed_base': claimed_base,
                'actual_base': 'NOT FOUND',
                'status': '⚠️  NOT IN GROUND TRUTH',
                'ground_truth_source': 'N/A'
            }

        results.append(result)

    return results


def verify_formulas(
    ground_truth: Dict,
    skeleton: Dict
) -> List[Dict[str, str]]:
    """
    Verify mathematical formulas in skeleton match ground truth.

    Returns:
        List of verification results
    """
    results = []
    gt_formulas = ground_truth.get('formulas', {})

    # Check theory sections for formulas
    theory_sections = skeleton.get('theory_sections', [])

    for section in theory_sections:
        limiter_functions = section.get('limiter_functions', [])

        for limiter_info in limiter_functions:
            limiter_name = limiter_info.get('name', '')
            claimed_formula = limiter_info.get('formula', '')

            # Try to find matching ground truth formula
            actual_formula = None
            actual_source = None

            for gt_name, gt_info in gt_formulas.items():
                if limiter_name.lower() in gt_name.lower() or gt_name.lower() in limiter_name.lower():
                    actual_formula = gt_info['formula']
                    actual_source = gt_info['file']
                    break

            if actual_formula:
                # Normalize formulas for comparison
                claimed_normalized = normalize_formula(claimed_formula)
                actual_normalized = normalize_formula(actual_formula)

                result = {
                    'limiter': limiter_name,
                    'type': 'formula',
                    'claimed_formula': claimed_formula,
                    'actual_formula': actual_formula,
                    'status': '✅ VERIFIED' if claimed_normalized == actual_normalized else '❌ MISMATCH',
                    'ground_truth_source': actual_source
                }
            else:
                result = {
                    'limiter': limiter_name,
                    'type': 'formula',
                    'claimed_formula': claimed_formula,
                    'actual_formula': 'NOT FOUND',
                    'status': '⚠️  NOT IN GROUND TRUTH',
                    'ground_truth_source': 'N/A'
                }

            results.append(result)

    return results


def normalize_formula(formula: str) -> str:
    """
    Normalize formula string for comparison.

    Removes spaces, converts common notation, etc.
    """
    normalized = formula.lower()
    normalized = normalized.replace(' ', '')
    normalized = normalized.replace('\\frac', '')
    normalized = normalized.replace('left(', '')
    normalized = normalized.replace('right(', '')
    normalized = normalized.replace('\\left', '')
    normalized = normalized.replace('\\right', '')
    return normalized


def generate_report(
    results: List[Dict],
    ground_truth: Dict,
    skeleton: Dict,
    output_file: str
) -> bool:
    """
    Generate verification report in markdown format.

    Returns:
        True if all verified, False if any failures
    """
    has_errors = any('❌' in r.get('status', '') for r in results)

    with open(output_file, 'w') as f:
        f.write("# 🔒 Skeleton Verification Report\n\n")
        f.write(f"**Skeleton:** {skeleton.get('title', 'Unknown')}\n")
        f.write(f"**Day:** {skeleton.get('day', 'Unknown')}\n")
        f.write(f"**Verification Date:** {ground_truth.get('verification_date', 'Unknown')}\n\n")

        # Summary
        verified = sum(1 for r in results if '✅' in r.get('status', ''))
        failed = sum(1 for r in results if '❌' in r.get('status', ''))
        warnings = sum(1 for r in results if '⚠️' in r.get('status', ''))

        f.write("## Summary\n\n")
        f.write(f"| Status | Count |\n")
        f.write(f"|--------|-------|\n")
        f.write(f"| ✅ Verified | {verified} |\n")
        f.write(f"| ❌ Failed | {failed} |\n")
        f.write(f"| ⚠️  Warning | {warnings} |\n")
        f.write(f"| **Total** | {len(results)} |\n\n")

        if has_errors:
            f.write("## ❌ VERIFICATION FAILED\n\n")
            f.write("The skeleton contains errors that MUST be fixed before use:\n\n")
        else:
            f.write("## ✅ VERIFICATION PASSED\n\n")
            f.write("Skeleton is technically accurate and ready for content expansion.\n\n")

        # Detailed results
        f.write("## Detailed Results\n\n")

        # Group by type
        by_type = {}
        for r in results:
            rtype = r['type']
            if rtype not in by_type:
                by_type[rtype] = []
            by_type[rtype].append(r)

        for rtype, items in by_type.items():
            f.write(f"### {rtype.replace('_', ' ').title()}\n\n")

            for item in items:
                if rtype == 'class_hierarchy':
                    f.write(f"#### Class: {item['class']}\n\n")
                    f.write(f"- **Claimed Base:** `{item.get('claimed_base', 'N/A')}`\n")
                    f.write(f"- **Actual Base:** `{item.get('actual_base', 'N/A')}`\n")
                    f.write(f"- **Status:** {item['status']}\n")
                    if item.get('ground_truth_source') != 'N/A':
                        f.write(f"- **Source:** `{item['ground_truth_source']}`\n")
                    f.write("\n")

                elif rtype == 'formula':
                    f.write(f"#### Limiter: {item['limiter']}\n\n")
                    f.write(f"- **Claimed Formula:** `${item.get('claimed_formula', 'N/A')}$`\n")
                    f.write(f"- **Actual Formula:** `{item.get('actual_formula', 'N/A')}`\n")
                    f.write(f"- **Status:** {item['status']}\n")
                    if item.get('ground_truth_source') != 'N/A':
                        f.write(f"- **Source:** `{item['ground_truth_source']}`\n")
                    f.write("\n")

        # Recommendations if failed
        if has_errors:
            f.write("## 🔧 Required Actions\n\n")
            f.write("1. **Review the verification report** above\n")
            f.write("2. **Fix the skeleton manually** OR **rerun Stage 3** with stronger emphasis\n")
            f.write("3. **Re-verify** before proceeding to content expansion\n\n")
            f.write("### Common Fixes:\n\n")
            f.write("| Error Type | Fix |\n")
            f.write("|------------|-----|\n")
            f.write("| Wrong base class | Update inheritance_hierarchy to match actual source |\n")
            f.write("| Wrong formula | Copy exact formula from ground truth |\n")
            f.write("| Missing class | Add to skeleton or verify it exists in source |\n")

    return not has_errors


def main():
    import re  # Need to import re for the function

    parser = argparse.ArgumentParser(
        description='Verify skeleton against ground truth'
    )
    parser.add_argument(
        '--ground-truth',
        required=True,
        help='Ground truth JSON file'
    )
    parser.add_argument(
        '--skeleton',
        required=True,
        help='Skeleton JSON file to verify'
    )
    parser.add_argument(
        '--output',
        required=True,
        help='Output verification report'
    )

    args = parser.parse_args()

    # Initialize logger
    logger = get_logger()
    log_phase(4, "Gate 4: Verify Skeleton (Manual Check)", f"Skeleton: {args.skeleton}")

    # Load files
    print("🔍 Loading ground truth and skeleton...")
    logger.logger.info(f"Loading ground truth: {args.ground_truth}")
    logger.logger.info(f"Loading skeleton: {args.skeleton}")
    
    ground_truth = load_ground_truth(args.ground_truth)
    skeleton = load_skeleton(args.skeleton)

    # Verify
    print("🔍 Verifying class hierarchy...")
    hierarchy_results = verify_class_hierarchy(ground_truth, skeleton)

    print("🔍 Verifying formulas...")
    formula_results = verify_formulas(ground_truth, skeleton)

    all_results = hierarchy_results + formula_results
    
    # Log detailed verification results
    verified_count = sum(1 for r in all_results if '✅' in r.get('status', ''))
    issues_count = sum(1 for r in all_results if '❌' in r.get('status', ''))
    log_verification(args.skeleton, {'verified': verified_count}, issues_count)

    # Generate report
    print(f"📝 Generating report: {args.output}")
    success = generate_report(all_results, ground_truth, skeleton, args.output)

    if success:
        print("✅ Skeleton verification PASSED")
        logger.logger.info("✅ Gate 4 PASSED: Skeleton verification successful")
        return 0
    else:
        print("❌ Skeleton verification FAILED")
        print(f"   Please review: {args.output}")
        logger.logger.info(f"❌ Gate 4 FAILED: {issues_count} issues found. See {args.output}")
        return 1


if __name__ == '__main__':
    sys.exit(main())
