#!/usr/bin/env python3
"""
Lab Blueprint Generator

Generates lab-specific blueprints based on:
- Lab template from structural_blueprints.json
- Day number and lab type (CFD/C++)
- Links to theory content

Usage:
    python3 generate_lab_blueprint.py --day=01 --type=cfd
    python3 generate_lab_blueprint.py --day=01 --type=cpp
"""

import argparse
import json
import sys
from pathlib import Path
from datetime import datetime

# Paths
PROJECT_ROOT = Path(__file__).parent.parent.parent
TEMPLATES_FILE = PROJECT_ROOT / ".claude/templates/structural_blueprints.json"
OUTPUT_DIR = PROJECT_ROOT / "daily_learning/blueprints"


def load_template():
    """Load lab template from structural_blueprints.json"""
    with open(TEMPLATES_FILE, 'r') as f:
        data = json.load(f)
    return data["templates"]["lab"]


def load_theory_content(day):
    """Load theory content for the given day"""
    phase_dirs = [
        PROJECT_ROOT / "daily_learning/Phase_01_Foundation_Theory",
        PROJECT_ROOT / "daily_learning/Phase_02_Geometry_Mesh",
        # Add more phases as needed
    ]

    day_file = None
    for phase_dir in phase_dirs:
        potential = phase_dir / f"{day}.md"
        if potential.exists():
            day_file = potential
            break

    if day_file is None:
        return None

    with open(day_file, 'r') as f:
        return f.read()


def generate_blueprint(day, lab_type, theory_content):
    """Generate lab blueprint"""

    template = load_template()

    # Determine topic based on lab type and day
    if lab_type == "cfd":
        topic = get_cfd_topic(int(day))
        cpp_focus = get_cpp_concept_for_day(int(day))
    else:  # cpp
        topic = get_cpp_topic(int(day))
        cpp_focus = topic

    # Extract learning objectives from theory if available
    learning_objectives = []
    if theory_content:
        learning_objectives = extract_objectives(theory_content)

    blueprint = {
        "metadata": {
            "day": day,
            "lab_type": lab_type,
            "topic": topic,
            "generated_at": datetime.now().isoformat(),
            "template": "lab"
        },
        "lab_focus": {
            "primary": topic,
            "cpp_concept": cpp_focus,
            "difficulty": get_difficulty(int(day), lab_type)
        },
        "template": {
            "name": template["name"],
            "type": template["type"],
            "progressive_overload": template["progressive_overload"],
            "code_ratio": template["code_ratio"]
        },
        "structure": {
            "parts": template["structure"]["parts"]
        },
        "rules": template["rules"],
        "lab_requirements": {
            "estimated_duration": "2-4 hours",
            "environment": "OpenFOAM v2306",
            "deliverables": ["Working code", "Test results", "Performance metrics"]
        },
        "learning_outcomes": {
            "cfd": get_cfd_outcome(int(day), lab_type),
            "cpp": cpp_focus
        },
        "connections": {
            "theory_file": f"daily_learning/Phase_*/{day}.md",
            "prerequisite_days": get_prerequisites(int(day)),
            "related_cpp_modules": get_related_cpp_modules(cpp_focus)
        }
    }

    return blueprint


def get_cfd_topic(day):
    """Map day to CFD topic"""
    topics = {
        1: "Continuity Equation Implementation",
        2: "Finite Volume Discretization",
        3: "Upwind Interpolation Scheme",
        4: "Temporal Discretization Methods",
        5: "Custom Boundary Conditions",
        6: "Pressure-Velocity Coupling",
        7: "Linear Solvers",
        8: "Turbulence Modeling Basics",
        9: "Debugging simpleFoam",
        10: "Heat Transfer Implementation",
        11: "Phase Change Fundamentals",
        12: "Mass Transfer Models"
    }
    return topics.get(day, f"CFD Concept Day {day}")


