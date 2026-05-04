"""infrastructure/repositories/resource_type_repository.py — Kaynak türü DB işlemleri."""

import logging

from infrastructure.database.db_manager import DBManager
from domain.models.resource_type_model import ResourceTypeDynamic
from domain.exceptions.domain_exceptions import NotFoundError, DatabaseError

logger = logging.getLogger(__name__)


class ResourceTypeRepository:
    def __init__(self, db: DBManager):
        self._db = db

    def get_all(self) -> list[ResourceTypeDynamic]:
        rows = self._db.fetch_all(
            "SELECT * FROM resource_types ORDER BY display_order ASC, name ASC"
        )
        return [self._row_to_model(r) for r in rows]

    def get_by_id(self, type_id: int) -> ResourceTypeDynamic:
        row = self._db.fetch_one("SELECT * FROM resource_types WHERE id=?", (type_id,))
        if not row:
            raise NotFoundError(f"Kaynak türü bulunamadı: id={type_id}")
        return self._row_to_model(row)

    def get_by_name(self, name: str) -> ResourceTypeDynamic | None:
        row = self._db.fetch_one("SELECT * FROM resource_types WHERE name=?", (name,))
        return self._row_to_model(row) if row else None

    def create(self, rt: ResourceTypeDynamic) -> ResourceTypeDynamic:
        try:
            cursor = self._db.execute(
                """INSERT INTO resource_types (name, color, emoji, display_order)
                   VALUES (?,?,?,?)""",
                (rt.name, rt.color, rt.emoji, rt.display_order),
            )
            rt.id = cursor.lastrowid
            logger.info(f"Kaynak türü oluşturuldu: id={rt.id}, name={rt.name}")
            return rt
        except Exception:
            logger.exception("Kaynak türü oluşturma hatası")
            raise DatabaseError("Kaynak türü oluşturulamadı.")

    def update(self, rt: ResourceTypeDynamic) -> ResourceTypeDynamic:
        self._db.execute(
            """UPDATE resource_types SET name=?, color=?, emoji=?, display_order=?
               WHERE id=?""",
            (rt.name, rt.color, rt.emoji, rt.display_order, rt.id),
        )
        logger.info(f"Kaynak türü güncellendi: id={rt.id}")
        return rt

    def delete(self, type_id: int) -> None:
        self._db.execute("DELETE FROM resource_types WHERE id=?", (type_id,))
        logger.info(f"Kaynak türü silindi: id={type_id}")

    def count_resources_by_type(self, type_name: str) -> int:
        """Bu türdeki kaynak sayısını döner (silme öncesi kontrol için)."""
        row = self._db.fetch_one(
            "SELECT COUNT(*) as cnt FROM resources WHERE type=?", (type_name,)
        )
        return row["cnt"] if row else 0

    @staticmethod
    def _row_to_model(row) -> ResourceTypeDynamic:
        return ResourceTypeDynamic(
            id=row["id"],
            name=row["name"],
            color=row["color"],
            emoji=row["emoji"],
            display_order=row["display_order"],
            created_at=row["created_at"],
        )
