"""presentation/showcase/widgets/project_card.py — Vitrin proje kartı."""

import webbrowser
from PySide6.QtWidgets import (
    QFrame, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
)
from PySide6.QtCore import Qt

from domain.models.project import Project
from domain.enums.project_status import ProjectStatus


class ProjectCard(QFrame):
    """Vitrin'de gösterilen proje kartı — GitHub dark tema."""

    def __init__(self, project: Project, parent=None):
        super().__init__(parent)
        self.setObjectName("project_card")
        self._project = project
        self._build_ui()

    def _build_ui(self) -> None:
        self.setStyleSheet("""
            QFrame#project_card {
                background: #161B22;
                border: 1px solid #30363D;
                border-radius: 12px;
            }
            QFrame#project_card:hover {
                border-color: #2F81F7;
            }
            QPushButton#gh_btn {
                background: transparent;
                border: 1px solid #30363D;
                color: #8B949E;
                padding: 8px 16px;
                border-radius: 6px;
                font-size: 13px;
                text-align: left;
            }
            QPushButton#gh_btn:hover {
                border-color: #2F81F7;
                color: #2F81F7;
            }
            QPushButton#demo_btn {
                background: transparent;
                border: 1px solid #30363D;
                color: #8B949E;
                padding: 8px 16px;
                border-radius: 6px;
                font-size: 13px;
            }
            QPushButton#demo_btn:hover {
                border-color: #2F81F7;
                color: #2F81F7;
            }
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
            featured_lbl.setStyleSheet("""
                color: #D29922;
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
        title.setStyleSheet("""
            color: #E6EDF3;
            font-size: 18px;
            font-weight: 600;
        """)
        title.setWordWrap(True)
        layout.addWidget(title)
        layout.addSpacing(8)

        # Kısa açıklama
        desc = QLabel(self._project.short_description or "")
        desc.setWordWrap(True)
        desc.setStyleSheet("color: #8B949E; font-size: 14px;")
        layout.addWidget(desc)
        layout.addSpacing(12)

        # Teknoloji etiketleri
        if self._project.tags:
            tags_row = QHBoxLayout()
            tags_row.setSpacing(8)
            for tag in self._project.tags[:5]:
                lbl = QLabel(tag.tag_name)
                lbl.setStyleSheet("""
                    background: rgba(47, 129, 247, 0.1);
                    border: 1px solid rgba(47, 129, 247, 0.3);
                    border-radius: 20px;
                    color: #79C0FF;
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
            lbl.setStyleSheet("""
                background: rgba(63, 185, 80, 0.15);
                border: 1px solid rgba(63, 185, 80, 0.4);
                border-radius: 20px;
                color: #3FB950;
                font-size: 12px;
                font-weight: 500;
                padding: 4px 10px;
            """)
        elif status == ProjectStatus.BEKLEMEDE:
            lbl.setText("◐ Beklemede")
            lbl.setStyleSheet("""
                background: rgba(210, 153, 34, 0.15);
                border: 1px solid rgba(210, 153, 34, 0.4);
                border-radius: 20px;
                color: #D29922;
                font-size: 12px;
                font-weight: 500;
                padding: 4px 10px;
            """)
        elif status == ProjectStatus.TAMAMLANDI:
            lbl.setText("✓ Tamamlandı")
            lbl.setStyleSheet("""
                background: rgba(47, 129, 247, 0.15);
                border: 1px solid rgba(47, 129, 247, 0.4);
                border-radius: 20px;
                color: #2F81F7;
                font-size: 12px;
                font-weight: 500;
                padding: 4px 10px;
            """)
        elif status == ProjectStatus.IPTAL:
            lbl.setText("✕ İptal")
            lbl.setStyleSheet("""
                background: rgba(239, 68, 68, 0.1);
                border: 1px solid rgba(239, 68, 68, 0.3);
                border-radius: 20px;
                color: #EF4444;
                font-size: 12px;
                font-weight: 500;
                padding: 4px 10px;
            """)
        else:
            lbl.setText(status.label() if hasattr(status, 'label') else str(status))
            lbl.setStyleSheet("""
                background: rgba(72, 79, 88, 0.2);
                border: 1px solid #30363D;
                border-radius: 20px;
                color: #8B949E;
                font-size: 12px;
                font-weight: 500;
                padding: 4px 10px;
            """)

        return lbl
