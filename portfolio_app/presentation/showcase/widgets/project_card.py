"""presentation/showcase/widgets/project_card.py — Vitrin proje kartı."""

import webbrowser
from PySide6.QtWidgets import (
    QFrame, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
)
from PySide6.QtCore import Qt

from styles.constants import COLORS
from domain.models.project import Project
from domain.enums.project_status import ProjectStatus


class ProjectCard(QFrame):
    """Vitrin'de gösterilen proje kartı — tema uyumlu."""

    def __init__(self, project: Project, parent=None):
        super().__init__(parent)
        self.setObjectName("project_card")
        self._project = project
        self._build_ui()

    def _build_ui(self) -> None:
        self.setStyleSheet(f"""
            QFrame#project_card {{
                background: {COLORS['bg_card']};
                border: 1px solid {COLORS['border']};
                border-radius: 12px;
            }}
            QFrame#project_card:hover {{
                border-color: {COLORS['accent_blue']};
            }}
            QPushButton#gh_btn {{
                background: transparent;
                border: 1px solid {COLORS['border']};
                color: {COLORS['text_secondary']};
                padding: 6px 14px;
                border-radius: 6px;
                font-size: 12px;
                text-align: left;
            }}
            QPushButton#gh_btn:hover {{
                border-color: {COLORS['accent_blue']};
                color: {COLORS['accent_blue']};
            }}
            QPushButton#demo_btn {{
                background: transparent;
                border: 1px solid {COLORS['border']};
                color: {COLORS['text_secondary']};
                padding: 6px 14px;
                border-radius: 6px;
                font-size: 12px;
            }}
            QPushButton#demo_btn:hover {{
                border-color: {COLORS['accent_blue']};
                color: {COLORS['accent_blue']};
            }}
        """)
        self.setMinimumWidth(280)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(0)

        # Üst satır: status badge + featured
        top_row = QHBoxLayout()
        top_row.setSpacing(8)

        status_badge = self._make_status_badge(self._project.status)
        top_row.addWidget(status_badge)
        top_row.addStretch()

        if self._project.is_featured:
            featured_lbl = QLabel("✦ Öne Çıkan")
            featured_lbl.setStyleSheet(f"""
                color: {COLORS['warning']};
                font-size: 11px;
                font-weight: 600;
                background: rgba(210, 153, 34, 0.1);
                border: 1px solid rgba(210, 153, 34, 0.4);
                border-radius: 10px;
                padding: 2px 8px;
            """)
            top_row.addWidget(featured_lbl)

        layout.addLayout(top_row)
        layout.addSpacing(16)

        # Başlık
        title = QLabel(self._project.title)
        title.setStyleSheet(f"""
            color: {COLORS['text_primary']};
            font-size: 18px;
            font-weight: 600;
        """)
        title.setWordWrap(True)
        layout.addWidget(title)
        layout.addSpacing(8)

        # Kısa açıklama
        desc = QLabel(self._project.short_description or "")
        desc.setWordWrap(True)
        desc.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 14px;")
        layout.addWidget(desc)
        layout.addSpacing(12)

        # Teknoloji etiketleri
        if self._project.tags:
            tags_row = QHBoxLayout()
            tags_row.setSpacing(8)
            for tag in self._project.tags[:5]:
                lbl = QLabel(tag.tag_name)
                lbl.setStyleSheet(f"""
                    background: {COLORS['tag_bg']};
                    border: 1px solid {COLORS['tag_border']};
                    border-radius: 20px;
                    color: {COLORS['tag_text']};
                    font-size: 12px;
                    font-weight: 500;
                    padding: 3px 10px;
                """)
                tags_row.addWidget(lbl)
            tags_row.addStretch()
            layout.addLayout(tags_row)
            layout.addSpacing(12)

        # Boşluk — butonları alta iter
        layout.addStretch()

        # Linkler
        link_row = QHBoxLayout()
        link_row.setSpacing(8)
        if self._project.github_url:
            gh_btn = QPushButton("⊕  GitHub")
            gh_btn.setObjectName("gh_btn")
            gh_btn.setCursor(Qt.PointingHandCursor)
            url = self._project.github_url
            gh_btn.clicked.connect(lambda: webbrowser.open(url))
            link_row.addWidget(gh_btn)
        if self._project.demo_url:
            demo_btn = QPushButton("Demo →")
            demo_btn.setObjectName("demo_btn")
            demo_btn.setCursor(Qt.PointingHandCursor)
            url = self._project.demo_url
            demo_btn.clicked.connect(lambda: webbrowser.open(url))
            link_row.addWidget(demo_btn)
        link_row.addStretch()
        layout.addLayout(link_row)

    def _make_status_badge(self, status: ProjectStatus) -> QLabel:
        lbl = QLabel()

        if status == ProjectStatus.DEVAM_EDIYOR:
            lbl.setText("● Devam Ediyor")
            lbl.setStyleSheet(f"""
                background: rgba(63, 185, 80, 0.15);
                border: 1px solid rgba(63, 185, 80, 0.4);
                border-radius: 20px;
                color: {COLORS['success']};
                font-size: 12px;
                font-weight: 500;
                padding: 4px 10px;
            """)
        elif status == ProjectStatus.BEKLEMEDE:
            lbl.setText("◐ Beklemede")
            lbl.setStyleSheet(f"""
                background: rgba(210, 153, 34, 0.15);
                border: 1px solid rgba(210, 153, 34, 0.4);
                border-radius: 20px;
                color: {COLORS['warning']};
                font-size: 12px;
                font-weight: 500;
                padding: 4px 10px;
            """)
        elif status == ProjectStatus.TAMAMLANDI:
            lbl.setText("✓ Tamamlandı")
            lbl.setStyleSheet(f"""
                background: rgba(47, 129, 247, 0.15);
                border: 1px solid rgba(47, 129, 247, 0.4);
                border-radius: 20px;
                color: {COLORS['accent_blue']};
                font-size: 12px;
                font-weight: 500;
                padding: 4px 10px;
            """)
        elif status == ProjectStatus.IPTAL:
            lbl.setText("✕ İptal")
            lbl.setStyleSheet(f"""
                background: rgba(239, 68, 68, 0.1);
                border: 1px solid rgba(239, 68, 68, 0.3);
                border-radius: 20px;
                color: {COLORS['error']};
                font-size: 12px;
                font-weight: 500;
                padding: 4px 10px;
            """)
        else:
            lbl.setText(status.label() if hasattr(status, 'label') else str(status))
            lbl.setStyleSheet(f"""
                background: rgba(72, 79, 88, 0.2);
                border: 1px solid {COLORS['border']};
                border-radius: 20px;
                color: {COLORS['text_secondary']};
                font-size: 12px;
                font-weight: 500;
                padding: 4px 10px;
            """)

        return lbl
