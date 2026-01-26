#!/usr/bin/env python3
"""
Verify GLM output against ground truth facts.

This script checks that GLM-generated class hierarchy and
technical claims match the verified ground truth from source code.

Usage:
    python verify_glm_output.py --glm-output glm_out.md \
                                --ground-truth verified_facts.json \
                                --output verification_report.md
"""

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Dict, List, Any


def load_glm_output(output_file: str) -> str:
    """Load GLM output markdown file."""
    with open(output_file) as f:
        return f.read()


def load_ground_truth(gt_file: str) -> Dict[str, Any]:
    """Load verified ground truth from JSON file."""
    with open(gt_file) as f:
        return json.load(f)


def extract_class_hierarchy_from_glm(glm_output: str) -> List[Dict[str, str]]:
    """
    Extract class hierarchy claims from GLM output.

    Looks for patterns like:
    - "ClassName inherits from BaseClass"
    - "ClassName : public BaseClass"
    - Mermaid diagrams with inheritance arrows
    """
    claims = []

    # Pattern 1: Text descriptions
    text_patterns = [
        r'(\w+)\s+inherits?\s+from\s+(\w+)',
        r'(\w+)\s+:\s*public\s+(\w+)',
        r'class\s+(\w+).*?extends\s+(\w+)',
    ]

    for pattern in text_patterns:
        matches = re.finditer(pattern, glm_output, re.IGNORECASE)
        for match in matches:
            child, parent = match.groups()
            # Filter out common non-class terms
            if child.lower() not in ['return', 'class', 'template', 'type', 'void', 'bool']:
                claims.append({
                    'child': child,
                    'claimed_parent': parent,
                    'source': 'text_description'
                })

    # Pattern 2: Mermaid diagrams
    mermaid_matches = re.finditer(
        r'```mermaid\s+(.*?)```',
        glm_output,
        re.DOTALL
    )

    for match in mermaid_matches:
        diagram = match.group(1)
        # Look for inheritance arrows
        arrow_matches = re.finditer(r'(\w+)\s*-->\s*(\w+)', diagram)
        for arrow_match in arrow_matches:
            child, parent = arrow_match.groups()
            if child.lower() not in ['return', 'class', 'style', 'link']:
                claims.append({
                    'child': child,
                    'claimed_parent': parent,
                    'source': 'mermaid_diagram'
                })

    return claims


def verify_class_hierarchy_claims(
    claims: List[Dict[str, str]],
    ground_truth: Dict[str, Any]
) -> List[Dict[str, str]]:
    """
    Verify class hierarchy claims against ground truth.

    Returns list of verification results.
    """
    results = []
    gt_hierarchy = ground_truth.get('class_hierarchy', {})

    for claim in claims:
        child = claim['child']
        claimed_parent = claim['claimed_parent']

        if child in gt_hierarchy:
            actual_parent = gt_hierarchy[child].get('base_class', 'UNKNOWN')

            if claimed_parent == actual_parent:
                status = '✅ VERIFIED'
            else:
                status = '❌ MISMATCH'

            results.append({
                'type': 'class_hierarchy',
                'child': child,
                'claimed_parent': claimed_parent,
                'actual_parent': actual_parent,
                'source': claim['source'],
                'status': status
            })
        else:
            results.append({
                'type': 'class_hierarchy',
                'child': child,
                'claimed_parent': claimed_parent,
                'actual_parent': 'NOT FOUND IN GROUND TRUTH',
                'source': claim['source'],
                'status': '⚠️  NOT VERIFIED'
            })

    return results


def extract_formula_claims(glm_output: str) -> List[Dict[str, str]]:
    """
    Extract mathematical formula claims from GLM output.

    Looks for LaTeX math blocks and inline formulas.
    """
    claims = []

    # Block math: $$...$$
    block_matches = re.findall(r'\$\$([^$]+)\$\$', glm_output)
    for formula in block_matches:
        claims.append({
            'formula': formula.strip(),
            'source': 'block_latex'
        })

    # Inline math: $...$
    inline_matches = re.findall(r'\$([^$]+)\$', glm_output)
    for formula in inline_matches:
        # Only include if it looks like a formula (has operators or functions)
        if re.search(r'[+\-*/=^]|\\frac|\\sqrt|\\nabla', formula):
            claims.append({
                'formula': formula.strip(),
                'source': 'inline_latex'
            })

    return claims


def normalize_formula(formula: str) -> str:
    """Normalize formula for comparison."""
    normalized = formula.lower().replace(' ', '')
    normalized = normalized.replace('\\frac', '')
    normalized = normalized.replace('\\left(', '')
    normalized = normalized.replace('\\right(', '')
    normalized = normalized.replace('\\left', '')
    normalized = normalized.replace('\\right', '')
    return normalized


