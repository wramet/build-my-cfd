#!/usr/bin/env python3
"""
Audit daily learning files against tiered complexity minimums.
Reports which files need revision before proceeding to Phase 3.
"""

import re
import subprocess
from pathlib import Path
from typing import Dict, Tuple

# Tier minimums from tiered-complexity.md
TIER_MINIMUMS = {
    "T1": 350,
    "T2": 550,
    "T3": 750,
    "T4": 900,
}

# Day to Tier mapping (all 84 days)
DAY_TO_TIER = {
    # Phase 1
    1: "T1", 2: "T1", 3: "T2", 4: "T2", 5: "T2", 6: "T1", 7: "T2", 8: "T1",
    9: "T2", 10: "T3", 11: "T1", 12: "T2", 13: "T4", 14: "T4",
    # Phase 2
    15: "T2", 16: "T2", 17: "T3", 18: "T3", 19: "T2", 20: "T2", 21: "T2",
    22: "T2", 23: "T3", 24: "T2", 25: "T2", 26: "T3", 27: "T4", 28: "T4",
    # Phase 3
    29: "T2", 30: "T2", 31: "T3", 32: "T3", 33: "T2", 34: "T3", 35: "T3",
    36: "T3", 37: "T3", 38: "T2", 39: "T2", 40: "T2", 41: "T4", 42: "T4",
    # Phase 4
    43: "T2", 44: "T2", 45: "T2", 46: "T3", 47: "T2", 48: "T2", 49: "T3",
    50: "T2", 51: "T3", 52: "T3", 53: "T2", 54: "T2", 55: "T4", 56: "T4",
    # Phase 5
    57: "T3", 58: "T3", 59: "T3", 60: "T3", 61: "T3", 62: "T3", 63: "T4", 64: "T4",
    65: "T3", 66: "T3", 67: "T4", 68: "T4", 69: "T4", 70: "T4", 71: "T4", 72: "T4",
    73: "T4", 74: "T4", 75: "T4", 76: "T4", 77: "T3", 78: "T3", 79: "T3", 80: "T3",
    81: "T3", 82: "T3", 83: "T4", 84: "T4",
}

# Topic descriptions for context
TOPICS = {
    1: "Templates & Generic Programming",
    2: "C++20 Concepts & Constraints",
    3: "Mesh-to-Field Relationship",
    4: "CRTP — Static Polymorphism",
    5: "Policy-Based Design",
    6: "Smart Pointers",
    7: "Move Semantics",
    8: "Perfect Forwarding",
    9: "Expression Templates Part 1",
    10: "Expression Templates Part 2",
    11: "C++20 Ranges",
    12: "Type Traits & SFINAE",
    13: "Mini-Project Part 1",
    14: "Mini-Project Part 2",
    15: "LDU Matrix Format",
    16: "LDU Addressing",
    17: "Cache-Friendly LDU Multiply",
    18: "Sparse Matrix Assembly",
    19: "Cache Access Patterns",
    20: "Zero-Copy Views with std::span",
    21: "Flat Arrays & Offsets",
    22: "Modern Hashing",
    23: "Polymorphic Memory Resources (PMR)",
    24: "Mesh Topology Storage",
    25: "Memory Alignment",
    26: "Matrix Boundary Conditions",
    27: "Mini-Project Part 1",
    28: "Mini-Project Part 2",
    29: "Modern CMake Part 1",
    30: "Modern CMake Part 2",
    31: "The Modern Factory Pattern",
    32: "Plugin Self-Registration",
    33: "Configuration I/O — JSON",
    34: "Dynamic Configuration — Factory + JSON",
    35: "The Object Registry",
    36: "Time & State Control",
    37: "Boundary Condition Interface",
    38: "Modern Error Handling",
    39: "Dependency Management — FetchContent",
    40: "Logging — spdlog",
    41: "Mini-Project Part 1",
    42: "Mini-Project Part 2",
    43: "Profiling Workflows",
    44: "Flame Graphs",
    45: "Auto-Vectorization",
    46: "SIMD Intrinsics",
    47: "OpenMP Basics",
    48: "C++17 Parallel Algorithms",
    49: "False Sharing & Reductions",
    50: "Allocation Profiling",
    51: "Eliminating Temporaries",
    52: "Mesh Bandwidth Optimization",
    53: "Parallel I/O Concepts",
    54: "MPI Fundamentals",
    55: "Mini-Project Part 1",
    56: "Mini-Project Part 2",
    # Phase 5
    57: "Project Architecture — CMake Structure Part 1",
    58: "Project Architecture — CMake Structure Part 2",
    59: "1D Mesh Implementation Part 1",
    60: "1D Mesh Implementation Part 2",
    61: "Geometric Fields Part 1",
    62: "Geometric Fields Part 2",
    63: "Equation Assembly — fvMatrix Part 1",
    64: "Equation Assembly — fvMatrix Part 2",
    65: "Temporal Operators — fvm::ddt Part 1",
    66: "Temporal Operators — fvm::ddt Part 2",
    67: "Spatial Operators — div and laplacian Part 1",
    68: "Spatial Operators — div and laplacian Part 2",
    69: "Linear Solver Integration — PCG Part 1",
    70: "Linear Solver Integration — PCG Part 2",
    71: "SIMPLE Loop — Pressure-Velocity Part 1",
    72: "SIMPLE Loop — Pressure-Velocity Part 2",
    73: "Rhie-Chow Interpolation Part 1",
    74: "Rhie-Chow Interpolation Part 2",
    75: "Scalar Transport & Flux Limiters Part 1",
    76: "Scalar Transport & Flux Limiters Part 2",
    77: "Boundedness Testing — VOF alpha Part 1",
    78: "Boundedness Testing — VOF alpha Part 2",
    79: "Factory-Driven Source Terms Part 1",
    80: "Factory-Driven Source Terms Part 2",
    81: "VTK Output — ParaView Part 1",
    82: "VTK Output — ParaView Part 2",
    83: "Final Benchmark and Retrospective Part 1",
    84: "Final Benchmark and Retrospective Part 2",
}

