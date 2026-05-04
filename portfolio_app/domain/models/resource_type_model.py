"""domain/models/resource_type_model.py — Dinamik kaynak türü entity."""

from dataclasses import dataclass
from typing import Optional


@dataclass
class ResourceTypeDynamic:
    """DB'den yönetilen kaynak türü."""
    id: Optional[int]
    name: str
    color: str = "#2F81F7"
    emoji: str = "📄"
    display_order: int = 0
    created_at: str = ""

    def label(self) -> str:
        return self.name
