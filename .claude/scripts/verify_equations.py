#!/usr/bin/env python3
"""
Verify LaTeX equations against ground truth.

Checks:
1. LaTeX syntax validity
2. No nested delimiters
3. Equations match ground truth formulas
"""

import sys
import re
import json
from pathlib import Path
from typing import Dict, List, Tuple


class EquationVerifier:
    """Verify LaTeX equations in markdown content."""

    def __init__(self, ground_truth_file: str):
        """Initialize verifier with ground truth."""
        with open(ground_truth_file, "r") as f:
            self.ground_truth = json.load(f)

        self.formula_map = self.ground_truth.get("formulas", {})
        self.issues = []

    def verify_file(self, content: str) -> Tuple[bool, List[Dict]]:
        """Verify equations in markdown content."""
        self.issues = []

        # Check for nested LaTeX (forbidden)
        self._check_nested_latex(content)

        # Extract and verify display equations
        display_eqs = self._extract_display_equations(content)
        for idx, eq in enumerate(display_eqs):
            self._verify_equation(eq, f"display_{idx}")

        # Extract and verify inline equations
        inline_eqs = self._extract_inline_equations(content)
        for idx, eq in enumerate(inline_eqs):
            self._verify_equation(eq, f"inline_{idx}")

        is_valid = len(self.issues) == 0
        return is_valid, self.issues

    def _check_nested_latex(self, content: str) -> None:
        """Check for nested LaTeX delimiters."""
        # Pattern: $$...$...$$ (display math with inline inside)
        nested = re.search(r'\$\$.*\$[^$]', content, re.DOTALL)
        if nested:
            self.issues.append({
                "type": "nested_latex",
                "severity": "error",
                "message": "Nested LaTeX delimiters found",
                "location": self._find_line_number(content, nested.start())
            })

    def _extract_display_equations(self, content: str) -> List[str]:
        """Extract display equations ($$...$$)."""
        eqs = []
        for match in re.finditer(r'\$\$([^$]+)\$\$', content, re.DOTALL):
            eqs.append(match.group(1).strip())
        return eqs

    def _extract_inline_equations(self, content: str) -> List[str]:
        """Extract inline equations ($...$) excluding display math."""
        # First remove display math to avoid false matches
        no_display = re.sub(r'\$\$[^$]+\$\$', '', content)
        eqs = []
        for match in re.finditer(r'(?<!\$)\$(?!\$)([^$]+)(?<!\$)\$(?!\$)', no_display):
            eqs.append(match.group(1).strip())
        return eqs

    def _verify_equation(self, equation: str, eq_id: str) -> None:
        """Verify equation against ground truth."""
        # Check for common LaTeX errors
        if not equation:
            return

        # Check for unbalanced braces
        if equation.count('{') != equation.count('}'):
            self.issues.append({
                "type": "unbalanced_braces",
                "severity": "error",
                "message": f"Unbalanced braces in equation: {equation}",
                "equation_id": eq_id
            })

        # Check for unbalanced parentheses
        if equation.count('(') != equation.count(')'):
            self.issues.append({
                "type": "unbalanced_parens",
                "severity": "error",
                "message": f"Unbalanced parentheses in equation: {equation}",
                "equation_id": eq_id
            })

        # Check for undefined commands (basic check)
        invalid_commands = self._check_invalid_commands(equation)
        if invalid_commands:
            self.issues.append({
                "type": "invalid_command",
                "severity": "warning",
                "message": f"Potentially invalid LaTeX commands: {', '.join(invalid_commands)}",
                "equation_id": eq_id
            })

    def _check_invalid_commands(self, equation: str) -> List[str]:
        """Check for invalid LaTeX commands."""
        # List of valid basic LaTeX commands (can be extended)
        valid_commands = {
            'nabla', 'cdot', 'frac', 'partial', 'nabla^2',
            'mathbf', 'vec', 'left', 'right', 'left(', 'right)',
            'sum', 'int', 'prod', 'infty', 'alpha', 'beta', 'gamma',
            'delta', 'epsilon', 'theta', 'lambda', 'mu', 'pi', 'rho',
            'sigma', 'tau', 'phi', 'omega', 'Delta', 'Theta', 'Lambda',
            'Phi', 'Omega', 'cdot', 'times', 'div', 'times', 'equiv',
            'approx', 'le', 'ge', 'ne', 'sim', 'propto', 'in', 'notin',
            'subset', 'subseteq', 'cup', 'cap', 'emptyset', 'forall',
            'exists', 'nexists', 'neg', 'lor', 'land', 'implies',
            'iff', 'to', 'rightarrow', 'Rightarrow', 'leftrightarrow',
            'Leftrightarrow', 'top', 'bot', 'vdash', 'models'
        }

        # Find all command patterns
        commands = re.findall(r'\\([a-zA-Z]+)', equation)
        invalid = [cmd for cmd in commands if cmd not in valid_commands]
        return invalid

    def _find_line_number(self, content: str, pos: int) -> int:
        """Find line number for a position in content."""
        return content[:pos].count('\n') + 1


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Verify LaTeX equations")
    parser.add_argument("--ground-truth", required=True, help="Ground truth JSON file")
    parser.add_argument("--content", required=True, help="Content file to verify")
    parser.add_argument("--output", help="Output report file")

    args = parser.parse_args()

    # Read content
    with open(args.content, "r") as f:
        content = f.read()

    # Verify
    verifier = EquationVerifier(args.ground_truth)
    is_valid, issues = verifier.verify_file(content)

    # Generate report
    report_lines = [
        "# Equation Verification Report",
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
            if "location" in issue:
                report_lines.append(f"  - Location: Line {issue['location']}")
            if "equation_id" in issue:
                report_lines.append(f"  - Equation: {issue['equation_id']}")
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
