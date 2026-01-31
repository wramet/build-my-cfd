#!/usr/bin/env python3
# Quick R410A Test Suite Checker
# Author: CFD Engine Development Team
# Date: 2026-01-28

import os

def check_file_structure():
    """Check if all required files exist"""
    required_files = [
        '01_Single_Phase_Flow.md',
        '02_Two_Phase_Flow.md',
        '03_Evaporator_Case.md',
        '04_Property_Verification.md',
        '05_Phase_Change_Model.md',
        'README.md',
        'run_validation_suite.py',
        'run_r410a_validation.sh'
    ]

    missing_files = []

    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)

    return missing_files

def validate_markdown_content(file_path):
    """Basic markdown validation"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Check for required elements
        checks = {
            'has_headers': '##' in content,
            'has_formulas': '$$' in content,
            'has_code_blocks': '```' in content,
            'has_tables': '|' in content,
            'has_references': 'References:' in content,
            'has_source_first': 'Source-First' in content,
            'word_count': len(content.split())
        }

        return checks
    except Exception as e:
        return {'error': str(e)}

def main():
    print("Quick R410A Test Suite Checker")
    print("=" * 40)

    # Check file structure
    print("\n1. Checking file structure...")
    missing = check_file_structure()

    if missing:
        print("❌ Missing files:")
        for file in missing:
            print(f"   - {file}")
        return False
    else:
        print("✅ All required files present")

    # Validate markdown content
    print("\n2. Validating markdown content...")
    md_files = [f for f in os.listdir('.') if f.endswith('.md') and f != 'README.md']

    for md_file in md_files:
        print(f"\nValidating {md_file}...")
        checks = validate_markdown_content(md_file)

        if 'error' in checks:
            print(f"❌ Error: {checks['error']}")
        else:
            status = []
            for check, passed in checks.items():
                if isinstance(passed, bool):
                    status.append(f"{check}: {'✅' if passed else '❌'}")

            print(" ".join(status))
            print(f"   Word count: {checks['word_count']}")

    # Check scripts
    print("\n3. Checking scripts...")
    scripts = ['run_validation_suite.py', 'run_r410a_validation.sh']

    for script in scripts:
        if os.path.exists(script):
            print(f"✅ {script} exists")

            # Check if shell script is executable
            if script.endswith('.sh'):
                if os.access(script, os.X_OK):
                    print(f"   ✅ Executable")
                else:
                    print(f"   ❌ Not executable")
        else:
            print(f"❌ {script} missing")

    print("\n" + "=" * 40)
    print("Quick check complete!")
    print("For full validation, run: ./run_r410a_validation.sh")

if __name__ == "__main__":
    main()