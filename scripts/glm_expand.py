#!/usr/bin/env python3
"""
GLM Expansion Script
Expands DeepSeek R1 skeleton into full "hardcore" lesson content using GLM 4.7
"""

import argparse
import json
import os
from pathlib import Path

def main():
    parser = argparse.ArgumentParser(description='Expand R1 skeleton using GLM 4.7')
    parser.add_argument('--skeleton', required=True, help='Path to R1 skeleton JSON')
    parser.add_argument('--template', required=True, help='Path to GLM expansion template')
    parser.add_argument('--output', required=True, help='Output path for expanded content')
    args = parser.parse_args()

    # Check API key
    api_key = os.environ.get('ZHIPUAI_API_KEY')
    if not api_key:
        print("ERROR: ZHIPUAI_API_KEY not set")
        print("Please run: export ZHIPUAI_API_KEY='your-api-key'")
        return 1

    # Load skeleton
    print(f"Loading skeleton: {args.skeleton}")
    with open(args.skeleton, 'r', encoding='utf-8') as f:
        skeleton = f.read()

    # Load template
    print(f"Loading template: {args.template}")
    with open(args.template, 'r', encoding='utf-8') as f:
        template = f.read()

    # Import zhipuai
    try:
        from zhipuai import ZhipuAI
    except ImportError:
        print("ERROR: zhipuai not installed")
        print("Please run: pip install zhipuai")
        return 1

    # Create client
    client = ZhipuAI(api_key=api_key)

    # Build prompt
    system_prompt = f"""คุณคือ CFD Professor ที่กำลังเขียน "Hardcore" learning material

**Template Requirements:**
{template}

**Critical Requirements:**
1. ความยาวรวม ≥ 1500 บรรทัด
2. ทุก section ต้องครบตาม template
3. Code snippets ต้องมี syntax highlighting
4. Mermaid diagrams ต้อง valid
5. Bilingual headers (Thai + English)
6. Callouts: WARNING, TIP, INFO, IMPORTANT
7. Implementation code ≥ 300 lines
"""

    user_prompt = f"""Expand this JSON skeleton into a complete lesson:

{skeleton}

**Output:**
Complete Markdown file with ALL sections from the template.
Start with YAML frontmatter and end with Related Days section.
"""

    print("Calling GLM 4.7 API...")
    print("(This may take 2-5 minutes for full content generation)")

    try:
        response = client.chat.completions.create(
            model="glm-4-plus",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            max_tokens=8000,
            temperature=0.7
        )

        content = response.choices[0].message.content

        # Write output
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)

        # Report stats
        line_count = len(content.split('\n'))
        print(f"\n✓ Output written to: {args.output}")
        print(f"✓ Line count: {line_count}")
        
        if line_count < 1500:
            print(f"⚠ WARNING: Content shorter than target (1500 lines)")
            print(f"  Consider re-running with explicit length requirement")

        return 0

    except Exception as e:
        print(f"ERROR: API call failed: {e}")
        return 1


if __name__ == '__main__':
    exit(main())
