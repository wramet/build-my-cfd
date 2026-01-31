#!/usr/bin/env python3
"""
Skill Registry - Central repository for skill management

This module provides the core skill discovery, registration, and
dependency resolution capabilities for the skill orchestration system.
"""

import os
import json
import yaml
from pathlib import Path
from typing import Dict, List, Optional, Set
from dataclasses import dataclass, field
from enum import Enum


class SkillType(Enum):
    """Types of skills in the system"""
    COMMAND = "command"           # Slash command skills
    METHODOLOGY = "methodology"   # Process/documentation skills
    SPECIALIST = "specialist"     # Specialist reference skills
    REFERENCE = "reference"       # Reference material skills


@dataclass
class SkillMetadata:
    """Metadata for a registered skill"""
    skill_id: str
    name: str
    description: str
    skill_type: SkillType
    location: str                # Path to SKILL.md
    invocation: Optional[str] = None  # Command pattern
    dependencies: List[str] = field(default_factory=list)
    requires_source_first: bool = False
    execution_timeout: int = 30  # seconds
    cacheable: bool = True
    tags: List[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        """Convert to dictionary for serialization"""
        return {
            "skill_id": self.skill_id,
            "name": self.name,
            "description": self.description,
            "skill_type": self.skill_type.value,
            "location": self.location,
            "invocation": self.invocation,
            "dependencies": self.dependencies,
            "requires_source_first": self.requires_source_first,
            "execution_timeout": self.execution_timeout,
            "cacheable": self.cacheable,
            "tags": self.tags
        }


class SkillRegistry:
    """
    Central registry for skill management.

    Provides:
    - Skill discovery from filesystem
    - Skill registration and metadata management
    - Dependency resolution
    - Skill lookup and querying
    """

    def __init__(self, skills_dir: str = ".claude/skills"):
        self.skills_dir = Path(skills_dir)
        self.skills: Dict[str, SkillMetadata] = {}
        self.dependencies: Dict[str, List[str]] = {}
        self._load_builtin_skills()

    def _load_builtin_skills(self):
        """Load built-in skill definitions"""
        # Core CFD skills
        builtin_skills = [
            SkillMetadata(
                skill_id="content-creation",
                name="Content Creation",
                description="Daily learning content generation with Source-First approach",
                skill_type=SkillType.COMMAND,
                location=str(self.skills_dir / "content-creation"),
                invocation="/create-day --day=XX --topic=TOPIC",
                dependencies=["source-first"],
                requires_source_first=True,
                tags=["content", "daily", "source-first"]
            ),
            SkillMetadata(
                skill_id="create-module",
                name="Create Module",
                description="Module content creation with R410A integration",
                skill_type=SkillType.COMMAND,
                location=str(self.skills_dir / "create-module"),
                invocation="/create-module [module_id]",
                dependencies=["source-first"],
                requires_source_first=True,
                tags=["content", "module", "r410a"]
            ),
            SkillMetadata(
                skill_id="walkthrough",
                name="Walkthrough",
                description="Interactive walkthrough with Source-First verification",
                skill_type=SkillType.COMMAND,
                location=str(self.skills_dir / "walkthrough"),
                invocation="/walkthrough [day_number]",
                dependencies=["source-first"],
                requires_source_first=True,
                tags=["content", "walkthrough", "verification"]
            ),
            SkillMetadata(
                skill_id="qa",
                name="Q&A Capture",
                description="Active learning Q&A capture with smart model routing",
                skill_type=SkillType.COMMAND,
                location=str(self.skills_dir / "qa"),
                invocation="/qa --day X --section Y",
                tags=["qa", "interactive"]
            ),
            SkillMetadata(
                skill_id="source-first",
                name="Source-First",
                description="Ground truth extraction methodology",
                skill_type=SkillType.METHODOLOGY,
                location=str(self.skills_dir / "source-first"),
                requires_source_first=True,
                tags=["methodology", "verification", "ground-truth"]
            ),
            SkillMetadata(
                skill_id="systematic_debugging",
                name="Systematic Debugging",
                description="Iron Law debugging process - root cause first",
                skill_type=SkillType.METHODOLOGY,
                location=str(self.skills_dir / "systematic_debugging"),
                tags=["methodology", "debugging"]
            ),
            SkillMetadata(
                skill_id="git-operations",
                name="Git Operations",
                description="Git best practices and conventional commits",
                skill_type=SkillType.REFERENCE,
                location=str(self.skills_dir / "git-operations"),
                tags=["reference", "git"]
            ),
            SkillMetadata(
                skill_id="mermaid_expert",
                name="Mermaid Expert",
                description="Advanced diagram generation specialist",
                skill_type=SkillType.SPECIALIST,
                location=str(self.skills_dir / "mermaid_expert"),
                tags=["specialist", "diagrams", "mermaid"]
            ),
            SkillMetadata(
                skill_id="claude_code_guide",
                name="Claude Code Guide",
                description="Claude Code usage guide and best practices",
                skill_type=SkillType.REFERENCE,
                location=str(self.skills_dir / "claude_code_guide"),
                tags=["reference", "claude-code"]
            ),
            SkillMetadata(
                skill_id="cpp_pro",
                name="C++ Pro",
                description="Modern C++ best practices with OpenFOAM awareness",
                skill_type=SkillType.SPECIALIST,
                location=str(self.skills_dir / "cpp_pro"),
                tags=["specialist", "cpp", "openfoam"]
            ),
            SkillMetadata(
                skill_id="scientific_skills",
                name="Scientific Skills",
                description="LaTeX and physics analysis support",
                skill_type=SkillType.SPECIALIST,
                location=str(self.skills_dir / "scientific_skills"),
                tags=["specialist", "latex", "physics"]
            )
        ]

        for skill in builtin_skills:
            self.register_skill(skill)

    def register_skill(self, metadata: SkillMetadata):
        """Register a skill with its metadata"""
        self.skills[metadata.skill_id] = metadata
        self.dependencies[metadata.skill_id] = metadata.dependencies

    def discover_skills(self, directory: Optional[str] = None) -> int:
        """
        Auto-discover skills from directory structure.

        Scans for SKILL.md files and registers skills.
        """
        search_dir = Path(directory) if directory else self.skills_dir
        discovered = 0

        for skill_path in search_dir.iterdir():
            if skill_path.is_dir() and not skill_path.name.startswith('_'):
                skill_md = skill_path / "SKILL.md"
                if skill_md.exists():
                    # Extract metadata from SKILL.md
                    metadata = self._parse_skill_md(skill_path, skill_md)
                    if metadata and metadata.skill_id not in self.skills:
                        self.register_skill(metadata)
                        discovered += 1

        return discovered

    def _parse_skill_md(self, skill_path: Path, skill_md: Path) -> Optional[SkillMetadata]:
        """Parse SKILL.md file to extract metadata"""
        try:
            content = skill_md.read_text()

            # Extract YAML frontmatter
            if content.startswith('---'):
                parts = content.split('---', 2)
                if len(parts) >= 2:
                    frontmatter = parts[1]
                    try:
                        data = yaml.safe_load(frontmatter) or {}
                        return SkillMetadata(
                            skill_id=skill_path.name,
                            name=data.get('name', skill_path.name),
                            description=data.get('description', ''),
                            skill_type=SkillType(data.get('type', 'reference')),
                            location=str(skill_path),
                            invocation=data.get('usage'),
                            dependencies=data.get('dependencies', []),
                            requires_source_first=data.get('requires_source_first', False),
                            tags=data.get('tags', [])
                        )
                    except yaml.YAMLError:
                        pass

            # Fallback: basic metadata from directory
            return SkillMetadata(
                skill_id=skill_path.name,
                name=skill_path.name.replace('_', ' ').title(),
                description=f"Skill at {skill_path}",
                skill_type=SkillType.REFERENCE,
                location=str(skill_path)
            )
        except Exception as e:
            print(f"Warning: Failed to parse {skill_md}: {e}")
            return None

    def get_skill(self, skill_id: str) -> Optional[SkillMetadata]:
        """Get skill metadata by ID"""
        return self.skills.get(skill_id)

    def get_skills_by_type(self, skill_type: SkillType) -> List[SkillMetadata]:
        """Get all skills of a specific type"""
        return [s for s in self.skills.values() if s.skill_type == skill_type]

    def get_skills_by_tag(self, tag: str) -> List[SkillMetadata]:
        """Get all skills with a specific tag"""
        return [s for s in self.skills.values() if tag in s.tags]

    def resolve_dependencies(self, skill_ids: List[str]) -> List[str]:
        """
        Resolve skill dependencies using topological sort.

        Returns skills in execution order (dependencies first).
        Raises CycleError if circular dependencies detected.
        """
        visited: Set[str] = set()
        temp_visited: Set[str] = set()
        result: List[str] = []

        def visit(skill_id: str):
            if skill_id in temp_visited:
                raise ValueError(f"Circular dependency detected involving {skill_id}")
            if skill_id in visited:
                return

            temp_visited.add(skill_id)

            # Visit dependencies first
            for dep in self.dependencies.get(skill_id, []):
                if dep in self.skills:
                    visit(dep)

            temp_visited.remove(skill_id)
            visited.add(skill_id)
            result.append(skill_id)

        for skill_id in skill_ids:
            if skill_id in self.skills:
                visit(skill_id)

        return result

    def list_skills(self, skill_type: Optional[SkillType] = None) -> List[SkillMetadata]:
        """List all registered skills, optionally filtered by type"""
        if skill_type:
            return self.get_skills_by_type(skill_type)
        return list(self.skills.values())

    def to_dict(self) -> dict:
        """Export registry state to dictionary"""
        return {
            "skills": {
                skill_id: metadata.to_dict()
                for skill_id, metadata in self.skills.items()
            },
            "dependencies": self.dependencies
        }


def main():
    """CLI for skill registry operations"""
    import argparse

    parser = argparse.ArgumentParser(description="Skill Registry CLI")
    parser.add_argument("--list", action="store_true", help="List all skills")
    parser.add_argument("--type", choices=[t.value for t in SkillType],
                       help="Filter by skill type")
    parser.add_argument("--resolve", nargs="+", metavar="SKILL",
                       help="Resolve dependencies for skills")
    parser.add_argument("--discover", metavar="DIR",
                       help="Discover skills from directory")

    args = parser.parse_args()

    registry = SkillRegistry()

    if args.discover:
        count = registry.discover_skills(args.discover)
        print(f"Discovered {count} new skills")

    if args.resolve:
        try:
            ordered = registry.resolve_dependencies(args.resolve)
            print("Execution order:", " → ".join(ordered))
        except ValueError as e:
            print(f"Error: {e}")

    if args.list:
        filter_type = SkillType(args.type) if args.type else None
        skills = registry.list_skills(filter_type)

        print(f"\nRegistered Skills ({len(skills)} total):")
        print("=" * 60)

        for skill in sorted(skills, key=lambda s: s.skill_id):
            print(f"\n{skill.skill_id}")
            print(f"  Name: {skill.name}")
            print(f"  Type: {skill.skill_type.value}")
            print(f"  Description: {skill.description}")
            if skill.invocation:
                print(f"  Usage: {skill.invocation}")
            if skill.dependencies:
                print(f"  Depends on: {', '.join(skill.dependencies)}")
            if skill.tags:
                print(f"  Tags: {', '.join(skill.tags)}")


if __name__ == "__main__":
    main()
