"""controllers/personal_info_controller.py — Kişisel bilgi koordinasyonu."""

import logging

from PySide6.QtCore import QObject, Signal

from services.personal_info_service import PersonalInfoService
from domain.exceptions.domain_exceptions import DomainException

logger = logging.getLogger(__name__)


class PersonalInfoController(QObject):
    info_changed   = Signal()
    error_occurred = Signal(str)

    def __init__(self, service: PersonalInfoService):
        super().__init__()
        self._service = service

    def get(self):
        return self._service.get()

    def update(self, data: dict):
        try:
            info = self._service.update(data)
            self.info_changed.emit()
            return info
        except DomainException as e:
            logger.exception("Kişisel bilgi güncelleme hatası")
            self.error_occurred.emit(str(e))
            return None
