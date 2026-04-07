"""Skill tool for agent to retrieve skill context"""

from __future__ import annotations
from pathlib import Path
from typing import Dict, Any, Optional, Callable
from dataclasses import dataclass

from .manager import SkillManager
from ..types import ExecutionResult


@dataclass
class SkillToolResult:
    """Result from skill tool execution"""

    success: bool
    skill_name: str
    content: str
    error: Optional[str] = None


class SkillTool:
    """Tool for agents to retrieve skill context (similar to /skill in OpenCode)"""

    def __init__(self, skills_dir: Optional[str | Path] = None):
        self.skill_manager = SkillManager() if skills_dir is None else SkillManager(skills_dir)

    def get_skill(self, skill_name: str) -> SkillToolResult:
        """Get skill by name and return as context for agent"""
        try:
            content = self.skill_manager.get_skill_content(skill_name)
            if content is None:
                available = ", ".join(self.skill_manager.list_skills())
                return SkillToolResult(
                    success=False,
                    skill_name=skill_name,
                    content="",
                    error=f"Skill '{skill_name}' not found. Available skills: {available}",
                )

            return SkillToolResult(success=True, skill_name=skill_name, content=content)
        except Exception as e:
            return SkillToolResult(success=False, skill_name=skill_name, content="", error=str(e))

    def list_skills(self) -> Dict[str, Any]:
        """List all available skills"""
        return {
            "skills": self.skill_manager.list_skills(),
            "categories": self.skill_manager.list_categories(),
        }

    def search_skills(self, query: str) -> Dict[str, Any]:
        """Search skills by query"""
        results = self.skill_manager.search_skills(query)
        return {
            "query": query,
            "results": [
                {"name": s.name, "category": s.category, "description": s.description}
                for s in results
            ],
        }

    def get_skill_for_task(self, task_description: str) -> SkillToolResult:
        """Automatically find best matching skill for task"""
        results = self.skill_manager.search_skills(task_description)

        if not results:
            return SkillToolResult(
                success=False,
                skill_name="",
                content="",
                error=f"No matching skill found for: {task_description}",
            )

        best_match = results[0]
        return self.get_skill(best_match.name)


def create_skill_tool(skills_dir: Optional[str] = None) -> Callable[[str], SkillToolResult]:
    """Create a skill tool function for agent use"""
    tool = SkillTool(skills_dir)

    def get_skill(skill_name: str) -> SkillToolResult:
        return tool.get_skill(skill_name)

    return get_skill