def verify_formula_claims(
    claims: List[Dict[str, str]],
    ground_truth: Dict[str, Any]
) -> List[Dict[str, str]]:
    """
    Verify formula claims against ground truth.

    Returns list of verification results.
    """
    results = []
    gt_formulas = ground_truth.get('formulas', {})

    for claim in claims:
        formula = claim['formula']
        normalized_claim = normalize_formula(formula)

        # Try to find matching ground truth formula
        matched = False
        for gt_name, gt_info in gt_formulas.items():
            gt_formula = gt_info.get('formula', '')
            normalized_gt = normalize_formula(gt_formula)

            if normalized_claim == normalized_gt:
                results.append({
                    'type': 'formula',
                    'claimed_formula': formula,
                    'ground_truth_formula': gt_formula,
                    'limiter_name': gt_name,
                    'status': '✅ VERIFIED'
                })
                matched = True
                break

        if not matched:
            results.append({
                'type': 'formula',
                'claimed_formula': formula,
                'ground_truth_formula': 'NOT FOUND',
                'limiter_name': 'UNKNOWN',
                'status': '⚠️  NOT VERIFIED'
            })

    return results


def generate_report(
    hierarchy_results: List[Dict[str, str]],
    formula_results: List[Dict[str, str]],
    output_file: str
) -> bool:
    """
    Generate verification report in markdown format.

    Returns True if all verified, False if any failures.
    """
    all_results = hierarchy_results + formula_results
    has_errors = any('❌' in r.get('status', '') for r in all_results)

    with open(output_file, 'w') as f:
        f.write("# 🔒 GLM Output Verification Report\n\n")

        # Summary
        verified = sum(1 for r in all_results if '✅' in r.get('status', ''))
        failed = sum(1 for r in all_results if '❌' in r.get('status', ''))
        warnings = sum(1 for r in all_results if '⚠️' in r.get('status', ''))

        f.write("## Summary\n\n")
        f.write(f"| Status | Count |\n")
        f.write(f"|--------|-------|\n")
        f.write(f"| ✅ Verified | {verified} |\n")
        f.write(f"| ❌ Errors | {failed} |\n")
        f.write(f"| ⚠️  Warnings | {warnings} |\n")
        f.write(f"| **Total** | {len(all_results)} |\n\n")

        if has_errors:
            f.write("## ❌ VERIFICATION FAILED\n\n")
            f.write("GLM output contains technical errors. Use ground truth instead.\n\n")
        else:
            f.write("## ✅ VERIFICATION PASSED\n\n")
            f.write("GLM output is technically accurate. Safe to use.\n\n")

        # Detailed results
        if hierarchy_results:
            f.write("### Class Hierarchy Verification\n\n")
            for r in hierarchy_results:
                f.write(f"#### {r['child']} → {r['claimed_parent']}\n")
                f.write(f"- **Actual:** {r['actual_parent']}\n")
                f.write(f"- **Status:** {r['status']}\n")
                f.write(f"- **Source:** {r['source']}\n\n")

        if formula_results:
            f.write("### Formula Verification\n\n")
            for r in formula_results:
                f.write(f"- Claimed: `${r['claimed_formula']}`\n")
                if r['ground_truth_formula'] != 'NOT FOUND':
                    f.write(f"- Ground Truth: `{r['ground_truth_formula']}`\n")
                f.write(f"- **Status:** {r['status']}\n\n")

    return not has_errors


def main():
    parser = argparse.ArgumentParser(
        description='Verify GLM output against ground truth'
    )
    parser.add_argument(
        '--glm-output',
        required=True,
        help='GLM output markdown file'
    )
    parser.add_argument(
        '--ground-truth',
        required=True,
        help='Ground truth JSON file'
    )
    parser.add_argument(
        '--output',
        required=True,
        help='Output verification report'
    )

    args = parser.parse_args()

    # Load files
    print("🔍 Loading GLM output and ground truth...")
    glm_output = load_glm_output(args.glm_output)
    ground_truth = load_ground_truth(args.ground_truth)

    # Extract and verify class hierarchy
    print("🔍 Extracting class hierarchy claims...")
    hierarchy_claims = extract_class_hierarchy_from_glm(glm_output)

    print(f"🔍 Verifying {len(hierarchy_claims)} class hierarchy claims...")
    hierarchy_results = verify_class_hierarchy_claims(hierarchy_claims, ground_truth)

    # Extract and verify formulas
    print("🔍 Extracting formula claims...")
    formula_claims = extract_formula_claims(glm_output)

    print(f"🔍 Verifying {len(formula_claims)} formula claims...")
    formula_results = verify_formula_claims(formula_claims, ground_truth)

    # Generate report
    print(f"📝 Generating report: {args.output}")
    success = generate_report(hierarchy_results, formula_results, args.output)

    if success:
        print("✅ GLM output verification PASSED")
        return 0
    else:
        print("❌ GLM output verification FAILED")
        return 1


if __name__ == '__main__':
    sys.exit(main())
