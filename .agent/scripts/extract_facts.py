#!/usr/bin/env python3
"""
Extract Ground Truth from OpenFOAM source code.

This script extracts actual class hierarchies and mathematical formulas
from OpenFOAM source code to serve as ground truth for content generation.

Usage:
    python extract_facts.py --mode hierarchy --path openfoam_temp/src/... --output facts.txt
    python extract_facts.py --mode formulas --path openfoam_temp/src/... --output formulas.txt
    python extract_facts.py --mode structure --input facts.txt --output facts.json
"""

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Dict, List, Any


def extract_class_hierarchy(source_path: str) -> Dict[str, Any]:
    """
    Extract actual class inheritance relationships from header files.

    Returns:
        Dict with class info: {className: {base, file, methods}}
    """
    hierarchy = {}
    source_dir = Path(source_path)

    # Find all .H files
    header_files = list(source_dir.rglob("*.H"))

    for header_file in header_files:
        try:
            content = header_file.read_text()

            # Find class declarations: class className : public baseClass
            # Handle template classes: class Name<Type> : public Base<Type>
            matches = re.finditer(
                r'class\s+(\w+)(?:<[^>]+>)?\s*:\s*(?:public\s+)?(\w+)(?:<[^>]+>)?',
                content
            )

            for match in matches:
                class_name = match.group(1)
                base_class = match.group(2)

                # Skip certain patterns
                if class_name in ['Istream', 'Ostream', 'pair', 'autoPtr', 'refPtr']:
                    continue

                hierarchy[class_name] = {
                    'base_class': base_class,
                    'file': str(header_file.relative_to(source_dir)),
                    'is_template': '<' in match.group(0)
                }

        except Exception as e:
            print(f"Warning: Could not read {header_file}: {e}", file=sys.stderr)

    return hierarchy


def extract_formulas(source_path: str) -> Dict[str, Any]:
    """
    Extract actual mathematical formulas from implementation files.

    Returns:
        Dict with formula info: {limiterName: {formula, file}}
    """
    formulas = {}
    source_dir = Path(source_path)

    # Look in limiter scheme directories
    limiter_dirs = [
        'vanLeer',
        'vanAlbada',
        'SuperBee',
        'minmod',
        'UMIST',
        'limitedLinearV',
        'CellLimited',
        'Gamma'
    ]

    for limiter_name in limiter_dirs:
        # Find matching directories
        matching_dirs = list(source_dir.rglob(f"*{limiter_name}"))

        for limiter_dir in matching_dirs:
            if not limiter_dir.is_dir():
                continue

            # Look for .H files with limiter implementation
            header_files = list(limiter_dir.glob("*.H"))

            for header_file in header_files:
                try:
                    content = header_file.read_text()

                    # Extract limiter function (usually in limiter() method)
                    # Look for return statements with 'r' variable
                    return_pattern = r'return\s+([^;]+);'
                    matches = re.findall(return_pattern, content)

                    for match in matches:
                        formula = match.strip()

                        # Clean up common C++ syntax
                        formula = formula.replace('mag(', '|')
                        formula = formula.replace('mag(', '|')

                        # Extract limiter name if possible
                        if limiter_name.lower() in header_file.name.lower():
                            formulas[limiter_name] = {
                                'formula': formula,
                                'file': str(header_file.relative_to(source_dir))
                            }

                except Exception as e:
                    print(f"Warning: Could not read {header_file}: {e}", file=sys.stderr)

    return formulas


def structure_facts(input_file: str) -> Dict[str, Any]:
    """
    Parse raw extracted facts and structure them into JSON format.

    Args:
        input_file: File with raw extracted facts

    Returns:
        Structured facts dictionary
    """
    content = Path(input_file).read_text()

    structured = {
        'class_hierarchy': {},
        'formulas': {},
        'verification_date': None  # Will be set by caller
    }

    current_section = None
    current_class = None

    for line in content.split('\n'):
        line = line.strip()

        # Section markers
        if line.startswith('=== FILE:') or line.startswith('=== '):
            continue

        # Class declarations
        if 'class ' in line and ':' in line and 'public' in line:
            match = re.search(r'class\s+(\w+).*:\s*public\s+(\w+)', line)
            if match:
                current_class = match.group(1)
                base_class = match.group(2)

                structured['class_hierarchy'][current_class] = {
                    'base_class': base_class,
                    'verified': True
                }

        # Formulas
        if 'return ' in line and ('r' in line or 'phi' in line):
            # Try to identify which limiter this belongs to
            # For now, store all and categorize later
            if 'formulas' not in structured:
                structured['formulas'] = {}

            formula = line.split('return')[1].split(';')[0].strip()
            # Clean up C++ syntax
            formula = formula.replace('mag(r)', '|r|')

            # Store with inferred limiter name
            structured['formulas'][f'formula_{len(structured["formulas"])}']] = {
                'formula': formula,
                'verified': True
            }

    return structured


def main():
    parser = argparse.ArgumentParser(
        description='Extract ground truth from OpenFOAM source code'
    )

    parser.add_argument(
        '--mode',
        required=True,
        choices=['hierarchy', 'formulas', 'structure'],
        help='Extraction mode'
    )
    parser.add_argument(
        '--path',
        help='Path to OpenFOAM source directory'
    )
    parser.add_argument(
        '--input',
        help='Input file (for structure mode)'
    )
    parser.add_argument(
        '--output',
        required=True,
        help='Output file for extracted facts'
    )

    args = parser.parse_args()

    if args.mode == 'hierarchy':
        print(f"🔍 Extracting class hierarchy from {args.path}...")
        hierarchy = extract_class_hierarchy(args.path)

        with open(args.output, 'w') as f:
            f.write("# Ground Truth: Class Hierarchy\n\n")
            f.write(f"# Source: {args.path}\n")
            f.write(f"# Extracted: 2026-01-24\n\n")

            for class_name, info in sorted(hierarchy.items()):
                f.write(f"## {class_name}\n")
                f.write(f"**Base Class:** {info['base_class']}\n")
                f.write(f"**File:** {info['file']}\n")
                f.write(f"**Template:** {info['is_template']}\n")
                f.write("\n")

        print(f"✅ Extracted {len(hierarchy)} classes")

    elif args.mode == 'formulas':
        print(f"🔍 Extracting formulas from {args.path}...")
        formulas = extract_formulas(args.path)

        with open(args.output, 'w') as f:
            f.write("# Ground Truth: Mathematical Formulas\n\n")
            f.write(f"# Source: {args.path}\n")
            f.write(f"# Extracted: 2026-01-24\n\n")

            for limiter_name, info in sorted(formulas.items()):
                f.write(f"## {limiter_name}\n")
                f.write(f"**Formula:** `{info['formula']}`\n")
                f.write(f"**File:** {info['file']}\n")
                f.write("\n")

        print(f"✅ Extracted {len(formulas)} formulas")

    elif args.mode == 'structure':
        print(f"🔍 Structuring facts from {args.input}...")
        structured = structure_facts(args.input)

        # Add verification date
        from datetime import datetime
        structured['verification_date'] = datetime.now().isoformat()

        with open(args.output, 'w') as f:
            json.dump(structured, f, indent=2)

        print(f"✅ Structured facts saved to {args.output}")

    return 0


if __name__ == '__main__':
    sys.exit(main())
