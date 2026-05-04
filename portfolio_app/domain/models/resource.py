"""domain/models/resource.py — Kaynak entity."""

from dataclasses import dataclass, field
from typing import Optional

from domain.enums.resource_type import ResourceStatus, ResourcePriority


@dataclass
class Resource:
    id: Optional[int]
    type: str                                          # Dinamik tür adı (DB'den)
    title: str
    url: Optional[str] = None
    notes: str = ""
    status: ResourceStatus = ResourceStatus.PLANLI
    priority: ResourcePriority = ResourcePriority.MEDIUM
    progress: int = 0                                  # 0-100
    is_pinned: bool = False
    related_project_id: Optional[int] = None
    tags: list[str] = field(default_factory=list)
    created_at: str = ""

    # Ek alanlar (join ile doldurulur, DB'ye yazılmaz)
    related_project_title: Optional[str] = None
    type_color: str = "#2F81F7"
    type_emoji: str = "📄"
