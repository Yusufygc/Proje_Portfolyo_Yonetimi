"""controllers/education_controller.py — Eğitim CRUD koordinasyonu."""

import logging

from PySide6.QtCore import QObject, Signal

from services.education_service import EducationService
from domain.exceptions.domain_exceptions import DomainException

logger = logging.getLogger(__name__)


class EducationController(QObject):
    """Eğitim CRUD işlemlerini koordine eder."""

    education_changed = Signal()
    error_occurred    = Signal(str)

    def __init__(self, service: EducationService):
        super().__init__()
        self._service = service

    def get_all(self):
        """Tüm eğitim kayıtlarını döner."""
        return self._service.get_all()

    def get_by_id(self, edu_id: int):
        """ID ile eğitim kaydı getirir."""
        return self._service.get_by_id(edu_id)

    def create(self, data: dict):
        """Yeni eğitim kaydı oluşturur."""
        try:
            edu = self._service.create(data)
            self.education_changed.emit()
            return edu
        except DomainException as e:
            logger.exception("Eğitim kaydı oluşturma hatası")
            self.error_occurred.emit(str(e))
            return None

    def update(self, edu_id: int, data: dict):
        """Eğitim kaydını günceller."""
        try:
            edu = self._service.update(edu_id, data)
            self.education_changed.emit()
            return edu
        except DomainException as e:
            logger.exception("Eğitim kaydı güncelleme hatası")
            self.error_occurred.emit(str(e))
            return None

    def delete(self, edu_id: int):
        """Eğitim kaydını siler."""
        try:
            self._service.delete(edu_id)
            self.education_changed.emit()
        except DomainException as e:
            logger.exception("Eğitim kaydı silme hatası")
            self.error_occurred.emit(str(e))
