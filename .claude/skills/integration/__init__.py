"""
Skill Integration Package

Provides integration interfaces for connecting skills with:

- Agents: Agent-Skill bridge for agent-initiated skill execution
- Hooks: Hook-Skill triggers for event-based skill execution
- Scripts: Script API for programmatic skill access
- Verification: Integration with verification gates
"""

from .agent_bridge import AgentSkillBridge
from .hook_triggers import HookSkillTriggers
from .script_api import ScriptSkillAPI
from .verification_assistant import VerificationAssistant

__all__ = [
    "AgentSkillBridge",
    "HookSkillTriggers",
    "ScriptSkillAPI",
    "VerificationAssistant",
]
