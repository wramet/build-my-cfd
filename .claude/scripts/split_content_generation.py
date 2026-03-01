#!/usr/bin/env python3
"""
split_content_generation.py - Context-Aware Split Content Generation

Generates long-form content in 6 parts with context chaining to ensure
seamless integration. Each part receives:
- Global glossary (constants)
- Summary of previous parts
- Last paragraph of previous part
- State carryover (hanging code blocks)

Usage:
    python3 split_content_generation.py <day> <topic> <output_dir>
"""

import os
import sys
import json
import subprocess
from pathlib import Path

# Global constants injected into EVERY prompt
GLOBAL_CONSTANTS = """
=== GLOBAL GLOSSARY (INJECT INTO EVERY PROMPT) ===
PROJECT: R410A Evaporator CFD Engine
DAY: 01 - Governing Equations

NOTATION:
  - U = velocity vector (m/s)
  - v = velocity vector alternative (m/s)
  - p = pressure (Pa)
  - ρ = density (kg/m³) [rho]
  - μ = dynamic viscosity (Pa·s) [mu]
  - ν = kinematic viscosity (m²/s) [nu]
  - T = temperature (K)
  - h = specific enthalpy (J/kg)
  - α = volume fraction OR thermal diffusivity
  - ∇· = divergence operator
  - ∇² = Laplacian operator
  - ∂/∂t = partial time derivative

CODE STYLE: OpenFOAM conventions
  - volScalarField, volVectorField (GeometricField)
  - fvm:: for implicit operators (matrix assembly)
  - fvc:: for explicit operators (field calculations)
  - fvMatrix<Type> for equation matrices

VERIFIED FACTS: Preserve all ⭐ markers
  - ⭐ = Verified from source code
  - ⚠️ = From documentation, needs verification

CRITICAL FOR R410A:
  - Expansion term: ∇·U = ṁ(1/ρ_v - 1/ρ_l)
  - Density ratio: ~20:1 at evaporation conditions
  - Latent heat: S_h = ṁh_fg

OUTPUT FORMAT:
  - English ONLY (no Thai translation)
  - $$ for display math, $ for inline math
  - Mermaid diagrams with quoted node text
  - Code blocks with language tags (cpp, python, bash, mermaid)
==========================================
"""


