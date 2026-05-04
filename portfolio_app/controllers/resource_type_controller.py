"""controllers/resource_type_controller.py — Kaynak türü CRUD koordinasyonu."""

import logging

from PySide6.QtCore import QObject, Signal

from services.resource_type_service import ResourceTypeService
from domain.exceptions.domain_exceptions import DomainException

logger = logging.getLogger(__name__)


class ResourceTypeController(QObject):
    types_changed  = Signal()
    error_occurred = Signal(str)

    def __init__(self, service: ResourceTypeService):
        super().__init__()
        self._service = service

    def get_all(self):
        return self._service.get_all()

    def get_by_id(self, type_id: int):
        return self._service.get_by_id(type_id)

    def create(self, data: dict):
        try:
            rt = self._service.create(data)
            self.types_changed.emit()
            return rt
        except DomainException as e:
            logger.exception("Kaynak türü oluşturma hatası")
            self.error_occurred.emit(str(e))
            return None

    def update(self, type_id: int, data: dict):
        try:
            rt = self._service.update(type_id, data)
            self.types_changed.emit()
            return rt
        except DomainException as e:
            logger.exception("Kaynak türü güncelleme hatası")
            self.error_occurred.emit(str(e))
            return None

    def delete(self, type_id: int):
        try:
            self._service.delete(type_id)
            self.types_changed.emit()
        except DomainException as e:
            logger.exception("Kaynak türü silme hatası")
            self.error_occurred.emit(str(e))
