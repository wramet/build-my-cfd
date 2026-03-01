#!/usr/bin/env python3
"""
Mermaid AI Validator - Hybrid Validation System

Combines fast path (regex + CLI) with slow path (AI agent) for comprehensive
Mermaid diagram validation and fixing.

Usage:
    python3 mermaid_ai_validator.py --file file.md
    python3 mermaid_ai_validator.py --file file.md --fix
    python3 mermaid_ai_validator.py --file file.md --agent-only
"""

import argparse
import json
import re
import subprocess
import sys
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Tuple, Optional


@dataclass
class MermaidIssue:
    """Represents a single Mermaid validation issue."""
    block_start: int
    block_end: int
    error_type: str
    message: str
    confidence: float = 0.8
    fix_applied: str = ""
    fix_result: str = "pending"


@dataclass
class FixReport:
    """Report of fixes applied."""
    total_issues: int = 0
    fast_path_fixes: int = 0
    ai_agent_fixes: int = 0
    failed_fixes: int = 0
    issues: List[MermaidIssue] = field(default_factory=list)


class FastPathValidator:
    """
    Fast path validator using regex patterns and Mermaid CLI.

    Handles common, well-known errors quickly without AI overhead.
    """

    def __init__(self, mermaid_cli: str = "mmdc"):
        self.mermaid_cli = mermaid_cli
        self.cli_available = self._check_cli()

    def _check_cli(self) -> bool:
        """Check if Mermaid CLI is available."""
        try:
            result = subprocess.run(
                [self.mermaid_cli, "--version"],
                capture_output=True,
                timeout=5
            )
            return result.returncode == 0
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return False

    def extract_mermaid_blocks(self, content: str) -> List[Tuple[int, int, str]]:
        """Extract Mermaid blocks with line numbers."""
        blocks = []
        pattern = r'```mermaid\n(.*?)```'

        for match in re.finditer(pattern, content, re.DOTALL):
            start_line = content[:match.start()].count('\n') + 1
            end_line = content[:match.end()].count('\n') + 1
            mmd_code = match.group(1).strip()
            blocks.append((start_line, end_line, mmd_code))

        return blocks

    def validate_with_cli(self, mmd_code: str) -> Tuple[bool, str]:
        """Validate Mermaid code using official CLI."""
        if not self.cli_available:
            return False, "Mermaid CLI not installed"

        try:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.mmd', delete=False) as f:
                f.write(mmd_code)
                f.flush()
                temp_path = f.name

            result = subprocess.run(
                [self.mermaid_cli, '-i', temp_path, '-o', '/tmp/mermaid_ai_temp.png'],
                capture_output=True,
                text=True,
                timeout=10
            )

            Path(temp_path).unlink()

            if result.returncode != 0:
                error_msg = result.stderr.strip() or result.stdout.strip()
                return False, error_msg[:500]

            return True, "OK"

        except subprocess.TimeoutExpired:
            return False, "Validation timeout"
        except Exception as e:
            return False, f"Validation error: {str(e)}"

    def find_common_errors(self, content: str) -> List[MermaidIssue]:
        """Find common Mermaid errors using regex patterns."""
        issues = []
        blocks = self.extract_mermaid_blocks(content)

        for start_line, end_line, mmd_code in blocks:
            lines = mmd_code.split('\n')

            for offset, line in enumerate(lines, start=1):
                # Check 1: Non-breaking spaces
                if '\u00a0' in line:
                    issues.append(MermaidIssue(
                        block_start=start_line,
                        block_end=end_line,
                        error_type="non_breaking_space",
                        message=f"Non-breaking space (U+00A0) found on line {start_line + offset - 1}",
                        confidence=0.95,
                        fix_applied="Replace with standard space (U+0020)"
                    ))

                # Check 2: Pipe in unquoted node text
                if '[' in line and ']' in line:
                    for match in re.finditer(r'\[(?!"[^"]*?)([^"\]]*\|)', line):
                        node_text = match.group(1)
                        issues.append(MermaidIssue(
                            block_start=start_line,
                            block_end=end_line,
                            error_type="pipe_in_node",
                            message=f"Pipe character in node text (line {start_line + offset - 1}): {node_text[:50]}",
                            confidence=0.9,
                            fix_applied='Wrap in quotes: Node["text"]'
                        ))

                # Check 3: Unquoted edge labels with special chars
                for match in re.finditer(r'-->?\|([^\|]+)\|', line):
                    label = match.group(1)
                    if not label.startswith('"') and re.search(r'[(){}\[\]·φ]', label):
                        issues.append(MermaidIssue(
                            block_start=start_line,
                            block_end=end_line,
                            error_type="unquoted_edge_label",
                            message=f"Edge label with special chars (line {start_line + offset - 1}): {label[:50]}",
                            confidence=0.85,
                            fix_applied='Wrap in quotes: -->|"label"|'
                        ))

                # Check 4: Flowchart nodes with special chars
                if mmd_code.strip().startswith('flowchart'):
                    for match in re.finditer(r'\[(?!"[^"]*?)([^"\]]+)', line):
                        node_text = match.group(1)
                        # Check if node text (before the closing ]) has special chars
                        if re.search(r'[(){}\[\]·φ]', node_text):
                            issues.append(MermaidIssue(
                                block_start=start_line,
                                block_end=end_line,
                                error_type="flowchart_node",
                                message=f"Flowchart node with special chars (line {start_line + offset - 1}): {node_text[:50]}",
                                confidence=0.9,
                                fix_applied='Wrap in quotes: ["text"]'
                            ))

        return issues

    def auto_fix(self, content: str) -> Tuple[str, int]:
        """Auto-fix common Mermaid errors."""
        fix_count = [0]
        lines = content.split('\n')
        in_mermaid = False
        is_flowchart = False

        for i, line in enumerate(lines):
            stripped = line.strip()

            if stripped.startswith('```'):
                if not in_mermaid:
                    if 'mermaid' in stripped.lower():
                        in_mermaid = True
                        is_flowchart = False
                else:
                    in_mermaid = False
                    is_flowchart = False

            if in_mermaid:
                if 'flowchart' in stripped:
                    is_flowchart = True

                # Fix non-breaking spaces
                if '\u00a0' in line:
                    lines[i] = line.replace('\u00a0', ' ')
                    fix_count[0] += 1

                # Fix pipe in node text
                if '[' in line:
                    def fix_pipes(match):
                        text = match.group(1)
                        if '|' in text and not text.startswith('"'):
                            fix_count[0] += 1
                            return match.group(0).replace(text, f'"{text}"')
                        return match.group(0)
                    lines[i] = re.sub(r'\[(?!"[^"]*?)([^"\]]*\|)\]', fix_pipes, lines[i])

                # Fix edge labels
                def fix_labels(match):
                    label = match.group(1)
                    if re.search(r'[(){}\[\]·φ]', label) and not label.startswith('"'):
                        fix_count[0] += 1
                        return match.group(0).replace(label, f'"{label}"')
                    return match.group(0)
                lines[i] = re.sub(r'-->?\|([^\|]+)\|', fix_labels, lines[i])

                # Fix flowchart nodes
                if is_flowchart:
                    def fix_flowchart(match):
                        text = match.group(1)
                        if re.search(r'[(){}\[\]·φ]', text) and not text.startswith('"'):
                            fix_count[0] += 1
                            return match.group(0).replace(text, f'"{text}"')
                        return match.group(0)
                    lines[i] = re.sub(r'\[(?!"[^"]*?)([^"\]]+)', fix_flowchart, lines[i])

        return '\n'.join(lines), fix_count[0]


