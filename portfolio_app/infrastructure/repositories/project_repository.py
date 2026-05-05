"""infrastructure/repositories/project_repository.py — Proje DB işlemleri."""

import logging
from typing import Optional

from infrastructure.database.db_manager import DBManager
from domain.models.project import Project, ProjectTag, ProjectImage
from domain.enums.project_status import ProjectStatus
from domain.exceptions.domain_exceptions import NotFoundError, DatabaseError

logger = logging.getLogger(__name__)


class ProjectRepository:
    def __init__(self, db: DBManager):
        self._db = db

    # ── Proje CRUD ───────────────────────────────────────────────────────────

    def get_all(self) -> list[Project]:
        rows = self._db.fetch_all(
            "SELECT * FROM projects ORDER BY display_order, created_at DESC"
        )
        projects = [self._row_to_project(r) for r in rows]
        for p in projects:
            p.tags = self.get_tags(p.id)
            p.images = self.get_images(p.id)
        return projects

    def get_featured(self) -> list[Project]:
        rows = self._db.fetch_all(
            "SELECT * FROM projects WHERE is_featured=1 ORDER BY display_order"
        )
        projects = [self._row_to_project(r) for r in rows]
        for p in projects:
            p.tags = self.get_tags(p.id)
            p.images = self.get_images(p.id)
        return projects

    def get_by_id(self, project_id: int) -> Project:
        row = self._db.fetch_one("SELECT * FROM projects WHERE id=?", (project_id,))
        if not row:
            raise NotFoundError(f"Proje bulunamadı: id={project_id}")
        project = self._row_to_project(row)
        project.tags = self.get_tags(project_id)
        project.images = self.get_images(project_id)
        return project

    def create(self, project: Project) -> Project:
        try:
            cursor = self._db.execute(
                """INSERT INTO projects
                   (title, short_description, full_description, status,
                    github_url, demo_url, start_date, end_date,
                    is_featured, display_order, role_in_project)
                   VALUES (?,?,?,?,?,?,?,?,?,?,?)""",
                (project.title, project.short_description, project.full_description,
                 project.status.value, project.github_url, project.demo_url,
                 project.start_date, project.end_date,
                 int(project.is_featured), project.display_order,
                 project.role_in_project),
            )
            project.id = cursor.lastrowid
            self._save_tags(project.id, project.tags)
            logger.info(f"Proje oluşturuldu: id={project.id}, title={project.title}")
            return project
        except Exception:
            logger.exception("Proje oluşturma hatası")
            raise DatabaseError("Proje oluşturulamadı.")

    def update(self, project: Project) -> Project:
        if not project.id:
            raise ValueError("Güncellenecek proje ID'si eksik.")
        try:
            self._db.execute(
                """UPDATE projects SET
                   title=?, short_description=?, full_description=?, status=?,
                   github_url=?, demo_url=?, start_date=?, end_date=?,
                   is_featured=?, display_order=?, role_in_project=?
                   WHERE id=?""",
                (project.title, project.short_description, project.full_description,
                 project.status.value, project.github_url, project.demo_url,
                 project.start_date, project.end_date,
                 int(project.is_featured), project.display_order,
                 project.role_in_project, project.id),
            )
            self._db.execute("DELETE FROM project_tags WHERE project_id=?", (project.id,))
            self._save_tags(project.id, project.tags)
            logger.info(f"Proje güncellendi: id={project.id}")
            return project
        except Exception:
            logger.exception("Proje güncelleme hatası")
            raise DatabaseError("Proje güncellenemedi.")

    def delete(self, project_id: int) -> None:
        self._db.execute("DELETE FROM projects WHERE id=?", (project_id,))
        logger.info(f"Proje silindi: id={project_id}")

    # ── Tag işlemleri ────────────────────────────────────────────────────────

    def get_tags(self, project_id: int) -> list[ProjectTag]:
        rows = self._db.fetch_all(
            "SELECT * FROM project_tags WHERE project_id=?", (project_id,)
        )
        return [ProjectTag(id=r["id"], project_id=r["project_id"], tag_name=r["tag_name"]) for r in rows]

    def _save_tags(self, project_id: int, tags: list[ProjectTag]) -> None:
        for tag in tags:
            self._db.execute(
                "INSERT INTO project_tags (project_id, tag_name) VALUES (?,?)",
                (project_id, tag.tag_name),
            )

    # ── Görsel işlemleri ─────────────────────────────────────────────────────

    def get_images(self, project_id: int) -> list[ProjectImage]:
        rows = self._db.fetch_all(
            "SELECT * FROM project_images WHERE project_id=? ORDER BY display_order",
            (project_id,),
        )
        return [
            ProjectImage(
                id=r["id"], project_id=r["project_id"],
                image_path=r["image_path"], caption=r["caption"] or "",
                display_order=r["display_order"],
            )
            for r in rows
        ]

    def add_image(self, image: ProjectImage) -> ProjectImage:
        cursor = self._db.execute(
            "INSERT INTO project_images (project_id, image_path, caption, display_order) VALUES (?,?,?,?)",
            (image.project_id, image.image_path, image.caption, image.display_order),
        )
        image.id = cursor.lastrowid
        return image

    def delete_image(self, image_id: int) -> None:
        self._db.execute("DELETE FROM project_images WHERE id=?", (image_id,))

    # ── Task işlemleri ──────────────────────────────────────────────────────

    def get_tasks(self, project_id: int):
        from infrastructure.repositories.task_repository import TaskRepository
        return TaskRepository(self._db).get_by_project(project_id)

    # ── Yardımcı ────────────────────────────────────────────────────────────

    @staticmethod
    def _row_to_project(row) -> Project:
        return Project(
            id=row["id"],
            title=row["title"],
            short_description=row["short_description"] or "",
            full_description=row["full_description"] or "",
            status=ProjectStatus(row["status"]),
            github_url=row["github_url"],
            demo_url=row["demo_url"],
            start_date=row["start_date"],
            end_date=row["end_date"],
            is_featured=bool(row["is_featured"]),
            display_order=row["display_order"],
            role_in_project=row["role_in_project"] or "",
            created_at=row["created_at"],
        )
