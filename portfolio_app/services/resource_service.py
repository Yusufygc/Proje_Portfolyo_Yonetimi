"""services/resource_service.py — Kaynak iş kuralları."""

import logging

from services.interfaces.i_service import IResourceService
from infrastructure.repositories.resource_repository import ResourceRepository
from domain.models.resource import Resource
from domain.enums.resource_type import ResourceType, ResourceStatus
from domain.exceptions.domain_exceptions import ValidationError

logger = logging.getLogger(__name__)


class ResourceService(IResourceService):
    def __init__(self, repo: ResourceRepository):
        self._repo = repo

    def get_all(self) -> list[Resource]:
        return self._repo.get_all()

    def get_by_type(self, resource_type: ResourceType) -> list[Resource]:
        return self._repo.get_by_type(resource_type)

    def get_by_id(self, resource_id: int) -> Resource:
        return self._repo.get_by_id(resource_id)

    def create(self, data: dict) -> Resource:
        self._validate(data)
        resource = Resource(
            id=None,
            type=ResourceType(data.get("type", ResourceType.KURS)),
            title=data["title"].strip(),
            url=data.get("url") or None,
            notes=data.get("notes", "").strip(),
            status=ResourceStatus(data.get("status", ResourceStatus.PLANLI)),
            related_project_id=data.get("related_project_id") or None,
        )
        return self._repo.create(resource)

    def update(self, resource_id: int, data: dict) -> Resource:
        self._validate(data)
        resource = self._repo.get_by_id(resource_id)
        resource.type = ResourceType(data.get("type", resource.type))
        resource.title = data["title"].strip()
        resource.url = data.get("url") or None
        resource.notes = data.get("notes", "").strip()
        resource.status = ResourceStatus(data.get("status", resource.status))
        resource.related_project_id = data.get("related_project_id") or None
        return self._repo.update(resource)

    def delete(self, resource_id: int) -> None:
        self._repo.delete(resource_id)

    @staticmethod
    def _validate(data: dict) -> None:
        if not data.get("title", "").strip():
            raise ValidationError("Kaynak başlığı boş olamaz.")
