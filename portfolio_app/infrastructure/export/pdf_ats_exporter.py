"""infrastructure/export/pdf_ats_exporter.py — ATS uyumlu tek sayfa PDF üretici.

ATS Uyumluluk Kuralları (kesinlikle ihlal edilemez):
- Tek sütun layout, çok sütun YASAK
- Sadece Arial veya Helvetica font, görsel YASAK
- Header/Footer KULLANMA; iletişim bilgisi body'nin en üstünde
- Bölüm sırası sabit: İletişim → Summary → Skills → Projects → Experience → Education → Certifications
- Bullet nokta: sadece • sembolü
- Margin: her yönden 72pt (1 inch)
"""

import io
import logging

from services.interfaces.i_exporter import IExporter
from services.dto.export_config import ExportConfig

logger = logging.getLogger(__name__)


class PDFATSExporter(IExporter):
    """ATS (Applicant Tracking System) uyumlu PDF CV üretici."""

    def get_format_name(self) -> str:
        return "ATS Uyumlu CV (PDF)"

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
        """ATS uyumlu PDF üretir ve bytes olarak döner."""
        try:
            from reportlab.lib.pagesizes import A4
            from reportlab.lib.units import inch
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.enums import TA_LEFT, TA_CENTER
            from reportlab.platypus import (
                SimpleDocTemplate, Paragraph, Spacer, HRFlowable
            )
            from reportlab.lib.colors import HexColor, black
            from reportlab.pdfbase import pdfmetrics
            from reportlab.pdfbase.ttfonts import TTFont
        except ImportError:
            raise RuntimeError(
                "reportlab kütüphanesi bulunamadı. "
                "Lütfen 'pip install reportlab' komutunu çalıştırın."
            )

        # ── Font ayarları ────────────────────────────────────────────────────
        try:
            pdfmetrics.registerFont(TTFont("Arial", "Arial.ttf"))
            pdfmetrics.registerFont(TTFont("Arial-Bold", "Arialbd.ttf"))
            FONT = "Arial"
            FONT_BOLD = "Arial-Bold"
        except Exception:
            FONT = "Helvetica"
            FONT_BOLD = "Helvetica-Bold"

        # ── Sayfa ayarları ───────────────────────────────────────────────────
        buffer = io.BytesIO()
        full_name = getattr(personal_info, "full_name", "CV") or "CV"
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            topMargin=inch,
            bottomMargin=inch,
            leftMargin=inch,
            rightMargin=inch,
            title=f"{full_name} - CV",
            author=full_name,
        )

        # ── Stil tanımları ───────────────────────────────────────────────────
        styles = getSampleStyleSheet()

        s_name = ParagraphStyle(
            "ATSName", parent=styles["Normal"],
            fontName=FONT_BOLD, fontSize=16,
            alignment=TA_CENTER, spaceAfter=4, textColor=black,
        )
        s_title = ParagraphStyle(
            "ATSTitle", parent=styles["Normal"],
            fontName=FONT, fontSize=12,
            alignment=TA_CENTER, spaceAfter=4,
            textColor=HexColor("#4B5563"),
        )
        s_contact = ParagraphStyle(
            "ATSContact", parent=styles["Normal"],
            fontName=FONT, fontSize=10,
            alignment=TA_CENTER, spaceAfter=12,
            textColor=HexColor("#374151"),
        )
        s_heading = ParagraphStyle(
            "ATSHeading", parent=styles["Normal"],
            fontName=FONT_BOLD, fontSize=13,
            spaceBefore=14, spaceAfter=6, textColor=black,
        )
        s_body = ParagraphStyle(
            "ATSBody", parent=styles["Normal"],
            fontName=FONT, fontSize=11,
            leading=14, spaceAfter=4, textColor=black,
        )
        s_bold = ParagraphStyle(
            "ATSBold", parent=s_body, fontName=FONT_BOLD,
        )
        s_proj_title = ParagraphStyle(
            "ATSProjTitle", parent=s_body,
            fontName=FONT_BOLD, fontSize=11, spaceAfter=2,
        )
        s_tech = ParagraphStyle(
            "ATSTech", parent=s_body,
            fontName=FONT, fontSize=10,
            textColor=HexColor("#6B7280"), spaceAfter=8,
        )

        def hr() -> HRFlowable:
            return HRFlowable(
                width="100%", thickness=0.5,
                color=HexColor("#D1D5DB"),
                spaceBefore=2, spaceAfter=8,
            )

        # ── Flowable oluşturma ───────────────────────────────────────────────
        elements = []
        lang = config.language

        # 1. İletişim Bloğu
        elements.append(Paragraph(full_name, s_name))
        title_val = getattr(personal_info, "title", "") or ""
        if title_val:
            elements.append(Paragraph(title_val, s_title))
        contact_line = self._build_contact_line(personal_info, s_contact)
        if contact_line:
            elements.append(contact_line)
        elements.append(hr())

        # 2. Professional Summary
        bio = getattr(personal_info, "bio", "") or ""
        if bio:
            heading = "PROFESSIONAL SUMMARY" if lang == "en" else "PROFESYONEl ÖZET"
            elements.append(Paragraph(heading, s_heading))
            elements.append(hr())
            summary = bio
            if config.target_role:
                summary = (
                    f"Results-driven {config.target_role} with expertise in "
                    f"software development. {bio}"
                )
            elements.append(Paragraph(summary, s_body))
            elements.append(Spacer(1, 8))

        # 3. Technical Skills
        if skills:
            heading = "TECHNICAL SKILLS" if lang == "en" else "TEKNİK BECERİLER"
            elements.append(Paragraph(heading, s_heading))
            elements.append(hr())
            elements.extend(self._build_skills(skills, s_body))
            elements.append(Spacer(1, 8))

        # 4. Projects
        selected = (
            [p for p in projects if p.id in config.selected_project_ids]
            if config.selected_project_ids else projects
        )
        if selected:
            heading = "PROJECTS" if lang == "en" else "PROJELER"
            elements.append(Paragraph(heading, s_heading))
            elements.append(hr())
            for proj in selected:
                elements.extend(self._build_project(proj, s_proj_title, s_body, s_tech))

        # 5. Experience
        if experience:
            heading = "EXPERIENCE" if lang == "en" else "DENEYİM"
            elements.append(Paragraph(heading, s_heading))
            elements.append(hr())
            sorted_exp = sorted(experience, key=lambda x: x.start_date or "", reverse=True)
            for exp in sorted_exp:
                elements.extend(self._build_experience(exp, s_bold, s_tech, s_body))

        # 6. Education
        if education:
            heading = "EDUCATION" if lang == "en" else "EĞİTİM"
            elements.append(Paragraph(heading, s_heading))
            elements.append(hr())
            for edu in education:
                elements.extend(self._build_education(edu, s_bold, s_tech))

        # 7. Certifications
        if certificates:
            heading = "CERTIFICATIONS" if lang == "en" else "SERTİFİKALAR"
            elements.append(Paragraph(heading, s_heading))
            elements.append(hr())
            for cert in certificates:
                self._build_certificate(cert, elements, s_body)

        doc.build(elements)
        return buffer.getvalue()

    # ── Yardımcı metodlar ────────────────────────────────────────────────────

    @staticmethod
    def _build_contact_line(personal_info, style):
        """İletişim bilgilerini pipe ayraçlı tek satır olarak döner."""
        from reportlab.platypus import Paragraph

        parts = []
        email = getattr(personal_info, "email", None)
        phone = getattr(personal_info, "phone", None)
        github = getattr(personal_info, "github_url", None)
        linkedin = getattr(personal_info, "linkedin_url", None)
        website = getattr(personal_info, "website_url", None)

        if email:
            parts.append(f'<a href="mailto:{email}" color="#374151">{email}</a>')
        if phone:
            parts.append(phone)
        if github:
            short = github.replace("https://", "").replace("http://", "")
            parts.append(f'<a href="{github}" color="#374151">{short}</a>')
        if linkedin:
            short = linkedin.replace("https://", "").replace("http://", "")
            parts.append(f'<a href="{linkedin}" color="#374151">{short}</a>')
        if website:
            short = website.replace("https://", "").replace("http://", "")
            parts.append(f'<a href="{website}" color="#374151">{short}</a>')

        if not parts:
            return None
        return Paragraph(" | ".join(parts), style)

    @staticmethod
    def _build_skills(skills: list, style) -> list:
        """Skill'leri kategori bazlı düz metin olarak gruplar."""
        from collections import defaultdict
        from reportlab.platypus import Paragraph

        grouped: dict[str, list[str]] = defaultdict(list)
        for s in skills:
            cat = (getattr(s, "category", "") or "OTHER").upper()
            grouped[cat].append(s.name)

        order = ["LANGUAGE", "FRAMEWORK", "DATABASE", "TOOL", "DEVOPS"]
        labels = {
            "LANGUAGE":  "Languages",
            "FRAMEWORK": "Frameworks",
            "DATABASE":  "Databases",
            "TOOL":      "Tools",
            "DEVOPS":    "DevOps",
        }
        # Bilinen kategoriler önce, geri kalanlar sona
        cats = [c for c in order if c in grouped]
        cats += [c for c in grouped if c not in order]

        elements = []
        for cat in cats:
            label = labels.get(cat, cat.title())
            text = f"<b>{label}:</b> {', '.join(grouped[cat])}"
            elements.append(Paragraph(text, style))
        return elements

    @staticmethod
    def _build_project(proj, s_title, s_body, s_tech) -> list:
        """Tek proje için flowable listesi döner."""
        from reportlab.platypus import Paragraph, Spacer

        elements = []
        elements.append(Paragraph(f"<b>{proj.title}</b>", s_title))

        # Tarih
        date_str = ""
        if getattr(proj, "start_date", None):
            date_str = proj.start_date
            if getattr(proj, "end_date", None):
                date_str += f" - {proj.end_date}"
            else:
                date_str += " - Present"
        if date_str:
            elements.append(Paragraph(date_str, s_tech))

        # Açıklama (full_description öncelikli)
        desc = getattr(proj, "full_description", "") or getattr(proj, "description", "") or ""
        if desc:
            elements.append(Paragraph(desc, s_body))

        # Teknolojiler (tags listesinden al)
        tags = getattr(proj, "tags", [])
        if tags:
            tech_str = ", ".join(t.tag_name for t in tags)
            elements.append(Paragraph(f"<i>Technologies: {tech_str}</i>", s_tech))
        else:
            elements.append(Spacer(1, 6))

        elements.append(Spacer(1, 6))
        return elements

    @staticmethod
    def _build_experience(exp, s_bold, s_tech, s_body) -> list:
        """Tek deneyim için flowable listesi döner."""
        from reportlab.platypus import Paragraph, Spacer

        elements = []
        elements.append(Paragraph(f"<b>{exp.company}</b>", s_bold))

        date_str = exp.start_date or ""
        if getattr(exp, "is_current", False):
            date_str += " - Present"
        elif getattr(exp, "end_date", None):
            date_str += f" - {exp.end_date}"
        elements.append(Paragraph(f"{exp.position} | {date_str}", s_tech))

        desc = getattr(exp, "description", "") or ""
        if desc:
            for line in desc.split("\n"):
                line = line.strip()
                if line:
                    elements.append(Paragraph(f"• {line}", s_body))

        elements.append(Spacer(1, 6))
        return elements

    @staticmethod
    def _build_education(edu, s_bold, s_tech) -> list:
        """Tek eğitim kaydı için flowable listesi döner."""
        from reportlab.platypus import Paragraph, Spacer

        elements = []
        elements.append(Paragraph(f"<b>{edu.institution}</b>", s_bold))

        date_str = edu.start_date or ""
        end = getattr(edu, "end_date", None)
        if end:
            date_str += f" - {end}"

        degree_line = edu.degree
        field = getattr(edu, "field", "") or ""
        if field:
            degree_line += f", {field}"
        elements.append(Paragraph(f"{degree_line} | {date_str}", s_tech))
        elements.append(Spacer(1, 4))
        return elements

    @staticmethod
    def _build_certificate(cert, elements: list, s_body) -> None:
        """Tek sertifika için flowable ekler."""
        from reportlab.platypus import Paragraph

        cert_text = f"<b>{cert.name}</b> - {cert.issuer} ({cert.date or ''})"
        url = getattr(cert, "verification_url", None) or getattr(cert, "url", None)
        if url:
            cert_text = f'<a href="{url}">{cert_text}</a>'
        elements.append(Paragraph(cert_text, s_body))
