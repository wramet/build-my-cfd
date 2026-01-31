#!/usr/bin/env python3
# R410A Test Suite Runner
# Author: CFD Engine Development Team
# Date: 2026-01-28

import os
import sys
import subprocess
import json
import pandas as pd
from datetime import datetime

class R410ATestSuite:
    def __init__(self):
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.test_cases = [
            '01_Single_Phase_Flow',
            '02_Two_Phase_Flow',
            '03_Evaporator_Case',
            '04_Property_Verification',
            '05_Phase_Change_Model'
        ]
        self.results = {}
        self.start_time = datetime.now()

    def run_all_tests(self):
        """Run all test cases in the suite"""
        print("="*60)
        print("R410A Test Suite Runner")
        print("="*60)
        print(f"Starting at: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print()

        # Check if we're in the correct directory
        if not os.path.exists('README.md'):
            print("ERROR: Please run this script from the 06_R410A_BENCHMARKS directory")
            return False

        # Run each test case
        for test_case in self.test_cases:
            print(f"Running {test_case}...")
            print("-" * 40)

            # Check if test file exists
            test_file = f"{self.base_dir}/{test_case}.md"
            if not os.path.exists(test_file):
                print(f"ERROR: Test file {test_case}.md not found")
                self.results[test_case] = {'status': 'FAILED', 'error': 'File not found'}
                continue

            # Extract test script (if exists)
            test_script = self.extract_test_script(test_file)

            if test_script:
                # Run test script
                result = self.run_test_script(test_script, test_case)
                self.results[test_case] = result
            else:
                # Validate markdown content
                result = self.validate_markdown(test_file)
                self.results[test_case] = result

            print()

        # Generate final report
        self.generate_report()

        return True

    def extract_test_script(self, markdown_file):
        """Extract test script from markdown file"""
        try:
            with open(markdown_file, 'r') as f:
                content = f.read()

            # Look for python script block
            start_marker = "```python"
            end_marker = "```"

            if start_marker in content:
                start_idx = content.find(start_marker) + len(start_marker)
                end_idx = content.find(end_marker, start_idx)

                if end_idx > start_idx:
                    script_content = content[start_idx:end_idx].strip()
                    script_path = f"{self.base_dir}/{markdown_file.stem}_script.py"

                    # Write script to file
                    with open(script_path, 'w') as f:
                        f.write(script_content)

                    return script_path
        except Exception as e:
            print(f"Error extracting script: {e}")

        return None

    def run_test_script(self, script_path, test_case):
        """Run the extracted test script"""
        try:
            # Change to test directory
            original_dir = os.getcwd()
            os.chdir(self.base_dir)

            # Run script
            result = subprocess.run([sys.executable, script_path],
                                 capture_output=True, text=True, timeout=300)

            # Check result
            if result.returncode == 0:
                status = 'PASSED'
                details = result.stdout
            else:
                status = 'FAILED'
                details = result.stderr

            return {
                'status': status,
                'output': details,
                'returncode': result.returncode,
                'duration': 0  # Will be set later
            }

        except subprocess.TimeoutExpired:
            return {
                'status': 'TIMEOUT',
                'output': 'Test timed out after 5 minutes',
                'returncode': -1,
                'duration': 300
            }
        except Exception as e:
            return {
                'status': 'ERROR',
                'output': str(e),
                'returncode': -1,
                'duration': 0
            }
        finally:
            os.chdir(original_dir)

    def validate_markdown(self, markdown_file):
        """Validate markdown content without running scripts"""
        checks = {
            'has_headers': False,
            'has_formulas': False,
            'has_code_blocks': False,
            'has_tables': False,
            'has_references': False,
            'word_count': 0,
            'line_count': 0
        }

        try:
            with open(markdown_file, 'r') as f:
                content = f.read()
                lines = content.split('\n')

                checks['line_count'] = len(lines)
                checks['word_count'] = len(content.split())

                # Check for required sections
                checks['has_headers'] = '##' in content
                checks['has_formulas'] = '$$' in content or '$' in content
                checks['has_code_blocks'] = '```' in content
                checks['has_tables'] = '|' in content
                checks['has_references'] = 'References:' in content

            # Determine status based on checks
            if all(checks.values()[:-2]):  # Exclude word_count and line_count
                status = 'VALIDATED'
                details = f"Content check passed: {checks}"
            else:
                status = 'INCOMPLETE'
                details = f"Missing content: {checks}"

            return {
                'status': status,
                'details': details,
                'checks': checks
            }

        except Exception as e:
            return {
                'status': 'ERROR',
                'output': str(e)
            }

    def generate_report(self):
        """Generate comprehensive test report"""
        end_time = datetime.now()
        duration = end_time - self.start_time

        # Create results directory
        results_dir = f"{self.base_dir}/results"
        os.makedirs(results_dir, exist_ok=True)

        # Generate markdown report
        report_md = f"""# R410A Test Suite Validation Report

**Generated:** {end_time.strftime('%Y-%m-%d %H:%M:%S')}
**Duration:** {duration.total_seconds():.1f} seconds
**Total Tests:** {len(self.test_cases)}

## Test Results Summary

| Test Case | Status | Details |
|-----------|--------|---------|
"""

        passed = 0
        for test_case, result in self.results.items():
            status = result.get('status', 'UNKNOWN')
            details = result.get('details', 'No details')

            if status in ['PASSED', 'VALIDATED']:
                passed += 1

            report_md += f"| {test_case} | {status} | {details[:50]}... |\n"

        report_md += f"\n## Summary\n"
        report_md += f"- **Passed:** {passed}/{len(self.test_cases)}\n"
        report_md += f"- **Failed:** {len(self.test_cases) - passed}\n"
        report_md += f"- **Success Rate:** {passed/len(self.test_cases)*100:.1f}%\n"

        if passed == len(self.test_cases):
            report_md += "\n✅ **All tests passed!**\n"
        else:
            report_md += "\n❌ **Some tests failed.** Please review results.\n"

        # Save report
        report_path = f"{results_dir}/validation_report.md"
        with open(report_path, 'w') as f:
            f.write(report_md)

        print(report_md)
        print(f"\nReport saved to: {report_path}")

        # Save JSON results
        json_path = f"{results_dir}/results.json"
        with open(json_path, 'w') as f:
            json.dump(self.results, f, indent=2)

        print(f"Results saved to: {json_path}")

        # Save CSV summary
        df = pd.DataFrame([(k, v.get('status', 'UNKNOWN'))
                          for k, v in self.results.items()],
                         columns=['Test Case', 'Status'])
        df.to_csv(f"{results_dir}/summary.csv", index=False)

        print(f"Summary saved to: {results_dir}/summary.csv")

def main():
    """Main function to run the test suite"""
    suite = R410ATestSuite()
    success = suite.run_all_tests()

    if success:
        print("\n✅ Test suite completed successfully!")
    else:
        print("\n❌ Test suite failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()