class MermaidAIValidator:
    """
    Main orchestrator for hybrid Mermaid validation.

    Combines fast path (regex/CLI) with AI agent for comprehensive coverage.
    """

    def __init__(self, use_ai: bool = True):
        self.fast_path = FastPathValidator()
        self.use_ai = use_ai
        self.ai_agent_available = self._check_ai_agent()

    def _check_ai_agent(self) -> bool:
        """Check if mermaid-validator agent is available."""
        agent_path = Path('.claude/agents/mermaid-validator.md')
        return agent_path.exists()

    def validate(self, content: str) -> FixReport:
        """
        Validate Mermaid diagrams using hybrid approach.

        Returns:
            FixReport with all issues found
        """
        report = FixReport()

        # Fast path: Common errors
        fast_issues = self.fast_path.find_common_errors(content)
        report.issues.extend(fast_issues)
        report.fast_path_fixes = len(fast_issues)

        # Slow path: CLI validation for remaining issues
        if self.fast_path.cli_available:
            blocks = self.fast_path.extract_mermaid_blocks(content)

            for start_line, end_line, mmd_code in blocks:
                is_valid, error_msg = self.fast_path.validate_with_cli(mmd_code)

                if not is_valid:
                    # Check if we already caught this with fast path
                    already_caught = False
                    for issue in report.issues:
                        if issue.block_start == start_line:
                            already_caught = True
                            break

                    if not already_caught:
                        # New error detected by CLI - use AI to analyze
                        if self.use_ai and self.ai_agent_available:
                            ai_issue = self._analyze_with_ai(start_line, end_line, mmd_code, error_msg)
                            report.issues.append(ai_issue)
                            report.ai_agent_fixes += 1
                        else:
                            # Fallback: report CLI error without AI
                            report.issues.append(MermaidIssue(
                                block_start=start_line,
                                block_end=end_line,
                                error_type="cli_error",
                                message=error_msg,
                                confidence=0.7,
                                fix_applied="Manual review required"
                            ))

        report.total_issues = len(report.issues)
        return report

    def _analyze_with_ai(self, start_line: int, end_line: int, mmd_code: str, error_msg: str) -> MermaidIssue:
        """
        Analyze error using AI agent (placeholder for Task tool integration).

        In full implementation, this would delegate to the mermaid-validator agent
        via the Task tool for intelligent analysis and fix generation.
        """
        # Placeholder for AI agent integration
        # In production, this would call:
        # Task("mermaid-validator", f"Analyze and fix this Mermaid error:\n{error_msg}\n\nCode:\n{mmd_code}")

        return MermaidIssue(
            block_start=start_line,
            block_end=end_line,
            error_type="ai_analyzed",
            message=f"CLI Error: {error_msg[:200]}",
            confidence=0.8,
            fix_applied="AI analysis: Manual review recommended"
        )

    def auto_fix(self, content: str) -> Tuple[str, FixReport]:
        """
        Auto-fix Mermaid issues using hybrid approach.

        Returns:
            (fixed_content, FixReport)
        """
        # Validate first
        report = self.validate(content)

        # Apply fast path fixes
        fixed_content, fast_fixes = self.fast_path.auto_fix(content)
        report.fast_path_fixes = fast_fixes

        # Note: AI agent fixes would be applied here in full implementation
        # For now, we rely on fast path fixes

        report.total_fixes = report.fast_path_fixes + report.ai_agent_fixes
        return fixed_content, report