class SplitContentGenerator:
    def __init__(self, day_num, topic, output_dir):
        self.day_num = day_num
        self.topic = topic
        self.output_dir = Path(output_dir)
        self.parts_dir = self.output_dir / "parts"
        self.parts_dir.mkdir(parents=True, exist_ok=True)

        # Part definitions based on blueprint (Mathematician template)
        self.parts = [
            {
                "id": 1,
                "title": "Part 1: Core Theory - Conservation Laws Foundation",
                "ratio": 0.30,
                "target_lines": 570,
                "sections": [
                    "The Three Pillars of Fluid Dynamics",
                    "Mathematical Operators: Nabla (∇)",
                    "Tensor Notation Primer"
                ]
            },
            {
                "id": 2,
                "title": "Part 2: Physical Challenge - Two-Phase Complexity",
                "ratio": 0.20,
                "target_lines": 380,
                "sections": [
                    "Why Standard Equations Fail for Phase Change",
                    "The Expansion Term: ∇·U = ṁ(1/ρ_v - 1/ρ_l)",
                    "R410A Density Ratio Impact"
                ]
            },
            {
                "id": 3,
                "title": "Part 3: Architecture & Implementation - OpenFOAM Framework",
                "ratio": 0.35,
                "target_lines": 665,
                "sections": [
                    "Field Classes: volScalarField and volVectorField",
                    "fvMatrix: Equation Assembly",
                    "Operators: fvm vs fvc",
                    "Pressure-Velocity Coupling Preview"
                ]
            },
            {
                "id": 4,
                "title": "Part 4: Quality Assurance - Concept Checks",
                "ratio": 0.15,
                "target_lines": 285,
                "sections": [
                    "Exercises",
                    "Detailed Solutions"
                ]
            }
        ]

        # Track context between parts
        self.context_chain = []

    def read_ground_truth(self):
        """Read verified facts JSON"""
        gt_path = Path(f"/tmp/verified_facts_day{self.day_num:02d}.json")
        if not gt_path.exists():
            raise FileNotFoundError(f"Ground truth not found: {gt_path}")
        with open(gt_path, 'r') as f:
            return json.load(f)

    def read_skeleton(self):
        """Read skeleton JSON"""
        skel_path = Path(f"daily_learning/skeletons/day{self.day_num:02d}_skeleton.json")
        if not skel_path.exists():
            raise FileNotFoundError(f"Skeleton not found: {skel_path}")
        with open(skel_path, 'r') as f:
            return json.load(f)

    def read_blueprint(self):
        """Read blueprint JSON"""
        bp_path = Path(f"daily_learning/blueprints/day{self.day_num:02d}_blueprint.json")
        if not bp_path.exists():
            raise FileNotFoundError(f"Blueprint not found: {bp_path}")
        with open(bp_path, 'r') as f:
            return json.load(f)

    def detect_hanging_state(self, content):
        """Detect if content ends with unclosed code block"""
        lines = content.split('\n')

        # Count backticks - odd number means we're inside a code block
        backtick_count = content.count('```')
        in_code_block = (backtick_count % 2 != 0)

        # Check for incomplete code patterns
        incomplete_patterns = [
            ('{', '}'),  # Unclosed brace
            ('(', ')'),  # Unclosed paren
            ('[', ']'),  # Unclosed bracket
        ]

        last_lines = '\n'.join(lines[-10:])
        for open_char, close_char in incomplete_patterns:
            if last_lines.count(open_char) > last_lines.count(close_char):
                return f"IN_CODE_{open_char}"

        return "IN_CODE_BLOCK" if in_code_block else "NORMAL"

    def build_part_prompt(self, part_num, part_info, previous_content=None):
        """Build prompt for a specific part with full context"""

        # Start with global constants
        prompt_parts = [GLOBAL_CONSTANTS]

        # Add context from previous parts
        if self.context_chain:
            prompt_parts.append("\n=== PREVIOUS PARTS SUMMARY ===\n")
            for i, ctx in enumerate(self.context_chain, 1):
                prompt_parts.append(f"Part {i} ({ctx['title']}):\n")
                prompt_parts.append(f"  Summary: {ctx['summary']}\n")
                prompt_parts.append(f"  Key Topics: {', '.join(ctx['topics'])}\n")

        # Add last paragraph of previous part for continuity
        if previous_content:
            state = self.detect_hanging_state(previous_content)
            prompt_parts.append(f"\n=== STATE CARRYOVER ===\n")
            prompt_parts.append(f"Current State: {state}\n")

            if state.startswith("IN_CODE"):
                prompt_parts.append("⚠️ YOU ARE INSIDE AN OPEN CODE BLOCK.\n")
                prompt_parts.append("Continue code immediately. Do NOT add opening ```.\n")

            # Get last few lines for context
            lines = previous_content.split('\n')
            last_paragraph = '\n'.join(lines[-10:])
            prompt_parts.append(f"\nLast paragraph of Part {part_num-1}:\n{last_paragraph}\n")

        # Add current part requirements
        prompt_parts.append(f"\n=== YOUR PART: {part_info['title']} ===\n")
        prompt_parts.append(f"You are generating Part {part_num} of 4\n")
        prompt_parts.append(f"Target length: ~{part_info['target_lines']} lines\n")
        prompt_parts.append(f"Sections to cover:\n")
        for section in part_info['sections']:
            prompt_parts.append(f"  - {section}\n")

        prompt_parts.append("\nREQUIREMENTS:\n")
        prompt_parts.append("- Continue seamlessly from previous part\n")
        prompt_parts.append("- Use consistent notation with previous parts\n")
        prompt_parts.append("- Output ONLY your part content (no reintroduction)\n")
        prompt_parts.append("- Preserve all ⭐ verified facts\n")
        prompt_parts.append("- Use $$ for display math, $ for inline math\n")
        prompt_parts.append("- Mermaid diagrams with quoted node text\n")
        prompt_parts.append("- Code blocks with language tags\n")

        # Add full skeleton and blueprint for reference
        prompt_parts.append("\n=== REFERENCE MATERIAL ===\n")
        prompt_parts.append("SKELETON:\n" + json.dumps(self.read_skeleton(), indent=2) + "\n\n")
        prompt_parts.append("BLUEPRINT:\n" + json.dumps(self.read_blueprint(), indent=2) + "\n\n")
        prompt_parts.append("GROUND TRUTH:\n" + json.dumps(self.read_ground_truth(), indent=2) + "\n\n")

        prompt_parts.append("\nGenerate your part now:\n")

        return ''.join(prompt_parts)

    def call_deepseek(self, prompt, model="deepseek-chat"):
        """Call DeepSeek API"""
        script_path = Path(".claude/scripts/deepseek_content.py")

        # Write prompt to temp file
        temp_prompt = Path("/tmp/part_prompt.txt")
        with open(temp_prompt, 'w') as f:
            f.write(prompt)

        # Call DeepSeek
        result = subprocess.run(
            ["python3", str(script_path), model, str(temp_prompt)],
            capture_output=True,
            text=True,
            timeout=300
        )

        if result.returncode != 0:
            raise RuntimeError(f"DeepSeek API call failed: {result.stderr}")

        return result.stdout

    def generate_part(self, part_num, part_info, previous_content=None):
        """Generate a single part"""
        print(f"\n🔄 Generating Part {part_num}: {part_info['title']}")

        # Build prompt with context
        prompt = self.build_part_prompt(part_num, part_info, previous_content)

        # Call DeepSeek
        content = self.call_deepseek(prompt)

        # Save to file
        part_file = self.parts_dir / f"part_{part_num}.md"
        with open(part_file, 'w') as f:
            f.write(content)

        line_count = len(content.split('\n'))
        print(f"✅ Part {part_num} complete: {line_count} lines")

        # Extract summary for next part
        summary = self.extract_summary(content)

        return content, summary

    def extract_summary(self, content):
        """Extract brief summary from generated content"""
        lines = content.split('\n')

        # Look for key headers
        topics = []
        for line in lines:
            if line.startswith('###') or line.startswith('##'):
                # Remove markdown and clean
                topic = line.lstrip('#').strip()
                if topic and len(topics) < 5:
                    topics.append(topic)

        # Get first paragraph as description
        first_para = []
        for line in lines:
            stripped = line.strip()
            if stripped and not stripped.startswith('#'):
                first_para.append(stripped)
            if len(first_para) >= 3:
                break

        return {
            'title': topics[0] if topics else "Unknown",
            'topics': topics[:3],
            'summary': ' '.join(first_para)[:200]
        }

    def generate_all(self):
        """Generate all parts with context chaining"""
        print(f"\n🚀 Starting split content generation for Day {self.day_num}")
        print(f"Topic: {self.topic}")
        print(f"Output: {self.parts_dir}")

        previous_content = None

        for part_info in self.parts:
            content, summary = self.generate_part(
                part_info['id'],
                part_info,
                previous_content
            )

            # Add to context chain
            self.context_chain.append(summary)
            previous_content = content

        print(f"\n✅ All parts generated!")
        print(f"Parts directory: {self.parts_dir}")

        # Generate merge script
        self.create_merge_script()

    def create_merge_script(self):
        """Create a script to merge all parts with SEAM MARKERS"""
        merge_script = self.parts_dir / "merge.sh"
        with open(merge_script, 'w') as f:
            f.write("#!/bin/bash\n")
            f.write("# Merge all parts with invisible seam markers\n\n")
            f.write(f"OUTPUT=\"daily_learning/Phase_01_Foundation_Theory/{self.day_num:02d}.md\"\n")
            f.write("rm -f $OUTPUT\n\n")

            # Loop through parts and append with marker
            for i, p in enumerate(self.parts):
                filename = f"part_{p['id']}.md"
                f.write(f"cat {filename} >> $OUTPUT\n")
                # Add marker between parts (but not after the last one)
                if i < len(self.parts) - 1:
                    f.write(f"echo \"<!--SEAM-->\" >> $OUTPUT\n")
                    f.write(f"echo \"\" >> $OUTPUT\n")
                    f.write(f"echo \"\" >> $OUTPUT\n")

            f.write("\necho \"✅ Merged with seam markers to: $OUTPUT\"\n")
            f.write("wc -l $OUTPUT\n")

        os.chmod(merge_script, 0o755)
        print(f"\n📝 Merge script created: {merge_script}")


def main():
    if len(sys.argv) < 4:
        print("Usage: python3 split_content_generation.py <day> <topic> <output_dir>")
        print("Example: python3 split_content_generation.py 01 'Governing Equations' daily_learning")
        sys.exit(1)

    day_num = int(sys.argv[1])
    topic = sys.argv[2]
    output_dir = sys.argv[3]

    generator = SplitContentGenerator(day_num, topic, output_dir)
    generator.generate_all()


if __name__ == "__main__":
    main()
