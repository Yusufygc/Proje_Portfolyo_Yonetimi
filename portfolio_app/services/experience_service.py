"""services/experience_service.py — İş deneyimi iş kuralları."""

import logging

from infrastructure.repositories.experience_repository import ExperienceRepository
from domain.models.experience import Experience
from domain.exceptions.domain_exceptions import ValidationError

logger = logging.getLogger(__name__)


class ExperienceService:
    def __init__(self, repo: ExperienceRepository):
        self._repo = repo

    def get_all(self) -> list[Experience]:
        """Tüm deneyim kayıtlarını döner."""
        return self._repo.get_all()

    def get_by_id(self, exp_id: int) -> Experience:
        """ID ile deneyim kaydı getirir."""
        return self._repo.get_by_id(exp_id)

    def create(self, data: dict) -> Experience:
        """Yeni deneyim kaydı oluşturur."""
        self._validate(data)
        exp = Experience(
            id=None,
            company=data["company"].strip(),
            position=data.get("position", "").strip(),
            start_date=data.get("start_date", "").strip(),
            end_date=data.get("end_date") or None,
            description=data.get("description") or None,
            is_current=bool(data.get("is_current", False)),
            display_order=int(data.get("display_order", 0)),
        )
        return self._repo.create(exp)

    def update(self, exp_id: int, data: dict) -> Experience:
        """Mevcut deneyim kaydını günceller."""
        self._validate(data)
        exp = self._repo.get_by_id(exp_id)
        exp.company = data["company"].strip()
        exp.position = data.get("position", "").strip()
        exp.start_date = data.get("start_date", "").strip()
        exp.end_date = data.get("end_date") or None
        exp.description = data.get("description") or None
        exp.is_current = bool(data.get("is_current", False))
        exp.display_order = int(data.get("display_order", 0))
        return self._repo.update(exp)

    def delete(self, exp_id: int) -> None:
        """Deneyim kaydını siler."""
        self._repo.delete(exp_id)

    @staticmethod
    def _validate(data: dict) -> None:
        if not data.get("company", "").strip():
            raise ValidationError("Şirket adı boş olamaz.")
