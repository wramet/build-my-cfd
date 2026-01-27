#!/usr/bin/env python3
"""
DeepSeek MCP Server

Exposes DeepSeek models as MCP tools with full Claude Code integration.
Supports both DeepSeek Chat V3 and DeepSeek R1 (Reasoner).
"""

import asyncio
import json
import os
import sys
from typing import Any, Optional
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

# Create server instance
server = Server("deepseek-mcp-server")


async def call_deepseek(
    model: str,
    messages: list[dict[str, Any]],
    max_tokens: int = 8192,
    temperature: float = 0.7,
) -> str:
    """Call DeepSeek API directly."""
    if not DEEPSEEK_API_KEY:
        return "Error: DEEPSEEK_API_KEY environment variable not set"

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
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                f"{DEEPSEEK_BASE_URL}/chat/completions",
                headers=headers,
                json=payload,
            )
            response.raise_for_status()
            result = response.json()
            return result["choices"][0]["message"]["content"]
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
                "code analysis, and practical explanations."
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
                "architecture decisions, and in-depth analysis."
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

    # Get response
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
                server_version="1.0.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )


if __name__ == "__main__":
    asyncio.run(main())
