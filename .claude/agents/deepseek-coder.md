---
name: deepseek-coder
description: Specialized C++ and CFD coding agent using DeepSeek Coder V2.
---

# DeepSeek Coder Agent

This agent uses the **DeepSeek Coder V2** model via the local proxy (Port 4000).
It is specialized for:
- Writing C++ OpenFOAM code
- Generating mathematical derivations (LaTeX)
- Technical documentation
- Refactoring complex logic

## Usage
Simply mention `@deepseek-coder` in your prompt or use the slash command.

## Configuration
- **Model**: `deepseek/deepseek-coder` (routed via proxy)
- **Base URL**: `http://localhost:4000`
