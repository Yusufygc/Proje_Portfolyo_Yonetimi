"""services/education_service.py — Eğitim iş kuralları."""

import logging

from infrastructure.repositories.education_repository import EducationRepository
from domain.models.education import Education
from domain.exceptions.domain_exceptions import ValidationError

logger = logging.getLogger(__name__)


class EducationService:
    def __init__(self, repo: EducationRepository):
        self._repo = repo

    def get_all(self) -> list[Education]:
        """Tüm eğitim kayıtlarını döner."""
        return self._repo.get_all()

    def get_by_id(self, edu_id: int) -> Education:
        """ID ile eğitim kaydı getirir."""
        return self._repo.get_by_id(edu_id)

    def create(self, data: dict) -> Education:
        """Yeni eğitim kaydı oluşturur."""
        self._validate(data)
        edu = Education(
            id=None,
            institution=data["institution"].strip(),
            degree=data.get("degree", "").strip(),
            field=data.get("field", "").strip(),
            start_date=data.get("start_date", "").strip(),
            end_date=data.get("end_date") or None,
            description=data.get("description") or None,
            display_order=int(data.get("display_order", 0)),
        )
        return self._repo.create(edu)

    def update(self, edu_id: int, data: dict) -> Education:
        """Mevcut eğitim kaydını günceller."""
        self._validate(data)
        edu = self._repo.get_by_id(edu_id)
        edu.institution = data["institution"].strip()
        edu.degree = data.get("degree", "").strip()
        edu.field = data.get("field", "").strip()
        edu.start_date = data.get("start_date", "").strip()
        edu.end_date = data.get("end_date") or None
        edu.description = data.get("description") or None
        edu.display_order = int(data.get("display_order", 0))
        return self._repo.update(edu)

    def delete(self, edu_id: int) -> None:
        """Eğitim kaydını siler."""
        self._repo.delete(edu_id)

    @staticmethod
    def _validate(data: dict) -> None:
        if not data.get("institution", "").strip():
            raise ValidationError("Kurum adı boş olamaz.")
