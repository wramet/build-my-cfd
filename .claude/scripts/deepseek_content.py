#!/usr/bin/env python3
"""
Direct DeepSeek API Integration (Option 3)
Calls DeepSeek API directly when model switching via environment doesn't work
"""

import os
import json
import sys
import requests
from pathlib import Path

# DeepSeek API Configuration
DEEPSEEK_API_KEY = "sk-a8d183f6f9904326913cb4e799eaba17"
DEEPSEEK_BASE_URL = "https://api.deepseek.com/v1"

def call_deepseek_chat(messages, max_tokens=8192, temperature=0.7):
    """
    Call DeepSeek Chat V3 API directly
    """
    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "deepseek-chat",
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": temperature
    }

    response = requests.post(
        f"{DEEPSEEK_BASE_URL}/chat/completions",
        headers=headers,
        json=payload,
        timeout=120
    )

    response.raise_for_status()
    return response.json()

def validate_content(content):
    """
    Validate generated content meets structural quality requirements.

    Returns: (is_valid, issues_list)
    """
    issues = []
    lines = content.split('\n')

    # Check 1: No debug pollution
    first_line = lines[0].strip() if lines else ""
    if first_line.startswith("Calling") or first_line.startswith("Error:") or first_line.startswith("Usage:"):
        issues.append(f"Debug pollution detected: '{first_line}'")

    # Check 2: Starts with header
    if not first_line.startswith("# Day") and not first_line.startswith("# "):
        issues.append(f"Invalid first line (should start with '# Day'): '{first_line[:50]}'")

    # Check 3: Has required sections
    required_sections = ["## Appendix: Complete File Listings"]
    for section in required_sections:
        if section not in content:
            issues.append(f"Missing required section: {section}")

    # Check 4: Warn if suspiciously short (but don't fail)
    if len(lines) < 300:
        issues.append(f"Warning: Content seems short ({len(lines)} lines) - verify completeness")

    return len(issues) == 0, issues


def clean_content(content):
    """
    Remove common debug artifacts from content.
    """
    lines = content.split('\n')
    cleaned = []

    skip_patterns = [
        "Calling ",
        "Usage:",
        "Error:",
        "Models:",
    ]

    for line in lines:
        # Skip lines that match debug patterns at the start
        is_debug = False
        for pattern in skip_patterns:
            if line.strip().startswith(pattern):
                is_debug = True
                break
        if not is_debug:
            cleaned.append(line)

    return '\n'.join(cleaned)


def call_deepseek_reasoner(messages, max_tokens=8192, temperature=0.7):
    """
    Call DeepSeek R1 (reasoner) API directly
    """
    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "deepseek-reasoner",
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": temperature
    }

    response = requests.post(
        f"{DEEPSEEK_BASE_URL}/chat/completions",
        headers=headers,
        json=payload,
        timeout=120
    )

    response.raise_for_status()
    return response.json()


def main():
    """Main entry point for direct DeepSeek calls"""
    if len(sys.argv) < 3:
        print("Usage: python3 deepseek_content.py <model> <prompt_file>")
        print("Models: deepseek-chat, deepseek-reasoner")
        sys.exit(1)

    model = sys.argv[1]
    prompt_file = sys.argv[2]

    if not Path(prompt_file).exists():
        print(f"Error: Prompt file not found: {prompt_file}")
        sys.exit(1)

    # Read prompt
    with open(prompt_file, 'r') as f:
        prompt_text = f.read()

    messages = [{"role": "user", "content": prompt_text}]

    try:
        # Removed debug output to prevent pollution in content files

        if model == "deepseek-chat":
            response = call_deepseek_chat(messages)
        elif model == "deepseek-reasoner":
            response = call_deepseek_reasoner(messages)
        else:
            print(f"Error: Unknown model: {model}", file=sys.stderr)
            sys.exit(1)

        # Get and clean content
        if "choices" in response and len(response["choices"]) > 0:
            raw_content = response["choices"][0]["message"]["content"]

            # Clean any debug artifacts
            content = clean_content(raw_content)

            # For content generation (deepseek-chat), validate quality
            if model == "deepseek-chat":
                is_valid, issues = validate_content(content)
                if not is_valid:
                    print("Content validation failed:", file=sys.stderr)
                    for issue in issues:
                        print(f"  - {issue}", file=sys.stderr)
                    # Still output content, but warn user
                    print("⚠️  WARNING: Content quality issues detected (see stderr above)", file=sys.stderr)

            print(content)
        else:
            print("Error: No response content", file=sys.stderr)
            print(json.dumps(response, indent=2), file=sys.stderr)
            sys.exit(1)

    except requests.exceptions.RequestException as e:
        print(f"API Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
