"""
Skill Orchestrator Package

Provides core skill management and execution capabilities:

- SkillRegistry: Central skill repository with dependency resolution
- SkillExecutor: Execution engine with caching and metrics
- SkillChain: Orchestration of multiple skills
"""

from .skill_registry import SkillRegistry, SkillMetadata, SkillType
from .skill_executor import SkillExecutor, ExecutionResult, SkillCache, SkillMetrics
from .skill_chain import SkillChain, ChainStep, ChainResult, ChainStatus

__all__ = [
    "SkillRegistry",
    "SkillMetadata",
    "SkillType",
    "SkillExecutor",
    "ExecutionResult",
    "SkillCache",
    "SkillMetrics",
    "SkillChain",
    "ChainStep",
    "ChainResult",
    "ChainStatus",
]


def create_orchestrator(skills_dir: str = ".claude/skills") -> SkillExecutor:
    """
    Create a configured skill executor.

    Args:
        skills_dir: Path to skills directory

    Returns:
        Configured SkillExecutor instance
    """
    registry = SkillRegistry(skills_dir)
    registry.discover_skills()
    return SkillExecutor(registry)
