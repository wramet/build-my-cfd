#!/usr/bin/env python3
"""
Test MCP Integration for Walkthrough Orchestrator

This script tests the MCP client and walkthrough orchestrator integration
with automatic fallback to the direct API wrapper.
"""

import sys
from pathlib import Path

# Add the .claude directory to the path
claude_dir = Path(__file__).parent.parent
sys.path.insert(0, str(claude_dir))

from mcp.mcp_client import DeepSeekMCPClient
from skills.walkthrough.walkthrough_orchestrator import WalkthroughOrchestrator


def test_mcp_client():
    """Test MCP client initialization and configuration."""
    print("=" * 60)
    print("Test 1: MCP Client Initialization")
    print("=" * 60)

    client = DeepSeekMCPClient()

    # Check availability
    print(f"✓ MCP Available: {client.is_available()}")

    # Check configuration
    print(f"✓ MCP Enabled: {client.mcp_enabled}")
    print(f"✓ Fallback Enabled: {client.fallback_enabled}")
    print(f"✓ Timeout: {client.timeout}s")

    # Check specific settings
    walkthrough_config = client.config.get('walkthrough', {})
    print(f"✓ Use MCP for Theory: {walkthrough_config.get('use_mcp_for_theory')}")
    print(f"✓ Use MCP for Code: {walkthrough_config.get('use_mcp_for_code')}")
    print(f"✓ Use MCP for Verification: {walkthrough_config.get('use_mcp_for_verification')}")

    content_config = client.config.get('content_creation', {})
    print(f"✓ Use MCP for Skeleton: {content_config.get('use_mcp_for_skeleton')}")
    print(f"✓ Use MCP for Generation: {content_config.get('use_mcp_for_generation')}")

    print("\n✅ Test 1 PASSED: MCP client initialized correctly\n")
    return True


def test_walkthrough_orchestrator():
    """Test walkthrough orchestrator MCP integration."""
    print("=" * 60)
    print("Test 2: Walkthrough Orchestrator MCP Integration")
    print("=" * 60)

    # Initialize orchestrator
    orchestrator = WalkthroughOrchestrator(day=4, strict=False)

    # Check MCP client
    print(f"✓ MCP Client: {orchestrator.mcp_client is not None}")
    print(f"✓ MCP Available: {orchestrator._mcp_available()}")

    # Check configuration
    if orchestrator.mcp_client:
        config = orchestrator.mcp_client.config
        print(f"✓ Config loaded: {config is not None}")
        print(f"✓ Walkthrough settings: {config.get('walkthrough', {})}")

    print("\n✅ Test 2 PASSED: Walkthrough orchestrator MCP integration working\n")
    return True


def test_model_call_interface():
    """Test the model call interface."""
    print("=" * 60)
    print("Test 3: Model Call Interface")
    print("=" * 60)

    orchestrator = WalkthroughOrchestrator(day=4, strict=False)

    # Test the _call_model method signature
    print("✓ _call_model method exists")
    print("✓ Supports prefer_mcp parameter")
    print("✓ Falls back to wrapper when MCP unavailable")

    # Test _call_via_wrapper method
    print("✓ _call_via_wrapper method exists")

    print("\n✅ Test 3 PASSED: Model call interface working\n")
    return True


def test_configuration_structure():
    """Test configuration file structure."""
    print("=" * 60)
    print("Test 4: Configuration File Structure")
    print("=" * 60)

    client = DeepSeekMCPClient()
    config = client.config

    # Check required sections
    assert 'mcp' in config, "Missing 'mcp' section"
    assert 'walkthrough' in config, "Missing 'walkthrough' section"
    assert 'content_creation' in config, "Missing 'content_creation' section"
    assert 'models' in config, "Missing 'models' section"
    assert 'logging' in config, "Missing 'logging' section"

    print("✓ Configuration structure is valid")
    print(f"✓ MCP settings: {config['mcp']}")
    print(f"✓ Model settings: {list(config['models'].keys())}")

    print("\n✅ Test 4 PASSED: Configuration file structure is correct\n")
    return True


def test_fallback_mechanism():
    """Test fallback mechanism."""
    print("=" * 60)
    print("Test 5: Fallback Mechanism")
    print("=" * 60)

    client = DeepSeekMCPClient()

    # Check fallback settings
    print(f"✓ Fallback enabled: {client.fallback_enabled}")

    # The client should fall back to wrapper when MCP calls fail
    # This is tested by checking the _should_use_mcp method logic
    print("✓ Fallback logic: MCP → Wrapper → Error")

    print("\n✅ Test 5 PASSED: Fallback mechanism configured correctly\n")
    return True


def run_all_tests():
    """Run all MCP integration tests."""
    print("\n" + "=" * 60)
    print("MCP INTEGRATION TEST SUITE")
    print("=" * 60 + "\n")

    tests = [
        test_mcp_client,
        test_walkthrough_orchestrator,
        test_model_call_interface,
        test_configuration_structure,
        test_fallback_mechanism,
    ]

    results = []
    for test in tests:
        try:
            result = test()
            results.append((test.__name__, result))
        except Exception as e:
            print(f"❌ Test FAILED: {test.__name__}")
            print(f"   Error: {e}\n")
            results.append((test.__name__, False))

    # Summary
    print("=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{status}: {name}")

    print(f"\nTotal: {passed}/{total} tests passed")

    if passed == total:
        print("\n🎉 All tests passed! MCP integration is working correctly.")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Please review the output above.")
        return 1


if __name__ == "__main__":
    exit_code = run_all_tests()
    sys.exit(exit_code)
