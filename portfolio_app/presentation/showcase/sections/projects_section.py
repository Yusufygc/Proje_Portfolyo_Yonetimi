"""presentation/showcase/sections/projects_section.py — Projelerim bölümü."""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QGridLayout
)
from PySide6.QtCore import Qt

from styles.constants import COLORS, FONTS
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
                background: {COLORS['bg_secondary']};
                border-top: 1px solid {COLORS['border_light']};
            }}
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(64, 80, 64, 80)
        layout.setSpacing(40)

        # Section header
        header_col = QVBoxLayout()
        header_col.setSpacing(8)

        label = QLabel("// PROJELER")
        label.setStyleSheet(f"""
            color: {COLORS['accent_blue']};
            font-size: 12px;
            font-weight: 600;
            letter-spacing: 3px;
        """)
        header_col.addWidget(label)

        title = QLabel("Projelerim")
        title.setStyleSheet(f"""
            color: {COLORS['text_primary']};
            font-size: 36px;
            font-weight: 700;
        """)
        header_col.addWidget(title)

        subtitle = QLabel("Geliştirdiğim ürünler ve açık kaynak katkılarım")
        subtitle.setStyleSheet(f"""
            color: {COLORS['text_secondary']};
            font-size: 15px;
        """)
        header_col.addWidget(subtitle)

        layout.addLayout(header_col)

        # Kart ızgarası — 2 sütun
        self._grid_widget = QWidget()
        self._grid_widget.setStyleSheet("background: transparent;")
        self._grid = QGridLayout(self._grid_widget)
        self._grid.setSpacing(20)
        self._grid.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self._grid_widget)

        self._empty_label = QLabel("Henüz proje eklenmemiş.")
        self._empty_label.setAlignment(Qt.AlignCenter)
        self._empty_label.setStyleSheet(f"color: {COLORS['text_muted']}; font-size: 15px;")
        self._empty_label.setVisible(False)
        layout.addWidget(self._empty_label)

    def load_data(self, projects: list[Project]) -> None:
        """Proje listesini görüntüler."""
        while self._grid.count():
            item = self._grid.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        if not projects:
            self._empty_label.setVisible(True)
            return

        self._empty_label.setVisible(False)
        cols = 2
        for i, project in enumerate(projects):
            card = ProjectCard(project)
            self._grid.addWidget(card, i // cols, i % cols)
