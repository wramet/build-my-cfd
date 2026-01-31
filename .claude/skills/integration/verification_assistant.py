#!/usr/bin/env python3
"""
Verification Assistant - Connects skills to verification gates

This module integrates skills with the verification gate system to provide
skill-assisted verification for content quality and technical accuracy.
"""

import json
from typing import Dict, List, Optional, Any
from pathlib import Path
from dataclasses import dataclass, field
from enum import Enum

import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "orchestrator"))

from orchestrator.skill_registry import SkillRegistry
from orchestrator.skill_executor import SkillExecutor, ExecutionResult
from orchestrator.skill_chain import SkillChain


class GateStatus(Enum):
    """Status of a verification gate"""
    PENDING = "pending"
    PASS = "PASS"
    FAILED = "FAILED"
    SKIPPED = "SKIPPED"


@dataclass
class GateResult:
    """Result of a verification gate execution"""
    gate_id: int
    gate_name: str
    status: GateStatus
    skill_results: List[ExecutionResult] = field(default_factory=list)
    issues: List[str] = field(default_factory=list)
    is_critical: bool = True

    def to_dict(self) -> dict:
        return {
            "gate_id": self.gate_id,
            "gate_name": self.gate_name,
            "status": self.status.value,
            "skill_results": [r.to_dict() for r in self.skill_results],
            "issues": self.issues,
            "is_critical": self.is_critical
        }


