"""presentation/admin/pages/dashboard_page.py — Admin dashboard."""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QGridLayout
)
from PySide6.QtCore import Qt

from styles.constants import COLORS, FONTS, SPACING
from controllers.project_controller import ProjectController
from controllers.certificate_controller import CertificateController
from controllers.resource_controller import ResourceController


class DashboardPage(QWidget):
    """Hızlı istatistikler: proje/sertifika/kaynak sayısı."""

    def __init__(
        self,
        project_ctrl: ProjectController,
        cert_ctrl: CertificateController,
        resource_ctrl: ResourceController,
        parent=None,
    ):
        super().__init__(parent)
        self._project_ctrl  = project_ctrl
        self._cert_ctrl     = cert_ctrl
        self._resource_ctrl = resource_ctrl
        self._build_ui()
        self.refresh()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 32, 32, 32)
        layout.setSpacing(32)

        title = QLabel("Dashboard")
        title.setStyleSheet(f"""
            color: {COLORS['text_primary']};
            font-size: {FONTS['size_2xl']}px;
            font-weight: 700;
        """)
        layout.addWidget(title)

        subtitle = QLabel("Portföy içeriklerine genel bakış")
        subtitle.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 14px;")
        layout.addWidget(subtitle)

        # İstatistik kartları
        self._stat_grid = QGridLayout()
        self._stat_grid.setSpacing(20)
        layout.addLayout(self._stat_grid)

        layout.addStretch()

    def refresh(self) -> None:
        # Mevcut kartları temizle
        while self._stat_grid.count():
            item = self._stat_grid.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        projects  = self._project_ctrl.get_all()
        certs     = self._cert_ctrl.get_all()
        resources = self._resource_ctrl.get_all()

        stats = [
            ("Toplam Proje",     len(projects),                              COLORS["accent_blue"]),
            ("Öne Çıkan",        sum(1 for p in projects if p.is_featured), COLORS["warning"]),
            ("Sertifika",        len(certs),                                 COLORS["success"]),
            ("Kaynak",           len(resources),                             COLORS["accent_silver"]),
        ]

        for i, (label, count, color) in enumerate(stats):
            card = self._make_stat_card(label, count, color)
            self._stat_grid.addWidget(card, i // 2, i % 2)

    def _make_stat_card(self, label: str, count: int, color: str) -> QFrame:
        frame = QFrame()
        frame.setStyleSheet(f"""
            QFrame {{
                background: {COLORS['bg_card']};
                border: 1px solid {COLORS['border']};
                border-left: 4px solid {color};
                border-radius: 12px;
                padding: 0;
            }}
        """)
        col = QVBoxLayout(frame)
        col.setContentsMargins(24, 20, 24, 20)
        col.setSpacing(8)

        count_lbl = QLabel(str(count))
        count_lbl.setStyleSheet(f"""
            color: {color};
            font-size: 40px;
            font-weight: 700;
        """)
        col.addWidget(count_lbl)

        lbl = QLabel(label)
        lbl.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 14px;")
        col.addWidget(lbl)

        return frame
