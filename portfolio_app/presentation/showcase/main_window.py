"""presentation/showcase/main_window.py — Tek sayfa kaydırmalı vitrin penceresi."""

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QScrollArea
)
from PySide6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QTimer

from controllers.showcase_controller import ShowcaseController
from presentation.showcase.navbar import ShowcaseNavbar
from presentation.showcase.sections.about_section import AboutSection
from presentation.showcase.sections.projects_section import ProjectsSection
from presentation.showcase.sections.vision_section import VisionSection
from presentation.showcase.sections.certificates_section import CertificatesSection
from styles.constants import COLORS
from config import WINDOW_MIN_WIDTH, WINDOW_MIN_HEIGHT, APP_NAME


class ShowcaseWindow(QMainWindow):
    """
    Vitrin ana penceresi.
    - Sabit navbar üstte
    - Tek scroll area altında 4 bölüm
    - Gizli admin trigger: başlık çubuğuna 5 kez çift tıklama
    """

    admin_requested = None  # main.py tarafından atanır

    def __init__(self, controller: ShowcaseController):
        super().__init__()
        self._controller = controller
        self._click_count = 0
        self._click_timer = QTimer()
        self._click_timer.setSingleShot(True)
        self._click_timer.timeout.connect(self._reset_click_count)

        self.setWindowTitle(APP_NAME)
        self.setMinimumSize(WINDOW_MIN_WIDTH, WINDOW_MIN_HEIGHT)

        self._build_ui()
        self._load_data()

    def _build_ui(self) -> None:
        central = QWidget()
        self.setCentralWidget(central)

        root = QVBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # Navbar (sabit)
        self._navbar = ShowcaseNavbar()
        self._navbar.scroll_requested.connect(self._scroll_to_section)
        root.addWidget(self._navbar)

        # Scroll area
        self._scroll = QScrollArea()
        self._scroll.setWidgetResizable(True)
        self._scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self._scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self._scroll.setStyleSheet("QScrollArea { border: none; }")
        root.addWidget(self._scroll)

        # Scroll içeriği
        self._content = QWidget()
        self._content.setStyleSheet(f"background: {COLORS['bg_primary']};")
        content_layout = QVBoxLayout(self._content)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)

        self._about_section   = AboutSection()
        self._projects_section = ProjectsSection()
        self._vision_section  = VisionSection()
        self._certs_section   = CertificatesSection()

        content_layout.addWidget(self._about_section)
        content_layout.addWidget(self._projects_section)
        content_layout.addWidget(self._vision_section)
        content_layout.addWidget(self._certs_section)

        self._scroll.setWidget(self._content)

        # Bölüm referansları
        self._sections = {
            "about":        self._about_section,
            "projects":     self._projects_section,
            "vision":       self._vision_section,
            "certificates": self._certs_section,
        }

        self.setStyleSheet(f"QMainWindow {{ background: {COLORS['bg_primary']}; }}")

    def _load_data(self) -> None:
        info     = self._controller.get_personal_info()
        projects = self._controller.get_all_projects()
        certs    = self._controller.get_certificates()

        self._about_section.load_data(info)
        self._projects_section.load_data(projects)
        self._vision_section.load_data(info)
        self._certs_section.load_data(certs)

    def _scroll_to_section(self, section_id: str) -> None:
        section = self._sections.get(section_id)
        if not section:
            return
        # Smooth scroll
        target_y = section.mapTo(self._content, section.rect().topLeft()).y()
        current_y = self._scroll.verticalScrollBar().value()

        self._anim = QPropertyAnimation(self._scroll.verticalScrollBar(), b"value", self)
        self._anim.setStartValue(current_y)
        self._anim.setEndValue(target_y)
        self._anim.setDuration(300)
        self._anim.setEasingCurve(QEasingCurve.OutCubic)
        self._anim.start()

    def reload(self) -> None:
        """Admin değişiklikleri sonrası veriyi yeniden yükler."""
        self._load_data()

    # ── Gizli admin trigger — başlık çubuğuna 5 kez çift tıklama ───────────

    def mouseDoubleClickEvent(self, event) -> None:
        self._click_count += 1
        self._click_timer.start(2000)  # 2 saniye içinde 5 çift tıklama
        if self._click_count >= 5:
            self._click_count = 0
            self._click_timer.stop()
            if callable(self.admin_requested):
                self.admin_requested()
        super().mouseDoubleClickEvent(event)

    def _reset_click_count(self) -> None:
        self._click_count = 0
