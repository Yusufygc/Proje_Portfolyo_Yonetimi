"""controllers/skill_controller.py — Yetenekler için controller."""

from domain.models.skill import Skill
from services.skill_service import SkillService

class SkillController:
    def __init__(self, service: SkillService):
        self._service = service

    def get_all(self) -> list[Skill]:
        return self._service.get_all()

    def create(self, name: str, category: str, rating: int, local_icon_path: str = "") -> Skill:
        skill = Skill(id=None, name=name, category=category, rating=rating)
        return self._service.create(skill, local_icon_path)

    def update(self, skill: Skill, new_local_icon_path: str = "") -> Skill:
        return self._service.update(skill, new_local_icon_path)

    def delete(self, skill_id: int) -> None:
        self._service.delete(skill_id)
