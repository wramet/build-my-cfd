#!/usr/bin/env python3
"""
Compatibility shim for workflow_logger.

This provides backward compatibility for scripts that imported workflow_logger.
It uses the unified_logger underneath but provides the same function signatures.

DEPRECATED: New code should import unified_logger directly.
"""

import sys
from pathlib import Path
from typing import Optional, Dict, Any

# Import unified logger
from scripts.unified_logger import UnifiedLogger, get_logger as _get_unified_logger

# Global logger instance
_logger: Optional[UnifiedLogger] = None


def get_logger(log_file: Optional[str] = None) -> UnifiedLogger:
    """
    Get or create global logger instance.

    Args:
        log_file: Ignored for compatibility (kept for API compatibility)

    Returns:
        UnifiedLogger instance
    """
    global _logger
    if _logger is None:
        # Extract session_id from log_file path if provided
        session_id = None
        if log_file:
            # Try to extract a session identifier from the path
            session_id = Path(log_file).stem.replace("workflow_debug", "").replace("log", "")
            if not session_id:
                from datetime import datetime
                session_id = datetime.now().strftime("%Y%m%d_%H%M%S")

        _logger = _get_unified_logger(session_id=session_id)
    return _logger


def log_phase(phase_num: int, phase_name: str, details: Optional[str] = None):
    """
    Log a workflow phase (compatibility function).

    Args:
        phase_num: Phase number (used as stage number)
        phase_name: Name of the phase
        details: Optional details
    """
    logger = get_logger()
    # Use the stage_start method for compatibility
    key = logger.stage_start(phase_num, phase_name)
    # Immediately end it since this is just logging a phase name
    logger.stage_end(key, phase_num, phase_name, True, details)


def log_verification(gate_name: str, passed: bool, details: Optional[str] = None):
    """
    Log a verification gate result.

    Args:
        gate_name: Name of the verification gate
        passed: Whether the gate passed
        details: Optional details about the verification
    """
    logger = get_logger()
    logger.verification_gate(gate_name, passed, details)


def log_agent(agent_name: str, task: str, model: Optional[str] = None):
    """
    Log an agent delegation.

    Args:
        agent_name: Name of the agent
        task: Task description
        model: Optional model name
    """
    logger = get_logger()
    logger.subagent_delegate(agent_name, task, model)


def log_proxy_routing(model: str, prompt: str, response: Optional[str] = None):
    """
    Log a proxy routing event (for MCP calls).

    Args:
        model: Model name
        prompt: Prompt text
        response: Optional response
    """
    logger = get_logger()
    logger.log_mcp_start(model, {"prompt": prompt[:100] if prompt else ""})
    if response:
        logger.log_mcp_end(model, model, True, {"response": response[:100]})


def log_task_start(task_name: str, details: Optional[Dict[str, Any]] = None):
    """
    Log the start of a task.

    Args:
        task_name: Name of the task
        details: Optional task details
    """
    logger = get_logger()
    # Import LogEvent from unified_logger
    from scripts.unified_logger import LogEvent
    data = details or {}
    logger._log_event(LogEvent(
        timestamp=logger._now(),
        event_type="info",
        component="workflow",
        name=f"Task Start: {task_name}",
        data=data
    ))


def log_task_complete(task_name: str, result: Optional[str] = None):
    """
    Log the completion of a task.

    Args:
        task_name: Name of the task
        result: Optional result description
    """
    logger = get_logger()
    from scripts.unified_logger import LogEvent
    data = {"result": result} if result else {}
    logger._log_event(LogEvent(
        timestamp=logger._now(),
        event_type="info",
        component="workflow",
        name=f"Task Complete: {task_name}",
        data=data,
        success=True
    ))


# Export all functions for backward compatibility
__all__ = [
    'get_logger',
    'log_phase',
    'log_verification',
    'log_agent',
    'log_proxy_routing',
    'log_task_start',
    'log_task_complete',
]
