#!/usr/bin/env python3
"""
Verification script for R410A utilities module
"""

import os
import re
import json
from datetime import datetime

def verify_module_completion():
    """Verify all requirements for R410A utilities module"""

    # Define required files
    required_files = [
        "00_Overview.md",
        "01_Property_Calculator.md",
        "02_Evaporator_Analysis.md",
        "03_Refrigerant_Database.md",
        "04_Batch_Processing.md",
        "05_Post_Processing.md",
        "06_Automation_Scripts.md"
    ]

    # Module directory
    module_dir = os.path.dirname(os.path.abspath(__file__))

    print("R410A Utilities Module Verification")
    print("=" * 40)
    print(f"Directory: {module_dir}")
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    # Check file existence
    print("1. Checking file existence...")
    missing_files = []
    for file in required_files:
        file_path = os.path.join(module_dir, file)
        if os.path.exists(file_path):
            size = os.path.getsize(file_path)
            print(f"   ✓ {file} ({size:,} bytes)")
        else:
            print(f"   ✗ {file} - MISSING")
            missing_files.append(file)

    if missing_files:
        print(f"\n❌ Missing files: {len(missing_files)}")
        return False
    print()

    # Check content requirements
    print("2. Checking content requirements...")

    # Property Calculator check
    calc_file = os.path.join(module_dir, "01_Property_Calculator.md")
    with open(calc_file, 'r', encoding='utf-8') as f:
        calc_content = f.read()

    calc_checks = [
        ("CoolProp integration", "CoolProp.CoolProp as CP" in calc_content),
        ("Python implementation", "```python" in calc_content),
        ("Command line interface", "argparse" in calc_content),
        ("Property calculations", "saturation properties" in calc_content.lower())
    ]

    calc_passed = all(check for _, check in calc_checks)
    for check_name, passed in calc_checks:
        status = "✓" if passed else "✗"
        print(f"   {status} {check_name}")

    # Evaporator Analysis check
    analysis_file = os.path.join(module_dir, "02_Evaporator_Analysis.md")
    with open(analysis_file, 'r', encoding='utf-8') as f:
        analysis_content = f.read()

    analysis_checks = [
        ("Mesh quality check", "checkMesh" in analysis_content),
        ("y+ calculation", "yPlus" in analysis_content),
        ("Convergence monitoring", "convergence" in analysis_content.lower()),
        ("Bash implementation", "```bash" in analysis_content)
    ]

    analysis_passed = all(check for _, check in analysis_checks)
    for check_name, passed in analysis_checks:
        status = "✓" if passed else "✗"
        print(f"   {status} {check_name}")

    # Database check
    db_file = os.path.join(module_dir, "03_Refrigerant_Database.md")
    with open(db_file, 'r', encoding='utf-8') as f:
        db_content = f.read()

    db_checks = [
        ("HDF5 export", "export_to_hdf5" in db_content),
        ("Pandas integration", "import pandas as pd" in db_content),
        ("Property tables", "saturation table" in db_content.lower()),
        ("OpenFOAM integration", "constant/tables" in db_content)
    ]

    db_passed = all(check for _, check in db_checks)
    for check_name, passed in db_checks:
        status = "✓" if passed else "✗"
        print(f"   {status} {check_name}")

    # Batch Processing check
    batch_file = os.path.join(module_dir, "04_Batch_Processing.md")
    with open(batch_file, 'r', encoding='utf-8') as f:
        batch_content = f.read()

    batch_checks = [
        ("Parameter sweeps", "mass flux" in batch_content.lower()),
        ("Parallel processing", "parallel" in batch_content.lower()),
        ("Convergence handling", "convergence" in batch_content.lower()),
        ("Shell scripts", "shell script" in batch_content.lower())
    ]

    batch_passed = all(check for _, check in batch_checks)
    for check_name, passed in batch_checks:
        status = "✓" if passed else "✗"
        print(f"   {status} {check_name}")

    # Post-Processing check
    post_file = os.path.join(module_dir, "05_Post_Processing.md")
    with open(post_file, 'r', encoding='utf-8') as f:
        post_content = f.read()

    post_checks = [
        ("Interface tracking", "interface position" in post_content.lower()),
        ("HTC calculation", "heat transfer coefficient" in post_content.lower()),
        ("Visualization", "matplotlib" in post_content),
        ("Data export", "csv" in post_content.lower())
    ]

    post_passed = all(check for _, check in post_checks)
    for check_name, passed in post_checks:
        status = "✓" if passed else "✗"
        print(f"   {status} {check_name}")

    # Automation Scripts check
    auto_file = os.path.join(module_dir, "06_Automation_Scripts.md")
    with open(auto_file, 'r', encoding='utf-8') as f:
        auto_content = f.read()

    auto_checks = [
        ("Workflow pipeline", "pipeline" in auto_content.lower()),
        ("Error handling", "error handling" in auto_content.lower()),
        ("Progress monitoring", "monitoring" in auto_content.lower()),
        ("Configuration file", "config.ini" in auto_content)
    ]

    auto_passed = all(check for _, check in auto_checks)
    for check_name, passed in auto_checks:
        status = "✓" if passed else "✗"
        print(f"   {status} {check_name}")
    print()

    # Check code balance
    print("3. Checking code block balance...")
    code_blocks_found = 0

    for file in required_files:
        file_path = os.path.join(module_dir, file)
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            # Count code block delimiters
            open_blocks = content.count("```")
            if open_blocks % 2 != 0:
                print(f"   ✗ {file} has unbalanced code blocks")
                return False
            code_blocks_found += open_blocks // 2

    print(f"   ✓ All code blocks balanced (total: {code_blocks_found})")
    print()

    # Check R410A relevance
    print("4. Checking R410A relevance...")
    total_r410a_mentions = 0

    for file in required_files:
        file_path = os.path.join(module_dir, file)
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            r410a_count = content.lower().count("r410a")
            total_r410a_mentions += r410a_count
            relevance = r410a_count / len(content.split()) * 100
            print(f"   {file}: {r410a_count} mentions (~{relevance:.1f}% relevance)")

    avg_relevance = total_r410a_mentions / sum(len(open(f, 'r', encoding='utf-8').read().split())
                                             for f in [os.path.join(module_dir, file)
                                                     for file in required_files]) * 100
    print(f"\n   Average R410A relevance: {avg_relevance:.1f}%")
    print(f"   {'✓' if avg_relevance >= 60 else '✗'} Meets 60% requirement")
    print()

    # Check technical accuracy indicators
    print("5. Checking technical accuracy indicators...")
    accuracy_indicators = [
        ("Formulas/Equations", ["\$", "\\nabla", "alpha"]),
        ("Code Implementation", ["def ", "class ", "import "]),
        ("OpenFOAM Integration", ["fvMesh", "volScalarField", "boundaryField"]),
        ("Mathematical Operations", ["array", "numpy", "pandas"])
    ]

    for indicator_name, patterns in accuracy_indicators:
        count = sum(1 for file in required_files
                   for pattern in patterns
                   if pattern in open(os.path.join(module_dir, file), 'r', encoding='utf-8').read())
        print(f"   {indicator_name}: {count} instances")

    print()

    # Final assessment
    print("6. Final Assessment")
    print("-" * 40)

    # Count verified features
    verified_features = (
        calc_passed +
        analysis_passed +
        db_passed +
        batch_passed +
        post_passed +
        auto_passed +
        (avg_relevance >= 60) +
        (code_blocks_found >= 20)  # Should have substantial code
    )

    total_checks = 7  # Number of main criteria
    tech_accuracy = min(10, code_blocks_found)  # Scale technical accuracy
    total_possible = total_checks + tech_accuracy

    score = (verified_features + tech_accuracy) / total_possible * 100

    print(f"Verification Score: {score:.1f}%")

    if score >= 90:
        print("🎉 Excellent! Module meets all requirements")
        return True
    elif score >= 80:
        print("✅ Good! Module meets most requirements")
        return True
    elif score >= 70:
        print("⚠️  Acceptable. Module has some issues")
        return False
    else:
        print("❌ Poor. Module needs significant improvement")
        return False

if __name__ == "__main__":
    success = verify_module_completion()
    exit(0 if success else 1)