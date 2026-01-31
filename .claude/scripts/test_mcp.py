#!/usr/bin/env python3
"""
Test script for DeepSeek MCP server
Verifies that MCP tools are accessible and working
"""

import json
import subprocess
import sys

def test_direct_api():
    """Test DeepSeek API directly (baseline)"""
    print("1. Testing DeepSeek API directly...")
    result = subprocess.run(
        ["python3", ".claude/scripts/deepseek_content.py", "deepseek-chat", "/dev/stdin"],
        input="Say 'API OK'",
        capture_output=True,
        text=True,
        cwd="/Users/woramet/Documents/th_new"
    )
    if "API OK" in result.stdout:
        print("   ✅ Direct API works")
        return True
    else:
        print("   ❌ Direct API failed")
        return False

def test_mcp_server_exists():
    """Test MCP server file exists"""
    print("\n2. Checking MCP server file...")
    import os
    server_path = "/Users/woramet/Documents/th_new/.claude/mcp/deepseek_mcp_server.py"
    if os.path.exists(server_path):
        print("   ✅ MCP server file exists")
        return True
    else:
        print("   ❌ MCP server file missing")
        return False

def test_mcp_config():
    """Test MCP configuration"""
    print("\n3. Checking MCP configuration...")
    mcp_json = "/Users/woramet/Documents/th_new/.mcp.json"
    try:
        with open(mcp_json) as f:
            config = json.load(f)
        if "deepseek" in config.get("mcpServers", {}):
            print("   ✅ .mcp.json has deepseek server")
            return True
        else:
            print("   ❌ .mcp.json missing deepseek server")
            return False
    except Exception as e:
        print(f"   ❌ Error reading .mcp.json: {e}")
        return False

def test_agent_files():
    """Test agent definition files"""
    print("\n4. Checking agent files...")
    import os
    agents = [
        "/Users/woramet/Documents/th_new/.claude/agents/deepseek-chat-mcp.md",
        "/Users/woramet/Documents/th_new/.claude/agents/deepseek-reasoner-mcp.md"
    ]
    all_exist = True
    for agent in agents:
        if os.path.exists(agent):
            print(f"   ✅ {os.path.basename(agent)} exists")
        else:
            print(f"   ❌ {os.path.basename(agent)} missing")
            all_exist = False
    return all_exist

def test_settings():
    """Test settings.json has MCP enabled"""
    print("\n5. Checking settings.json...")
    settings = "/Users/woramet/.claude/settings.json"
    try:
        with open(settings) as f:
            config = json.load(f)
        enabled = config.get("enabledMcpjsonServers", [])
        if "deepseek" in enabled:
            print("   ✅ deepseek server is enabled")
            return True
        else:
            print("   ❌ deepseek server not enabled")
            print(f"   Enabled servers: {enabled}")
            return False
    except Exception as e:
        print(f"   ❌ Error reading settings: {e}")
        return False

def main():
    print("=" * 60)
    print("DeepSeek MCP Server Test")
    print("=" * 60)

    results = {
        "Direct API": test_direct_api(),
        "MCP Server": test_mcp_server_exists(),
        "MCP Config": test_mcp_config(),
        "Agent Files": test_agent_files(),
        "Settings": test_settings(),
    }

    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)

    for test, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{test:20s}: {status}")

    all_passed = all(results.values())
    print("\n" + "=" * 60)
    if all_passed:
        print("✅ All tests passed! MCP should be working.")
        print("\nTo test in Claude Code, try:")
        print("  'Use deepseek-chat-mcp to list files in .claude/mcp/'")
    else:
        print("⚠️ Some tests failed. Check configuration.")
    print("=" * 60)

    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())
