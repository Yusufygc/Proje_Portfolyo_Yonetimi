"""presentation/admin/admin_window.py — Gizli admin panel ana penceresi."""

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QStackedWidget
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QKeySequence, QShortcut

from presentation.admin.sidebar import AdminSidebar
from presentation.admin.pages.dashboard_page import DashboardPage
from presentation.admin.pages.projects_page import ProjectsPage
from presentation.admin.pages.personal_info_page import PersonalInfoPage
from presentation.admin.pages.certificates_page import CertificatesPage
from presentation.admin.pages.resources_page import ResourcesPage
from styles.constants import COLORS
from config import WINDOW_MIN_WIDTH, WINDOW_MIN_HEIGHT
from di_container import DIContainer


class AdminWindow(QMainWindow):
    """
    Admin panel penceresi.
    Gizli — URL yok, menü yok.
    Kapatınca vitrin yeniden yüklenir.
    """

    closed = Signal()  # vitrine dönüş sinyali

    def __init__(self, container: DIContainer):
        super().__init__()
        self._container = container
        self.setWindowTitle("Admin Panel")
        self.setMinimumSize(WINDOW_MIN_WIDTH, WINDOW_MIN_HEIGHT)
        self._build_ui()

    def _build_ui(self) -> None:
        central = QWidget()
        self.setCentralWidget(central)

        layout = QHBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Sidebar
        self._sidebar = AdminSidebar()
        self._sidebar.page_requested.connect(self._switch_page)
        layout.addWidget(self._sidebar)

        # Sayfa stack
        self._stack = QStackedWidget()
        self._stack.setStyleSheet(f"background: {COLORS['bg_primary']};")
        layout.addWidget(self._stack)

        # Sayfaları oluştur
        c = self._container
        self._pages = {
            "dashboard":     DashboardPage(c.project_controller, c.certificate_controller, c.resource_controller),
            "projects":      ProjectsPage(c.project_controller),
            "personal_info": PersonalInfoPage(c.personal_info_controller),
            "certificates":  CertificatesPage(c.certificate_controller),
            "resources":     ResourcesPage(c.resource_controller),
        }
        for page in self._pages.values():
            self._stack.addWidget(page)

        self._switch_page("dashboard")
        self.setStyleSheet(f"QMainWindow {{ background: {COLORS['bg_primary']}; }}")

    def _switch_page(self, page_id: str) -> None:
        if page_id == "__back__":
            self.close()
            return
        page = self._pages.get(page_id)
        if page:
            self._stack.setCurrentWidget(page)
            # Refresh destekleyen sayfaları güncelle
            if hasattr(page, "refresh"):
                page.refresh()

    def closeEvent(self, event) -> None:
        self.closed.emit()
        super().closeEvent(event)
