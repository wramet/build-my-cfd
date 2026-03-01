#!/usr/bin/env python3
"""
heal_seams.py - Intelligent Seam Healing (FIXED)

Detects and performs surgical text replacement at seam points using explicit markers.

Modes:
- TEXT: Prose smoothing (transitions, flow)
- CODE: Conservative syntax-only healing (preserves logic/names)

Usage:
    python3 heal_seams.py <input_file> <output_file>
"""

import sys
import json
import re
import subprocess
from pathlib import Path


class SeamHealer:
    def __init__(self, input_path):
        self.input_path = Path(input_path)
        self.content = ""
        self.lines = []
        self.seam_reports = []

    def read_file(self):
        """Read input file and split into lines"""
        with open(self.input_path, 'r', encoding='utf-8') as f:
            self.content = f.read()
            self.lines = self.content.split('\n')
        return self.content

    def identify_cut_points(self):
        """Find lines containing the explicit marker"""
        cut_points = []
        for i, line in enumerate(self.lines):
            if "<!--SEAM-->" in line:
                cut_points.append({
                    'line_num': i,
                    'type': 'EXPLICIT_MARKER'
                })
        return cut_points

    def extract_surgery_window(self, marker_line_idx, window_size=6):
        """
        Extract a tight window of lines around the marker for 'surgery'.
        We take N lines before and N lines after.
        """
        # Start index (exclusive of marker)
        start_idx = max(0, marker_line_idx - window_size)
        # End index (exclusive of marker)
        end_idx = min(len(self.lines), marker_line_idx + window_size + 1)

        # We grab the text, excluding the marker line itself
        lines_before = self.lines[start_idx:marker_line_idx]
        lines_after = self.lines[marker_line_idx+1:end_idx]

        return {
            'start_idx': start_idx,
            'end_idx': end_idx,
            'text_before': '\n'.join(lines_before),
            'text_after': '\n'.join(lines_after),
            'full_block': lines_before + lines_after
        }

    def detect_seam_mode(self, text_chunk):
        """Check if the chunk contains code patterns"""
        code_indicators = ['{', '}', ';', 'int ', 'void ', 'return ', '```']
        if any(x in text_chunk for x in code_indicators):
            return 'CODE'
        return 'TEXT'

    def build_prompt(self, mode, text_before, text_after):
        """Build appropriate prompt based on seam mode"""
        if mode == 'CODE':
            return f"""
You are fixing a broken code seam.

Here are the lines around the break:
---
{text_before}
[SEAM BREAK]
{text_after}
---

TASK: Join these into valid code.
1. Remove the artificial break.
2. Fix any syntax errors caused by the split (e.g. split variable names).
3. Do not change logic.

Output ONLY the corrected lines of code.
"""
        else:
            return f """
You are a Technical Editor smoothing a transition.

Here are the sentences around the break:
---
{text_before}
[SEAM BREAK]
{text_after}
---

TASK: Rewrite these lines to flow as one continuous paragraph.
1. Remove repetition (e.g. "In the previous section...").
2. Connect the thoughts logically.
3. Preserve all technical variables (U, p, rho).

Output ONLY the corrected paragraph.
"""

    def call_llm(self, prompt):
        """Call DeepSeek for seam healing"""
        script_path = Path(".claude/scripts/deepseek_content.py")
        temp_prompt = Path("/tmp/seam_heal_prompt.txt")
        with open(temp_prompt, 'w') as f:
            f.write(prompt)

        try:
            result = subprocess.run(
                ["python3", str(script_path), "deepseek-chat", str(temp_prompt)],
                capture_output=True,
                text=True,
                timeout=60
            )
            return result.stdout.strip() if result.returncode == 0 else None
        except Exception as e:
            print(f"  Error calling LLM: {e}")
            return None

    def heal_all_seams(self):
        """Heal all seams using line-based surgery"""
        print(f"🔧 Healing: {self.input_path}")
        self.read_file()
        cut_points = self.identify_cut_points()
        print(f"  Found {len(cut_points)} seams.")

        if not cut_points:
            print("  No seams found - content may already be complete")
            return self.content

        # Process in REVERSE order so line replacements don't mess up earlier indices
        for seam in reversed(cut_points):
            idx = seam['line_num']
            window = self.extract_surgery_window(idx, window_size=5)

            mode = self.detect_seam_mode(window['text_before'] + window['text_after'])
            print(f"  - Seam at line {idx} ({mode}): ", end="", flush=True)

            prompt = self.build_prompt(mode, window['text_before'], window['text_after'])
            healed = self.call_llm(prompt)

            if healed:
                print("✅ Healed")
                # SURGERY: Replace the window (including the marker line) with the healed text
                # window['start_idx'] to window['end_idx'] covers the whole area

                # Split healed text back into lines
                healed_lines = healed.split('\n')

                # Slice assignment to replace lines in-place
                self.lines[window['start_idx']:window['end_idx']] = healed_lines

                self.seam_reports.append({'line': idx, 'status': 'fixed', 'mode': mode})
            else:
                print("❌ Failed (keeping original)")
                # Just remove the marker line
                del self.lines[idx]

        # Reconstruct content
        self.content = '\n'.join(self.lines)
        return self.content

    def save(self, output_path):
        """Save healed content"""
        output_path = Path(output_path)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(self.content)
        print(f"✅ Saved to: {output_path}")

        # Save report
        report_path = output_path.with_suffix('.heal_report.json')
        with open(report_path, 'w') as f:
            json.dump({
                'file': str(self.input_path),
                'total_seams': len(self.seam_reports),
                'seams': self.seam_reports
            }, f, indent=2)
        print(f"📊 Healing report: {report_path}")


def main():
    if len(sys.argv) < 3:
        print("Usage: python3 heal_seams.py <input_file> <output_file>")
        print("\nThis script:")
        print("  - Identifies seams by <!--SEAM--> markers")
        print("  - Detects seam type (TEXT vs CODE)")
        print("  - Performs line-based surgery to replace disjointed text")
        print("\nModes:")
        print("  TEXT: Smooth prose transitions")
        print("  CODE: Conservative syntax-only healing")
        sys.exit(1)

    input_path = sys.argv[1]
    output_path = sys.argv[2]

    healer = SeamHealer(input_path)
    healer.heal_all_seams()
    healer.save(output_path)


if __name__ == "__main__":
    main()
