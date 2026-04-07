"""Skill management for Analytic Engine"""

from __future__ import annotations
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass, field


@dataclass
class Skill:
    """Represents a skill loaded from markdown file"""

    name: str
    category: str
    content: str
    file_path: Path
    description: str = ""
    tags: List[str] = field(default_factory=list)


class SkillManager:
    """Manages skills loaded from markdown files"""

    def __init__(self, skills_dir: Optional[str | Path] = None):
        self._skills: Dict[str, Skill] = {}
        self._categories: Dict[str, List[str]] = {}

        if skills_dir is None:
            base_dir = Path(__file__).parent.parent.parent.parent
            skills_dir = base_dir / "skills"

        if isinstance(skills_dir, str):
            skills_dir = Path(skills_dir)

        self.skills_dir = Path(skills_dir)
        if self.skills_dir.exists():
            self.load_all_skills()

    def load_all_skills(self) -> None:
        """Load all skill files from skills directory"""
        if not self.skills_dir.exists():
            return

        for category_dir in self.skills_dir.iterdir():
            if not category_dir.is_dir():
                continue

            category = category_dir.name
            for skill_file in category_dir.glob("*.md"):
                skill = self._load_skill_file(skill_file, category)
                if skill:
                    self._skills[skill.name.lower()] = skill

                    if category not in self._categories:
                        self._categories[category] = []
                    self._categories[category].append(skill.name.lower())

    def _load_skill_file(self, file_path: Path, category: str) -> Optional[Skill]:
        """Load a single skill file"""
        try:
            content = file_path.read_text(encoding="utf-8")

            lines = content.split("\n")
            title = ""
            description = ""

            for i, line in enumerate(lines):
                if line.startswith("# "):
                    title = line[2:].strip()
                elif line.startswith("## "):
                    break
                elif i > 0 and line.strip():
                    description = line.strip()
                    break

            if not title:
                title = file_path.stem.replace("_", " ").title()

            tags = self._extract_tags(content)

            return Skill(
                name=title,
                category=category,
                content=content,
                file_path=file_path,
                description=description[:200] if description else "",
                tags=tags,
            )
        except Exception:
            return None

    def _extract_tags(self, content: str) -> List[str]:
        """Extract tags from skill content"""
        tags = []
        for line in content.split("\n"):
            if line.strip().lower().startswith("tags:"):
                tag_str = line.split(":", 1)[1].strip()
                tags = [t.strip() for t in tag_str.split(",") if t.strip()]
                break
        return tags

    def get_skill(self, name: str) -> Optional[Skill]:
        """Get a skill by name"""
        name_lower = name.lower()
        if name_lower in self._skills:
            return self._skills[name_lower]

        for key, skill in self._skills.items():
            if name_lower in key or key in name_lower:
                return skill
        return None

    def get_skill_content(self, name: str) -> Optional[str]:
        """Get skill content by name"""
        skill = self.get_skill(name)
        return skill.content if skill else None

    def list_skills(self) -> List[str]:
        """List all available skill names"""
        return list(self._skills.keys())

    def list_categories(self) -> List[str]:
        """List all skill categories"""
        return list(self._categories.keys())

    def get_skills_by_category(self, category: str) -> List[Skill]:
        """Get all skills in a category"""
        skill_names = self._categories.get(category, [])
        return [self._skills[name] for name in skill_names if name in self._skills]

    def search_skills(self, query: str) -> List[Skill]:
        """Search skills by name or description"""
        query_lower = query.lower()
        results = []

        for skill in self._skills.values():
            if query_lower in skill.name.lower():
                results.append(skill)
            elif query_lower in skill.description.lower():
                results.append(skill)
            elif any(query_lower in tag.lower() for tag in skill.tags):
                results.append(skill)

        return results
