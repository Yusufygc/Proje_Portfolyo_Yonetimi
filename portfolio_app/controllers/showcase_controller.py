"""controllers/showcase_controller.py — Vitrin veri koordinasyonu."""

import logging

from services.personal_info_service import PersonalInfoService
from services.project_service import ProjectService
from services.certificate_service import CertificateService
from domain.models.personal_info import PersonalInfo
from domain.models.project import Project
from domain.models.certificate import Certificate
from services.skill_service import SkillService
from domain.models.skill import Skill
from services.education_service import EducationService
from domain.models.education import Education
from services.experience_service import ExperienceService
from domain.models.experience import Experience

logger = logging.getLogger(__name__)


class ShowcaseController:
    def __init__(
        self,
        personal_info_service: PersonalInfoService,
        project_service: ProjectService,
        certificate_service: CertificateService,
        skill_service: SkillService,
        education_service: EducationService,
        experience_service: ExperienceService
    ):
        self._pi_service   = personal_info_service
        self._proj_service = project_service
        self._cert_service = certificate_service
        self._skill_service = skill_service
        self._edu_service  = education_service
        self._exp_service  = experience_service

    def get_personal_info(self) -> PersonalInfo:
        return self._pi_service.get()

    def get_featured_projects(self) -> list[Project]:
        return self._proj_service.get_featured()

    def get_all_projects(self) -> list[Project]:
        return self._proj_service.get_all()

    def get_certificates(self) -> list[Certificate]:
        return self._cert_service.get_all()

    def get_skills(self) -> list[Skill]:
        return self._skill_service.get_all()

    def get_education(self) -> list[Education]:
        return self._edu_service.get_all()

    def get_experience(self) -> list[Experience]:
        return self._exp_service.get_all()
