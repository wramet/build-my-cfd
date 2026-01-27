#!/usr/bin/env python3
"""
Final coherence verification.

Checks:
1. Overall consistency across sections
2. All verified fact markers (⭐) are present
3. No truncated content
4. Cross-references are valid
"""

import sys
import re
from pathlib import Path
from typing import Dict, List, Tuple


class CoherenceVerifier:
    """Verify overall coherence of content."""

    def __init__(self):
        """Initialize verifier."""
        self.issues = []

    def verify_file(self, content: str) -> Tuple[bool, List[Dict]]:
        """Verify coherence of markdown content."""
        self.issues = []

        # Check for verified fact markers
        self._check_verified_markers(content)

        # Check for truncated content
        self._check_truncated_content(content)

        # Check for balanced code blocks
        self._check_code_blocks(content)

        # Check for balanced LaTeX
        self._check_latex_balance(content)

        # Check header hierarchy
        self._check_header_hierarchy(content)

        # Check for broken cross-references
        self._check_cross_references(content)

        is_valid = len([i for i in self.issues if i["severity"] == "error"]) == 0
        return is_valid, self.issues

    def _check_verified_markers(self, content: str) -> None:
        """Check that verified fact markers are present."""
        if "⭐" not in content:
            self.issues.append({
                "type": "no_verified_markers",
                "severity": "error",
                "message": "No verified fact markers (⭐) found"
            })

        # Check marker usage is appropriate
        star_count = content.count("⭐")
        warning_count = content.count("⚠️")
        error_count = content.count("❌")

        # Log marker statistics
        total_markers = star_count + warning_count + error_count
        if total_markers > 0:
            marker_ratio = star_count / total_markers
            if marker_ratio < 0.5:
                self.issues.append({
                    "type": "low_verification_ratio",
                    "severity": "warning",
                    "message": f"Low verification ratio: {star_count}/{total_markers} (⭐) markers"
                })

    def _check_truncated_content(self, content: str) -> None:
        """Check for indicators of truncated content."""
        # Check for lines ending with ** (incomplete markdown)
        for line_num, line in enumerate(content.split("\n"), 1):
            if re.match(r'^\*\*[^*]+$', line.strip()):
                self.issues.append({
                    "type": "truncated_content",
                    "severity": "error",
                    "message": f"Truncated content on line {line_num}: {line.strip()}"
                })

        # Check for incomplete code blocks
        code_count = content.count('```')
        if code_count % 2 != 0:
            self.issues.append({
                "type": "unclosed_code_block",
                "severity": "error",
                "message": "Unclosed code block detected"
            })

        # Check for incomplete list items ending with "..."
        for match in re.finditer(r'(?m)^[-*]\s+.*\.\.\.$', content):
            self.issues.append({
                "type": "incomplete_list_item",
                "severity": "warning",
                "message": f"Incomplete list item: {match.group(0)}"
            })

    def _check_code_blocks(self, content: str) -> None:
        """Check code block balance and syntax."""
        code_blocks = re.findall(r'```(\w+)', content)
        block_closes = content.count('```') // 2

        if len(code_blocks) != block_closes:
            self.issues.append({
                "type": "unbalanced_code_blocks",
                "severity": "error",
                "message": f"Code block mismatch: {len(code_blocks)} language tags, {block_closes} closes"
            })

        # Check for code blocks without language tags
        for match in re.finditer(r'```(?!\w)', content):
            self.issues.append({
                "type": "code_no_language",
                "severity": "warning",
                "message": "Code block missing language tag"
            })

    def _check_latex_balance(self, content: str) -> None:
        """Check LaTeX delimiter balance."""
        # Check display math
        display_count = content.count('$$')
        if display_count % 2 != 0:
            self.issues.append({
                "type": "unbalanced_display_math",
                "severity": "error",
                "message": f"Unbalanced display math ($$): {display_count} markers"
            })

        # Check for nested LaTeX (forbidden)
        nested = re.search(r'\$\$.*\$[^$]', content, re.DOTALL)
        if nested:
            self.issues.append({
                "type": "nested_latex",
                "severity": "error",
                "message": "Nested LaTeX delimiters found"
            })

    def _check_header_hierarchy(self, content: str) -> None:
        """Check that header levels don't skip levels."""
        headers = re.findall(r'^(#{1,6})\s', content, re.MULTILINE)

        if not headers:
            self.issues.append({
                "type": "no_headers",
                "severity": "warning",
                "message": "No headers found in content"
            })
            return

        # Check for skipped levels (H1 -> H3, etc.)
        for i in range(len(headers) - 1):
            current_level = len(headers[i])
            next_level = len(headers[i + 1])

            # H1 is only for document title
            if current_level == 1 and i > 0:
                self.issues.append({
                    "type": "h1_in_body",
                    "severity": "error",
                    "message": "H1 should only be used for document title"
                })

            # Check for skipped levels
            if current_level == 2 and next_level == 4:
                self.issues.append({
                    "type": "skipped_header_level",
                    "severity": "warning",
                    "message": "Skipped header level: H2 -> H4 (missing H3)"
                })

    def _check_cross_references(self, content: str) -> None:
        """Check for broken cross-references."""
        # Look for markdown links
        links = re.findall(r'\[([^\]]+)\]\(([^)]+)\)', content)

        for text, url in links:
            # Check for empty links
            if not url or url == "()":
                self.issues.append({
                    "type": "empty_link",
                    "severity": "error",
                    "message": f"Empty link URL: [{text}]()"
                })

            # Check for broken internal links (if they refer to sections)
            if url.startswith('#'):
                anchor = url[1:]
                # Check if anchor exists as header
                headers = re.findall(r'^#{1,6}\s+(.+)$', content, re.MULTILINE)
                header_anchors = [h.lower().replace(' ', '-') for h in headers]

                # Simple check - remove special chars from anchor
                simple_anchor = re.sub(r'[^a-z0-9-]', '', anchor.lower())

                if not any(simple_anchor in ha or ha == simple_anchor for ha in header_anchors):
                    self.issues.append({
                        "type": "broken_internal_link",
                        "severity": "warning",
                        "message": f"Internal link may be broken: {text} -> {url}"
                    })


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Verify coherence")
    parser.add_argument("--content", required=True, help="Content file to verify")
    parser.add_argument("--output", help="Output report file")

    args = parser.parse_args()

    # Read content
    with open(args.content, "r") as f:
        content = f.read()

    # Verify
    verifier = CoherenceVerifier()
    is_valid, issues = verifier.verify_file(content)

    # Generate report
    report_lines = [
        "# Coherence Verification Report",
        "",
        f"**Status:** {'✅ PASSED' if is_valid else '❌ FAILED'}",
        f"**Issues Found:** {len(issues)}",
        ""
    ]

    if issues:
        # Group by severity
        errors = [i for i in issues if i["severity"] == "error"]
        warnings = [i for i in issues if i["severity"] == "warning"]

        if errors:
            report_lines.append("## Errors")
            report_lines.append("")
            for issue in errors:
                report_lines.append(f"- ❌ {issue['message']}")
            report_lines.append("")

        if warnings:
            report_lines.append("## Warnings")
            report_lines.append("")
            for issue in warnings:
                report_lines.append(f"- ⚠️ {issue['message']}")
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
