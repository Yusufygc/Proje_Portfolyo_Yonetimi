"""domain/models/education.py — Eğitim geçmişi entity."""

from dataclasses import dataclass
from typing import Optional


@dataclass
class Education:
    id: Optional[int]
    institution: str
    degree: str
    field: str = ""
    start_date: str = ""
    end_date: Optional[str] = None
    description: Optional[str] = None
    display_order: int = 0
    created_at: str = ""
