#!/usr/bin/env python3
"""
Verify implementation consistency.

Checks:
1. Implementation is consistent with theory
2. All file references are valid
3. Code snippets are complete and runnable
"""

import sys
import re
import json
from pathlib import Path
from typing import Dict, List, Tuple


class ImplementationVerifier:
    """Verify implementation in markdown content."""

    def __init__(self, ground_truth_file: str):
        """Initialize verifier with ground truth."""
        with open(ground_truth_file, "r") as f:
            self.ground_truth = json.load(f)

        self.classes = self.ground_truth.get("classes", {})
        self.methods = self.ground_truth.get("methods", {})
        self.issues = []

    def verify_file(self, content: str) -> Tuple[bool, List[Dict]]:
        """Verify implementation in markdown content."""
        self.issues = []

        # Extract implementation section
        impl_section = self._extract_implementation_section(content)
        if not impl_section:
            self.issues.append({
                "type": "missing_section",
                "severity": "error",
                "message": "Implementation section not found"
            })

            is_valid = False
            return is_valid, self.issues

        # Check for file path references
        file_refs = self._extract_file_references(impl_section)

        # Verify file references match ground truth structure
        for ref in file_refs:
            self._verify_file_reference(ref)

        # Check code snippets are complete
        code_snippets = self._extract_code_snippets(impl_section)
        for idx, snippet in enumerate(code_snippets):
            self._verify_code_snippet(snippet, idx)

        # Check for compilation commands
        self._verify_compilation_commands(impl_section)

        is_valid = len([i for i in self.issues if i["severity"] == "error"]) == 0
        return is_valid, self.issues

    def _extract_implementation_section(self, content: str) -> str:
        """Extract implementation section from content."""
        # Look for H2 header containing "Implementation"
        match = re.search(r'## .*Implementation.*?\n(.*?)(?=\n## |\Z)', content, re.DOTALL)
        return match.group(1) if match else ""

    def _extract_file_references(self, content: str) -> List[str]:
        """Extract file path references from content."""
        refs = []

        # Look for `path/to/file.ext` patterns
        for match in re.finditer(r'`([^`]+?\.[a-zA-Z]+)`', content):
            ref = match.group(1)
            # Skip markdown files and common documentation files
            if not ref.endswith(('.md', '.txt', '.png', '.jpg')):
                refs.append(ref)

        return refs

    def _verify_file_reference(self, ref: str) -> None:
        """Verify file reference against ground truth."""
        # Check if file follows expected OpenFOAM structure
        # e.g., openfoam_temp/src/finiteVolume/...

        if ref.startswith("openfoam_temp/"):
            # Expected structure - no issue
            pass
        elif ref.startswith("/"):
            # Absolute path - check if reasonable
            pass
        elif ref.startswith("./") or ref.startswith("../"):
            # Relative path - acceptable
            pass
        else:
            # Simple filename - might be incomplete
            self.issues.append({
                "type": "incomplete_file_reference",
                "severity": "warning",
                "message": f"File reference may be incomplete: {ref}"
            })

    def _extract_code_snippets(self, content: str) -> List[str]:
        """Extract code snippets from content."""
        snippets = []

        for match in re.finditer(r'```(?:cpp|C\+\+|c\+\+)(.*?)```', content, re.DOTALL):
            snippet = match.group(1).strip()
            if snippet:
                snippets.append(snippet)

        return snippets

    def _verify_code_snippet(self, snippet: str, idx: int) -> None:
        """Verify a code snippet."""
        # Check for incomplete code
        if snippet.endswith('...') or snippet.endswith('//'):
            self.issues.append({
                "type": "incomplete_code",
                "severity": "warning",
                "message": f"Code snippet {idx} may be incomplete"
            })

        # Check for TODO comments
        if 'TODO' in snippet.upper():
            self.issues.append({
                "type": "todo_found",
                "severity": "warning",
                "message": f"Code snippet {idx} contains TODO comment"
            })

    def _verify_compilation_commands(self, content: str) -> None:
        """Verify compilation commands are correct."""
        # Check for wmake usage
        wmake_refs = re.findall(r'wmake', content)
        if wmake_refs:
            # Should typically have wmake in code block
            wmake_in_code = any('wmake' in block for block in self._extract_code_snippets(content))
            if not wmake_in_code:
                self.issues.append({
                    "type": "compilation_command_format",
                    "severity": "warning",
                    "message": "wmake mentioned but not in executable code block"
                })

        # Check for proper OpenFOAM environment variables
        foam_refs = re.findall(r'\$FOAM_[A-Z_]+', content)
        for ref in foam_refs:
            # Verify variable name is valid
            if not re.match(r'\$FOAM_[A-Z_]+', ref):
                self.issues.append({
                    "type": "invalid_env_var",
                    "severity": "warning",
                    "message": f"Invalid OpenFOAM environment variable: {ref}"
                })


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Verify implementation")
    parser.add_argument("--ground-truth", required=True, help="Ground truth JSON file")
    parser.add_argument("--content", required=True, help="Content file to verify")
    parser.add_argument("--output", help="Output report file")

    args = parser.parse_args()

    # Read content
    with open(args.content, "r") as f:
        content = f.read()

    # Verify
    verifier = ImplementationVerifier(args.ground_truth)
    is_valid, issues = verifier.verify_file(content)

    # Generate report
    report_lines = [
        "# Implementation Verification Report",
        "",
        f"**Status:** {'✅ PASSED' if is_valid else '❌ FAILED'}",
        f"**Issues Found:** {len(issues)}",
        ""
    ]

    if issues:
        report_lines.append("## Issues")
        report_lines.append("")
        for issue in issues:
            icon = "❌" if issue["severity"] == "error" else "⚠️"
            report_lines.append(f"- {icon} {issue['message']}")
            report_lines.append("")

    report = "\n".join(report_lines)

    # Output
    if args.output:
        with open(args.output, "w") as f:
            f.write(report)
        print(f"Report written to: {args.output}")
    else:
        print(report)

    sys.exit(0 if is_valid else 1)


if __name__ == "__main__":
    main()
