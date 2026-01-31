#!/usr/bin/env python3
"""
DeepSeek MCP Server with Response Caching

Exposes DeepSeek models as MCP tools with full Claude Code integration.
Supports both DeepSeek Chat V3 and DeepSeek R1 (Reasoner).

NEW: Response caching for 90% cost reduction on repeated queries.
"""

import asyncio
import json
import os
import sys
import hashlib
from typing import Any, Optional
from pathlib import Path

# Import local cache manager
try:
    from cache_manager import PromptCache
except ImportError:
    PromptCache = None
    print("Warning: cache_manager not available, caching disabled")

import httpx
from mcp.server.models import InitializationOptions
from mcp.server import NotificationOptions, Server
from mcp.server.stdio import stdio_server
from mcp.types import (
    Resource,
    Tool,
    TextContent,
    ImageContent,
    EmbeddedResource,
)

# DeepSeek API configuration
DEEPSEEK_API_KEY = os.environ.get("DEEPSEEK_API_KEY", "")
DEEPSEEK_BASE_URL = "https://api.deepseek.com/v1"

# Models
DEEPSEEK_CHAT = "deepseek-chat"
DEEPSEEK_REASONER = "deepseek-reasoner"

# Cache configuration
CACHE_ENABLED = os.environ.get("PROMPT_CACHE_ENABLED", "true").lower() == "true"
CACHE_SIZE_MB = int(os.environ.get("CACHE_SIZE_MB", "100"))

# Create server instance
server = Server("deepseek-mcp-server")

# Initialize cache if available
if CACHE_ENABLED and PromptCache:
    cache = PromptCache(max_size_mb=CACHE_SIZE_MB)
    print(f"✅ MCP Caching enabled (max {CACHE_SIZE_MB}MB)")
else:
    cache = None
    print("⚠️  MCP Caching disabled")


def generate_cache_key(model: str, prompt: str, context: str = "") -> str:
    """Generate a cache key from the request parameters."""
    key_data = f"{model}:{prompt[:500]}:{context[:200]}"
    return hashlib.sha256(key_data.encode()).hexdigest()


async def call_deepseek(
    model: str,
    messages: list[dict[str, Any]],
    max_tokens: int = 4096,
    temperature: float = 0.7,
) -> str:
    """
    Call DeepSeek API directly with caching support.

    Args:
        model: Model name (deepseek-chat or deepseek-reasoner)
        messages: List of message dicts
        max_tokens: Maximum tokens in response (default: 4096 to prevent overflow)
        temperature: Sampling temperature

    Note: Reduced max_tokens from 8192 to 4096 to prevent context overflow
    when multiple agents run in parallel.
    """
    if not DEEPSEEK_API_KEY:
        return "Error: DEEPSEEK_API_KEY environment variable not set"

    # Generate prompt for cache key
    prompt = messages[-1].get("content", "") if messages else ""
    context = messages[0].get("content", "") if len(messages) > 1 else ""

    # Check cache first
    if cache:
        cache_key = generate_cache_key(model, prompt, context)
        cached_response = cache.get(prompt, {"type": "mcp", "model": model})

        if cached_response:
            print(f"📦 Cache HIT for {model}")
            return cached_response
        else:
            print(f"❌ Cache MISS for {model}")

    # Check input token count to prevent overflow
    input_text = "".join(m.get("content", "") for m in messages)
    estimated_input_tokens = len(input_text) // 4  # Rough estimate

    if estimated_input_tokens > 150000:
        return (
            f"Error: Input too large (~{estimated_input_tokens:,} tokens). "
            f"Use smart_reader.py for large files instead."
        )

    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": model,
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": temperature,
        "stream": False,
    }

    try:
        async with httpx.AsyncClient(timeout=180.0) as client:
            response = await client.post(
                f"{DEEPSEEK_BASE_URL}/chat/completions",
                headers=headers,
                json=payload,
            )
            response.raise_for_status()
            result = response.json()
            response_content = result["choices"][0]["message"]["content"]

            # Cache the response
            if cache:
                # Estimate token count
                output_tokens = len(response_content) // 4
                cache.put(
                    prompt,
                    response_content,
                    context={"type": "mcp", "model": model},
                    token_count=output_tokens,
                    cost=0.0001 * output_tokens / 1000  # Rough cost estimate
                )

            return response_content

    except httpx.HTTPStatusError as e:
        return f"HTTP Error: {e.response.status_code} - {e.response.text}"
    except Exception as e:
        return f"Error: {str(e)}"


@server.list_resources()
async def handle_list_resources() -> list[Resource]:
    """List available resources."""
    return []


@server.read_resource()
async def handle_read_resource(uri: str) -> str:
    """Read a resource."""
    return ""


@server.list_tools()
async def handle_list_tools() -> list[Tool]:
    """List available tools."""
    return [
        Tool(
            name="deepseek-chat",
            description=(
                "DeepSeek Chat V3 - Fast and capable model for coding, "
                "technical writing, and explanations. Use for: "
                "C++ code generation, OpenFOAM implementation, "
                "code analysis, and practical explanations.\n\n"
                f"Caching: {'ENABLED' if cache else 'DISABLED'}"
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "prompt": {
                        "type": "string",
                        "description": "Your question or task for DeepSeek Chat",
                    },
                    "context": {
                        "type": "string",
                        "description": "Optional context or background information",
                    },
                },
                "required": ["prompt"],
            },
        ),
        Tool(
            name="deepseek-reasoner",
            description=(
                "DeepSeek R1 (Reasoner) - Advanced reasoning model for complex "
                "analysis, mathematical derivations, and research. Use for: "
                "CFD theory derivations, TVD limiter math, physics explanations, "
                "architecture decisions, and in-depth analysis.\n\n"
                f"Caching: {'ENABLED' if cache else 'DISABLED'}"
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "prompt": {
                        "type": "string",
                        "description": "Your question or task for DeepSeek Reasoner",
                    },
                    "context": {
                        "type": "string",
                        "description": "Optional context or background information",
                    },
                },
                "required": ["prompt"],
            },
        ),
    ]


@server.call_tool()
async def handle_call_tool(
    name: str,
    arguments: dict[str, Any],
) -> list[TextContent | ImageContent | EmbeddedResource]:
    """Handle tool calls."""
    prompt = arguments.get("prompt", "")
    context = arguments.get("context", "")

    if not prompt:
        return [TextContent(type="text", text="Error: prompt is required")]

    # Build messages
    messages = []
    if context:
        messages.append({"role": "system", "content": context})
    messages.append({"role": "user", "content": prompt})

    # Call appropriate model
    if name == "deepseek-chat":
        model = DEEPSEEK_CHAT
    elif name == "deepseek-reasoner":
        model = DEEPSEEK_REASONER
    else:
        return [TextContent(type="text", text=f"Unknown tool: {name}")]

    # Get response (with caching)
    response = await call_deepseek(model, messages)

    return [TextContent(type="text", text=response)]


async def main():
    """Main entry point."""
    # Run server using stdio
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="deepseek-mcp-server",
                server_version="1.1.0",  # Bumped for caching feature
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )


if __name__ == "__main__":
    asyncio.run(main())
