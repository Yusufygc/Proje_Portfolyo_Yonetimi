"""domain/models/experience.py — İş deneyimi entity."""

from dataclasses import dataclass
from typing import Optional


@dataclass
class Experience:
    id: Optional[int]
    company: str
    position: str
    start_date: str = ""
    end_date: Optional[str] = None
    description: Optional[str] = None
    is_current: bool = False
    display_order: int = 0
    created_at: str = ""
