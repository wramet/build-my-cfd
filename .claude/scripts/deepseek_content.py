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
        print(f"Calling {model}...", file=sys.stderr)

        if model == "deepseek-chat":
            response = call_deepseek_chat(messages)
        elif model == "deepseek-reasoner":
            response = call_deepseek_reasoner(messages)
        else:
            print(f"Error: Unknown model: {model}", file=sys.stderr)
            sys.exit(1)

        # Print response
        if "choices" in response and len(response["choices"]) > 0:
            print(response["choices"][0]["message"]["content"])
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
