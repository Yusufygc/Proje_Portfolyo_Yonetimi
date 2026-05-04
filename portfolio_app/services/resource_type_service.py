"""services/resource_type_service.py — Kaynak türü iş kuralları."""

import logging

from infrastructure.repositories.resource_type_repository import ResourceTypeRepository
from domain.models.resource_type_model import ResourceTypeDynamic
from domain.exceptions.domain_exceptions import ValidationError

logger = logging.getLogger(__name__)


class ResourceTypeService:
    def __init__(self, repo: ResourceTypeRepository):
        self._repo = repo

    def get_all(self) -> list[ResourceTypeDynamic]:
        return self._repo.get_all()

    def get_by_id(self, type_id: int) -> ResourceTypeDynamic:
        return self._repo.get_by_id(type_id)

    def create(self, data: dict) -> ResourceTypeDynamic:
        self._validate(data)
        existing = self._repo.get_by_name(data["name"].strip())
        if existing:
            raise ValidationError(f'"{data["name"]}" adlı tür zaten mevcut.')
        rt = ResourceTypeDynamic(
            id=None,
            name=data["name"].strip(),
            color=data.get("color", "#2F81F7"),
            emoji=data.get("emoji", "📄"),
            display_order=data.get("display_order", 0),
        )
        return self._repo.create(rt)

    def update(self, type_id: int, data: dict) -> ResourceTypeDynamic:
        self._validate(data)
        rt = self._repo.get_by_id(type_id)
        # İsim değiştiyse benzersizlik kontrolü
        new_name = data["name"].strip()
        if new_name != rt.name:
            existing = self._repo.get_by_name(new_name)
            if existing:
                raise ValidationError(f'"{new_name}" adlı tür zaten mevcut.')
        rt.name = new_name
        rt.color = data.get("color", rt.color)
        rt.emoji = data.get("emoji", rt.emoji)
        rt.display_order = data.get("display_order", rt.display_order)
        return self._repo.update(rt)

    def delete(self, type_id: int) -> None:
        rt = self._repo.get_by_id(type_id)
        count = self._repo.count_resources_by_type(rt.name)
        if count > 0:
            raise ValidationError(
                f'"{rt.name}" türünde {count} kaynak bulunuyor. '
                f'Önce bu kaynakları silin veya türünü değiştirin.'
            )
        self._repo.delete(type_id)

    @staticmethod
    def _validate(data: dict) -> None:
        if not data.get("name", "").strip():
            raise ValidationError("Tür adı boş olamaz.")
