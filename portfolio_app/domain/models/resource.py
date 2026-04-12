"""domain/models/resource.py — Kaynak entity."""

from dataclasses import dataclass
from typing import Optional

from domain.enums.resource_type import ResourceType, ResourceStatus


@dataclass
class Resource:
    id: Optional[int]
    type: ResourceType
    title: str
    url: Optional[str] = None
    notes: str = ""
    status: ResourceStatus = ResourceStatus.PLANLI
    related_project_id: Optional[int] = None
    created_at: str = ""