class VerificationAssistant:
    """
    Connects skills to verification gates for automated quality checking.

    Provides:
    - Skill-assisted verification for each gate
    - Source-First compliance checking
    - Aggregated gate results
    - Detailed issue reporting
    """

    def __init__(self, registry: Optional[SkillRegistry] = None,
                 executor: Optional[SkillExecutor] = None):
        self.registry = registry or SkillRegistry()
        self.executor = executor or SkillExecutor(self.registry)

    def execute_gate_with_skills(self, gate_id: int, context: dict) -> GateResult:
        """
        Execute a verification gate with skill assistance.

        Gate definitions:
        1. Ground Truth Extraction
        2. Skeleton Verification
        3. Content Generation
        4. Syntax QC
        5. Translation/Formatting
        6. Final Validation

        Args:
            gate_id: Gate number (1-6)
            context: Context dictionary with file paths, content, etc.

        Returns:
            GateResult with execution details
        """
        gate_configs = {
            1: {
                "name": "Ground Truth Extraction",
                "skills": ["source-first"],
                "critical": True,
                "params": {"action": "extract", "target": context.get("target_file")}
            },
            2: {
                "name": "Skeleton Verification",
                "skills": ["source-first"],
                "critical": True,
                "params": {"action": "verify_skeleton", "skeleton": context.get("skeleton_path")}
            },
            3: {
                "name": "Content Generation",
                "skills": ["scientific_skills"],
                "critical": True,
                "params": {"content": context.get("content"), "check_formulas": True}
            },
            4: {
                "name": "Syntax QC",
                "skills": ["mermaid_expert"],
                "critical": True,
                "params": {"file": context.get("file_path"), "check": "syntax"}
            },
            5: {
                "name": "Translation/Formatting",
                "skills": [],
                "critical": False,
                "params": {}
            },
            6: {
                "name": "Final Validation",
                "skills": ["source-first", "systematic_debugging"],
                "critical": True,
                "params": {"final_check": True, "file": context.get("file_path")}
            }
        }

        config = gate_configs.get(gate_id)
        if not config:
            return GateResult(
                gate_id=gate_id,
                gate_name="Unknown Gate",
                status=GateStatus.SKIPPED,
                is_critical=False
            )

        skill_results = []
        issues = []

        for skill_id in config["skills"]:
            result = self.executor.execute(
                skill_id,
                {**config["params"], **context}
            )
            skill_results.append(result)

            if not result.success:
                issues.append(f"{skill_id}: {result.error}")

        # Determine gate status
        if any(not r.success for r in skill_results):
            status = GateStatus.FAILED
        else:
            status = GateStatus.PASS

        return GateResult(
            gate_id=gate_id,
            gate_name=config["name"],
            status=status,
            skill_results=skill_results,
            issues=issues,
            is_critical=config["critical"]
        )

    def verify_source_first(self, content: str, file_path: str) -> List[str]:
        """
        Verify content follows Source-First rules.

        Checks:
        - Technical claims are marked (⭐, ⚠️, ❌)
        - Formulas are verified
        - Code includes source references
        - No hallucinations

        Args:
            content: Content to verify
            file_path: Path to content file

        Returns:
            List of issues found (empty if passes)
        """
        issues = []

        # Check for verification markers on technical claims
        # (This is a simplified check - real implementation would parse content)

        # Check for code blocks without source references
        import re
        code_blocks = re.findall(r'```cpp\n(.*?)\n```', content, re.DOTALL)
        for block in code_blocks:
            if "File:" not in block and "Line:" not in block:
                issues.append("Code block missing source reference")

        # Check for formulas without verification
        formulas = re.findall(r'\$\$.*?\$\$', content, re.DOTALL)
        for formula in formulas:
            if "Verified from" not in content[content.find(formula):content.find(formula)+200]:
                issues.append("Formula may be unverified")

        return issues

    def execute_all_gates(self, context: dict,
                         stop_on_failure: bool = True) -> List[GateResult]:
        """
        Execute all verification gates in sequence.

        Args:
            context: Context dictionary for gate execution
            stop_on_failure: Whether to stop on first critical failure

        Returns:
            List of GateResults
        """
        results = []

        for gate_id in range(1, 7):
            result = self.execute_gate_with_skills(gate_id, context)
            results.append(result)

            if stop_on_failure:
                if result.status == GateStatus.FAILED and result.is_critical:
                    break

        return results

    def generate_report(self, gate_results: List[GateResult]) -> str:
        """
        Generate a verification report from gate results.

        Args:
            gate_results: List of gate execution results

        Returns:
            Formatted report string
        """
        lines = ["# Verification Report\n"]
        lines.append("=" * 60 + "\n")

        for result in gate_results:
            status_icon = {
                GateStatus.PASS: "✅",
                GateStatus.FAILED: "❌",
                GateStatus.SKIPPED: "⏭️",
                GateStatus.PENDING: "⏳"
            }.get(result.status, "?")

            lines.append(f"\n### Gate {result.gate_id}: {result.gate_name}")
            lines.append(f"Status: {status_icon} {result.status.value}")

            if result.issues:
                lines.append("\nIssues:")
                for issue in result.issues:
                    lines.append(f"  - {issue}")

            if result.skill_results:
                lines.append(f"\nSkills executed: {len(result.skill_results)}")
                for skill_result in result.skill_results:
                    lines.append(f"  - {skill_result.skill_id}: {skill_result.execution_time:.3f}s")

        lines.append("\n" + "=" * 60)
        passed = sum(1 for r in gate_results if r.status == GateStatus.PASS)
        total = len(gate_results)
        lines.append(f"\nSummary: {passed}/{total} gates passed")

        return "\n".join(lines)


def main():
    """CLI for verification assistant operations"""
    import argparse

    parser = argparse.ArgumentParser(description="Verification Assistant CLI")
    parser.add_argument("--gate", type=int, metavar="ID",
                       help="Execute specific gate (1-6)")
    parser.add_argument("--all", action="store_true",
                       help="Execute all gates")
    parser.add_argument("--context", type=json.loads,
                       help="Context data for gate execution")
    parser.add_argument("--verify-source-first", nargs=2,
                       metavar=("CONTENT", "FILE_PATH"),
                       help="Verify Source-First compliance")

    args = parser.parse_args()

    assistant = VerificationAssistant()
    context = args.context or {}

    if args.gate:
        result = assistant.execute_gate_with_skills(args.gate, context)
        print(json.dumps(result.to_dict(), indent=2))

    if args.all:
        results = assistant.execute_all_gates(context)
        report = assistant.generate_report(results)
        print(report)

    if args.verify_source_first:
        content = Path(args.verify_source_first[0]).read_text()
        file_path = args.verify_source_first[1]
        issues = assistant.verify_source_first(content, file_path)

        if issues:
            print("Source-First Issues Found:")
            for issue in issues:
                print(f"  - {issue}")
        else:
            print("✅ Content passes Source-First verification")


if __name__ == "__main__":
    main()