# Phase directories
PHASE_DIRS = {
    (1, 14): "Phase_01_CppThroughOpenFOAM",
    (15, 28): "Phase_02_DataStructures_Memory",
    (29, 42): "Phase_03_SoftwareArchitecture",
    (43, 56): "Phase_04_PerformanceOptimization",
    (57, 84): "Phase_05_FocusedCFDComponent",
}


def get_file_path(day: int) -> Path:
    """Get the expected file path for a given day."""
    for (start, end), dirname in PHASE_DIRS.items():
        if start <= day <= end:
            return Path(f"daily_learning/{dirname}/{day:02d}.md")
    return None


def get_line_count(file_path: Path) -> int:
    """Get line count of a file."""
    if not file_path.exists():
        return 0
    result = subprocess.run(["wc", "-l", str(file_path)],
                          capture_output=True, text=True)
    return int(result.stdout.split()[0])


def audit_file(day: int) -> Dict:
    """Audit a single file against its tier requirements."""
    file_path = get_file_path(day)

    if not file_path or not file_path.exists():
        return {
            "day": day,
            "topic": TOPICS.get(day, "Unknown"),
            "tier": DAY_TO_TIER.get(day, "Unknown"),
            "exists": False,
            "lines": 0,
            "minimum": TIER_MINIMUMS.get(DAY_TO_TIER.get(day, "T1"), 0),
            "status": "missing",
        }

    lines = get_line_count(file_path)
    tier = DAY_TO_TIER.get(day, "T1")
    minimum = TIER_MINIMUMS[tier]

    if lines >= minimum:
        status = "✅ PASS"
    else:
        shortage = minimum - lines
        if shortage > 200:
            status = f"❌ FAIL (-{shortage} lines)"
        else:
            status = f"⚠️  WARN (-{shortage} lines)"

    return {
        "day": day,
        "topic": TOPICS.get(day, "Unknown"),
        "tier": tier,
        "exists": True,
        "lines": lines,
        "minimum": minimum,
        "status": status,
        "file": str(file_path),
    }


def main():
    """Run the audit and print a report."""
    base_path = Path.cwd()

    print(f"📊 Tiered Complexity Audit")
    print(f"Base: {base_path}")
    print(f"Standard: .claude/rules/tiered-complexity.md")
    print()

    results = []
    failing = []
    warning = []

    for day in range(1, 85):  # Days 1-84
        result = audit_file(day)
        results.append(result)

        if "FAIL" in result["status"]:
            failing.append(result)
        elif "WARN" in result["status"]:
            warning.append(result)

    # Summary
    print(f"## Summary")
    print(f"Total files checked: {len(results)}")
    print(f"✅ Passing: {len([r for r in results if 'PASS' in r['status']])}")
    print(f"⚠️  Warnings: {len(warning)}")
    print(f"❌ Failing: {len(failing)}")
    print()

    # Failing files (priority revision)
    if failing:
        print(f"## ❌ FAILING FILES (Require Revision)")
        print(f"| Day | Topic | Tier | Lines | Min | Shortage |")
        print(f"-----|-------|------|-------|-----|----------|")
        for r in sorted(failing, key=lambda x: x["lines"]):
            shortage = r["minimum"] - r["lines"]
            print(f"| {r['day']:02d} | {r['topic']} | {r['tier']} | {r['lines']} | {r['minimum']} | -{shortage} |")
        print()

    # Warning files (optional revision)
    if warning:
        print(f"## ⚠️  WARNING FILES (Minor Gaps)")
        print(f"| Day | Topic | Tier | Lines | Min | Shortage |")
        print(f"-----|-------|------|-------|-----|----------|")
        for r in sorted(warning, key=lambda x: x["lines"]):
            shortage = r["minimum"] - r["lines"]
            print(f"| {r['day']:02d} | {r['topic']} | {r['tier']} | {r['lines']} | {r['minimum']} | -{shortage} |")
        print()

    # Priority revision order (most severe first)
    if failing or warning:
        print(f"## 📋 Priority Revision Order")
        all_needing_revision = sorted(failing + warning, key=lambda x: x["lines"])
        for i, r in enumerate(all_needing_revision, 1):
            shortage = r["minimum"] - r["lines"]
            print(f"{i}. Day {r['day']:02d}: {r['topic']} ({r['tier']}, {r['lines']} lines, need -{shortage})")
        print()

    # Phase breakdown
    print(f"## 📁 Phase Breakdown")
    phases = [
        (1, 14, "Phase 1: Modern C++ Foundation"),
        (15, 28, "Phase 2: Data Structures & Memory"),
        (29, 42, "Phase 3: Architecture & Build Systems"),
        (43, 56, "Phase 4: Performance Optimization"),
        (57, 84, "Phase 5: VOF-Ready CFD Component"),
    ]

    for start, end, name in phases:
        phase_results = [r for r in results if start <= r["day"] <= end]
        passing = len([r for r in phase_results if "PASS" in r["status"]])
        total = len(phase_results)
        print(f"{name}: {passing}/{total} passing")

        # Show any issues in this phase
        issues = [r for r in phase_results if "PASS" not in r["status"]]
        if issues:
            for r in issues:
                shortage = r["minimum"] - r["lines"]
                print(f"  ⚠️  Day {r['day']:02d}: {r['topic']} ({r['lines']}/{r['minimum']}, -{shortage})")
        print()

    return 0 if not failing else 1


if __name__ == "__main__":
    exit(main())
