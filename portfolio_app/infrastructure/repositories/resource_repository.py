"""infrastructure/repositories/resource_repository.py — Kaynak DB işlemleri."""

import logging
from typing import Optional

from infrastructure.database.db_manager import DBManager
from domain.models.resource import Resource
from domain.enums.resource_type import ResourceType, ResourceStatus
from domain.exceptions.domain_exceptions import NotFoundError, DatabaseError

logger = logging.getLogger(__name__)


class ResourceRepository:
    def __init__(self, db: DBManager):
        self._db = db

    def get_all(self) -> list[Resource]:
        rows = self._db.fetch_all(
            "SELECT * FROM resources ORDER BY created_at DESC"
        )
        return [self._row_to_resource(r) for r in rows]

    def get_by_type(self, resource_type: ResourceType) -> list[Resource]:
        rows = self._db.fetch_all(
            "SELECT * FROM resources WHERE type=? ORDER BY created_at DESC",
            (resource_type.value,),
        )
        return [self._row_to_resource(r) for r in rows]

    def get_by_id(self, resource_id: int) -> Resource:
        row = self._db.fetch_one("SELECT * FROM resources WHERE id=?", (resource_id,))
        if not row:
            raise NotFoundError(f"Kaynak bulunamadı: id={resource_id}")
        return self._row_to_resource(row)

    def create(self, resource: Resource) -> Resource:
        try:
            cursor = self._db.execute(
                """INSERT INTO resources
                   (type, title, url, notes, status, related_project_id)
                   VALUES (?,?,?,?,?,?)""",
                (resource.type.value, resource.title, resource.url,
                 resource.notes, resource.status.value, resource.related_project_id),
            )
            resource.id = cursor.lastrowid
            logger.info(f"Kaynak oluşturuldu: id={resource.id}")
            return resource
        except Exception:
            logger.exception("Kaynak oluşturma hatası")
            raise DatabaseError("Kaynak oluşturulamadı.")

    def update(self, resource: Resource) -> Resource:
        self._db.execute(
            """UPDATE resources SET
               type=?, title=?, url=?, notes=?, status=?, related_project_id=?
               WHERE id=?""",
            (resource.type.value, resource.title, resource.url,
             resource.notes, resource.status.value,
             resource.related_project_id, resource.id),
        )
        return resource

    def delete(self, resource_id: int) -> None:
        self._db.execute("DELETE FROM resources WHERE id=?", (resource_id,))
        logger.info(f"Kaynak silindi: id={resource_id}")

    @staticmethod
    def _row_to_resource(row) -> Resource:
        return Resource(
            id=row["id"],
            type=ResourceType(row["type"]),
            title=row["title"],
            url=row["url"],
            notes=row["notes"] or "",
            status=ResourceStatus(row["status"]),
            related_project_id=row["related_project_id"],
            created_at=row["created_at"],
        )
