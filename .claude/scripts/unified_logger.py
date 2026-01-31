#!/usr/bin/env python3
"""
Unified Logger for Claude Code Multi-Agent Workflows

Captures:
- MCP tool invocations
- Subagent delegations
- Hook triggers
- Skill executions
- Workflow stages
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field, asdict
from enum import Enum


class EventType(Enum):
    """Types of events that can be logged."""
    WORKFLOW_START = "workflow_start"
    WORKFLOW_END = "workflow_end"
    STAGE_START = "stage_start"
    STAGE_END = "stage_end"
    MCP_CALL = "mcp_call"
    MCP_RESPONSE = "mcp_response"
    SUBAGENT_DELEGATE = "subagent_delegate"
    SUBAGENT_RESPONSE = "subagent_response"
    HOOK_TRIGGER = "hook_trigger"
    HOOK_COMPLETE = "hook_complete"
    SKILL_INVOKE = "skill_invoke"
    SKILL_COMPLETE = "skill_complete"
    VERIFICATION_GATE = "verification_gate"
    ERROR = "error"
    INFO = "info"


@dataclass
class LogEvent:
    """A single log event."""
    timestamp: str
    event_type: str
    component: str  # mcp, subagent, hook, skill, workflow
    name: str
    data: Dict[str, Any] = field(default_factory=dict)
    duration_ms: Optional[float] = None
    success: Optional[bool] = None
    error: Optional[str] = None
    
    def to_dict(self) -> dict:
        return {k: v for k, v in asdict(self).items() if v is not None}
    
    def to_json(self) -> str:
        return json.dumps(self.to_dict())


class UnifiedLogger:
    """
    Unified logging system for multi-agent workflows.
    
    Usage:
        logger = UnifiedLogger()
        
        # Log MCP call
        with logger.mcp_call("deepseek-chat", {"prompt": "test"}):
            result = call_mcp(...)
        
        # Log skill execution
        logger.skill_invoke("source-first", {"action": "extract"})
        logger.skill_complete("source-first", success=True)
        
        # Log subagent delegation
        logger.subagent_delegate("researcher", "Find upwind class")
    """
    
    def __init__(self, 
                 log_dir: str = "/tmp/claude_logs",
                 session_id: Optional[str] = None):
        """Initialize the unified logger."""
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        self.session_id = session_id or datetime.now().strftime("%Y%m%d_%H%M%S")
        self.log_file = self.log_dir / f"session_{self.session_id}.jsonl"
        self.summary_file = self.log_dir / f"summary_{self.session_id}.md"
        
        self.events: List[LogEvent] = []
        self._start_times: Dict[str, float] = {}
        
        # Write session header
        self._log_event(LogEvent(
            timestamp=self._now(),
            event_type=EventType.INFO.value,
            component="logger",
            name="session_start",
            data={"session_id": self.session_id}
        ))
    
    def _now(self) -> str:
        return datetime.now().isoformat()
    
    def _time_ms(self) -> float:
        return datetime.now().timestamp() * 1000
    
    def _log_event(self, event: LogEvent):
        """Write event to log file and memory."""
        self.events.append(event)
        with open(self.log_file, "a") as f:
            f.write(event.to_json() + "\n")
    
    # ─────────────────────────────────────────────────────────────
    # MCP Logging
    # ─────────────────────────────────────────────────────────────
    
    def mcp_call(self, tool_name: str, parameters: dict):
        """Context manager for MCP calls."""
        return MCPCallContext(self, tool_name, parameters)
    
    def log_mcp_start(self, tool_name: str, parameters: dict):
        """Log MCP call start."""
        key = f"mcp_{tool_name}_{self._time_ms()}"
        self._start_times[key] = self._time_ms()
        self._log_event(LogEvent(
            timestamp=self._now(),
            event_type=EventType.MCP_CALL.value,
            component="mcp",
            name=tool_name,
            data={"parameters": parameters}
        ))
        return key
    
    def log_mcp_end(self, key: str, tool_name: str, 
                   success: bool, response: Optional[dict] = None,
                   error: Optional[str] = None):
        """Log MCP call completion."""
        duration = self._time_ms() - self._start_times.get(key, self._time_ms())
        self._log_event(LogEvent(
            timestamp=self._now(),
            event_type=EventType.MCP_RESPONSE.value,
            component="mcp",
            name=tool_name,
            data={"response_preview": str(response)[:200] if response else None},
            duration_ms=duration,
            success=success,
            error=error
        ))
    
    # ─────────────────────────────────────────────────────────────
    # Subagent Logging
    # ─────────────────────────────────────────────────────────────
    
    def subagent_delegate(self, agent_name: str, task: str, 
                         model: Optional[str] = None):
        """Log subagent delegation start."""
        key = f"subagent_{agent_name}_{self._time_ms()}"
        self._start_times[key] = self._time_ms()
        self._log_event(LogEvent(
            timestamp=self._now(),
            event_type=EventType.SUBAGENT_DELEGATE.value,
            component="subagent",
            name=agent_name,
            data={"task": task, "model": model}
        ))
        return key
    
    def subagent_response(self, key: str, agent_name: str,
                         success: bool, result: Optional[str] = None,
                         error: Optional[str] = None):
        """Log subagent response."""
        duration = self._time_ms() - self._start_times.get(key, self._time_ms())
        self._log_event(LogEvent(
            timestamp=self._now(),
            event_type=EventType.SUBAGENT_RESPONSE.value,
            component="subagent",
            name=agent_name,
            data={"result_preview": result[:200] if result else None},
            duration_ms=duration,
            success=success,
            error=error
        ))
    
    # ─────────────────────────────────────────────────────────────
    # Hook Logging
    # ─────────────────────────────────────────────────────────────
    
    def hook_trigger(self, hook_type: str, matcher: str, 
                    context: Optional[dict] = None):
        """Log hook trigger."""
        key = f"hook_{hook_type}_{self._time_ms()}"
        self._start_times[key] = self._time_ms()
        self._log_event(LogEvent(
            timestamp=self._now(),
            event_type=EventType.HOOK_TRIGGER.value,
            component="hook",
            name=hook_type,
            data={"matcher": matcher, "context": context}
        ))
        return key
    
    def hook_complete(self, key: str, hook_type: str,
                     success: bool, output: Optional[str] = None):
        """Log hook completion."""
        duration = self._time_ms() - self._start_times.get(key, self._time_ms())
        self._log_event(LogEvent(
            timestamp=self._now(),
            event_type=EventType.HOOK_COMPLETE.value,
            component="hook",
            name=hook_type,
            data={"output": output[:100] if output else None},
            duration_ms=duration,
            success=success
        ))
    
    # ─────────────────────────────────────────────────────────────
    # Skill Logging
    # ─────────────────────────────────────────────────────────────
    
    def skill_invoke(self, skill_id: str, parameters: dict):
        """Log skill invocation."""
        key = f"skill_{skill_id}_{self._time_ms()}"
        self._start_times[key] = self._time_ms()
        self._log_event(LogEvent(
            timestamp=self._now(),
            event_type=EventType.SKILL_INVOKE.value,
            component="skill",
            name=skill_id,
            data={"parameters": parameters}
        ))
        return key
    
    def skill_complete(self, key: str, skill_id: str,
                      success: bool, result: Optional[str] = None,
                      error: Optional[str] = None):
        """Log skill completion."""
        duration = self._time_ms() - self._start_times.get(key, self._time_ms())
        self._log_event(LogEvent(
            timestamp=self._now(),
            event_type=EventType.SKILL_COMPLETE.value,
            component="skill",
            name=skill_id,
            data={"result_preview": result[:200] if result else None},
            duration_ms=duration,
            success=success,
            error=error
        ))
    
    # ─────────────────────────────────────────────────────────────
    # Workflow Logging
    # ─────────────────────────────────────────────────────────────
    
    def workflow_start(self, workflow_name: str, context: dict):
        """Log workflow start."""
        self._start_times["workflow"] = self._time_ms()
        self._log_event(LogEvent(
            timestamp=self._now(),
            event_type=EventType.WORKFLOW_START.value,
            component="workflow",
            name=workflow_name,
            data=context
        ))
    
    def workflow_end(self, workflow_name: str, success: bool,
                    summary: Optional[dict] = None):
        """Log workflow end."""
        duration = self._time_ms() - self._start_times.get("workflow", self._time_ms())
        self._log_event(LogEvent(
            timestamp=self._now(),
            event_type=EventType.WORKFLOW_END.value,
            component="workflow",
            name=workflow_name,
            data={"summary": summary},
            duration_ms=duration,
            success=success
        ))
        # Generate summary report
        self._generate_summary()
    
    def stage_start(self, stage_num: int, stage_name: str, 
                   model: Optional[str] = None):
        """Log stage start."""
        key = f"stage_{stage_num}"
        self._start_times[key] = self._time_ms()
        self._log_event(LogEvent(
            timestamp=self._now(),
            event_type=EventType.STAGE_START.value,
            component="workflow",
            name=f"Stage {stage_num}: {stage_name}",
            data={"model": model}
        ))
        return key
    
    def stage_end(self, key: str, stage_num: int, stage_name: str,
                 success: bool, result: Optional[str] = None):
        """Log stage end."""
        duration = self._time_ms() - self._start_times.get(key, self._time_ms())
        self._log_event(LogEvent(
            timestamp=self._now(),
            event_type=EventType.STAGE_END.value,
            component="workflow",
            name=f"Stage {stage_num}: {stage_name}",
            data={"result": result},
            duration_ms=duration,
            success=success
        ))
    
    def verification_gate(self, gate_name: str, passed: bool,
                         details: Optional[str] = None):
        """Log verification gate result."""
        self._log_event(LogEvent(
            timestamp=self._now(),
            event_type=EventType.VERIFICATION_GATE.value,
            component="workflow",
            name=gate_name,
            data={"details": details},
            success=passed
        ))
    
    # ─────────────────────────────────────────────────────────────
    # Reporting
    # ─────────────────────────────────────────────────────────────
    
    def _generate_summary(self):
        """Generate markdown summary report."""
        # Count events by component
        component_counts = {}
        component_times = {}
        for e in self.events:
            comp = e.component
            component_counts[comp] = component_counts.get(comp, 0) + 1
            if e.duration_ms:
                component_times[comp] = component_times.get(comp, 0) + e.duration_ms
        
        # Generate report
        report = f"""# Workflow Session Summary

