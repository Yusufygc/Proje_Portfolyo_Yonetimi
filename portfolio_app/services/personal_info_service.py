"""services/personal_info_service.py — Kişisel bilgi iş kuralları."""

import logging

from services.interfaces.i_service import IPersonalInfoService
from infrastructure.repositories.personal_info_repository import PersonalInfoRepository
from infrastructure.storage.image_storage import ImageStorage
from domain.models.personal_info import PersonalInfo

logger = logging.getLogger(__name__)


class PersonalInfoService(IPersonalInfoService):
    def __init__(self, repo: PersonalInfoRepository, storage: ImageStorage):
        self._repo = repo
        self._storage = storage

    def get(self) -> PersonalInfo:
        return self._repo.get()

    def update(self, data: dict) -> PersonalInfo:
        info = self._repo.get()
        info.full_name = data.get("full_name", info.full_name).strip()
        info.title = data.get("title", info.title).strip()
        info.bio = data.get("bio", info.bio).strip()
        info.github_url = data.get("github_url") or None
        info.linkedin_url = data.get("linkedin_url") or None
        info.website_url = data.get("website_url") or None
        info.email = data.get("email") or None
        info.vision_text = data.get("vision_text", info.vision_text).strip()
        info.mission_text = data.get("mission_text", info.mission_text).strip()
        info.hobbies = data.get("hobbies", info.hobbies).strip()

        if data.get("avatar_source_path"):
            if info.avatar_path:
                self._storage.delete(info.avatar_path)
            info.avatar_path = self._storage.save_profile_image(
                data["avatar_source_path"]
            )

        return self._repo.update(info)
