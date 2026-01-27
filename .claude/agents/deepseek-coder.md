---
name: deepseek-coder
description: Specialized C++ and CFD coding agent using DeepSeek Coder V2.
---

# DeepSeek Coder Agent

This agent uses the **DeepSeek Coder V2** model via direct API connection.
It is specialized for:
- Writing C++ OpenFOAM code
- Generating mathematical derivations (LaTeX)
- Technical documentation
- Refactoring complex logic

## Usage
Simply mention `@deepseek-coder` in your prompt or use the slash command.

## Configuration
- **Model**: `deepseek/deepseek-coder`
- **Base URL**: `https://api.deepseek.com/v1` (direct API - no proxy required)
- **Implementation**: Uses `deepseek_content.py` for direct API calls
