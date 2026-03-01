#!/usr/bin/env python3
"""
Lab Type Auto-Detection Script

Analyzes day content to automatically determine lab type:
- CFD lab: For implementing CFD concepts
- C++ lab: For learning new C++ language features
- Both: Some days may need both types

Usage:
    python3 detect_lab_type.py --day=01
    python3 detect_lab_type.py --day=01 --content-file=/path/to/01.md
"""

import argparse
import json
import re
import sys
from pathlib import Path
from collections import Counter

# Keywords that indicate CFD content
CFD_KEYWORDS = [
    "equation", "conservation", "continuity", "momentum", "energy",
    "discretization", "finite volume", "finite difference", "finite element",
    "scheme", "upwind", "central", "tvd", "limiter",
    "solver", "pressure", "velocity", "coupling",
    "boundary condition", "initial condition",
    "turbulence", "laminar", "reynolds",
    "convection", "diffusion", "advection",
    "stability", "convergence", "residual",
    "mesh", "grid", "cell", "face",
    "phase change", "multiphase", "vof", "eulerian",
    "scalar", "vector", "tensor", "field",
    "divergence", "gradient", "laplacian",
    "flux", "source", "sink",
    "piso", "simple", "pimple",
    "openfoam", "cfd", "computational fluid dynamics"
]

# Keywords that indicate C++ language features
CPP_KEYWORDS = [
    "class", "struct", "inheritance", "polymorphism",
    "template", "generic", "typename",
    "virtual function", "override", "abstract",
    "operator overloading", "operator+", "operator*",
    "constructor", "destructor",
    "smart pointer", "unique_ptr", "shared_ptr", "auto_ptr", "tmp",
    "raii", "resource acquisition",
    "move semantics", "std::move", "rvalue", "lvalue",
    "const", "constexpr", "consteval",
    "stl", "container", "vector", "list", "map",
    "iterator", "algorithm",
    "memory management", "new", "delete",
    "reference", "pointer", "dereference",
    "access specifier", "public", "private", "protected",
    "friend", "static", "virtual",
    "base class", "derived class",
    "function object", "lambda", "closure",
    "exception", "try", "catch", "throw"
]

# C++ concepts that should trigger a dedicated C++ lab
CPP_CONCEPTS = {
    "inheritance": "cpp_04_inheritance",
    "polymorphism": "cpp_05_polymorphism",
    "operator overloading": "cpp_06_operators",
    "templates": "cpp_07_templates",
    "stl": "cpp_08_stl",
    "smart pointer": "cpp_09_memory",
    "move semantics": "cpp_10_move",
    "constexpr": "cpp_11_constexpr",
    "concept": "cpp_12_concepts",
    "sparse": "cpp_13_dsa_arrays",
    "graph": "cpp_14_dsa_graphs",
    "tree": "cpp_15_dsa_trees",
    "solver": "cpp_16_algorithms"
}


def detect_lab_type(content, day_num=None):
    """
    Analyze content to determine appropriate lab type(s)

    Returns:
        dict with:
        - primary_type: "cfd", "cpp", or "both"
        - confidence: 0-100 score
        - cfd_score: CFD relevance score
        - cpp_score: C++ relevance score
        - cfd_topic: Detected CFD topic
        - cpp_concept: Detected C++ concept
        - recommendation: Explanation of why this type was chosen
    """

    # Count keyword matches
    content_lower = content.lower()

    cfd_matches = []
    for keyword in CFD_KEYWORDS:
        pattern = r'\b' + re.escape(keyword) + r'\b'
        matches = re.findall(pattern, content_lower, re.IGNORECASE)
        cfd_matches.extend(matches)

    cpp_matches = []
    for keyword in CPP_KEYWORDS:
        pattern = r'\b' + re.escape(keyword) + r'\b'
        matches = re.findall(pattern, content_lower, re.IGNORECASE)
        cpp_matches.extend(matches)

    # Calculate scores
    cfd_score = len(cfd_matches)
    cpp_score = len(cpp_matches)

    # Boost scores based on content patterns
    # Math content (LaTeX) indicates CFD theory
    math_blocks = len(re.findall(r'\$\$.*?\$\$', content, re.DOTALL))
    inline_math = len(re.findall(r'\$[^$]+\$', content))
    cfd_score += (math_blocks * 5) + (inline_math * 2)

    # Code blocks with class/struct indicate C++ focus
    class_definitions = len(re.findall(r'class\s+\w+', content))
    template_usage = len(re.findall(r'template\s*<', content))
    cpp_score += (class_definitions * 3) + (template_usage * 2)

    # Detect specific C++ concepts
    cpp_concept = None
    for concept, module in CPP_CONCEPTS.items():
        if concept in content_lower:
            cpp_concept = {
                "name": concept,
                "module": module
            }
            cpp_score += 10  # Boost for dedicated concept
            break

    # Detect CFD topic from content
    cfd_topic = detect_cfd_topic(content, day_num)

    # Normalize scores to 0-100
    total_score = cfd_score + cpp_score
    if total_score == 0:
        total_score = 1  # Avoid division by zero

    cfd_percent = min(100, int((cfd_score / total_score) * 100))
    cpp_percent = min(100, int((cpp_score / total_score) * 100))

    # Determine primary type
    confidence = abs(cfd_percent - cpp_percent)

    if cfd_percent > cpp_percent + 20:
        primary_type = "cfd"
    elif cpp_percent > cfd_percent + 20:
        primary_type = "cpp"
    else:
        primary_type = "both"
        confidence = 100 - confidence  # Lower confidence when balanced

    # Generate recommendation
    recommendation = generate_recommendation(
        primary_type, cfd_percent, cpp_percent,
        cfd_topic, cpp_concept
    )

    return {
        "primary_type": primary_type,
        "confidence": confidence,
        "cfd_score": cfd_percent,
        "cpp_score": cpp_percent,
        "cfd_topic": cfd_topic,
        "cpp_concept": cpp_concept,
        "recommendation": recommendation
    }


