"""infrastructure/export/pdf_portfolio_exporter.py — Görsel zengin çok sayfalı portfolyo PDF."""

import io
import logging

from services.interfaces.i_exporter import IExporter
from services.dto.export_config import ExportConfig

logger = logging.getLogger(__name__)


class PDFPortfolioExporter(IExporter):
    """Görsel zengin, çok sayfalı portfolyo PDF üretici."""

    def get_format_name(self) -> str:
        return "Tam Portfolyo (PDF)"

    def get_file_extension(self) -> str:
        return ".pdf"

    def export(
        self,
        personal_info,
        projects: list,
        skills: list,
        education: list,
        experience: list,
        certificates: list,
        config: ExportConfig,
    ) -> bytes:
        """Görsel zengin portfolyo PDF'i üretir ve bytes döner."""
        try:
            from reportlab.lib.pagesizes import A4
            from reportlab.lib.units import inch, cm
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.enums import TA_LEFT, TA_CENTER
            from reportlab.platypus import (
                SimpleDocTemplate, Paragraph, Spacer, HRFlowable,
                PageBreak, Image as RLImage
            )
            from reportlab.lib.colors import HexColor, white, black
            from reportlab.pdfbase import pdfmetrics
            from reportlab.pdfbase.ttfonts import TTFont
            from reportlab.graphics.shapes import Drawing, Rect, String
            from reportlab.graphics import renderPDF
        except ImportError:
            raise RuntimeError(
                "reportlab kütüphanesi bulunamadı. "
                "Lütfen 'pip install reportlab Pillow' komutunu çalıştırın."
            )

        # Font
        try:
            pdfmetrics.registerFont(TTFont("Arial", "Arial.ttf"))
            pdfmetrics.registerFont(TTFont("Arial-Bold", "Arialbd.ttf"))
            FONT = "Arial"
            FONT_BOLD = "Arial-Bold"
        except Exception:
            FONT = "Helvetica"
            FONT_BOLD = "Helvetica-Bold"

        accent = config.accent_color or "#6366F1"
        accent_color = HexColor(accent)
        full_name = getattr(personal_info, "full_name", "CV") or "CV"

        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            topMargin=inch,
            bottomMargin=inch,
            leftMargin=inch,
            rightMargin=inch,
            title=f"{full_name} - Portfolyo",
            author=full_name,
        )

        styles = getSampleStyleSheet()
        s_name = ParagraphStyle(
            "PFName", fontName=FONT_BOLD, fontSize=28,
            alignment=TA_LEFT, textColor=accent_color, spaceAfter=6,
        )
        s_title = ParagraphStyle(
            "PFTitle", fontName=FONT, fontSize=16,
            alignment=TA_LEFT, textColor=HexColor("#4B5563"), spaceAfter=16,
        )
        s_heading = ParagraphStyle(
            "PFHeading", fontName=FONT_BOLD, fontSize=16,
            textColor=accent_color, spaceBefore=12, spaceAfter=8,
        )
        s_body = ParagraphStyle(
            "PFBody", fontName=FONT, fontSize=11,
            leading=16, spaceAfter=6, textColor=black,
        )
        s_contact = ParagraphStyle(
            "PFContact", fontName=FONT, fontSize=10,
            textColor=HexColor("#6B7280"), spaceAfter=4,
        )
        s_proj_title = ParagraphStyle(
            "PFProjTitle", fontName=FONT_BOLD, fontSize=18,
            textColor=accent_color, spaceAfter=4,
        )
        s_badge = ParagraphStyle(
            "PFBadge", fontName=FONT, fontSize=9,
            textColor=HexColor("#6B7280"), spaceAfter=8,
        )

        def hr(color=None) -> HRFlowable:
            return HRFlowable(
                width="100%", thickness=1,
                color=HexColor(color or "#E5E7EB"),
                spaceBefore=4, spaceAfter=12,
            )

        PAGE_W = A4[0] - 2 * inch  # Kullanılabilir genişlik

        elements = []

        # ─────────────────────────────────────────────────────────────────────
        # SAYFA 1: Kapak
        # ─────────────────────────────────────────────────────────────────────
        elements.append(Spacer(1, 0.5 * inch))
        elements.append(Paragraph(full_name, s_name))
        title_val = getattr(personal_info, "title", "") or ""
        if title_val:
            elements.append(Paragraph(title_val, s_title))

        # Avatar (config.include_photo aktifse)
        avatar = getattr(personal_info, "avatar_path", None)
        if config.include_photo and avatar:
            img = self._load_image(avatar, max_width=120, max_height=120)
            if img:
                elements.append(img)
                elements.append(Spacer(1, 12))

        bio = getattr(personal_info, "bio", "") or ""
        if bio:
            elements.append(Paragraph(bio, s_body))
            elements.append(Spacer(1, 12))

        # İletişim
        elements.append(Paragraph("İletişim", s_heading))
        elements.append(hr())
        contact_items = [
            ("E-posta",   getattr(personal_info, "email", None)),
            ("Telefon",   getattr(personal_info, "phone", None)),
            ("GitHub",    getattr(personal_info, "github_url", None)),
            ("LinkedIn",  getattr(personal_info, "linkedin_url", None)),
            ("Web",       getattr(personal_info, "website_url", None)),
        ]
        for label, val in contact_items:
            if val:
                elements.append(Paragraph(f"<b>{label}:</b> {val}", s_contact))

        elements.append(PageBreak())

        # ─────────────────────────────────────────────────────────────────────
        # SAYFA 2: Beceriler
        # ─────────────────────────────────────────────────────────────────────
        if skills:
            elements.append(Paragraph("Beceriler", s_heading))
            elements.append(hr())

            if config.include_skills_chart:
                level_map = {
                    "BEGINNER": 0.25, "INTERMEDIATE": 0.50,
                    "ADVANCED": 0.75, "EXPERT": 1.0,
                }
                for skill in skills:
                    # rating (0-100) → level string
                    rating = getattr(skill, "rating", 50) or 50
                    if rating <= 25:
                        level_str = "BEGINNER"
                    elif rating <= 50:
                        level_str = "INTERMEDIATE"
                    elif rating <= 75:
                        level_str = "ADVANCED"
                    else:
                        level_str = "EXPERT"

                    pct = level_map.get(level_str, 0.5)
                    bar = self._draw_skill_bar(
                        skill.name, pct, PAGE_W, 16, accent, FONT
                    )
                    elements.append(bar)
                    elements.append(Spacer(1, 4))
            else:
                # Düz metin listesi
                from collections import defaultdict
                grouped: dict = defaultdict(list)
                for s in skills:
                    cat = (getattr(s, "category", "") or "Diğer").title()
                    grouped[cat].append(s.name)
                for cat, names in grouped.items():
                    elements.append(
                        Paragraph(f"<b>{cat}:</b> {', '.join(names)}", s_body)
                    )

            elements.append(PageBreak())

        # ─────────────────────────────────────────────────────────────────────
        # SAYFA 3+: Proje Sayfaları
        # ─────────────────────────────────────────────────────────────────────
        selected = (
            [p for p in projects if p.id in config.selected_project_ids]
            if config.selected_project_ids else projects
        )
        for proj in selected:
            elements.append(Paragraph(proj.title, s_proj_title))

            # Durum badge
            status_val = getattr(proj, "status", None)
            status_text = status_val.value if status_val else ""
            elements.append(Paragraph(status_text, s_badge))
            elements.append(hr())

            # Açıklama
            desc = getattr(proj, "full_description", "") or getattr(proj, "description", "") or ""
            if desc:
                elements.append(Paragraph(desc, s_body))

            # Rol
            role = getattr(proj, "role_in_project", "") or ""
            if role:
                elements.append(Paragraph(f"<b>Rol:</b> {role}", s_body))

            # Teknolojiler
            tags = getattr(proj, "tags", [])
            if tags:
                tech_str = " · ".join(t.tag_name for t in tags)
                elements.append(Paragraph(f"<b>Teknolojiler:</b> {tech_str}", s_body))

            # Tarih
            date_str = getattr(proj, "start_date", "") or ""
            if date_str:
                end = getattr(proj, "end_date", None)
                date_str += f" — {end}" if end else " — Devam ediyor"
                elements.append(Paragraph(f"<b>Süre:</b> {date_str}", s_body))

            # Linkler
            github = getattr(proj, "github_url", None)
            demo = getattr(proj, "demo_url", None)
            if github:
                elements.append(Paragraph(f'<b>GitHub:</b> <a href="{github}">{github}</a>', s_body))
            if demo:
                elements.append(Paragraph(f'<b>Demo:</b> <a href="{demo}">{demo}</a>', s_body))

            # Proje görselleri
            images = getattr(proj, "images", [])
            for img_obj in images[:3]:  # Max 3 görsel per proje
                img_path = getattr(img_obj, "image_path", None)
                if img_path:
                    img = self._load_image(img_path, max_width=PAGE_W, max_height=300)
                    if img:
                        elements.append(Spacer(1, 8))
                        elements.append(img)

            elements.append(PageBreak())

        # ─────────────────────────────────────────────────────────────────────
        # SON SAYFA: Eğitim, Deneyim, Sertifikalar
        # ─────────────────────────────────────────────────────────────────────
        if education:
            elements.append(Paragraph("Eğitim", s_heading))
            elements.append(hr())
            for edu in education:
                elements.append(Paragraph(f"<b>{edu.institution}</b>", s_body))
                degree = edu.degree
                field = getattr(edu, "field", "") or ""
                if field:
                    degree += f", {field}"
                date_str = edu.start_date or ""
                end = getattr(edu, "end_date", None)
                if end:
                    date_str += f" — {end}"
                elements.append(Paragraph(f"{degree} | {date_str}", s_contact))
                elements.append(Spacer(1, 8))

        if experience:
            elements.append(Paragraph("İş Deneyimi", s_heading))
            elements.append(hr())
            for exp in sorted(experience, key=lambda x: x.start_date or "", reverse=True):
                elements.append(Paragraph(f"<b>{exp.company}</b> — {exp.position}", s_body))
                date_str = exp.start_date or ""
                if getattr(exp, "is_current", False):
                    date_str += " — Devam ediyor"
                elif getattr(exp, "end_date", None):
                    date_str += f" — {exp.end_date}"
                elements.append(Paragraph(date_str, s_contact))
                desc = getattr(exp, "description", "") or ""
                if desc:
                    elements.append(Paragraph(desc, s_body))
                elements.append(Spacer(1, 8))

        if certificates:
            elements.append(Paragraph("Sertifikalar", s_heading))
            elements.append(hr())
            for cert in certificates:
                cert_text = f"<b>{cert.name}</b> — {cert.issuer} ({cert.date or ''})"
                url = getattr(cert, "verification_url", None)
                if url:
                    cert_text = f'<a href="{url}">{cert_text}</a>'
                elements.append(Paragraph(cert_text, s_body))

        doc.build(elements)
        return buffer.getvalue()

    @staticmethod
    def _draw_skill_bar(
        skill_name: str, pct: float,
        width: float, height: float,
        accent: str, font_name: str,
    ):
        """Tek beceri için yatay seviye barı çizer."""
        from reportlab.graphics.shapes import Drawing, Rect, String
        from reportlab.lib.colors import HexColor

        d = Drawing(width, height + 18)
        # Label
        d.add(String(0, height + 4, skill_name, fontSize=9, fontName=font_name))
        # Arka plan
        d.add(Rect(0, 0, width, height, fillColor=HexColor("#E5E7EB"), strokeColor=None))
        # Dolu kısım
        d.add(Rect(0, 0, width * pct, height, fillColor=HexColor(accent), strokeColor=None))
        return d

    @staticmethod
    def _load_image(image_path: str, max_width: float, max_height: float):
        """Görseli yükler ve boyutlandırır; hata varsa None döner."""
        try:
            from reportlab.platypus import Image as RLImage
            img = RLImage(image_path)
            aspect = img.imageWidth / max(img.imageHeight, 1)
            if img.imageWidth > max_width:
                img.drawWidth = max_width
                img.drawHeight = max_width / aspect
            if img.drawHeight > max_height:
                img.drawHeight = max_height
                img.drawWidth = max_height * aspect
            return img
        except Exception:
            return None
