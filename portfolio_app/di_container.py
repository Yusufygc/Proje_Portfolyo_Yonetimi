"""
di_container.py — Dependency Injection container.
main.py → DI Container → Repos → Services → Controllers → Views
"""

from infrastructure.database.db_manager import DBManager
from infrastructure.repositories.project_repository import ProjectRepository
from infrastructure.repositories.task_repository import TaskRepository
from infrastructure.repositories.certificate_repository import CertificateRepository
from infrastructure.repositories.personal_info_repository import PersonalInfoRepository
from infrastructure.repositories.resource_repository import ResourceRepository
from infrastructure.repositories.resource_type_repository import ResourceTypeRepository
from infrastructure.repositories.skill_repository import SkillRepository
from infrastructure.storage.image_storage import ImageStorage

from services.project_service import ProjectService
from services.certificate_service import CertificateService
from services.personal_info_service import PersonalInfoService
from services.resource_service import ResourceService
from services.resource_type_service import ResourceTypeService
from services.skill_service import SkillService

from controllers.project_controller import ProjectController
from controllers.certificate_controller import CertificateController
from controllers.personal_info_controller import PersonalInfoController
from controllers.resource_controller import ResourceController
from controllers.resource_type_controller import ResourceTypeController
from controllers.skill_controller import SkillController
from controllers.showcase_controller import ShowcaseController


class DIContainer:
    """Tüm bağımlılıkları oluşturur ve bağlar."""

    def __init__(self, db: DBManager):
        # ── Infrastructure ───────────────────────────────────────────────────
        self.db = db
        self.storage = ImageStorage()

        # ── Repositories ─────────────────────────────────────────────────────
        self.project_repo       = ProjectRepository(db)
        self.task_repo          = TaskRepository(db)
        self.certificate_repo   = CertificateRepository(db)
        self.personal_info_repo = PersonalInfoRepository(db)
        self.resource_repo      = ResourceRepository(db)
        self.resource_type_repo = ResourceTypeRepository(db)
        self.skill_repo         = SkillRepository(db)

        # ── Services ─────────────────────────────────────────────────────────
        self.project_service       = ProjectService(self.project_repo, self.task_repo, self.storage)
        self.certificate_service   = CertificateService(self.certificate_repo, self.storage)
        self.personal_info_service = PersonalInfoService(self.personal_info_repo, self.storage)
        self.resource_service      = ResourceService(self.resource_repo)
        self.resource_type_service = ResourceTypeService(self.resource_type_repo)
        self.skill_service         = SkillService(self.skill_repo, self.storage)

        # ── Controllers ──────────────────────────────────────────────────────
        self.project_controller       = ProjectController(self.project_service)
        self.certificate_controller   = CertificateController(self.certificate_service)
        self.personal_info_controller = PersonalInfoController(self.personal_info_service)
        self.resource_controller      = ResourceController(self.resource_service)
        self.resource_type_controller = ResourceTypeController(self.resource_type_service)
        self.skill_controller         = SkillController(self.skill_service)
        self.showcase_controller      = ShowcaseController(
            self.personal_info_service,
            self.project_service,
            self.certificate_service,
            self.skill_service,
        )
