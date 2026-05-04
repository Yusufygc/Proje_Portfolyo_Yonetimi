"""infrastructure/repositories/resource_repository.py — Kaynak DB işlemleri."""

import logging
from typing import Optional

from infrastructure.database.db_manager import DBManager
from domain.models.resource import Resource
from domain.enums.resource_type import ResourceStatus, ResourcePriority
from domain.exceptions.domain_exceptions import NotFoundError, DatabaseError

logger = logging.getLogger(__name__)


class ResourceRepository:
    def __init__(self, db: DBManager):
        self._db = db

    # ── Okuma ────────────────────────────────────────────────────────────────

    def get_all(self, sort_by: str = "created_at", sort_dir: str = "DESC") -> list[Resource]:
        allowed_sorts = {"created_at", "title", "status", "priority", "progress"}
        if sort_by not in allowed_sorts:
            sort_by = "created_at"
        sort_dir = "ASC" if sort_dir.upper() == "ASC" else "DESC"

        rows = self._db.fetch_all(
            f"""SELECT r.*, p.title as project_title,
                       rt.color as rt_color, rt.emoji as rt_emoji
                FROM resources r
                LEFT JOIN projects p ON r.related_project_id = p.id
                LEFT JOIN resource_types rt ON r.type = rt.name
                ORDER BY r.is_pinned DESC, r.{sort_by} {sort_dir}"""
        )
        return [self._row_to_resource(r) for r in rows]

    def get_by_type(self, type_name: str) -> list[Resource]:
        rows = self._db.fetch_all(
            """SELECT r.*, p.title as project_title,
                      rt.color as rt_color, rt.emoji as rt_emoji
               FROM resources r
               LEFT JOIN projects p ON r.related_project_id = p.id
               LEFT JOIN resource_types rt ON r.type = rt.name
               WHERE r.type=?
               ORDER BY r.is_pinned DESC, r.created_at DESC""",
            (type_name,),
        )
        return [self._row_to_resource(r) for r in rows]

    def get_by_id(self, resource_id: int) -> Resource:
        row = self._db.fetch_one(
            """SELECT r.*, p.title as project_title,
                      rt.color as rt_color, rt.emoji as rt_emoji
               FROM resources r
               LEFT JOIN projects p ON r.related_project_id = p.id
               LEFT JOIN resource_types rt ON r.type = rt.name
               WHERE r.id=?""",
            (resource_id,),
        )
        if not row:
            raise NotFoundError(f"Kaynak bulunamadı: id={resource_id}")
        return self._row_to_resource(row)

    def search(self, query: str) -> list[Resource]:
        """Başlık ve notlarda arama yapar."""
        pattern = f"%{query}%"
        rows = self._db.fetch_all(
            """SELECT r.*, p.title as project_title,
                      rt.color as rt_color, rt.emoji as rt_emoji
               FROM resources r
               LEFT JOIN projects p ON r.related_project_id = p.id
               LEFT JOIN resource_types rt ON r.type = rt.name
               WHERE r.title LIKE ? OR r.notes LIKE ?
               ORDER BY r.is_pinned DESC, r.created_at DESC""",
            (pattern, pattern),
        )
        return [self._row_to_resource(r) for r in rows]

    # ── Yazma ────────────────────────────────────────────────────────────────

    def create(self, resource: Resource) -> Resource:
        try:
            cursor = self._db.execute(
                """INSERT INTO resources
                   (type, title, url, notes, status, priority, progress, is_pinned, related_project_id)
                   VALUES (?,?,?,?,?,?,?,?,?)""",
                (resource.type, resource.title, resource.url,
                 resource.notes, resource.status.value,
                 resource.priority.value, resource.progress,
                 1 if resource.is_pinned else 0,
                 resource.related_project_id),
            )
            resource.id = cursor.lastrowid
            # Etiketleri kaydet
            self._save_tags(resource.id, resource.tags)
            logger.info(f"Kaynak oluşturuldu: id={resource.id}")
            return resource
        except Exception:
            logger.exception("Kaynak oluşturma hatası")
            raise DatabaseError("Kaynak oluşturulamadı.")

    def update(self, resource: Resource) -> Resource:
        self._db.execute(
            """UPDATE resources SET
               type=?, title=?, url=?, notes=?, status=?, priority=?,
               progress=?, is_pinned=?, related_project_id=?
               WHERE id=?""",
            (resource.type, resource.title, resource.url,
             resource.notes, resource.status.value,
             resource.priority.value, resource.progress,
             1 if resource.is_pinned else 0,
             resource.related_project_id, resource.id),
        )
        # Etiketleri güncelle
        self._save_tags(resource.id, resource.tags)
        return resource

    def delete(self, resource_id: int) -> None:
        self._db.execute("DELETE FROM resources WHERE id=?", (resource_id,))
        logger.info(f"Kaynak silindi: id={resource_id}")

    def toggle_pin(self, resource_id: int) -> bool:
        """Pin durumunu tersine çevirir, yeni durumu döner."""
        row = self._db.fetch_one("SELECT is_pinned FROM resources WHERE id=?", (resource_id,))
        if not row:
            raise NotFoundError(f"Kaynak bulunamadı: id={resource_id}")
        new_val = 0 if row["is_pinned"] else 1
        self._db.execute("UPDATE resources SET is_pinned=? WHERE id=?", (new_val, resource_id))
        return bool(new_val)

    def update_progress(self, resource_id: int, progress: int) -> None:
        self._db.execute("UPDATE resources SET progress=? WHERE id=?", (progress, resource_id))

    # ── Etiketler ────────────────────────────────────────────────────────────

    def _save_tags(self, resource_id: int, tags: list[str]) -> None:
        """Mevcut etiketleri temizleyip yenilerini yazar."""
        self._db.execute("DELETE FROM resource_tags WHERE resource_id=?", (resource_id,))
        for tag in tags:
            tag = tag.strip()
            if tag:
                self._db.execute(
                    "INSERT INTO resource_tags (resource_id, tag_name) VALUES (?,?)",
                    (resource_id, tag),
                )

    def _get_tags(self, resource_id: int) -> list[str]:
        rows = self._db.fetch_all(
            "SELECT tag_name FROM resource_tags WHERE resource_id=?", (resource_id,)
        )
        return [r["tag_name"] for r in rows]

    # ── İstatistik ───────────────────────────────────────────────────────────

    def get_stats(self) -> dict:
        """Tür ve durum bazlı kaynak sayılarını döner."""
        type_rows = self._db.fetch_all(
            "SELECT type, COUNT(*) as cnt FROM resources GROUP BY type"
        )
        status_rows = self._db.fetch_all(
            "SELECT status, COUNT(*) as cnt FROM resources GROUP BY status"
        )
        total = self._db.fetch_one("SELECT COUNT(*) as cnt FROM resources")
        return {
            "total": total["cnt"] if total else 0,
            "by_type": {r["type"]: r["cnt"] for r in type_rows},
            "by_status": {r["status"]: r["cnt"] for r in status_rows},
        }

    # ── Dönüştürme ──────────────────────────────────────────────────────────

    def _row_to_resource(self, row) -> Resource:
        resource_id = row["id"]
        tags = self._get_tags(resource_id)

        return Resource(
            id=resource_id,
            type=row["type"],
            title=row["title"],
            url=row["url"],
            notes=row["notes"] or "",
            status=ResourceStatus(row["status"]),
            priority=ResourcePriority(row["priority"]) if row["priority"] else ResourcePriority.MEDIUM,
            progress=row["progress"] or 0,
            is_pinned=bool(row["is_pinned"]),
            related_project_id=row["related_project_id"],
            tags=tags,
            created_at=row["created_at"],
            related_project_title=row["project_title"] if "project_title" in row.keys() else None,
            type_color=row["rt_color"] if "rt_color" in row.keys() and row["rt_color"] else "#2F81F7",
            type_emoji=row["rt_emoji"] if "rt_emoji" in row.keys() and row["rt_emoji"] else "📄",
        )
