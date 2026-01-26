#!/usr/bin/env python3
"""
Generate daily learning content with full workflow logging.

This script runs the complete Source-First workflow for generating
daily CFD learning content with proper phase-by-phase logging.

Usage:
    python generate_day.py --day 03 --topic "Spatial Discretization" --source-path openfoam_temp/src/...
"""

import argparse
import json
import os
import sys
from pathlib import Path
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.workflow_logger import get_logger

def run_workflow(day_num, topic, source_path, output_file):
    """
    Run the complete Source-First workflow for a single day.
    """
    # Initialize logger
    logger = get_logger("/tmp/workflow_debug.log")

    logger.log_phase(1, f"Day {day_num}: {topic}", f"Output: {output_file}")

    # ========================================================================
    # GATE 1: Ground Truth Extraction
    # ========================================================================
    logger.log_phase(2, "Gate 1: Ground Truth Extraction", f"Source: {source_path}")

    from scripts.extract_facts import extract_class_hierarchy

    print(f"\n{'='*70}")
    print(f"🚀 Day {day_num}: {topic}")
    print(f"{'='*70}")

    print("\n📍 GATE 1: Ground Truth Extraction")
    print("-" * 70)

    hierarchy = extract_class_hierarchy(source_path)
    logger.log_task_complete("Ground Truth Extraction", f"Extracted {len(hierarchy)} classes")

    # Save ground truth
    gt_file = f"/tmp/verified_facts_day{day_num}.json"
    with open(gt_file, 'w') as f:
        json.dump({
            'day': day_num,
            'topic': topic,
            'hierarchy': hierarchy,
            'extraction_date': datetime.now().isoformat()
        }, f, indent=2)

    logger.log_file_operation("write", gt_file, f"{len(hierarchy)} classes")

    # ========================================================================
    # GATE 2: Skeleton Verification
    # ========================================================================
    logger.log_phase(3, "Gate 2: Skeleton Verification")

    print("\n📍 GATE 2: Skeleton Verification")
    print("-" * 70)

    skeleton_file = f"daily_learning/skeletons/day{day_num}_skeleton_verified.json"

    if os.path.exists(skeleton_file):
        print(f"✅ Verified skeleton found: {skeleton_file}")
        with open(skeleton_file, 'r') as f:
            skeleton = json.load(f)
        logger.log_task_complete("Skeleton Verification", "Verified skeleton exists")
    else:
        print(f"⚠️ No verified skeleton found at {skeleton_file}")
        logger.log_task_complete("Skeleton Verification", "No skeleton - will generate from ground truth")
        skeleton = None

    # ========================================================================
    # GATE 3: Content Generation
    # ========================================================================
    logger.log_phase(4, "Gate 3: Content Generation", "English-only")

    print("\n📍 GATE 3: Content Generation")
    print("-" * 70)

    # Note: Content generation is done outside this script (via AI)
    # This just marks the phase for logging
    logger.log_task_start("Content Generation (External)")

    print("\n📝 Content generation will be done via AI agent...")
    print("   Use the verified skeleton and ground truth to generate content.")

    # ========================================================================
    # GATE 4: Syntax QC
    # ========================================================================
    # This will be called after content is generated
    print("\n📍 GATE 4: Syntax QC (Pending)")
    print("   Run: python .claude/scripts/qc_syntax_check.py --file=<output_file>")

    # ========================================================================
    # Summary
    # ========================================================================
    logger.log_phase(5, "Workflow Summary")

    print("\n" + "="*70)
    print("📋 WORKFLOW SUMMARY")
    print("="*70)
    print(f"Day: {day_num}")
    print(f"Topic: {topic}")
    print(f"Ground truth: {len(hierarchy)} classes extracted")
    print(f"Skeleton: {'Verified' if skeleton else 'Not found'}")
    print(f"Output file: {output_file}")
    print(f"Log file: /tmp/workflow_debug.log")
    print("="*70)

    return {
        'day': day_num,
        'ground_truth_classes': len(hierarchy),
        'skeleton_verified': skeleton is not None,
        'output_file': output_file
    }


def main():
    parser = argparse.ArgumentParser(
        description='Generate daily learning content with workflow logging'
    )
    parser.add_argument('--day', required=True, help='Day number (e.g., 03)')
    parser.add_argument('--topic', required=True, help='Topic name')
    parser.add_argument('--source-path', required=True, help='OpenFOAM source path')
    parser.add_argument('--output', required=True, help='Output file path')
    args = parser.parse_args()

    result = run_workflow(
        args.day,
        args.topic,
        args.source_path,
        args.output
    )

    # Log final summary
    logger = get_logger("/tmp/workflow_debug.log")
    logger.log_session_summary(0, result)

    return 0


if __name__ == '__main__':
    sys.exit(main())
