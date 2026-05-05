"""controllers/export_controller.py — CV/PDF export koordinasyonu."""

import logging

from PySide6.QtCore import QObject, Signal

from services.export_service import ExportService
from services.dto.export_config import ExportConfig

logger = logging.getLogger(__name__)


class ExportController(QObject):
    """
    Export işlemlerini koordine eder.
    UI → ExportController → ExportService → IExporter
    """

    export_completed = Signal(bytes, str)  # (dosya_içeriği, dosya_uzantısı)
    error_occurred   = Signal(str)

    def __init__(
        self,
        export_service: ExportService,
        personal_info_service,
        project_service,
        skill_service,
        education_service,
        experience_service,
        certificate_service,
    ):
        super().__init__()
        self._export_svc = export_service
        self._info_svc   = personal_info_service
        self._proj_svc   = project_service
        self._skill_svc  = skill_service
        self._edu_svc    = education_service
        self._exp_svc    = experience_service
        self._cert_svc   = certificate_service

    def get_available_formats(self) -> list[dict[str, str]]:
        """Kullanılabilir export formatlarını döner."""
        return self._export_svc.get_available_formats()

    def get_suggestions(self) -> list[str]:
        """CV kalitesi için öneriler üretir."""
        try:
            info = self._info_svc.get()
            projects = self._proj_svc.get_all()
            skills = self._skill_svc.get_all()
            education = self._edu_svc.get_all()
            experience = self._exp_svc.get_all()
            return self._export_svc.suggest_improvements(
                info, projects, skills, education, experience
            )
        except Exception as e:
            logger.exception("Öneri üretme hatası")
            return [f"Öneri üretilemedi: {e}"]

    def export(self, format_key: str, config: ExportConfig) -> None:
        """
        Export işlemini başlatır.
        Sonuç export_completed sinyali ile iletilir.
        """
        try:
            info = self._info_svc.get()
            projects = self._proj_svc.get_all()
            skills = self._skill_svc.get_all()
            education = self._edu_svc.get_all()
            experience = self._exp_svc.get_all()
            certificates = self._cert_svc.get_all()

            data = self._export_svc.export(
                format_key, info, projects, skills,
                education, experience, certificates, config
            )
            ext = next(
                (f["ext"] for f in self._export_svc.get_available_formats() if f["key"] == format_key),
                ".pdf"
            )
            self.export_completed.emit(data, ext)
            logger.info(f"Export tamamlandı: format={format_key}")
        except Exception as e:
            logger.exception("Export hatası")
            self.error_occurred.emit(str(e))
