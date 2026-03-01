#!/usr/bin/env python3
"""
Load Project Context for C++ Learning Content Generation

Injects C++ and OpenFOAM learning context into the content creation pipeline.
This ensures all generated content is aligned with the learning objectives.

Usage:
    python3 .claude/scripts/load_project_context.py --day=XX
"""

import json
import yaml
import sys
from pathlib import Path

# Import phase_utils for centralized day-to-phase resolution
sys.path.insert(0, str(Path(__file__).parent))
from phase_utils import get_phase_for_day, get_folder_for_day, get_template_for_day, get_target_lines


def load_project_context():
    """Load project context from YAML file."""
    context_file = Path(".claude/config/project_context.yaml")

    if not context_file.exists():
        print(f"Warning: Project context file not found: {context_file}")
        return None

    with open(context_file) as f:
        return yaml.safe_load(f)


def generate_stage4_prompt_with_context(day, topic, skeleton, blueprint, ground_truth):
    """
    Generate Stage 4 prompt with C++ learning project context.

    Args:
        day: Day number (e.g., "01")
        topic: Topic name (e.g., "Smart Pointers in OpenFOAM")
        skeleton: Skeleton JSON content
        blueprint: Blueprint JSON content
        ground_truth: Ground truth JSON content

    Returns:
        Enhanced prompt string or None if context unavailable
    """
    project_ctx = load_project_context()

    if not project_ctx:
        print("Warning: Could not load project context, using generic prompt")
        return None

    # Extract key learning objectives
    learning_goals = project_ctx.get("learning_objectives", [])
    content_reqs = project_ctx.get("content_requirements", {})
    every_session = content_reqs.get("every_session_must_include", [])

    # Resolve phase info using phase_utils (single source of truth)
    try:
        day_num = int(day)
        phase_info = get_phase_for_day(day_num)
        phase_folder = phase_info["folder"]
        template_name = phase_info["template"]
        target_lines = phase_info["target_lines"]
        content_focus = phase_info.get("content_focus", "")
    except (ValueError, Exception) as e:
        print(f"Warning: Could not resolve phase for day {day}: {e}")
        phase_folder = "Phase_01_CppThroughOpenFOAM"
        template_name = "cpp_deep_dive"
        target_lines = 900
        content_focus = "cpp_patterns"

    prompt = f"""Expand Day {day}: {topic} - ENGLISH ONLY

PHASE INFO:
  Phase Folder: {phase_folder}
  Template: {template_name}
  Target Lines: {target_lines}
  Content Focus: {content_focus}

SKELETON:
{skeleton}

BLUEPRINT:
{blueprint}

GROUND TRUTH:
{ground_truth}

PROJECT CONTEXT (CRITICAL):
===========================
Learning Focus: {project_ctx.get("project_name", "C++ & Software Engineering Through OpenFOAM")}

Learning Objectives:
{chr(10).join(f"- {obj}" for obj in learning_goals)}

Content Requirements:
{chr(10).join(f"- {req}" for req in every_session)}

Code Ratio Target: {content_reqs.get("code_ratio", {}).get("target", 0.65)} (code / total lines)

CRITICAL REQUIREMENTS:
- ENGLISH-ONLY content (no Thai translation)
- Every C++ concept MUST connect to OpenFOAM source code examples
- Use concrete code patterns with file:line references
- Show how real-world OpenFOAM implements these patterns
- Include practical implementation examples

MANDATORY CONTENT:
1. Source Code Reading:
   - Read from actual OpenFOAM .H/.C files
   - Extract concrete patterns (not just theory)
   - Include file paths and line numbers

2. Pattern Identification:
   - Identify specific C++ patterns used
   - Show the pattern in OpenFOAM code
   - Explain WHY this pattern is used

3. Implementation Practice:
   - Provide mini-implementation of the pattern
   - Show compilation and testing
   - Connect back to OpenFOAM usage

4. Best Practices:
   - Modern C++ standards (C++11/14/17)
   - Performance considerations
   - Memory safety and RAII

STRUCTURAL RULES:
- Follow blueprint progressive overload exactly
- Theory → Code Example → Implementation → Practice
- Every code block must have language tags
- All file references include paths and line numbers

APPENDIX REQUIREMENT (MANDATORY):
- Every output MUST end with "## Appendix: Complete File Listings"
- Include complete, compilable code examples
- All files must be 100% copy-pasteable

Format:
- Use $$ for display math equations (for algorithm analysis)
- Use $ for inline math
- Include Mermaid diagrams for class hierarchies and flow charts
- All code blocks must have language tags
- Headers in English only

Output complete markdown file content for C++ learning through OpenFOAM.
"""

    return prompt


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: python3 load_project_context.py --day=XX")
        sys.exit(1)

    # Parse arguments
    day = None
    for arg in sys.argv[1:]:
        if arg.startswith("--day="):
            day = arg.split("=")[1]
            break

    if not day:
        print("Usage: python3 load_project_context.py --day=XX")
        sys.exit(1)

    # Load context
    project_ctx = load_project_context()

    if not project_ctx:
        print("❌ Could not load project context")
        sys.exit(1)

    # Resolve phase info using phase_utils
    try:
        day_num = int(day)
        phase_info = get_phase_for_day(day_num)
        print("C++ Learning Project Context Loaded:")
        print(f"  Project: {project_ctx.get('project', {}).get('name', 'OpenFOAM C++ Learning')}")
        print(f"  Day: {day}")
        print(f"  Phase: {phase_info['name']}")
        print(f"  Folder: {phase_info['folder']}")
        print(f"  Template: {phase_info['template']}")
        print(f"  Target Lines: {phase_info['target_lines']}")
    except (ValueError, Exception) as e:
        print(f"❌ Error resolving phase for day {day}: {e}")
        sys.exit(1)

    print()
    print("Learning Objectives:")
    for obj in project_ctx.get("learning_objectives", {}).get("primary", []):
        print(f"  - {obj}")
    print()
    print("✅ Project context ready for content generation")


if __name__ == "__main__":
    main()
