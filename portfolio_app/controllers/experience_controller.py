"""controllers/experience_controller.py — İş deneyimi CRUD koordinasyonu."""

import logging

from PySide6.QtCore import QObject, Signal

from services.experience_service import ExperienceService
from domain.exceptions.domain_exceptions import DomainException

logger = logging.getLogger(__name__)


class ExperienceController(QObject):
    """İş deneyimi CRUD işlemlerini koordine eder."""

    experience_changed = Signal()
    error_occurred     = Signal(str)

    def __init__(self, service: ExperienceService):
        super().__init__()
        self._service = service

    def get_all(self):
        """Tüm deneyim kayıtlarını döner."""
        return self._service.get_all()

    def get_by_id(self, exp_id: int):
        """ID ile deneyim kaydı getirir."""
        return self._service.get_by_id(exp_id)

    def create(self, data: dict):
        """Yeni deneyim kaydı oluşturur."""
        try:
            exp = self._service.create(data)
            self.experience_changed.emit()
            return exp
        except DomainException as e:
            logger.exception("Deneyim kaydı oluşturma hatası")
            self.error_occurred.emit(str(e))
            return None

    def update(self, exp_id: int, data: dict):
        """Deneyim kaydını günceller."""
        try:
            exp = self._service.update(exp_id, data)
            self.experience_changed.emit()
            return exp
        except DomainException as e:
            logger.exception("Deneyim kaydı güncelleme hatası")
            self.error_occurred.emit(str(e))
            return None

    def delete(self, exp_id: int):
        """Deneyim kaydını siler."""
        try:
            self._service.delete(exp_id)
            self.experience_changed.emit()
        except DomainException as e:
            logger.exception("Deneyim kaydı silme hatası")
            self.error_occurred.emit(str(e))
