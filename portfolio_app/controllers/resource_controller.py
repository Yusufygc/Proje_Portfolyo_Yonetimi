"""controllers/resource_controller.py — Kaynak CRUD koordinasyonu."""

import logging

from PySide6.QtCore import QObject, Signal

from services.resource_service import ResourceService
from domain.enums.resource_type import ResourceType
from domain.exceptions.domain_exceptions import DomainException

logger = logging.getLogger(__name__)


class ResourceController(QObject):
    resources_changed = Signal()
    error_occurred    = Signal(str)

    def __init__(self, service: ResourceService):
        super().__init__()
        self._service = service

    def get_all(self):
        return self._service.get_all()

    def get_by_type(self, resource_type: ResourceType):
        return self._service.get_by_type(resource_type)

    def get_by_id(self, resource_id: int):
        return self._service.get_by_id(resource_id)

    def create(self, data: dict):
        try:
            resource = self._service.create(data)
            self.resources_changed.emit()
            return resource
        except DomainException as e:
            logger.exception("Kaynak oluşturma hatası")
            self.error_occurred.emit(str(e))
            return None

    def update(self, resource_id: int, data: dict):
        try:
            resource = self._service.update(resource_id, data)
            self.resources_changed.emit()
            return resource
        except DomainException as e:
            logger.exception("Kaynak güncelleme hatası")
            self.error_occurred.emit(str(e))
            return None

    def delete(self, resource_id: int):
        try:
            self._service.delete(resource_id)
            self.resources_changed.emit()
        except DomainException as e:
            logger.exception("Kaynak silme hatası")
            self.error_occurred.emit(str(e))
