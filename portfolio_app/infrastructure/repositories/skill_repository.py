"""infrastructure/repositories/skill_repository.py — Yetenek DB işlemleri."""

import logging
from typing import Optional

from infrastructure.database.db_manager import DBManager
from domain.models.skill import Skill
from domain.exceptions.domain_exceptions import NotFoundError, DatabaseError

logger = logging.getLogger(__name__)

class SkillRepository:
    def __init__(self, db: DBManager):
        self._db = db

    def get_all(self) -> list[Skill]:
        rows = self._db.fetch_all("SELECT * FROM skills ORDER BY display_order, created_at DESC")
        return [self._row_to_skill(r) for r in rows]

    def get_by_id(self, skill_id: int) -> Skill:
        row = self._db.fetch_one("SELECT * FROM skills WHERE id=?", (skill_id,))
        if not row:
            raise NotFoundError(f"Yetenek bulunamadı: id={skill_id}")
        return self._row_to_skill(row)

    def create(self, skill: Skill) -> Skill:
        try:
            cursor = self._db.execute(
                """INSERT INTO skills (name, category, rating, icon_path, display_order)
                   VALUES (?, ?, ?, ?, ?)""",
                (skill.name, skill.category, skill.rating, skill.icon_path, skill.display_order)
            )
            skill.id = cursor.lastrowid
            logger.info(f"Yetenek oluşturuldu: {skill.name}")
            return skill
        except Exception:
            logger.exception("Yetenek oluşturma hatası")
            raise DatabaseError("Yetenek oluşturulamadı.")

    def update(self, skill: Skill) -> Skill:
        if not skill.id:
            raise ValueError("Güncellenecek yetenek ID'si eksik.")
        try:
            self._db.execute(
                """UPDATE skills SET name=?, category=?, rating=?, icon_path=?, display_order=?
                   WHERE id=?""",
                (skill.name, skill.category, skill.rating, skill.icon_path, skill.display_order, skill.id)
            )
            logger.info(f"Yetenek güncellendi: {skill.name}")
            return skill
        except Exception:
            logger.exception("Yetenek güncelleme hatası")
            raise DatabaseError("Yetenek güncellenemedi.")

    def delete(self, skill_id: int) -> None:
        self._db.execute("DELETE FROM skills WHERE id=?", (skill_id,))
        logger.info(f"Yetenek silindi: id={skill_id}")

    @staticmethod
    def _row_to_skill(row) -> Skill:
        return Skill(
            id=row["id"],
            name=row["name"],
            category=row["category"] or "",
            rating=row["rating"],
            icon_path=row["icon_path"] or "",
            display_order=row["display_order"],
            created_at=row["created_at"]
        )
