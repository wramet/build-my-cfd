#!/usr/bin/env python3
"""
Generate structural blueprint for CFD content creation.

This script reads:
- Skeleton JSON (content structure)
- Ground truth JSON (verified facts)
- Template library (structural patterns)

And outputs:
- Blueprint JSON (learning structure with progressive overload)

Usage:
    python3 .claude/scripts/generate_blueprint.py <day_number> <topic>
"""

import json
import sys
import os
from pathlib import Path


def load_json(filepath):
    """Load JSON file with error handling."""
    try:
        with open(filepath, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"❌ File not found: {filepath}")
        return None
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON in {filepath}: {e}")
        return None


def save_json(data, filepath):
    """Save JSON file with pretty formatting."""
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=2)
    print(f"✅ Saved: {filepath}")


def _get_phase_info(day):
    """
    Determine phase and R410A integration percentage from day number.

    Args:
        day: Day number (string or int)

    Returns:
        Tuple of (phase_name, r410a_percent)
    """
    day_int = int(day) if isinstance(day, str) else day

    if 1 <= day_int <= 12:
        return "Foundation Theory", 15
    elif 13 <= day_int <= 19:
        return "Geometry & Mesh", 20
    elif 20 <= day_int <= 49:
        return "Solver Core", 25
    elif 50 <= day_int <= 77:
        return "VOF & Phase Change", 80  # Structure flip!
    elif 78 <= day_int <= 87:
        return "Advanced Features", 90
    else:  # 88-90
        return "Integration & Validation", 100


def _get_template_for_phase(phase):
    """
    Map phase to template file name.

    Args:
        phase: Phase name string

    Returns:
        Template file name (without .json extension)
    """
    template_map = {
        "Foundation Theory": "foundation_with_r410a",
        "Geometry & Mesh": "geometry_with_r410a",
        "Solver Core": "solver_with_r410a",
        "VOF & Phase Change": "r410a_implementation",  # Structure flip
        "Advanced Features": "r410a_advanced",
        "Integration & Validation": "r410a_capstone"
    }
    return template_map.get(phase, "foundation_with_r410a")


def _get_target_lines(phase):
    """
    Get target line count based on phase.

    Phases with more R410A content get more lines.
    """
    lines_map = {
        "Foundation Theory": 800,
        "Geometry & Mesh": 900,
        "Solver Core": 1000,
        "VOF & Phase Change": 1500,  # More R410A content
        "Advanced Features": 1500,
        "Integration & Validation": 1200
    }
    return lines_map.get(phase, 800)


def determine_template(topic, template_mapping):
    """
    Determine which template to use based on topic keywords.

    Args:
        topic: Topic string (e.g., "Temporal Discretization")
        template_mapping: Dictionary mapping keywords to template names

    Returns:
        Template name (e.g., "mathematician", "engine_builder", "scientist")
    """
    topic_lower = topic.lower()

    # Check for keyword matches
    for keyword, template_name in template_mapping.items():
        if keyword in topic_lower:
            return template_name

    # Special case: Phase 4 integration topics
    integration_keywords = [
        "expansion", "dilatation", "pressure source",
        "tabulation", "property table", "lookup",
        "boiling", "stefan", "evaporation test",
        "spurious", "current", "interface",
        "htc", "validation", "correlation",
        "phase change", "mass source", "energy source"
    ]
    for keyword in integration_keywords:
        if keyword in topic_lower:
            return "integration_engineer"

    # Default: use mathematician for theory-heavy content
    return "mathematician"


