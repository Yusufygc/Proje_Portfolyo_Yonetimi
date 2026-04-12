"""presentation/showcase/sections/projects_section.py — Projelerim bölümü."""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QScrollArea,
    QFrame, QPushButton, QGridLayout
)
from PySide6.QtCore import Qt

from styles.constants import COLORS, FONTS, SPACING
from domain.models.project import Project
from presentation.showcase.widgets.project_card import ProjectCard


class ProjectsSection(QWidget):
    """Vitrin projeler bölümü — ProjectCard ızgarası."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("projects_section")
        self._build_ui()

    def _build_ui(self) -> None:
        self.setStyleSheet(f"""
            QWidget#projects_section {{
                background: {COLORS['grad_projects']};
            }}
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(64, 80, 64, 80)
        layout.setSpacing(40)

        # Başlık
        header_col = QVBoxLayout()
        header_col.setSpacing(8)

        title = QLabel("Projelerim")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet(f"""
            color: {COLORS['text_primary']};
            font-size: {FONTS['size_2xl']}px;
            font-weight: 700;
        """)
        header_col.addWidget(title)

        subtitle = QLabel("Geliştirdiğim ürünler ve açık kaynak katkılarım")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: {FONTS['size_md']}px;")
        header_col.addWidget(subtitle)

        accent = QFrame()
        accent.setFixedHeight(3)
        accent.setFixedWidth(60)
        accent.setStyleSheet(f"background: {COLORS['accent_blue']}; border-radius: 2px;")
        accent_wrapper = QHBoxLayout()
        accent_wrapper.setAlignment(Qt.AlignCenter)
        accent_wrapper.addWidget(accent)
        header_col.addLayout(accent_wrapper)

        layout.addLayout(header_col)

        # Kart ızgarası
        self._grid_widget = QWidget()
        self._grid_widget.setStyleSheet("background: transparent;")
        self._grid = QGridLayout(self._grid_widget)
        self._grid.setSpacing(24)
        self._grid.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self._grid_widget)

        self._empty_label = QLabel("Henüz proje eklenmemiş.")
        self._empty_label.setAlignment(Qt.AlignCenter)
        self._empty_label.setStyleSheet(f"color: {COLORS['text_muted']}; font-size: {FONTS['size_md']}px;")
        self._empty_label.setVisible(False)
        layout.addWidget(self._empty_label)

    def load_data(self, projects: list[Project]) -> None:
        """Proje listesini görüntüler."""
        # Mevcut kartları temizle
        while self._grid.count():
            item = self._grid.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        if not projects:
            self._empty_label.setVisible(True)
            return

        self._empty_label.setVisible(False)
        cols = 3
        for i, project in enumerate(projects):
            card = ProjectCard(project)
            self._grid.addWidget(card, i // cols, i % cols)
