"""services/project_service.py — Proje iş kuralları."""

import logging

from services.interfaces.i_service import IProjectService
from infrastructure.repositories.project_repository import ProjectRepository
from infrastructure.repositories.task_repository import TaskRepository
from infrastructure.storage.image_storage import ImageStorage
from domain.models.project import Project, ProjectTag, ProjectImage
from domain.models.task import Task
from domain.enums.project_status import ProjectStatus
from domain.enums.task_type import TaskType, TaskStatus
from domain.exceptions.domain_exceptions import ValidationError

logger = logging.getLogger(__name__)


class ProjectService(IProjectService):
    def __init__(self, repo: ProjectRepository, task_repo: TaskRepository, storage: ImageStorage):
        self._repo = repo
        self._task_repo = task_repo
        self._storage = storage

    def get_all(self) -> list[Project]:
        return self._repo.get_all()

    def get_featured(self) -> list[Project]:
        return self._repo.get_featured()

    def get_by_id(self, project_id: int) -> Project:
        return self._repo.get_by_id(project_id)

    def create(self, data: dict) -> Project:
        self._validate(data)
        tags = [ProjectTag(id=None, project_id=0, tag_name=t.strip())
                for t in data.get("tags", []) if t.strip()]
        project = Project(
            id=None,
            title=data["title"],
            short_description=data.get("short_description", ""),
            full_description=data.get("full_description", ""),
            status=ProjectStatus(data.get("status", ProjectStatus.DEVAM_EDIYOR)),
            github_url=data.get("github_url") or None,
            demo_url=data.get("demo_url") or None,
            start_date=data.get("start_date") or None,
            end_date=data.get("end_date") or None,
            is_featured=bool(data.get("is_featured", False)),
            display_order=int(data.get("display_order", 0)),
            tags=tags,
        )
        return self._repo.create(project)

    def update(self, project_id: int, data: dict) -> Project:
        self._validate(data)
        project = self._repo.get_by_id(project_id)
        project.title = data["title"]
        project.short_description = data.get("short_description", "")
        project.full_description = data.get("full_description", "")
        project.status = ProjectStatus(data.get("status", project.status))
        project.github_url = data.get("github_url") or None
        project.demo_url = data.get("demo_url") or None
        project.start_date = data.get("start_date") or None
        project.end_date = data.get("end_date") or None
        project.is_featured = bool(data.get("is_featured", False))
        project.display_order = int(data.get("display_order", 0))
        project.tags = [
            ProjectTag(id=None, project_id=project_id, tag_name=t.strip())
            for t in data.get("tags", []) if t.strip()
        ]
        return self._repo.update(project)

    def delete(self, project_id: int) -> None:
        self._repo.delete(project_id)

    def add_image(self, project_id: int, source_path: str) -> ProjectImage:
        stored_path = self._storage.save_project_image(source_path, project_id)
        image = ProjectImage(id=None, project_id=project_id, image_path=stored_path)
        return self._repo.add_image(image)

    def delete_image(self, image_id: int, image_path: str) -> None:
        self._storage.delete(image_path)
        self._repo.delete_image(image_id)

    # ── Task işlemleri ──────────────────────────────────────────────────────

    def get_tasks(self, project_id: int) -> list[Task]:
        return self._task_repo.get_by_project(project_id)

    def create_task(self, project_id: int, data: dict) -> Task:
        if not data.get("title", "").strip():
            raise ValidationError("Task başlığı boş olamaz.")
        task = Task(
            id=None,
            project_id=project_id,
            type=TaskType(data.get("type", TaskType.GOREV)),
            title=data["title"].strip(),
            description=data.get("description", ""),
            status=TaskStatus(data.get("status", TaskStatus.BEKLIYOR)),
            display_order=int(data.get("display_order", 0)),
        )
        return self._task_repo.create(task)

    def update_task(self, task_id: int, data: dict) -> Task:
        task = self._task_repo.get_by_id(task_id)
        task.type = TaskType(data.get("type", task.type))
        task.title = data.get("title", task.title).strip()
        task.description = data.get("description", task.description)
        task.status = TaskStatus(data.get("status", task.status))
        task.display_order = int(data.get("display_order", task.display_order))
        return self._task_repo.update(task)

    def delete_task(self, task_id: int) -> None:
        self._task_repo.delete(task_id)

    @staticmethod
    def _validate(data: dict) -> None:
        if not data.get("title", "").strip():
            raise ValidationError("Proje başlığı boş olamaz.")