def get_cpp_topic(day):
    """Map day to C++ topic (for standalone C++ labs)"""
    topics = {
        1: "Basic Types and Operators",
        2: "Functions and References",
        3: "Classes and Objects",
        4: "Inheritance and Virtual Functions",
        5: "Polymorphism and Abstract Classes",
        6: "Operator Overloading",
        7: "Template Fundamentals",
        8: "STL Containers and Algorithms",
        9: "Smart Pointers and RAII",
        10: "Move Semantics",
        11: "Constexpr and Compile-Time Computation",
        12: "C++20 Concepts",
        13: "Sparse Arrays (DSA)",
        14: "Graph Data Structures",
        15: "Tree Structures for Mesh",
        16: "Iterative Solvers (CG, BiCGStab)"
    }
    return topics.get(day, f"C++ Concept Day {day}")


def get_cpp_concept_for_day(day):
    """Get C++ concept to highlight for CFD lab"""
    concepts = {
        1: "Basic types, operators, control flow",
        2: "Functions, parameters, file I/O",
        3: "Templates introduction",
        4: "Class hierarchies",
        5: "Virtual functions",
        6: "Operator overloading"
    }
    return concepts.get(day, "C++ fundamentals")


def get_difficulty(day, lab_type):
    """Get difficulty level for the lab"""
    if day <= 3:
        return "Beginner"
    elif day <= 7:
        return "Intermediate"
    else:
        return "Advanced"


def get_cfd_outcome(day, lab_type):
    """Get CFD learning outcome"""
    if lab_type == "cpp":
        return "Apply C++ to CFD problems"

    outcomes = {
        1: "Implement continuity equation with source terms",
        2: "Apply finite volume discretization to scalar transport",
        3: "Implement upwind interpolation scheme",
        4: "Compare Euler, Crank-Nicolson, and backward schemes",
        5: "Create custom fixedValue boundary condition",
        6: "Debug pressure-velocity coupling in simpleFoam",
        7: "Implement custom linear solver",
        8: "Add k-epsilon turbulence model",
        9: "Profile and optimize simpleFoam",
        10: "Implement heat transfer with buoyancy",
        11: "Create phase change model",
        12: "Implement mass transfer between phases"
    }
    return outcomes.get(day, f"CFD implementation for day {day}")


def get_prerequisites(day):
    """Get prerequisite days"""
    if day == 1:
        return []
    elif day <= 3:
        return [str(day - 1)]
    else:
        return [str(day - 2), str(day - 1)]


def get_related_cpp_modules(cpp_concept):
    """Get related MODULE_05/09 sections"""
    # This will be populated after MODULE verification
    return {
        "status": "pending_verification",
        "note": "MODULE_05/09 content needs Source-First verification before referencing"
    }


def extract_objectives(theory_content):
    """Extract learning objectives from theory content"""
    objectives = []

    # Look for learning objectives section
    if "## Learning Objectives" in theory_content:
        start = theory_content.find("## Learning Objectives")
        section = theory_content[start:start+500]

        # Extract bullet points
        lines = section.split('\n')
        for line in lines:
            if line.strip().startswith('-'):
                objectives.append(line.strip()[1:].strip())

    return objectives[:5]  # Max 5 objectives


def save_blueprint(blueprint, day, lab_type):
    """Save blueprint to file"""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    output_file = OUTPUT_DIR / f"lab{day}_{lab_type}_blueprint.json"

    with open(output_file, 'w') as f:
        json.dump(blueprint, f, indent=2)

    return output_file


def main():
    parser = argparse.ArgumentParser(
        description='Generate lab blueprint for a given day and type'
    )
    parser.add_argument('--day', required=True, help='Day number (e.g., 01, 02)')
    parser.add_argument('--type', required=True, choices=['cfd', 'cpp'],
                        help='Lab type: cfd or cpp')

    args = parser.parse_args()

    # Normalize day format
    day = args.day.zfill(2) if len(args.day) == 1 else args.day

    # Load theory content
    theory_content = load_theory_content(day)
    if theory_content is None:
        print(f"Warning: Theory content for Day {day} not found", file=sys.stderr)
        print("Generating blueprint without theory linkage", file=sys.stderr)

    # Generate blueprint
    blueprint = generate_blueprint(day, args.type, theory_content)

    # Save blueprint
    output_file = save_blueprint(blueprint, day, args.type)

    print(f"✅ Lab blueprint generated: {output_file}")
    print(f"   Day: {day}, Type: {args.type}")
    print(f"   Topic: {blueprint['lab_focus']['primary']}")
    print(f"   C++ Concept: {blueprint['lab_focus']['cpp_concept']}")


if __name__ == "__main__":
    main()
