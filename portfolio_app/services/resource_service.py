"""services/resource_service.py — Kaynak iş kuralları."""

import logging

from infrastructure.repositories.resource_repository import ResourceRepository
from domain.models.resource import Resource
from domain.enums.resource_type import ResourceStatus, ResourcePriority
from domain.exceptions.domain_exceptions import ValidationError

logger = logging.getLogger(__name__)


class ResourceService:
    def __init__(self, repo: ResourceRepository):
        self._repo = repo

    def get_all(self, sort_by: str = "created_at", sort_dir: str = "DESC") -> list[Resource]:
        return self._repo.get_all(sort_by, sort_dir)

    def get_by_type(self, type_name: str) -> list[Resource]:
        return self._repo.get_by_type(type_name)

    def get_by_id(self, resource_id: int) -> Resource:
        return self._repo.get_by_id(resource_id)

    def search(self, query: str) -> list[Resource]:
        return self._repo.search(query)

    def get_stats(self) -> dict:
        return self._repo.get_stats()

    def create(self, data: dict) -> Resource:
        self._validate(data)
        resource = Resource(
            id=None,
            type=data.get("type", "Kurs"),
            title=data["title"].strip(),
            url=data.get("url") or None,
            notes=data.get("notes", "").strip(),
            status=ResourceStatus(data.get("status", ResourceStatus.PLANLI.value)),
            priority=ResourcePriority(data.get("priority", ResourcePriority.MEDIUM.value)),
            progress=data.get("progress", 0),
            is_pinned=data.get("is_pinned", False),
            related_project_id=data.get("related_project_id") or None,
            tags=data.get("tags", []),
        )
        return self._repo.create(resource)

    def update(self, resource_id: int, data: dict) -> Resource:
        self._validate(data)
        resource = self._repo.get_by_id(resource_id)
        resource.type = data.get("type", resource.type)
        resource.title = data["title"].strip()
        resource.url = data.get("url") or None
        resource.notes = data.get("notes", "").strip()
        resource.status = ResourceStatus(data.get("status", resource.status.value))
        resource.priority = ResourcePriority(data.get("priority", resource.priority.value))
        resource.progress = data.get("progress", resource.progress)
        resource.is_pinned = data.get("is_pinned", resource.is_pinned)
        resource.related_project_id = data.get("related_project_id") or None
        resource.tags = data.get("tags", resource.tags)
        return self._repo.update(resource)

    def delete(self, resource_id: int) -> None:
        self._repo.delete(resource_id)

    def toggle_pin(self, resource_id: int) -> bool:
        return self._repo.toggle_pin(resource_id)

    def update_progress(self, resource_id: int, progress: int) -> None:
        if not 0 <= progress <= 100:
            raise ValidationError("İlerleme 0-100 arasında olmalıdır.")
        self._repo.update_progress(resource_id, progress)

    @staticmethod
    def _validate(data: dict) -> None:
        if not data.get("title", "").strip():
            raise ValidationError("Kaynak başlığı boş olamaz.")