def detect_cfd_topic(content, day_num=None):
    """Detect the main CFD topic from content"""
    # Look for headers and title
    title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
    if title_match:
        title = title_match.group(1)
        # Clean up title
        title = re.sub(r'\s*-\s*.*$', '', title)  # Remove subtitle
        title = re.sub(r'Day\s+\d+:\s*', '', title)  # Remove day prefix
        return title.strip()

    # Fallback: look for first ## header
    header_match = re.search(r'^##\s+(.+)$', content, re.MULTILINE)
    if header_match:
        return header_match.group(1).strip()

    return f"CFD Concept Day {day_num or 'XX'}"


def generate_recommendation(primary_type, cfd_percent, cpp_percent, cfd_topic, cpp_concept):
    """Generate human-readable recommendation"""

    if primary_type == "cfd":
        return (
            f"Content is CFD-focused ({cfd_percent}% CFD vs {cpp_percent}% C++). "
            f"Recommend creating a **CFD lab** for '{cfd_topic}' to implement the theory concepts. "
            f"C++ features will be highlighted as secondary learning points."
        )
    elif primary_type == "cpp":
        concept_name = cpp_concept["name"] if cpp_concept else "C++ feature"
        return (
            f"Content introduces a new C++ concept ({concept_name}). "
            f"Recommend creating a **C++ lab** to learn this language feature using OpenFOAM examples. "
            f"CFD application will provide practical context."
        )
    else:  # both
        return (
            f"Content balances CFD theory ({cfd_percent}%) and C++ concepts ({cpp_percent}%). "
            f"Recommend creating **both labs**: a CFD lab for implementation practice "
            f"and a C++ lab for language mastery. Learners can choose based on their focus."
        )


def load_day_content(day, content_file=None):
    """Load theory content for the given day"""
    if content_file:
        content_path = Path(content_file)
        if content_path.exists():
            with open(content_path, 'r') as f:
                return f.read()
        else:
            print(f"Error: Content file not found: {content_file}", file=sys.stderr)
            return None

    # Auto-detect content file location
    day_str = str(day).zfill(2)
    project_root = Path(__file__).parent.parent.parent

    # Search in phase directories
    for phase_num in range(1, 7):
        phase_dir = project_root / f"daily_learning/Phase_0{phase_num}_*" / f"{day_str}.md"
        matches = list(Path(project_root).glob(f"daily_learning/Phase_*/{day_str}.md"))

        if matches:
            with open(matches[0], 'r') as f:
                return f.read()

    print(f"Warning: Theory content for Day {day_str} not found", file=sys.stderr)
    return None


def main():
    parser = argparse.ArgumentParser(
        description='Auto-detect lab type from day content'
    )
    parser.add_argument('--day', help='Day number (e.g., 01, 02)')
    parser.add_argument('--content-file', help='Path to content file (optional)')
    parser.add_argument('--output', choices=['text', 'json'], default='text',
                        help='Output format')

    args = parser.parse_args()

    # Load content
    day_num = int(args.day) if args.day else None
    content = load_day_content(day_num, args.content_file)

    if content is None:
        # If no content, provide default based on day
        if day_num:
            print(f"Using default detection for Day {day_num}", file=sys.stderr)
            result = {
                "primary_type": "cfd" if day_num <= 12 else "cpp",
                "confidence": 50,
                "cfd_score": 60,
                "cpp_score": 40,
                "cfd_topic": f"Day {day_num} Topic",
                "cpp_concept": None,
                "recommendation": "Default recommendation (content not found)"
            }
        else:
            print("Error: No content available for detection", file=sys.stderr)
            sys.exit(1)
    else:
        result = detect_lab_type(content, day_num)

    # Output result
    if args.output == 'json':
        print(json.dumps(result, indent=2))
    else:
        print(f"\nLab Type Detection Result")
        print(f"{'='*50}")
        print(f"Primary Type:   {result['primary_type'].upper()}")
        print(f"Confidence:     {result['confidence']}%")
        print(f"\nScores:")
        print(f"  CFD:          {result['cfd_score']}%")
        print(f"  C++:          {result['cpp_score']}%")

        if result['cfd_topic']:
            print(f"\nCFD Topic:      {result['cfd_topic']}")

        if result['cpp_concept']:
            print(f"\nC++ Concept:   {result['cpp_concept']['name']}")
            print(f"  Module:       {result['cpp_concept']['module']}")

        print(f"\nRecommendation:")
        print(f"  {result['recommendation']}")

        print(f"\nCommand to create lab:")
        if result['primary_type'] == "both":
            print(f"  /create-lab --day={args.day or 'XX'} --type=cfd")
            print(f"  /create-lab --day={args.day or 'XX'} --type=cpp")
        else:
            print(f"  /create-lab --day={args.day or 'XX'} --type={result['primary_type']}")

        print()


if __name__ == "__main__":
    main()
