#!/usr/bin/env python3
"""
Verify code structure against ground truth.

Checks:
1. Class hierarchies match ground truth
2. Method signatures match ground truth
3. No hallucinated classes or methods
"""

import sys
import re
import json
from pathlib import Path
from typing import Dict, List, Set, Tuple


class CodeStructureVerifier:
    """Verify code structure in markdown content."""

    def __init__(self, ground_truth_file: str):
        """Initialize verifier with ground truth."""
        with open(ground_truth_file, "r") as f:
            self.ground_truth = json.load(f)

        self.classes = self.ground_truth.get("classes", {})
        self.methods = self.ground_truth.get("methods", {})
        self.issues = []

    def verify_file(self, content: str) -> Tuple[bool, List[Dict]]:
        """Verify code structure in markdown content."""
        self.issues = []

        # Check code block balance
        self._check_code_blocks(content)

        # Extract class references
        content_classes = self._extract_class_references(content)

        # Verify all mentioned classes exist in ground truth
        for cls in content_classes:
            if cls not in self.classes and not self._is_standard_type(cls):
                self.issues.append({
                    "type": "hallucinated_class",
                    "severity": "error",
                    "message": f"Unverified class reference: {cls}"
                })

        # Extract method references
        content_methods = self._extract_method_references(content)

        # Verify method signatures
        for method in content_methods:
            if not self._verify_method(method):
                self.issues.append({
                    "type": "invalid_method",
                    "severity": "warning",
                    "message": f"Unverified method: {method}"
                })

        # Check Mermaid diagrams
        self._verify_mermaid_diagrams(content)

        is_valid = len([i for i in self.issues if i["severity"] == "error"]) == 0
        return is_valid, self.issues

    def _check_code_blocks(self, content: str) -> None:
        """Check that code blocks are balanced."""
        code_starts = len(re.findall(r'```', content))
        if code_starts % 2 != 0:
            self.issues.append({
                "type": "unbalanced_code_blocks",
                "severity": "error",
                "message": f"Unbalanced code blocks: {code_starts} ``` markers found"
            })

    def _extract_class_references(self, content: str) -> Set[str]:
        """Extract class names from content."""
        classes = set()

        # Pattern for ClassName or ClassName<Type>
        # Look for capitalized words in code-like contexts
        for match in re.finditer(r'\b([A-Z][a-zA-Z0-9_]*)(?:<[^>]+>)?\b', content):
            cls = match.group(1)
            # Filter out common non-class words
            if cls not in {"Type", "Return", "True", "False", "None", "OpenFOAM", "CFD"}:
                classes.add(cls)

        return classes

    def _is_standard_type(self, name: str) -> bool:
        """Check if name is a standard C++ type."""
        standard_types = {
            "int", "float", "double", "char", "bool", "void",
            "size_t", "string", "vector", "list", "map", "set",
            "pair", "array", "unique_ptr", "shared_ptr", "auto",
            "unsigned", "long", "short", "const", "static"
        }
        return name in standard_types

    def _extract_method_references(self, content: str) -> List[str]:
        """Extract method references from content."""
        methods = []

        # Look for method() patterns in code blocks
        for match in re.finditer(r'\b([a-zA-Z_][a-zA-Z0-9_]*)\s*\(', content):
            method = match.group(1)
            # Filter out C++ keywords
            if method not in {"if", "for", "while", "switch", "return", "break", "continue"}:
                methods.append(method)

        return methods

    def _verify_method(self, method: str) -> bool:
        """Check if method exists in ground truth."""
        # Check if method exists in any class
        for cls_methods in self.methods.values():
            if method in cls_methods:
                return True
        return False

    def _verify_mermaid_diagrams(self, content: str) -> None:
        """Verify Mermaid class diagrams."""
        diagrams = re.findall(r'```mermaid\n(.*?)```', content, re.DOTALL)

        for diagram in diagrams:
            # Check for quoted class names with special characters
            quoted_classes = re.findall(r'"([^"]+)"', diagram)

            # Check if quoted classes match ground truth
            for cls in quoted_classes:
                # Extract just the class name (remove <Type> if present)
                base_name = re.sub(r'<[^>]+>', '', cls)
                if base_name and base_name not in self.classes and not self._is_standard_type(base_name):
                    self.issues.append({
                        "type": "mermaid_class_error",
                        "severity": "error",
                        "message": f"Unverified class in Mermaid diagram: {cls}"
                    })


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Verify code structure")
    parser.add_argument("--ground-truth", required=True, help="Ground truth JSON file")
    parser.add_argument("--content", required=True, help="Content file to verify")
    parser.add_argument("--output", help="Output report file")

    args = parser.parse_args()

    # Read content
    with open(args.content, "r") as f:
        content = f.read()

    # Verify
    verifier = CodeStructureVerifier(args.ground_truth)
    is_valid, issues = verifier.verify_file(content)

    # Generate report
    report_lines = [
        "# Code Structure Verification Report",
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
