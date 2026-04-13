"""presentation/showcase/main_window.py — Ana pencere: vitrin + admin stack."""

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QScrollArea, QStackedWidget
)
from PySide6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QTimer

from controllers.showcase_controller import ShowcaseController
from presentation.showcase.navbar import ShowcaseNavbar
from presentation.showcase.sections.about_section import AboutSection
from presentation.showcase.sections.projects_section import ProjectsSection
from presentation.showcase.sections.vision_section import VisionSection
from presentation.showcase.sections.certificates_section import CertificatesSection
from presentation.admin.admin_window import AdminPanel
from styles.constants import COLORS
from config import WINDOW_MIN_WIDTH, WINDOW_MIN_HEIGHT, APP_NAME
from di_container import DIContainer

# Stack indeksleri
_IDX_SHOWCASE = 0
_IDX_ADMIN    = 1


class ShowcaseWindow(QMainWindow):
    """
    Ana uygulama penceresi.
    QStackedWidget ile vitrin (0) ve admin panel (1) arasında geçiş yapar.
    Ayrı bir admin penceresi açılmaz.
    """

    def __init__(self, container: DIContainer):
        super().__init__()
        self._controller = container.showcase_controller
        self._container  = container
        self._click_count = 0
        self._click_timer = QTimer()
        self._click_timer.setSingleShot(True)
        self._click_timer.timeout.connect(self._reset_click_count)

        self.setWindowTitle(APP_NAME)
        self.setMinimumSize(WINDOW_MIN_WIDTH, WINDOW_MIN_HEIGHT)

        self._build_ui()
        self._load_data()

    # ── UI ──────────────────────────────────────────────────────────────────

    def _build_ui(self) -> None:
        self._root_stack = QStackedWidget()
        self.setCentralWidget(self._root_stack)

        # Sayfa 0: vitrin
        self._root_stack.addWidget(self._build_showcase_page())

        # Sayfa 1: admin panel (lazy-build, tek seferlik)
        self._admin_panel = AdminPanel(self._container, parent=self)
        self._admin_panel.back_requested.connect(self.switch_to_showcase)
        self._root_stack.addWidget(self._admin_panel)

        self.setStyleSheet("QMainWindow { background: #0D1117; }")

    def _build_showcase_page(self) -> QWidget:
        page = QWidget()
        root = QVBoxLayout(page)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # Navbar (sabit)
        self._navbar = ShowcaseNavbar()
        self._navbar.scroll_requested.connect(self._scroll_to_section)
        self._navbar.admin_requested.connect(self.switch_to_admin)
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
        self._content.setStyleSheet("background: #0D1117;")
        content_layout = QVBoxLayout(self._content)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)

        self._about_section    = AboutSection()
        self._projects_section = ProjectsSection()
        self._vision_section   = VisionSection()
        self._certs_section    = CertificatesSection()

        content_layout.addWidget(self._about_section)
        content_layout.addWidget(self._projects_section)
        content_layout.addWidget(self._vision_section)
        content_layout.addWidget(self._certs_section)

        self._scroll.setWidget(self._content)

        self._sections = {
            "about":        self._about_section,
            "projects":     self._projects_section,
            "vision":       self._vision_section,
            "certificates": self._certs_section,
        }

        return page

    # ── Geçiş ───────────────────────────────────────────────────────────────

    def switch_to_admin(self) -> None:
        """Vitrin → Admin."""
        self._admin_panel.activate()
        self._root_stack.setCurrentIndex(_IDX_ADMIN)

    def switch_to_showcase(self) -> None:
        """Admin → Vitrin (veriyi yenile)."""
        self._root_stack.setCurrentIndex(_IDX_SHOWCASE)
        self._load_data()

    # ── Veri ────────────────────────────────────────────────────────────────

    def _load_data(self) -> None:
        info     = self._controller.get_personal_info()
        projects = self._controller.get_all_projects()
        certs    = self._controller.get_certificates()

        self._about_section.load_data(info)
        self._projects_section.load_data(projects)
        self._vision_section.load_data(info)
        self._certs_section.load_data(certs)

    def reload(self) -> None:
        """Dışarıdan çağrılabilir yenileme."""
        self._load_data()

    # ── Scroll ──────────────────────────────────────────────────────────────

    def _scroll_to_section(self, section_id: str) -> None:
        section = self._sections.get(section_id)
        if not section:
            return
        target_y  = section.mapTo(self._content, section.rect().topLeft()).y()
        current_y = self._scroll.verticalScrollBar().value()

        self._anim = QPropertyAnimation(self._scroll.verticalScrollBar(), b"value", self)
        self._anim.setStartValue(current_y)
        self._anim.setEndValue(target_y)
        self._anim.setDuration(300)
        self._anim.setEasingCurve(QEasingCurve.OutCubic)
        self._anim.start()

    # ── Gizli admin trigger — başlık çubuğuna 5 kez çift tıklama ───────────

    def mouseDoubleClickEvent(self, event) -> None:
        self._click_count += 1
        self._click_timer.start(2000)
        if self._click_count >= 5:
            self._click_count = 0
            self._click_timer.stop()
            self.switch_to_admin()
        super().mouseDoubleClickEvent(event)

    def _reset_click_count(self) -> None:
        self._click_count = 0
