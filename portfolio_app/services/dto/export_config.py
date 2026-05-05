"""services/dto/export_config.py — Export konfigürasyon dataclass."""

from dataclasses import dataclass, field


@dataclass
class ExportConfig:
    """Export işlemi için kullanıcı tercihleri."""

    mode: str = "ats_pdf"
    """Export modu: 'ats_pdf' | 'portfolio_pdf' | 'ats_docx'"""

    selected_project_ids: list[int] = field(default_factory=list)
    """Boşsa tüm projeler dahil edilir."""

    target_role: str = ""
    """ATS özeti için hedef pozisyon. Örn: 'Backend Developer'"""

    include_photo: bool = False
    """Portfolyo modunda avatar dahil mi?"""

    include_skills_chart: bool = True
    """Portfolyo modunda beceri grafiği gösterilsin mi?"""

    accent_color: str = "#6366F1"
    """Tema rengi (portfolyo modu)."""

    language: str = "en"
    """Çıktı dili: 'en' | 'tr'"""

    max_pages: int = 1
    """ATS modu için sayfa limiti (1 = junior, 2 = senior)."""

    output_filename: str = ""
    """Boşsa otomatik: Ad_Soyad_CV.pdf"""
