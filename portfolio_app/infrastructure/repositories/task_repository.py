"""infrastructure/repositories/task_repository.py — Task DB işlemleri."""

import logging

from infrastructure.database.db_manager import DBManager
from domain.models.task import Task
from domain.enums.task_type import TaskType, TaskStatus
from domain.exceptions.domain_exceptions import NotFoundError, DatabaseError

logger = logging.getLogger(__name__)


class TaskRepository:
    def __init__(self, db: DBManager):
        self._db = db

    def get_by_project(self, project_id: int) -> list[Task]:
        rows = self._db.fetch_all(
            "SELECT * FROM project_tasks WHERE project_id=? ORDER BY display_order, created_at",
            (project_id,),
        )
        return [self._row_to_task(r) for r in rows]

    def get_by_id(self, task_id: int) -> Task:
        row = self._db.fetch_one("SELECT * FROM project_tasks WHERE id=?", (task_id,))
        if not row:
            raise NotFoundError(f"Task bulunamadı: id={task_id}")
        return self._row_to_task(row)

    def create(self, task: Task) -> Task:
        try:
            cursor = self._db.execute(
                """INSERT INTO project_tasks
                   (project_id, type, title, description, status, display_order)
                   VALUES (?,?,?,?,?,?)""",
                (task.project_id, task.type.value, task.title,
                 task.description, task.status.value, task.display_order),
            )
            task.id = cursor.lastrowid
            logger.info(f"Task oluşturuldu: id={task.id}")
            return task
        except Exception:
            logger.exception("Task oluşturma hatası")
            raise DatabaseError("Task oluşturulamadı.")

    def update(self, task: Task) -> Task:
        self._db.execute(
            """UPDATE project_tasks SET
               type=?, title=?, description=?, status=?, display_order=?
               WHERE id=?""",
            (task.type.value, task.title, task.description,
             task.status.value, task.display_order, task.id),
        )
        return task

    def delete(self, task_id: int) -> None:
        self._db.execute("DELETE FROM project_tasks WHERE id=?", (task_id,))
        logger.info(f"Task silindi: id={task_id}")

    @staticmethod
    def _row_to_task(row) -> Task:
        return Task(
            id=row["id"],
            project_id=row["project_id"],
            type=TaskType(row["type"]),
            title=row["title"],
            description=row["description"] or "",
            status=TaskStatus(row["status"]),
            display_order=row["display_order"],
            created_at=row["created_at"],
        )
