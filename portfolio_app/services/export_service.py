"""services/export_service.py — Strategy pattern ile export motorlarını yönetir."""

import logging

from services.interfaces.i_exporter import IExporter
from services.dto.export_config import ExportConfig

logger = logging.getLogger(__name__)


class ExportService:
    """
    Strategy pattern ile birden fazla export formatını yönetir.
    Yeni bir format eklemek için register_exporter() kullanılır.
    """

    def __init__(self) -> None:
        self._exporters: dict[str, IExporter] = {}

    def register_exporter(self, key: str, exporter: IExporter) -> None:
        """Yeni bir export stratejisi kaydeder."""
        self._exporters[key] = exporter
        logger.debug(f"Exporter kaydedildi: {key}")

    def get_available_formats(self) -> list[dict[str, str]]:
        """Kullanılabilir export formatlarını döner."""
        return [
            {"key": k, "name": e.get_format_name(), "ext": e.get_file_extension()}
            for k, e in self._exporters.items()
        ]

    def export(
        self,
        key: str,
        personal_info,
        projects: list,
        skills: list,
        education: list,
        experience: list,
        certificates: list,
        config: ExportConfig,
    ) -> bytes:
        """
        Belirtilen formatta export yapar.
        Raises ValueError if key is not registered.
        Returns: Export edilen dosyanın byte içeriği.
        """
        if key not in self._exporters:
            raise ValueError(f"Bilinmeyen export formatı: {key}")
        logger.info(f"Export başlatıldı: format={key}, mode={config.mode}")
        return self._exporters[key].export(
            personal_info, projects, skills, education, experience, certificates, config
        )

    def suggest_improvements(
        self,
        personal_info,
        projects: list,
        skills: list,
        education: list,
        experience: list,
    ) -> list[str]:
        """
        Export öncesi CV kalitesini artırmak için öneriler üretir.
        Returns: Kullanıcıya gösterilecek öneri metinleri listesi.
        """
        suggestions = []

        if not skills or len(skills) < 8:
            suggestions.append("En az 8-10 teknik beceri eklemeniz önerilir.")

        if not projects or len(projects) < 3:
            suggestions.append("ATS CV için en az 3 proje eklemeniz önerilir.")

        if not getattr(personal_info, "github_url", None):
            suggestions.append("GitHub profilinizi eklemeniz önerilir.")

        if not getattr(personal_info, "linkedin_url", None):
            suggestions.append("LinkedIn profilinizi eklemeniz önerilir.")

        if not getattr(personal_info, "title", ""):
            suggestions.append("Profesyonel ünvanınızı belirtin (ör: Full Stack Developer).")

        bio = getattr(personal_info, "bio", "") or ""
        if len(bio) < 50:
            suggestions.append(
                "Professional Summary için bio alanınız çok kısa. En az 2-3 cümle önerilir."
            )

        if not education:
            suggestions.append("Eğitim bilgilerinizi eklemeniz önerilir.")

        for proj in (projects or []):
            desc = getattr(proj, "full_description", "") or getattr(proj, "description", "") or ""
            has_metric = any(ch in desc for ch in ["%", "x", "X"]) or any(c.isdigit() for c in desc)
            if not has_metric:
                suggestions.append(
                    f'"{proj.title}" projesine ölçülebilir bir başarı ekleyin '
                    f'(örnek: "%X iyileştirme", "Y kullanıcıya hizmet" gibi).'
                )

        return suggestions
