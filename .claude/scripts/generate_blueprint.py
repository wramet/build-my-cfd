#!/usr/bin/env python3
"""
Generate structural blueprint for CFD learning content.

This script reads:
- Skeleton JSON (content structure)
- Ground truth JSON (verified facts)
- Template library (structural patterns)
- Phase mapping (day-to-phase resolution)

And outputs:
- Blueprint JSON (learning structure with progressive overload)

Usage:
    python3 .claude/scripts/generate_blueprint.py <day_number> <topic>
"""

import json
import sys
import os
from pathlib import Path

# Import phase utilities for day-to-phase resolution
sys.path.insert(0, str(Path(__file__).parent))
from phase_utils import get_phase_for_day, get_template_for_day, get_target_lines


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


def determine_template(topic, template_mapping):
    """
    Determine which template to use based on topic keywords.

    Args:
        topic: Topic string (e.g., "Temporal Discretization")
        template_mapping: Dictionary mapping keywords to template names

    Returns:
        Template name (e.g., "cpp_deep_dive", "architecture_analysis", "performance_lab")
    """
    topic_lower = topic.lower()

    # Check for keyword matches
    for keyword, template_name in template_mapping.items():
        if keyword in topic_lower:
            return template_name

    # Default: use cpp_deep_dive for code-heavy content
    return "cpp_deep_dive"


def generate_blueprint(day, topic, skeleton, ground_truth, template_lib):
    """
    Generate structural blueprint from inputs using phase-based templates.

    Args:
        day: Day number (string, e.g., "04")
        topic: Topic name
        skeleton: Skeleton JSON data
        ground_truth: Ground truth JSON data
        template_lib: Template library JSON data

    Returns:
        Blueprint dictionary with phase-appropriate template
    """
    day_int = int(day)

    # Get phase information using phase_utils
    phase_info = get_phase_for_day(day_int)
    phase_name = phase_info["name"]

    # Get template name for this day
    template_name = get_template_for_day(day_int)

    # Get target line count for this phase
    total_target_lines = get_target_lines(day_int)

    # Determine base template from topic (for content style override)
    topic_template = determine_template(topic, template_lib["topic_to_template_mapping"])

    # Use phase template if available in template library, otherwise use topic template
    if template_name in template_lib.get("templates", {}):
        template = template_lib["templates"][template_name]
    else:
        template = template_lib["templates"][topic_template]

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
            "phase": phase_name,
            "phase_id": phase_info["id"],
            "template": template_name,
            "template_type": template["type"],
            "purpose": template["purpose"],
            "generated_at": __import__('datetime').datetime.now().isoformat()
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
