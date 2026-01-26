#!/usr/bin/env python3
"""
Workflow Logger for /create-day multi-agent workflow.

Logs all workflow steps, agent invocations, proxy routing, and tool usage.
"""

import json
import os
import logging
from datetime import datetime
from pathlib import Path

class WorkflowLogger:
    def __init__(self, log_file=None):
        if log_file is None:
            log_file = "/tmp/workflow_debug.log"
        self.log_file = Path(log_file)
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Configure logging
        self.logger = logging.getLogger("WorkflowLogger")
        self.logger.setLevel(logging.DEBUG)

        # File handler (append mode to preserve all sessions)
        fh = logging.FileHandler(self.log_file, mode='a')
        fh.setLevel(logging.DEBUG)

        # Console handler
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)

        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s | %(levelname)-8s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        fh.setFormatter(formatter)
        ch.setFormatter(formatter)

        self.logger.addHandler(fh)
        self.logger.addHandler(ch)

        self.logger.info("="*70)
        self.logger.info(f"WORKFLOW SESSION: {self.session_id}")
        self.logger.info("="*70)

    def log_phase(self, phase_num, phase_name, details=None):
        """Log a workflow phase start."""
        self.logger.info("")
        self.logger.info(f"📍 PHASE {phase_num}: {phase_name}")
        if details:
            self.logger.info(f"   Details: {details}")
        self.logger.info("-" * 70)

    def log_agent_invocation(self, agent_name, model, backend, task):
        """Log when an agent is invoked."""
        self.logger.info(f"🤖 AGENT INVOKED: {agent_name}")
        self.logger.info(f"   Model: {model}")
        self.logger.info(f"   Backend: {backend}")
        self.logger.info(f"   Task: {task[:100]}...")

    def log_agent_completion(self, agent_name, agent_id, result_summary):
        """Log when an agent completes."""
        self.logger.info(f"✅ AGENT COMPLETE: {agent_name}")
        self.logger.info(f"   Agent ID: {agent_id}")
        self.logger.info(f"   Result: {result_summary[:200]}...")

    def log_proxy_routing(self, original_model, mapped_model, selected_backend, reason=""):
        """Log proxy routing decision."""
        self.logger.info(f"🔀 PROXY ROUTING:")
        self.logger.info(f"   Original model: {original_model}")
        self.logger.info(f"   Mapped to: {mapped_model}")
        self.logger.info(f"   Routes to: {selected_backend}")
        if reason:
            self.logger.info(f"   Reason: {reason}")

    def log_tool_usage(self, tool_name, details=None):
        """Log when a tool is used."""
        self.logger.debug(f"🔧 TOOL: {tool_name}")
        if details:
            self.logger.debug(f"   {details}")

    def log_task_start(self, task_name):
        """Log when a task starts."""
        self.logger.info(f"▶️  TASK: {task_name}")

    def log_task_complete(self, task_name, result=None):
        """Log when a task completes."""
        status = "✅ COMPLETE" if result else "⚠️  PARTIAL"
        self.logger.info(f"{status}: {task_name}")
        if result:
            self.logger.info(f"   Result: {result[:200]}...")

    def log_file_operation(self, operation, file_path, extra=None):
        """Log file operations."""
        self.logger.debug(f"📁 FILE {operation}: {file_path}")
        if extra:
            self.logger.debug(f"   {extra}")

    def log_script_execution(self, script, args, exit_code, output):
        """Log script execution."""
        status = "✅" if exit_code == 0 else "❌"
        self.logger.info(f"{status} SCRIPT: {script} {' '.join(args)}")
        if output:
            self.logger.debug(f"   Output: {output[:500]}...")

    def log_model_response(self, agent_name, model, input_tokens, output_tokens):
        """Log model token usage."""
        self.logger.info(f"📊 MODEL STATS: {agent_name} ({model})")
        self.logger.info(f"   Input tokens: {input_tokens}")
        self.logger.info(f"   Output tokens: {output_tokens}")

    def log_verification_result(self, file_path, verified, issues):
        """Log verification results."""
        self.logger.info(f"🔍 VERIFICATION: {file_path}")
        self.logger.info(f"   Verified items: {verified.get('verified', 0)}")
        self.logger.info(f"   Issues found: {issues}")

    def log_session_summary(self, total_time, summary):
        """Log end of session summary."""
        self.logger.info("")
        self.logger.info("="*70)
        self.logger.info(f"SESSION COMPLETE: {self.session_id}")
        self.logger.info(f"Total time: {total_time:.2f}s")
        self.logger.info("")
        for key, value in summary.items():
            self.logger.info(f"{key}: {value}")
        self.logger.info("="*70)


