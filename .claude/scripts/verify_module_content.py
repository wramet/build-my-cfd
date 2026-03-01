#!/usr/bin/env python3
"""
MODULE Content Verification Script

Verifies MODULE_05/09 content against OpenFOAM source code.
Marks verified sections with ⭐ and generates verification reports.

Usage:
    python3 verify_module_content.py MODULE_05
    python3 verify_module_content.py MODULE_09
    python3 verify_module_content.py MODULE_05 --verbose
"""

import argparse
import json
import re
import sys
from pathlib import Path
from datetime import datetime

# Paths
PROJECT_ROOT = Path(__file__).parent.parent.parent
OPENFOAM_SRC = PROJECT_ROOT / "openfoam_temp/src"
MODULES_DIR = PROJECT_ROOT

# Verification results
VERIFIED = "⭐"
NEEDS_VERIFY = "⚠️"
ERROR = "❌"


class ModuleVerifier:
    """Verifies MODULE content against OpenFOAM source code"""

    def __init__(self, module_name, verbose=False):
        self.module_name = module_name
        self.module_path = PROJECT_ROOT / module_name
        self.verbose = verbose
        self.issues = []
        self.verifications = []

    def verify_module(self):
        """Main verification workflow"""
        print(f"\n{'='*60}")
        print(f"Verifying {self.module_name}")
        print(f"{'='*60}\n")

        if not self.module_path.exists():
            print(f"{ERROR} Module path not found: {self.module_path}")
            return False

        # Find all markdown files in module
        md_files = list(self.module_path.glob("**/*.md"))

        if not md_files:
            print(f"{NEEDS_VERIFY} No markdown files found in {self.module_name}")
            return False

        print(f"Found {len(md_files)} files to verify\n")

        # Verify each file
        for md_file in md_files:
            self.verify_file(md_file)

        # Generate report
        self.generate_report()

        return len(self.issues) == 0

    def verify_file(self, md_file):
        """Verify a single markdown file"""
        print(f"Verifying: {md_file.relative_to(PROJECT_ROOT)}")

        with open(md_file, 'r') as f:
            content = f.read()

        # Extract code snippets and class references
        code_blocks = self.extract_code_blocks(content)
        class_refs = self.extract_class_references(content)
        file_refs = self.extract_file_references(content)

        file_issues = []
        file_verifications = []

        # Verify code blocks compile (basic check)
        for i, block in enumerate(code_blocks):
            if block['lang'] == 'cpp':
                if self.verify_cpp_syntax(block['code']):
                    file_verifications.append(f"Code block {i+1}: Syntax OK")
                else:
                    file_issues.append(f"Code block {i+1}: Syntax error suspected")

        # Verify class references exist in OpenFOAM source
        for class_name in class_refs:
            if self.class_exists_in_source(class_name):
                file_verifications.append(f"Class {class_name}: Found in source")
            else:
                file_issues.append(f"Class {class_name}: Not found in source")

        # Verify file references exist
        for file_ref in file_refs:
            if self.file_exists_in_source(file_ref):
                file_verifications.append(f"File {file_ref}: Found")
            else:
                file_issues.append(f"File {file_ref}: Not found")

        # Store results
        if file_issues:
            self.issues.extend([
                {
                    "file": str(md_file.relative_to(PROJECT_ROOT)),
                    "issue": issue
                }
                for issue in file_issues
            ])

        self.verifications.append({
            "file": str(md_file.relative_to(PROJECT_ROOT)),
            "verifications": file_verifications,
            "issues": file_issues,
            "status": "verified" if not file_issues else "needs_review"
        })

        # Print summary for this file
        if file_verifications:
            print(f"  {VERIFIED} {len(file_verifications)} verifications")
        if file_issues:
            print(f"  {NEEDS_VERIFY} {len(file_issues)} issues")

        if self.verbose:
            for v in file_verifications:
                print(f"    ✓ {v}")
            for i in file_issues:
                print(f"    ⚠ {i}")

        print()

    def extract_code_blocks(self, content):
        """Extract code blocks from markdown"""
        pattern = r'```(\w+)?\n(.*?)```'
        matches = re.findall(pattern, content, re.DOTALL)

        blocks = []
        for lang, code in matches:
            blocks.append({
                'lang': lang or 'text',
                'code': code
            })
        return blocks

    def extract_class_references(self, content):
        """Extract class references from content"""
        # Look for code references like `fvMesh`, `volScalarField`, etc.
        pattern = r'\b([A-Z][a-zA-Z0-9_]*)\b'
        matches = set(re.findall(pattern, content))

        # Filter out common non-class words
        skip_words = {'C++', 'OpenFOAM', 'The', 'This', 'That', 'What', 'Why', 'How', 'See'}
        return [m for m in matches if m not in skip_words and len(m) > 2]

    def extract_file_references(self, content):
        """Extract file path references from content"""
        # Look for patterns like "file.H", "path/to/file.C"
        pattern = r'[\w/]+\.(H|C|h|cpp|cc)'
        matches = re.findall(pattern, content)
        return list(set(matches))

    def verify_cpp_syntax(self, code):
        """Basic C++ syntax check"""
        # Check for balanced braces
        if code.count('{') != code.count('}'):
            return False

        # Check for balanced parentheses
        if code.count('(') != code.count(')'):
            return False

        return True

    def class_exists_in_source(self, class_name):
        """Check if class exists in OpenFOAM source"""
        if not OPENFOAM_SRC.exists():
            return None  # Source not available

        # Search for class definition
        # This is a simplified check - real verification would parse the files
        for header_file in OPENFOAM_SRC.rglob("*.H"):
            try:
                content = header_file.read_text()
                if f"class {class_name}" in content or f"struct {class_name}" in content:
                    return True
            except:
                continue

        return False

    def file_exists_in_source(self, file_ref):
        """Check if file exists in OpenFOAM source"""
        if not OPENFOAM_SRC.exists():
            return None  # Source not available

        # Search for the file
        found = list(OPENFOAM_SRC.rglob(file_ref))
        return len(found) > 0

    def generate_report(self):
        """Generate verification report"""
        report_file = PROJECT_ROOT / f"{self.module_name}_VERIFICATION_REPORT.md"

        with open(report_file, 'w') as f:
            f.write(f"# {self.module_name} Verification Report\n\n")
            f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write(f"**Status:** {'PASSED' if not self.issues else 'NEEDS REVIEW'}\n\n")
            f.write("---\n\n")

            # Summary
            f.write("## Summary\n\n")
            f.write(f"- Files verified: {len(self.verifications)}\n")
            f.write(f"- Issues found: {len(self.issues)}\n")
            f.write(f"- Verification rate: {self.verification_rate():.1f}%\n\n")

            # Detailed results
            f.write("## Detailed Results\n\n")

            for v in self.verifications:
                f.write(f"### {v['file']}\n\n")
                f.write(f"**Status:** {v['status'].upper()}\n\n")

                if v['verifications']:
                    f.write("**Verified:**\n")
                    for item in v['verifications']:
                        f.write(f"- {VERIFIED} {item}\n")
                    f.write("\n")

                if v['issues']:
                    f.write("**Issues:**\n")
                    for item in v['issues']:
                        f.write(f"- {NEEDS_VERIFY} {item}\n")
                    f.write("\n")

            # Issues list
            if self.issues:
                f.write("## All Issues\n\n")
                for issue in self.issues:
                    f.write(f"- **{issue['file']}**: {issue['issue']}\n")

        print(f"\n{'='*60}")
        print(f"Report saved: {report_file}")
        print(f"{'='*60}\n")

    def verification_rate(self):
        """Calculate verification rate"""
        total = len(self.verifications)
        verified = sum(1 for v in self.verifications if v['status'] == 'verified')
        return (verified / total * 100) if total > 0 else 0


def main():
    parser = argparse.ArgumentParser(
        description='Verify MODULE content against OpenFOAM source code'
    )
    parser.add_argument('module', help='Module name (e.g., MODULE_05, MODULE_09)')
    parser.add_argument('--verbose', '-v', action='store_true',
                        help='Verbose output')

    args = parser.parse_args()

    verifier = ModuleVerifier(args.module, args.verbose)
    success = verifier.verify_module()

    if not success:
        print(f"\n{NEEDS_VERIFY} Verification completed with issues")
        print("Review the verification report for details")
        sys.exit(1)
    else:
        print(f"\n{VERIFIED} All verifications passed!")
        sys.exit(0)


if __name__ == "__main__":
    main()
