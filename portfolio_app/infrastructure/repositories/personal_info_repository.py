"""infrastructure/repositories/personal_info_repository.py — Kişisel bilgi DB işlemleri."""

import logging

from infrastructure.database.db_manager import DBManager
from domain.models.personal_info import PersonalInfo
from domain.exceptions.domain_exceptions import DatabaseError

logger = logging.getLogger(__name__)


class PersonalInfoRepository:
    def __init__(self, db: DBManager):
        self._db = db

    def get(self) -> PersonalInfo:
        row = self._db.fetch_one("SELECT * FROM personal_info WHERE id=1")
        if not row:
            return PersonalInfo()
        return self._row_to_info(row)

    def update(self, info: PersonalInfo) -> PersonalInfo:
        try:
            self._db.execute(
                """UPDATE personal_info SET
                   full_name=?, title=?, bio=?, avatar_path=?,
                   github_url=?, linkedin_url=?, website_url=?, email=?,
                   vision_text=?, mission_text=?, hobbies=?,
                   updated_at=datetime('now')
                   WHERE id=1""",
                (info.full_name, info.title, info.bio, info.avatar_path,
                 info.github_url, info.linkedin_url, info.website_url, info.email,
                 info.vision_text, info.mission_text, info.hobbies),
            )
            logger.info("Kişisel bilgi güncellendi.")
            return info
        except Exception:
            logger.exception("Kişisel bilgi güncelleme hatası")
            raise DatabaseError("Kişisel bilgi güncellenemedi.")

    @staticmethod
    def _row_to_info(row) -> PersonalInfo:
        return PersonalInfo(
            id=row["id"],
            full_name=row["full_name"] or "",
            title=row["title"] or "",
            bio=row["bio"] or "",
            avatar_path=row["avatar_path"],
            github_url=row["github_url"],
            linkedin_url=row["linkedin_url"],
            website_url=row["website_url"],
            email=row["email"],
            vision_text=row["vision_text"] or "",
            mission_text=row["mission_text"] or "",
            hobbies=row["hobbies"] or "",
            updated_at=row["updated_at"] or "",
        )