def generate_blueprint(day, topic, skeleton, ground_truth, template_lib):
    """
    Generate structural blueprint from inputs with R410A integration.

    Args:
        day: Day number (string, e.g., "04")
        topic: Topic name
        skeleton: Skeleton JSON data
        ground_truth: Ground truth JSON data
        template_lib: Template library JSON data

    Returns:
        Blueprint dictionary with Part 5 for R410A application
    """
    # Determine phase and R410A integration percentage
    phase, r410a_percent = _get_phase_info(day)

    # Get phase-specific template name
    phase_template_name = _get_template_for_phase(phase)

    # Get target line count for this phase
    total_target_lines = _get_target_lines(phase)

    # Determine base template from topic (for content style)
    template_name = determine_template(topic, template_lib["topic_to_template_mapping"])

    # Try to use phase-specific template if available
    if phase_template_name in template_lib.get("templates", {}):
        template = template_lib["templates"][phase_template_name]
    else:
        template = template_lib["templates"][template_name]
    # Handle nested structure (template may have "structure" -> "parts")
    if "structure" in template:
        parts_data = template["structure"]["parts"]
    else:
        parts_data = template.get("parts", [])

    # Extract content needs from skeleton
    content_needs = []
    if "sections" in skeleton:
        for section in skeleton["sections"]:
            if "title" in section:
                content_needs.append(section["title"])

    # Extract formulas from ground truth
    formulas = []
    if ground_truth and "formulas" in ground_truth:
        for key, formula_data in ground_truth["formulas"].items():
            formulas.append({
                "name": key,
                "latex": formula_data.get("latex", ""),
                "source": formula_data.get("source", "")
            })

    # Extract class hierarchy from ground truth
    class_hierarchy = ground_truth.get("class_hierarchy", {}) if ground_truth else {}

    # Build blueprint
    blueprint = {
        "metadata": {
            "version": template_lib["version"],
            "day": day,
            "topic": topic,
            "phase": phase,
            "r410a_integration": f"{r410a_percent}%",
            "template": template_name,
            "template_type": template["type"],
            "purpose": template["purpose"],
            "generated_at": __import__('datetime').datetime.now().isoformat()
        },
        "r410a_context": {
            "application": "Evaporator two-phase flow",
            "refrigerant": "R410A",
            "conditions": "P = 1.0-1.2 MPa, T = 280-285 K"
        },
        "template": {
            "name": template["name"],
            "type": template["type"],
            "progressive_overload": template["progressive_overload"],
            "boilerplate_policy": template["boilerplate_policy"],
            "code_ratio": template["code_ratio"]
        },
        "structure": {
            "parts": []
        },
        "content_requirements": {
            "topics_to_cover": content_needs,
            "formulas_to_include": formulas,
            "class_hierarchy": class_hierarchy
        },
        "rules": {
            "ratio_tolerance": template_lib["rules"]["ratio_tolerance"],
            "boilerplate_policy": template["boilerplate_policy"],
            "concept_first": template_lib["rules"]["concept_first_markers"],
            "progressive_complexity": template_lib["rules"]["progressive_complexity_markers"]
        }
    }

    # Generate part structure from template
    for i, part_template in enumerate(parts_data, 1):
        part = {
            "id": part_template.get("id", f"p{i}"),
            "title": part_template["title"],
            "ratio": part_template["ratio"],
            "readability": part_template["readability"],
            "approach": part_template.get("approach", "standard"),
            "content_type": part_template.get("content_type", "mixed"),
            "guideline": part_template.get("guideline", ""),
            "estimated_lines": 0  # Will be calculated based on total target
        }
        blueprint["structure"]["parts"].append(part)

    # Add Part 5 for R410A application
    part_5 = {
        "id": "p5",
        "title": "R410A Evaporator Application",
        "ratio": r410a_percent / 100,
        "readability": "intermediate",
        "approach": "application",
        "content_type": "domain_specific",
        "guideline": "Connect general theory to R410A evaporator simulation",
        "sections": [
            "5.1 Why it matters for R410A evaporator",
            "5.2 R410A property data",
            "5.3 Equation modifications for R410A",
            "5.4 Implementation preview (OpenFOAM code)"
        ],
        "estimated_lines": 0  # Will be calculated
    }
    blueprint["structure"]["parts"].append(part_5)

    # Calculate estimated line counts based on phase target
    for part in blueprint["structure"]["parts"]:
        part["estimated_lines"] = int(total_target_lines * part["ratio"])

    return blueprint


def main():
    """Main execution."""
    if len(sys.argv) < 3:
        print("Usage: python3 generate_blueprint.py <day> <topic>")
        print("Example: python3 generate_blueprint.py 04 'Temporal Discretization'")
        sys.exit(1)

    day = sys.argv[1]
    topic = ' '.join(sys.argv[2:])

    # Define file paths
    project_root = Path(__file__).parent.parent.parent
    skeleton_path = project_root / "daily_learning" / "skeletons" / f"day{day}_skeleton.json"
    ground_truth_path = Path(f"/tmp/verified_facts_day{day}.json")
    blueprint_path = project_root / "daily_learning" / "blueprints" / f"day{day}_blueprint.json"
    template_lib_path = project_root / ".claude" / "templates" / "structural_blueprints.json"

    # Load inputs
    print(f"\n🔵 Stage 2.5: Structural Blueprint Generation")
    print(f"   Day: {day}")
    print(f"   Topic: {topic}")
    print()

    skeleton = load_json(skeleton_path)
    if skeleton is None:
        sys.exit(1)

    ground_truth = load_json(ground_truth_path)
    if ground_truth is None:
        print(f"⚠️  Ground truth not found, proceeding without it")

    template_lib = load_json(template_lib_path)
    if template_lib is None:
        sys.exit(1)

    # Generate blueprint
    print("📝 Generating blueprint...")
    blueprint = generate_blueprint(day, topic, skeleton, ground_truth, template_lib)

    # Create blueprint directory if needed
    blueprint_path.parent.mkdir(parents=True, exist_ok=True)

    # Save blueprint
    save_json(blueprint, blueprint_path)

    # Print summary
    print()
    print("📊 Blueprint Summary:")
    print(f"   Template: {blueprint['metadata']['template']} ({blueprint['template']['name']})")
    print(f"   Type: {blueprint['metadata']['template_type']}")
    print(f"   Parts: {len(blueprint['structure']['parts'])}")
    print()
    print("   Part Structure:")
    for part in blueprint["structure"]["parts"]:
        print(f"   - {part['title']}: {part['ratio']*100:.0f}% (~{part['estimated_lines']} lines)")
    print()
    print("✅ Stage 2.5 Complete")


if __name__ == "__main__":
    main()
