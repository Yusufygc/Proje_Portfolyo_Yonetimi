"""domain/models/skill.py — Beceri / Yetenek entity."""

from dataclasses import dataclass
from typing import Optional

@dataclass
class Skill:
    id: Optional[int]
    name: str
    category: str = ""
    rating: int = 0
    icon_path: str = ""
    display_order: int = 0
    created_at: str = ""
