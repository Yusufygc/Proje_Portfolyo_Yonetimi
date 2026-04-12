"""controllers/project_controller.py — Proje CRUD koordinasyonu."""

import logging

from PySide6.QtCore import QObject, Signal

from services.project_service import ProjectService
from domain.exceptions.domain_exceptions import DomainException

logger = logging.getLogger(__name__)


class ProjectController(QObject):
    projects_changed = Signal()
    error_occurred   = Signal(str)

    def __init__(self, service: ProjectService):
        super().__init__()
        self._service = service

    def get_all(self):
        return self._service.get_all()

    def get_by_id(self, project_id: int):
        return self._service.get_by_id(project_id)

    def create(self, data: dict):
        try:
            project = self._service.create(data)
            self.projects_changed.emit()
            return project
        except DomainException as e:
            logger.exception("Proje oluşturma hatası")
            self.error_occurred.emit(str(e))
            return None

    def update(self, project_id: int, data: dict):
        try:
            project = self._service.update(project_id, data)
            self.projects_changed.emit()
            return project
        except DomainException as e:
            logger.exception("Proje güncelleme hatası")
            self.error_occurred.emit(str(e))
            return None

    def delete(self, project_id: int):
        try:
            self._service.delete(project_id)
            self.projects_changed.emit()
        except DomainException as e:
            logger.exception("Proje silme hatası")
            self.error_occurred.emit(str(e))

    def add_image(self, project_id: int, source_path: str):
        try:
            return self._service.add_image(project_id, source_path)
        except DomainException as e:
            self.error_occurred.emit(str(e))
            return None

    def delete_image(self, image_id: int, image_path: str):
        try:
            self._service.delete_image(image_id, image_path)
        except DomainException as e:
            self.error_occurred.emit(str(e))

    # ── Task'lar ──────────────────────────────────────────────────────────────

    def get_tasks(self, project_id: int):
        return self._service.get_tasks(project_id)

    def create_task(self, project_id: int, data: dict):
        try:
            task = self._service.create_task(project_id, data)
            self.projects_changed.emit()
            return task
        except DomainException as e:
            self.error_occurred.emit(str(e))
            return None

    def update_task(self, task_id: int, data: dict):
        try:
            task = self._service.update_task(task_id, data)
            self.projects_changed.emit()
            return task
        except DomainException as e:
            self.error_occurred.emit(str(e))
            return None

    def delete_task(self, task_id: int):
        try:
            self._service.delete_task(task_id)
            self.projects_changed.emit()
        except DomainException as e:
            self.error_occurred.emit(str(e))
