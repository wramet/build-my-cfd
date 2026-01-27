#!/usr/bin/env python3
"""
GLM-4.7 API Helper Script for /teach-deep workflow
Now connects directly to Z.ai (no proxy required)
"""

import argparse
import json
import os
import sys
from openai import OpenAI

# Z.ai DIRECT API CONFIGURATION
# Uses Z.ai's OpenAI-compatible endpoint
API_KEY = os.environ.get("ANTHROPIC_API_KEY", "your-zai-api-key")
BASE_URL = "https://open.bigmodel.cn/api/paas/v4"  # Z.ai OpenAI-compatible endpoint

def ask_glm(prompt: str, system: str = None, model: str = "glm-4.7", max_tokens: int = 8192, tools: bool = False) -> str:
    """Send a prompt to the Local Proxy and return the response."""
    
    # Simple Client - No Logic Here!
    # The proxy at port 4000 handles routing based on 'model' name.
    client = OpenAI(api_key=API_KEY, base_url=BASE_URL)
    
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})
    
    # Define available tools
    available_tools = None
    if tools:
        available_tools = [
            {
                "type": "function",
                "function": {
                    "name": "web_search",
                    "description": "Search the web for information using a query",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {"type": "string", "description": "The search query"}
                        },
                        "required": ["query"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "web_reader",
                    "description": "Read content from a URL (zread)",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "url": {"type": "string", "description": "The URL to read"}
                        },
                        "required": ["url"]
                    }
                }
            }
        ]

    try:
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            max_tokens=max_tokens,
            temperature=0.7,
            tools=available_tools if tools else None,
            tool_choice="auto" if tools else None
        )
        
        # Handle simple response
        return response.choices[0].message.content or ""
        
        # Note: A full implementation would need to handle the tool call execution loop,
        # but for this text-based extraction task, we might rely on the model simply 
        # using the capability internally (if the provider supports implicit tool use) 
        # or we might need a more complex loop. 
        # For now, let's keep it simple and see if enabling tools provides better context.
        
    except Exception as e:
        return f"Error: {str(e)}"

def main():
    parser = argparse.ArgumentParser(description="GLM-4.7 API Helper")
    parser.add_argument("prompt", nargs="?", help="Instruction prompt (can combine with stdin)")
    parser.add_argument("-s", "--system", help="System prompt")
    parser.add_argument("-m", "--model", default="glm-4.7", help="Model name")
    parser.add_argument("--max-tokens", type=int, default=8192, help="Max tokens")
    parser.add_argument("--tools", action="store_true", help="Enable web_search and web_reader tools")
    args = parser.parse_args()
    
    # Read stdin if available (non-blocking check)
    stdin_content = ""
    if not sys.stdin.isatty():
        stdin_content = sys.stdin.read()
    
    # Combine: instruction from arg + content from stdin
    if args.prompt and stdin_content:
        # Both provided: instruction + content
        prompt = f"{args.prompt}\n\n---\n\n{stdin_content}"
    elif args.prompt:
        # Only argument
        prompt = args.prompt
    elif stdin_content:
        # Only stdin
        prompt = stdin_content
    else:
        print("Error: No prompt provided (use argument or pipe stdin)", file=sys.stderr)
        sys.exit(1)
    
    if not prompt.strip():
        print("Error: Empty prompt", file=sys.stderr)
        sys.exit(1)
    
    result = ask_glm(prompt, system=args.system, model=args.model, max_tokens=args.max_tokens, tools=args.tools)
    print(result)

if __name__ == "__main__":
    main()
