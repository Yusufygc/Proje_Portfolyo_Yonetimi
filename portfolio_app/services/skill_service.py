"""services/skill_service.py — Yetenek iş kuralları ve ikon indirme."""

import logging
import requests
from typing import Optional

from domain.models.skill import Skill
from infrastructure.repositories.skill_repository import SkillRepository
from infrastructure.storage.image_storage import ImageStorage

logger = logging.getLogger(__name__)

class SkillService:
    def __init__(self, repo: SkillRepository, storage: ImageStorage):
        self._repo = repo
        self._storage = storage

    def get_all(self) -> list[Skill]:
        return self._repo.get_all()

    def create(self, skill: Skill, local_icon_path: str = "") -> Skill:
        # Eğer kullanici lokal ikon seçmişse onu kaydet,
        # seçmemişse internetten bulmaya çalıs
        if local_icon_path:
            skill.icon_path = self._storage.save_skill_icon(local_icon_path)
            created = self._repo.create(skill)
            return created
        
        # İnternetten otomatik ikon indirme denemesi
        downloaded_path = self._fetch_and_save_icon(skill.name)
        if downloaded_path:
            skill.icon_path = downloaded_path
            
        return self._repo.create(skill)

    def update(self, skill: Skill, new_local_icon_path: str = "") -> Skill:
        # Mevcutu bilmek lazim ki silebiliriz, ama su an basit tutalim
        if new_local_icon_path:
            old_path = skill.icon_path
            skill.icon_path = self._storage.save_skill_icon(new_local_icon_path)
            # Eski ikonu diskten sil
            if old_path:
                try:
                    self._storage.delete(old_path)
                except Exception as e:
                    logger.warning(f"Eski ikon silinemedi: {e}")
        
        return self._repo.update(skill)

    def delete(self, skill_id: int) -> None:
        try:
            skill = self._repo.get_by_id(skill_id)
            if skill.icon_path:
                self._storage.delete(skill.icon_path)
        except Exception as e:
            logger.warning(f"Silinirken ikon dosyasını kaldırma hatası: {e}")
        self._repo.delete(skill_id)

    def _fetch_and_save_icon(self, skill_name: str) -> Optional[str]:
        """Devicon veya Clearbit üzerinden ikon indirmeyi dener."""
        name_clean = skill_name.lower().replace(" ", "").replace(".", "")
        
        # 1. Devicon SVG denemesi (En iyi teknoloji ikonlari)
        devicon_url = f"https://cdn.jsdelivr.net/gh/devicons/devicon@latest/icons/{name_clean}/{name_clean}-original.svg"
        try:
            resp = requests.get(devicon_url, timeout=5)
            if resp.status_code == 200:
                logger.info(f"Devicon ikonu bulundu: {devicon_url}")
                return self._storage.save_skill_icon_from_bytes(resp.content, ".svg", name_clean)
        except requests.RequestException:
            pass

        # 2. Alternatif devicon denemesi (plain)
        devicon_plain_url = f"https://cdn.jsdelivr.net/gh/devicons/devicon@latest/icons/{name_clean}/{name_clean}-plain.svg"
        try:
            resp = requests.get(devicon_plain_url, timeout=5)
            if resp.status_code == 200:
                return self._storage.save_skill_icon_from_bytes(resp.content, ".svg", name_clean)
        except requests.RequestException:
            pass

        # 3. Clearbit Logo API denemesi
        clearbit_url = f"https://logo.clearbit.com/{name_clean}.com"
        try:
            resp = requests.get(clearbit_url, timeout=5)
            if resp.status_code == 200:
                logger.info(f"Clearbit ikonu bulundu: {clearbit_url}")
                return self._storage.save_skill_icon_from_bytes(resp.content, ".png", name_clean)
        except requests.RequestException:
            pass
            
        logger.warning(f"Yetenek için otomatik ikon bulunamadı: {skill_name}")
        return None
