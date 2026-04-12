"""presentation/showcase/widgets/project_card.py — Vitrin proje kartı."""

import webbrowser
from PySide6.QtWidgets import (
    QFrame, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

from styles.constants import COLORS, FONTS, SPACING
from domain.models.project import Project
from domain.enums.project_status import ProjectStatus


class ProjectCard(QFrame):
    """Vitrin'de gösterilen proje kartı."""

    STATUS_COLORS = {
        ProjectStatus.DEVAM_EDIYOR: COLORS["info"],
        ProjectStatus.TAMAMLANDI:   COLORS["success"],
        ProjectStatus.BEKLEMEDE:    COLORS["warning"],
        ProjectStatus.IPTAL:        COLORS["error"],
    }

    def __init__(self, project: Project, parent=None):
        super().__init__(parent)
        self.setObjectName("card")
        self._project = project
        self._build_ui()

    def _build_ui(self) -> None:
        self.setStyleSheet(f"""
            QFrame#card {{
                background: {COLORS['bg_card']};
                border: 1px solid {COLORS['border']};
                border-radius: 12px;
            }}
            QFrame#card:hover {{
                border-color: {COLORS['accent_blue']};
            }}
        """)
        self.setMinimumWidth(280)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        # Durum badge + featured
        top_row = QHBoxLayout()
        status_badge = QLabel(self._project.status.label())
        color = self.STATUS_COLORS.get(self._project.status, COLORS["info"])
        status_badge.setStyleSheet(f"""
            QLabel {{
                background: rgba(74, 158, 255, 0.1);
                color: {color};
                border: 1px solid {color};
                border-radius: 10px;
                font-size: 10px;
                font-weight: 600;
                padding: 2px 10px;
            }}
        """)
        top_row.addWidget(status_badge)
        top_row.addStretch()
        if self._project.is_featured:
            star = QLabel("Öne Çıkan")
            star.setStyleSheet(f"""
                color: {COLORS['warning']};
                font-size: 10px;
                font-weight: 600;
            """)
            top_row.addWidget(star)
        layout.addLayout(top_row)

        # Başlık
        title = QLabel(self._project.title)
        title.setStyleSheet(f"""
            color: {COLORS['text_primary']};
            font-size: {FONTS['size_md']}px;
            font-weight: 700;
        """)
        title.setWordWrap(True)
        layout.addWidget(title)

        # Kısa açıklama
        desc = QLabel(self._project.short_description)
        desc.setWordWrap(True)
        desc.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 13px;")
        desc.setMaximumHeight(60)
        layout.addWidget(desc)

        # Etiketler
        if self._project.tags:
            tags_row = QHBoxLayout()
            tags_row.setSpacing(6)
            for tag in self._project.tags[:4]:
                lbl = QLabel(tag.tag_name)
                lbl.setObjectName("tag")
                lbl.setStyleSheet(f"""
                    background: {COLORS['tag_bg']};
                    border: 1px solid {COLORS['tag_border']};
                    border-radius: 10px;
                    color: {COLORS['tag_text']};
                    font-size: 11px;
                    padding: 2px 8px;
                """)
                tags_row.addWidget(lbl)
            tags_row.addStretch()
            layout.addLayout(tags_row)

        layout.addStretch()

        # Linkler
        link_row = QHBoxLayout()
        link_row.setSpacing(8)
        if self._project.github_url:
            gh_btn = QPushButton("GitHub")
            gh_btn.setObjectName("btn_flat")
            gh_btn.setCursor(Qt.PointingHandCursor)
            url = self._project.github_url
            gh_btn.clicked.connect(lambda: webbrowser.open(url))
            link_row.addWidget(gh_btn)
        if self._project.demo_url:
            demo_btn = QPushButton("Demo")
            demo_btn.setCursor(Qt.PointingHandCursor)
            url = self._project.demo_url
            demo_btn.clicked.connect(lambda: webbrowser.open(url))
            link_row.addWidget(demo_btn)
        link_row.addStretch()
        layout.addLayout(link_row)
