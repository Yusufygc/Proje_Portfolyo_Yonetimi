"""infrastructure/repositories/certificate_repository.py — Sertifika DB işlemleri."""

import logging

from infrastructure.database.db_manager import DBManager
from domain.models.certificate import Certificate
from domain.exceptions.domain_exceptions import NotFoundError, DatabaseError

logger = logging.getLogger(__name__)


class CertificateRepository:
    def __init__(self, db: DBManager):
        self._db = db

    def get_all(self) -> list[Certificate]:
        rows = self._db.fetch_all(
            "SELECT * FROM certificates ORDER BY display_order, date DESC"
        )
        return [self._row_to_cert(r) for r in rows]

    def get_by_id(self, cert_id: int) -> Certificate:
        row = self._db.fetch_one("SELECT * FROM certificates WHERE id=?", (cert_id,))
        if not row:
            raise NotFoundError(f"Sertifika bulunamadı: id={cert_id}")
        return self._row_to_cert(row)

    def create(self, cert: Certificate) -> Certificate:
        try:
            cursor = self._db.execute(
                """INSERT INTO certificates
                   (name, issuer, date, verification_url, image_path, display_order)
                   VALUES (?,?,?,?,?,?)""",
                (cert.name, cert.issuer, cert.date,
                 cert.verification_url, cert.image_path, cert.display_order),
            )
            cert.id = cursor.lastrowid
            logger.info(f"Sertifika oluşturuldu: id={cert.id}")
            return cert
        except Exception:
            logger.exception("Sertifika oluşturma hatası")
            raise DatabaseError("Sertifika oluşturulamadı.")

    def update(self, cert: Certificate) -> Certificate:
        self._db.execute(
            """UPDATE certificates SET
               name=?, issuer=?, date=?, verification_url=?, image_path=?, display_order=?
               WHERE id=?""",
            (cert.name, cert.issuer, cert.date,
             cert.verification_url, cert.image_path, cert.display_order, cert.id),
        )
        return cert

    def delete(self, cert_id: int) -> None:
        self._db.execute("DELETE FROM certificates WHERE id=?", (cert_id,))
        logger.info(f"Sertifika silindi: id={cert_id}")

    @staticmethod
    def _row_to_cert(row) -> Certificate:
        return Certificate(
            id=row["id"],
            name=row["name"],
            issuer=row["issuer"] or "",
            date=row["date"],
            verification_url=row["verification_url"],
            image_path=row["image_path"],
            display_order=row["display_order"],
        )
