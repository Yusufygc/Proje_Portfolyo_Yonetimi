"""infrastructure/repositories/education_repository.py — Eğitim DB işlemleri."""

import logging

from infrastructure.database.db_manager import DBManager
from domain.models.education import Education
from domain.exceptions.domain_exceptions import NotFoundError, DatabaseError

logger = logging.getLogger(__name__)


class EducationRepository:
    def __init__(self, db: DBManager):
        self._db = db

    def get_all(self) -> list[Education]:
        rows = self._db.fetch_all(
            "SELECT * FROM education ORDER BY display_order, start_date DESC"
        )
        return [self._row_to_edu(r) for r in rows]

    def get_by_id(self, edu_id: int) -> Education:
        row = self._db.fetch_one("SELECT * FROM education WHERE id=?", (edu_id,))
        if not row:
            raise NotFoundError(f"Eğitim kaydı bulunamadı: id={edu_id}")
        return self._row_to_edu(row)

    def create(self, edu: Education) -> Education:
        try:
            cursor = self._db.execute(
                """INSERT INTO education
                   (institution, degree, field, start_date, end_date,
                    description, display_order)
                   VALUES (?,?,?,?,?,?,?)""",
                (edu.institution, edu.degree, edu.field, edu.start_date,
                 edu.end_date, edu.description, edu.display_order),
            )
            edu.id = cursor.lastrowid
            logger.info(f"Eğitim kaydı oluşturuldu: id={edu.id}")
            return edu
        except Exception:
            logger.exception("Eğitim kaydı oluşturma hatası")
            raise DatabaseError("Eğitim kaydı oluşturulamadı.")

    def update(self, edu: Education) -> Education:
        try:
            self._db.execute(
                """UPDATE education SET
                   institution=?, degree=?, field=?, start_date=?, end_date=?,
                   description=?, display_order=?
                   WHERE id=?""",
                (edu.institution, edu.degree, edu.field, edu.start_date,
                 edu.end_date, edu.description, edu.display_order, edu.id),
            )
            logger.info(f"Eğitim kaydı güncellendi: id={edu.id}")
            return edu
        except Exception:
            logger.exception("Eğitim kaydı güncelleme hatası")
            raise DatabaseError("Eğitim kaydı güncellenemedi.")

    def delete(self, edu_id: int) -> None:
        self._db.execute("DELETE FROM education WHERE id=?", (edu_id,))
        logger.info(f"Eğitim kaydı silindi: id={edu_id}")

    @staticmethod
    def _row_to_edu(row) -> Education:
        return Education(
            id=row["id"],
            institution=row["institution"],
            degree=row["degree"] or "",
            field=row["field"] or "",
            start_date=row["start_date"] or "",
            end_date=row["end_date"],
            description=row["description"],
            display_order=row["display_order"],
            created_at=row["created_at"] or "",
        )