**Session ID:** {self.session_id}
**Generated:** {self._now()}

## Event Counts

| Component | Events | Total Time (ms) |
|-----------|--------|-----------------|
"""
        for comp in sorted(component_counts.keys()):
            count = component_counts[comp]
            time_ms = component_times.get(comp, 0)
            report += f"| {comp} | {count} | {time_ms:.0f} |\n"
        
        # Add timeline
        report += "\n## Event Timeline\n\n"
        for e in self.events:
            status = "✅" if e.success else ("❌" if e.success is False else "ℹ️")
            duration = f" ({e.duration_ms:.0f}ms)" if e.duration_ms else ""
            report += f"- {e.timestamp[11:19]} | {status} [{e.component}] {e.name}{duration}\n"
        
        with open(self.summary_file, "w") as f:
            f.write(report)
    
    def get_summary(self) -> dict:
        """Get summary statistics."""
        stats = {
            "session_id": self.session_id,
            "total_events": len(self.events),
            "by_component": {},
            "by_type": {}
        }
        for e in self.events:
            stats["by_component"][e.component] = stats["by_component"].get(e.component, 0) + 1
            stats["by_type"][e.event_type] = stats["by_type"].get(e.event_type, 0) + 1
        return stats


class MCPCallContext:
    """Context manager for MCP calls."""
    
    def __init__(self, logger: UnifiedLogger, tool_name: str, parameters: dict):
        self.logger = logger
        self.tool_name = tool_name
        self.parameters = parameters
        self.key = None
    
    def __enter__(self):
        self.key = self.logger.log_mcp_start(self.tool_name, self.parameters)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        success = exc_type is None
        error = str(exc_val) if exc_val else None
        self.logger.log_mcp_end(self.key, self.tool_name, success, error=error)
        return False


# ─────────────────────────────────────────────────────────────────
# Global logger instance
# ─────────────────────────────────────────────────────────────────

_global_logger: Optional[UnifiedLogger] = None


def get_logger(session_id: Optional[str] = None) -> UnifiedLogger:
    """Get or create global logger instance."""
    global _global_logger
    if _global_logger is None or session_id:
        _global_logger = UnifiedLogger(session_id=session_id)
    return _global_logger


# ─────────────────────────────────────────────────────────────────
# CLI
# ─────────────────────────────────────────────────────────────────

def main():
    """CLI for viewing logs."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Unified Logger CLI")
    parser.add_argument("--list", action="store_true", 
                       help="List recent sessions")
    parser.add_argument("--view", metavar="SESSION_ID",
                       help="View session events")
    parser.add_argument("--summary", metavar="SESSION_ID",
                       help="View session summary")
    parser.add_argument("--tail", action="store_true",
                       help="Tail latest session")
    parser.add_argument("--stats", action="store_true",
                       help="Show overall statistics")
    
    args = parser.parse_args()
    log_dir = Path("/tmp/claude_logs")
    
    if args.list:
        if log_dir.exists():
            sessions = sorted(log_dir.glob("session_*.jsonl"))
            print(f"\n📋 Recent Sessions ({len(sessions)}):\n")
            for s in sessions[-10:]:
                name = s.stem.replace("session_", "")
                size = s.stat().st_size
                print(f"  {name} ({size} bytes)")
        else:
            print("No sessions found")
    
    elif args.view:
        log_file = log_dir / f"session_{args.view}.jsonl"
        if log_file.exists():
            print(f"\n📜 Events for session {args.view}:\n")
            with open(log_file) as f:
                for line in f:
                    event = json.loads(line)
                    status = "✅" if event.get("success") else "❌" if event.get("success") is False else "ℹ️"
                    ts = event.get("timestamp", "")[11:19]
                    print(f"{ts} | {status} [{event['component']}] {event['name']}")
        else:
            print(f"Session {args.view} not found")
    
    elif args.summary:
        summary_file = log_dir / f"summary_{args.summary}.md"
        if summary_file.exists():
            print(summary_file.read_text())
        else:
            print(f"Summary for {args.summary} not found")
    
    elif args.tail:
        sessions = sorted(log_dir.glob("session_*.jsonl"))
        if sessions:
            latest = sessions[-1]
            print(f"\n📡 Tailing {latest.name}...\n")
            with open(latest) as f:
                for line in f:
                    event = json.loads(line)
                    print(f"[{event['component']}] {event['name']}")
        else:
            print("No sessions found")
    
    elif args.stats:
        if log_dir.exists():
            sessions = list(log_dir.glob("session_*.jsonl"))
            total_events = 0
            component_counts = {}
            for s in sessions:
                with open(s) as f:
                    for line in f:
                        total_events += 1
                        event = json.loads(line)
                        comp = event.get("component", "unknown")
                        component_counts[comp] = component_counts.get(comp, 0) + 1
            
            print(f"\n📊 Overall Statistics:\n")
            print(f"  Sessions: {len(sessions)}")
            print(f"  Total Events: {total_events}")
            print(f"\n  By Component:")
            for comp, count in sorted(component_counts.items()):
                print(f"    {comp}: {count}")
        else:
            print("No logs found")
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