def print_report(report: FixReport, verbose: bool = False):
    """Print validation report."""
    print(f"\n{'='*60}")
    print(f"Mermaid AI Validator Report")
    print(f"{'='*60}")
    print(f"Total Issues: {report.total_issues}")
    print(f"Fast Path Fixes: {report.fast_path_fixes}")
    print(f"AI Agent Fixes: {report.ai_agent_fixes}")

    if verbose or report.total_issues > 0:
        print(f"\n{'='*60}")
        print("Issues Details:")
        print(f"{'='*60}")

        for i, issue in enumerate(report.issues, 1):
            print(f"\n## Issue #{i}")
            print(f"   Location: Lines {issue.block_start}-{issue.block_end}")
            print(f"   Type: {issue.error_type}")
            print(f"   Confidence: {issue.confidence:.0%}")
            print(f"   Message: {issue.message}")
            print(f"   Fix: {issue.fix_applied}")


def main():
    parser = argparse.ArgumentParser(
        description="AI-powered Mermaid diagram validator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Validate a file
  python3 mermaid_ai_validator.py --file Day_01.md

  # Validate and auto-fix
  python3 mermaid_ai_validator.py --file Day_01.md --fix

  # Verbose output
  python3 mermaid_ai_validator.py --file Day_01.md --verbose
        """
    )
    parser.add_argument("--file", type=Path, required=True, help="Path to markdown file")
    parser.add_argument("--fix", action="store_true", help="Auto-fix detected issues")
    parser.add_argument("--verbose", action="store_true", help="Verbose output")
    parser.add_argument("--no-ai", action="store_true", help="Disable AI agent (fast path only)")
    args = parser.parse_args()

    if not args.file.exists():
        print(f"❌ Error: File not found: {args.file}")
        sys.exit(1)

    validator = MermaidAIValidator(use_ai=not args.no_ai)

    try:
        content = args.file.read_text()
    except Exception as e:
        print(f"❌ Error reading file: {e}")
        sys.exit(1)

    if args.fix:
        # Auto-fix mode
        fixed_content, report = validator.auto_fix(content)

        if report.total_fixes > 0:
            # Backup original
            backup_path = args.file.with_suffix('.md.backup')
            args.file.rename(backup_path)

            # Write fixed
            args.file.write_text(fixed_content)

            print(f"✅ Applied {report.total_fixes} fix(es)")
            print(f"   Original backed up to: {backup_path}")
        else:
            print("✅ No fixable issues found")

        print_report(report, verbose=args.verbose)

        sys.exit(0 if report.total_issues == 0 else 1)

    else:
        # Validation mode only
        report = validator.validate(content)
        print_report(report, verbose=args.verbose)

        sys.exit(0 if report.total_issues == 0 else 1)


if __name__ == "__main__":
    main()
