#!/usr/bin/env python3
"""
Verify final content against ground truth and skeleton verification.

This script checks that the final expanded content maintains
technical accuracy and doesn't introduce hallucinations.

Usage:
    python verify_content.py --content draft_english.md \
                         --ground-truth verified_facts.json \
                         --skeleton-verification skeleton_verification.md \
                         --output content_verification.md
"""

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Dict, List, Any

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.workflow_logger import get_logger, log_phase, log_verification



def load_files(content_file: str, gt_file: str, sv_file: str) -> tuple:
    """Load all input files."""
    with open(content_file) as f:
        content = f.read()

    with open(gt_file) as f:
        ground_truth = json.load(f)

    with open(sv_file) as f:
        skeleton_verification = f.read()

    return content, ground_truth, skeleton_verification


def verify_class_hierarchy_in_content(
    content: str,
    ground_truth: Dict
) -> List[Dict]:
    """Verify class hierarchy mentions in content."""
    results = []
    gt_hierarchy = ground_truth.get('class_hierarchy', {})

    # Look for Mermaid diagrams or class declarations
    # Pattern 1: Mermaid: Child --> Parent
    mermaid_matches = re.findall(r'(\w+)\s*-->\s*(\w+)', content)

    for child, parent in mermaid_matches:
        # Filter out common non-class terms
        if child.lower() in ['return', 'class', 'style', 'link']:
            continue

        if child in gt_hierarchy:
            actual_parent = gt_hierarchy[child]['base_class']
            status = '✅' if parent == actual_parent else '❌ MISMATCH'

            results.append({
                'type': 'class_hierarchy',
                'location': 'Mermaid diagram',
                'child': child,
                'claimed_parent': parent,
                'actual_parent': actual_parent,
                'status': status
            })

    # Pattern 2: Text: "ClassName : public BaseClass"
    text_matches = re.findall(r'(\w+)\s*:\s*public\s+(\w+)', content)

    for child, parent in text_matches:
        if child.lower() in ['return', 'template', 'typedef']:
            continue

        if child in gt_hierarchy:
            actual_parent = gt_hierarchy[child]['base_class']
            status = '✅' if parent == actual_parent else '❌ MISMATCH'

            results.append({
                'type': 'class_hierarchy',
                'location': 'Text/code block',
                'child': child,
                'claimed_parent': parent,
                'actual_parent': actual_parent,
                'status': status
            })

    return results


def verify_formulas_in_content(
    content: str,
    ground_truth: Dict
) -> List[Dict]:
    """Verify mathematical formulas in content."""
    results = []
    gt_formulas = ground_truth.get('formulas', {})

    # Look for formula blocks in LaTeX
    # Pattern: $formula$ or $$formula$$
    latex_matches = re.findall(r'\$\$([^$]+)\$\$', content)

    for formula in latex_matches:
        # Clean up LaTeX for comparison
        formula_clean = formula.replace('\\frac', '').replace('{', '/(').replace('}', ')/')

        # Try to identify which limiter this might be
        # Check if formula contains known patterns
        for gt_name, gt_info in gt_formulas.items():
            gt_formula = gt_info['formula'].replace('mag(r)', '|r|')

            # Simple substring check (could be improved)
            if normalize_formula(formula_clean) == normalize_formula(gt_formula):
                results.append({
                    'type': 'formula',
                    'formula_in_content': formula,
                    'ground_truth_formula': gt_formula,
                    'status': '✅ VERIFIED'
                })
                break

    return results


def check_custom_vs_standard_labeling(content: str) -> List[Dict]:
    """Check that OpenFOAM standard vs custom code is clearly labeled."""
    results = []

    # Check for keywords indicating custom code
    has_custom = bool(re.search(
        r'(project.?specific|custom.?implementation| SpatialDiscretizer | TVDLimiter)',
        content,
        re.IGNORECASE
    ))

    # Check for OpenFOAM standard code sections
    has_openfoam = bool(re.search(
        r'OpenFOAM( standard)?|openfoam/src/',
        content,
        re.IGNORECASE
    ))

    # Check if there's code without clear labeling
    code_blocks = re.findall(r'```(?:cpp)?\n([\s\S]*?)```', content, re.MULTILINE)

    for i, code in enumerate(code_blocks):
        # Check if code contains OpenFOAM-like patterns but no label
        if 'surfaceInterpolation' in code or 'volField' in code:
            # Look for labels in surrounding text
            # This is simplified - could be improved with context analysis
            results.append({
                'type': 'labeling',
                'code_block': i + 1,
                'has_custom_label': has_custom,
                'has_openfoam_label': has_openfoam,
                'status': '⚠️  CHECK LABELING'
            })

    return results


