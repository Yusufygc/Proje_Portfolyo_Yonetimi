"""infrastructure/repositories/experience_repository.py — İş deneyimi DB işlemleri."""

import logging

from infrastructure.database.db_manager import DBManager
from domain.models.experience import Experience
from domain.exceptions.domain_exceptions import NotFoundError, DatabaseError

logger = logging.getLogger(__name__)


class ExperienceRepository:
    def __init__(self, db: DBManager):
        self._db = db

    def get_all(self) -> list[Experience]:
        rows = self._db.fetch_all(
            "SELECT * FROM experience ORDER BY display_order, start_date DESC"
        )
        return [self._row_to_exp(r) for r in rows]

    def get_by_id(self, exp_id: int) -> Experience:
        row = self._db.fetch_one("SELECT * FROM experience WHERE id=?", (exp_id,))
        if not row:
            raise NotFoundError(f"Deneyim kaydı bulunamadı: id={exp_id}")
        return self._row_to_exp(row)

    def create(self, exp: Experience) -> Experience:
        try:
            cursor = self._db.execute(
                """INSERT INTO experience
                   (company, position, start_date, end_date,
                    description, is_current, display_order)
                   VALUES (?,?,?,?,?,?,?)""",
                (exp.company, exp.position, exp.start_date, exp.end_date,
                 exp.description, int(exp.is_current), exp.display_order),
            )
            exp.id = cursor.lastrowid
            logger.info(f"Deneyim kaydı oluşturuldu: id={exp.id}")
            return exp
        except Exception:
            logger.exception("Deneyim kaydı oluşturma hatası")
            raise DatabaseError("Deneyim kaydı oluşturulamadı.")

    def update(self, exp: Experience) -> Experience:
        try:
            self._db.execute(
                """UPDATE experience SET
                   company=?, position=?, start_date=?, end_date=?,
                   description=?, is_current=?, display_order=?
                   WHERE id=?""",
                (exp.company, exp.position, exp.start_date, exp.end_date,
                 exp.description, int(exp.is_current), exp.display_order, exp.id),
            )
            logger.info(f"Deneyim kaydı güncellendi: id={exp.id}")
            return exp
        except Exception:
            logger.exception("Deneyim kaydı güncelleme hatası")
            raise DatabaseError("Deneyim kaydı güncellenemedi.")

    def delete(self, exp_id: int) -> None:
        self._db.execute("DELETE FROM experience WHERE id=?", (exp_id,))
        logger.info(f"Deneyim kaydı silindi: id={exp_id}")

    @staticmethod
    def _row_to_exp(row) -> Experience:
        return Experience(
            id=row["id"],
            company=row["company"],
            position=row["position"] or "",
            start_date=row["start_date"] or "",
            end_date=row["end_date"],
            description=row["description"],
            is_current=bool(row["is_current"]),
            display_order=row["display_order"],
            created_at=row["created_at"] or "",
        )