class WorkflowProgress:
    """Track workflow progress for display."""

    def __init__(self):
        self.steps = []
        self.current_step = 0

    def add_step(self, step_name, status="pending"):
        """Add a workflow step."""
        self.steps.append({
            "step": len(self.steps) + 1,
            "name": step_name,
            "status": status,  # pending, in_progress, completed, failed
            "start_time": None,
            "end_time": None
        })

    def start_step(self, step_number):
        """Mark a step as in progress."""
        if 0 <= step_number < len(self.steps):
            self.steps[step_number]["status"] = "in_progress"
            self.steps[step_number]["start_time"] = datetime.now().isoformat()

    def complete_step(self, step_number, result=None):
        """Mark a step as completed."""
        if 0 <= step_number < len(self.steps):
            self.steps[step_number]["status"] = "completed"
            self.steps[step_number]["end_time"] = datetime.now().isoformat()
            if result:
                self.steps[step_number]["result"] = result

    def fail_step(self, step_number, error):
        """Mark a step as failed."""
        if 0 <= step_number < len(self.steps):
            self.steps[step_number]["status"] = "failed"
            self.steps[step_number]["error"] = str(error)

    def get_progress_bar(self):
        """Get a text progress bar."""
        total = len(self.steps)
        completed = sum(1 for s in self.steps if s["status"] == "completed")
        in_progress = sum(1 for s in self.steps if s["status"] == "in_progress")

        bar_length = 40
        filled = int((completed / total) * bar_length)
        progress = "█" * filled + "░" * (bar_length - filled)

        status_line = []
        for step in self.steps:
            status_char = {
                "pending": "○",
                "in_progress": "●",
                "completed": "✓",
                "failed": "✗"
            }[step["status"]]
            status_line.append(f"{status_char} {step['name']}")

        return f"[{progress}] {completed}/{total} steps\n" + "\n".join(status_line)

    def get_summary(self):
        """Get session summary."""
        completed = sum(1 for s in self.steps if s["status"] == "completed")
        total = len(self.steps)

        summary = {
            "session_id": None,  # Will be set by logger
            "total_steps": total,
            "completed": completed,
            "failed": sum(1 for s in self.steps if s["status"] == "failed"),
            "progress_percent": int((completed / total) * 100) if total > 0 else 0
        }
        return summary


# Global instance
_workflow_logger = None
_workflow_progress = None

def get_logger(log_file="/tmp/workflow_debug.log"):
    """Get or create the workflow logger."""
    global _workflow_logger
    if _workflow_logger is None:
        _workflow_logger = WorkflowLogger(log_file)
    return _workflow_logger

def get_progress():
    """Get or create the workflow progress tracker."""
    global _workflow_progress
    if _workflow_progress is None:
        _workflow_progress = WorkflowProgress()
    return _workflow_progress

# Convenience functions
def log_phase(phase_num, phase_name, details=None):
    """Log a workflow phase."""
    get_logger().log_phase(phase_num, phase_name, details)

def log_agent(agent_name, model, backend, task):
    """Log agent invocation."""
    get_logger().log_agent_invocation(agent_name, model, backend, task)

def log_proxy_routing(original_model, mapped_model, backend, reason=""):
    """Log proxy routing."""
    get_logger().log_proxy_routing(original_model, mapped_model, backend, reason)

def log_tool(tool_name, details=None):
    """Log tool usage."""
    get_logger().log_tool_usage(tool_name, details)

def log_task_start(task_name):
    """Log task start."""
    get_logger().log_task_start(task_name)

def log_task_complete(task_name, result=None):
    """Log task completion."""
    get_logger().log_task_complete(task_name, result)

def log_file_op(operation, file_path, extra=None):
    """Log file operation."""
    get_logger().log_file_operation(operation, file_path, extra)

def log_script(script, args, exit_code, output):
    """Log script execution."""
    get_logger().log_script_execution(script, args, exit_code, output)

def log_model_stats(agent_name, model, input_tokens, output_tokens):
    """Log model token usage."""
    get_logger().log_model_response(agent_name, model, input_tokens, output_tokens)

def log_verification(file_path, verified, issues):
    """Log verification results."""
    get_logger().log_verification_result(file_path, verified, issues)

def log_session_summary(total_time, summary):
    """Log session summary."""
    get_logger().log_session_summary(total_time, summary)

def show_progress():
    """Display current progress bar."""
    if _workflow_progress:
        print(get_progress().get_progress_bar())
