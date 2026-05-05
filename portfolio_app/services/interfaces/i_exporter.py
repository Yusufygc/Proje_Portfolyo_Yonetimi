"""services/interfaces/i_exporter.py — Export stratejileri için ABC."""

from abc import ABC, abstractmethod


class IExporter(ABC):
    """Tüm export stratejilerinin implement etmesi gereken arayüz."""

    @abstractmethod
    def export(
        self,
        personal_info,
        projects: list,
        skills: list,
        education: list,
        experience: list,
        certificates: list,
        config,
    ) -> bytes:
        """
        Verilen verileri belirtilen formatta export eder.
        Returns: PDF/DOCX dosyasının byte içeriği.
        """

    @abstractmethod
    def get_format_name(self) -> str:
        """Export formatının görünen adı. Örnek: 'ATS CV (PDF)'"""

    @abstractmethod
    def get_file_extension(self) -> str:
        """Dosya uzantısı. Örnek: '.pdf' veya '.docx'"""
