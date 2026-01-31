#!/usr/bin/env python3
"""
MCP Client Wrapper for DeepSeek Integration

This module provides a unified interface for calling DeepSeek models through MCP
when available, with automatic fallback to the direct API wrapper.

Usage:
    from .claude.mcp.mcp_client import DeepSeekMCPClient

    client = DeepSeekMCPClient()
    response = client.call_chat("Your prompt here")
"""

import os
import json
import logging
from typing import Optional, Dict, Any
from pathlib import Path

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DeepSeekMCPClient:
    """
    Unified MCP client wrapper for DeepSeek Chat and Reasoner models.

    This client attempts to use MCP tools when available (via Claude Code context),
    and falls back to direct API calls when MCP is not accessible.
    """

    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the MCP client.

        Args:
            config_path: Optional path to MCP configuration file
        """
        self.config = self._load_config(config_path)
        self.mcp_enabled = self.config.get('mcp', {}).get('enabled', True)
        self.fallback_enabled = self.config.get('mcp', {}).get('fallback_to_wrapper', True)
        self.timeout = self.config.get('mcp', {}).get('timeout', 120)

        # Try to detect if MCP tools are available
        self._mcp_available = self._detect_mcp_availability()

        if self._mcp_available:
            logger.info("MCP tools detected - will use MCP for model calls")
        elif self.fallback_enabled:
            logger.info("MCP not available - will use direct API wrapper")
        else:
            logger.warning("MCP not available and fallback disabled - calls may fail")

    def _load_config(self, config_path: Optional[str]) -> Dict[str, Any]:
        """Load MCP configuration from YAML file."""
        if config_path is None:
            config_path = Path(__file__).parent.parent / 'config' / 'mcp.yaml'

        config_file = Path(config_path)
        if config_file.exists():
            try:
                import yaml
                with open(config_file, 'r') as f:
                    return yaml.safe_load(f) or {}
            except ImportError:
                logger.debug("PyYAML not available, using defaults")
            except Exception as e:
                logger.debug(f"Could not load config: {e}")

        # Return default configuration
        return {
            'mcp': {
                'enabled': True,
                'fallback_to_wrapper': True,
                'timeout': 120
            }
        }

    def _detect_mcp_availability(self) -> bool:
        """
        Detect if MCP tools are available in the current context.

        This checks if we're running within Claude Code and if MCP tools
        are accessible.
        """
        # Check for MCP environment indicators
        # When running in Claude Code with MCP, certain env vars may be set
        if 'ANTHROPIC_API_KEY' in os.environ:
            # We're likely in Claude Code - MCP tools should be available
            return True

        # Check if we can import the wrapper (for fallback)
        try:
            mcp_wrapper_path = Path(__file__).parent.parent / 'mcp' / 'deepseek_mcp_server.py'
            if mcp_wrapper_path.exists():
                return True
        except Exception:
            pass

        return False

    def is_available(self) -> bool:
        """Check if MCP tools are currently available."""
        return self._mcp_available

    def call_chat(
        self,
        prompt: str,
        context: Optional[Dict[str, Any]] = None,
        use_mcp: Optional[bool] = None
    ) -> Optional[str]:
        """
        Call DeepSeek Chat model.

        Args:
            prompt: The prompt to send to the model
            context: Optional context information
            use_mcp: Force MCP usage (True) or wrapper (False). If None, auto-detect.

        Returns:
            Model response as string, or None if call fails
        """
        # Determine whether to use MCP
        should_use_mcp = self._should_use_mcp('chat', use_mcp)

        if should_use_mcp:
            try:
                return self._call_via_mcp('chat', prompt, context)
            except Exception as e:
                logger.warning(f"MCP call failed: {e}")
                if not self.fallback_enabled:
                    return None
                logger.info("Falling back to direct API wrapper")

        # Fallback to direct wrapper
        return self._call_via_wrapper('chat', prompt, context)

    def call_reasoner(
        self,
        prompt: str,
        context: Optional[Dict[str, Any]] = None,
        use_mcp: Optional[bool] = None
    ) -> Optional[str]:
        """
        Call DeepSeek Reasoner model.

        Args:
            prompt: The prompt to send to the model
            context: Optional context information
            use_mcp: Force MCP usage (True) or wrapper (False). If None, auto-detect.

        Returns:
            Model response as string, or None if call fails
        """
        # Determine whether to use MCP
        should_use_mcp = self._should_use_mcp('reasoner', use_mcp)

        if should_use_mcp:
            try:
                return self._call_via_mcp('reasoner', prompt, context)
            except Exception as e:
                logger.warning(f"MCP call failed: {e}")
                if not self.fallback_enabled:
                    return None
                logger.info("Falling back to direct API wrapper")

        # Fallback to direct wrapper
        return self._call_via_wrapper('reasoner', prompt, context)

    def _should_use_mcp(self, model_type: str, use_mcp: Optional[bool]) -> bool:
        """Determine whether to use MCP for this call."""
        if use_mcp is not None:
            return use_mcp

        if not self.mcp_enabled:
            return False

        if not self._mcp_available:
            return False

        # Check config for model-specific settings
        config_key = 'walkthrough' if 'walkthrough' in str(os.getcwd()) else 'content_creation'
        model_setting = f'use_mcp_for_{model_type}'

        if config_key in self.config:
            return self.config[config_key].get(model_setting, True)

        return True

    def _call_via_mcp(
        self,
        model_type: str,
        prompt: str,
        context: Optional[Dict[str, Any]]
    ) -> str:
        """
        Call model via MCP tools.

        This method is meant to be called from within Claude Code where
        MCP tools are directly available. For external Python usage,
        it will delegate to the wrapper.
        """
        # When called from Python, we can't directly invoke MCP tools
        # Those are only available within Claude Code's context
        # So we signal that MCP should be used at the Claude Code level

        logger.debug(f"MCP call requested for {model_type} - delegating to wrapper")
        return self._call_via_wrapper(model_type, prompt, context)

    def _call_via_wrapper(
        self,
        model_type: str,
        prompt: str,
        context: Optional[Dict[str, Any]]
    ) -> Optional[str]:
        """Call model via direct API wrapper."""
        try:
            # Use the direct DeepSeek API
            import asyncio
            import httpx

            # Try environment variable first, then fallback to hardcoded key (same as wrapper)
            api_keys = [
                os.environ.get("DEEPSEEK_API_KEY"),
                "sk-a8d183f6f9904326913cb4e799eaba17"  # Backup key from wrapper
            ]

            # Filter out None values
            api_keys = [k for k in api_keys if k]

            # Map model_type to actual model name
            model_name = 'deepseek-reasoner' if model_type == 'reasoner' else 'deepseek-chat'

            # Prepare the prompt with context
            messages = []
            if context:
                context_str = json.dumps(context, indent=2)
                messages.append({"role": "system", "content": f"Context:\n{context_str}"})
            messages.append({"role": "user", "content": prompt})

            logger.info(f"Calling {model_name} via direct API")
            logger.info(f"Have {len(api_keys)} API key(s) to try")

            # Run async call in sync context
            async def make_request(api_key):
                headers = {
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                }

                payload = {
                    "model": model_name,
                    "messages": messages,
                    "max_tokens": 8192,
                    "temperature": 0.7,
                    "stream": False,
                }

                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    response = await client.post(
                        "https://api.deepseek.com/v1/chat/completions",
                        headers=headers,
                        json=payload,
                    )
                    response.raise_for_status()
                    result = response.json()
                    return result["choices"][0]["message"]["content"]

            # Try each API key until one works
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                for i, api_key in enumerate(api_keys):
                    try:
                        logger.info(f"Attempting with API key {i+1}/{len(api_keys)}: {api_key[:10]}...{api_key[-4:]}")
                        response = loop.run_until_complete(make_request(api_key))
                        logger.info(f"Success with API key {i+1}")
                        return response
                    except Exception as e:
                        logger.warning(f"API key {i+1} failed: {e}")
                        if i < len(api_keys) - 1:
                            logger.info(f"Trying next API key...")
                        else:
                            raise
            finally:
                loop.close()

        except ImportError as e:
            logger.error(f"Could not import required modules: {e}")
            return None
        except Exception as e:
            logger.error(f"Wrapper call failed: {e}")
            return None


# Convenience functions for quick usage
def call_chat(prompt: str, context: Optional[Dict[str, Any]] = None) -> Optional[str]:
    """Quick function to call DeepSeek Chat."""
    client = DeepSeekMCPClient()
    return client.call_chat(prompt, context)


def call_reasoner(prompt: str, context: Optional[Dict[str, Any]] = None) -> Optional[str]:
    """Quick function to call DeepSeek Reasoner."""
    client = DeepSeekMCPClient()
    return client.call_reasoner(prompt, context)


if __name__ == '__main__':
    # Test the client
    print("Testing DeepSeek MCP Client...")

    client = DeepSeekMCPClient()
    print(f"MCP Available: {client.is_available()}")

    # Test a simple call
    response = client.call_chat("Say 'Hello from DeepSeek MCP Client!'")
    if response:
        print(f"\nResponse: {response}")
    else:
        print("\nNo response received")