def normalize_formula(formula: str) -> str:
    """Normalize formula for comparison."""
    normalized = formula.lower().replace(' ', '')
    normalized = normalized.replace('\\frac', '')
    normalized = normalized.replace('\\left(', '')
    normalized = normalized.replace('\\right(', '')
    return normalized


def generate_report(
    hierarchy_results: List[Dict],
    formula_results: List[Dict],
    labeling_results: List[Dict],
    output_file: str
) -> bool:
    """Generate content verification report."""
    all_results = hierarchy_results + formula_results + labeling_results
    has_errors = any('❌' in r.get('status', '') for r in all_results)

    with open(output_file, 'w') as f:
        f.write("# 🔒 Content Verification Report\n\n")

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
            f.write("Content contains technical errors that MUST be fixed:\n\n")
        else:
            f.write("## ✅ VERIFICATION PASSED\n\n")
            f.write("Content is technically accurate. Proceeding to QC...\n\n")

        # Detailed results
        if hierarchy_results:
            f.write("### Class Hierarchy Verification\n\n")
            for r in hierarchy_results:
                f.write(f"#### {r['child']} → {r['claimed_parent']}\n")
                f.write(f"- **Actual:** {r['actual_parent']}\n")
                f.write(f"- **Status:** {r['status']}\n")
                f.write(f"- **Location:** {r['location']}\n\n")

        if formula_results:
            f.write("### Formula Verification\n\n")
            for r in formula_results:
                f.write(f"- Formula: `{r['formula_in_content']}`\n")
                f.write(f"- **Ground Truth:** `{r['ground_truth_formula']}`\n")
                f.write(f"- **Status:** {r['status']}\n\n")

        if labeling_results:
            f.write("### Labeling Verification\n\n")
            for r in labeling_results:
                f.write(f"- Code block #{r['code_block']}: ")
                if r['has_custom_label']:
                    f.write("Has custom label ✓\n")
                else:
                    f.write("⚠️ May need clearer custom/standard labeling\n")
                f.write("\n")

        if has_errors:
            f.write("\n## 🔧 Required Actions\n\n")
            f.write("1. **Review technical errors** above\n")
            f.write("2. **Fix errors in draft content**\n")
            f.write("3. **Re-run verification** until all pass\n")
            f.write("4. **Only then proceed to QC translation**\n")

    return not has_errors


def main():
    parser = argparse.ArgumentParser(
        description='Verify final content against ground truth'
    )
    parser.add_argument('--content', required=True)
    parser.add_argument('--ground-truth', required=True)
    parser.add_argument('--skeleton-verification', required=True)
    parser.add_argument('--output', required=True)

    args = parser.parse_args()

    # Initialize logger
    logger = get_logger()
    log_phase(6, "Gate 6: Content Verification", f"Content: {args.content}")

    # Load files
    print("🔍 Loading files...")
    logger.logger.info(f"Loading content: {args.content}")
    logger.logger.info(f"Loading ground truth: {args.ground_truth}")
    
    content, ground_truth, skeleton_verification = load_files(
        args.content,
        args.ground_truth,
        args.skeleton_verification
    )

    # Verify
    print("🔍 Verifying class hierarchy in content...")
    hierarchy_results = verify_class_hierarchy_in_content(content, ground_truth)

    print("🔍 Verifying formulas in content...")
    formula_results = verify_formulas_in_content(content, ground_truth)

    print("🔍 Checking custom vs standard labeling...")
    labeling_results = check_custom_vs_standard_labeling(content)
    
    # Log detailed results
    all_results = hierarchy_results + formula_results + labeling_results
    verified_count = sum(1 for r in all_results if '✅' in r.get('status', ''))
    issues_count = sum(1 for r in all_results if '❌' in r.get('status', ''))
    log_verification(args.content, {'verified': verified_count}, issues_count)

    # Generate report
    print(f"📝 Generating report: {args.output}")
    success = generate_report(
        hierarchy_results,
        formula_results,
        labeling_results,
        args.output
    )

    if success:
        print("✅ Content verification PASSED")
        logger.logger.info("✅ Gate 6 PASSED: Content verification successful")
        return 0
    else:
        print("❌ Content verification FAILED")
        logger.logger.info(f"❌ Gate 6 FAILED: {issues_count} issues found. See {args.output}")
        return 1


if __name__ == '__main__':
    sys.exit(main())
