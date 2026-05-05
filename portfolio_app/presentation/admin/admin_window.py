"""presentation/admin/admin_window.py — Gizli admin panel widget'ı (gömülü)."""

from PySide6.QtWidgets import QWidget, QHBoxLayout, QStackedWidget
from PySide6.QtCore import Signal

from presentation.admin.sidebar import AdminSidebar
from presentation.admin.pages.dashboard_page import DashboardPage
from presentation.admin.pages.projects_page import ProjectsPage
from presentation.admin.pages.personal_info_page import PersonalInfoPage
from presentation.admin.pages.certificates_page import CertificatesPage
from presentation.admin.pages.resources_page import ResourcesPage
from presentation.admin.pages.skills_page import SkillsPage
from presentation.admin.pages.education_page import EducationPage
from presentation.admin.pages.experience_page import ExperiencePage
from presentation.admin.pages.export_page import ExportPage
from presentation.admin.pages.settings_page import SettingsPage
from styles.constants import COLORS
from di_container import DIContainer


class AdminPanel(QWidget):
    """
    Admin panel içeriği — ayrı pencere değil, gömülü widget.
    ShowcaseWindow'un QStackedWidget'ına yerleştirilir.
    Geri butonu vitrine dönüş sinyali gönderir.
    """

    back_requested = Signal()

    def __init__(self, container: DIContainer, parent=None):
        super().__init__(parent)
        self._container = container
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self._sidebar = AdminSidebar()
        self._sidebar.page_requested.connect(self._switch_page)
        layout.addWidget(self._sidebar)

        self._stack = QStackedWidget()
        layout.addWidget(self._stack)

        self._pages = {}
        self._build_pages()
        self._switch_page("dashboard")
        self.apply_theme()

    def _build_pages(self):
        c = self._container
        self._pages = {
            "dashboard":     DashboardPage(c.project_controller, c.certificate_controller, c.resource_controller),
            "projects":      ProjectsPage(c.project_controller),
            "personal_info": PersonalInfoPage(c.personal_info_controller),
            "certificates":  CertificatesPage(c.certificate_controller),
            "education":     EducationPage(c.education_controller),
            "experience":    ExperiencePage(c.experience_controller),
            "resources":     ResourcesPage(c.resource_controller, c.resource_type_controller, c.project_controller),
            "skills":        SkillsPage(c.skill_controller),
            "export":        ExportPage(c.export_controller),
            "settings":      SettingsPage(),
        }
        for page in self._pages.values():
            self._stack.addWidget(page)

    def apply_theme(self):
        self._stack.setStyleSheet(f"background: {COLORS['bg_primary']};")
        
        # Tema değiştiğinde tüm admin sayfalarını baştan oluştur ki yeni renkleri alsınlar
        current_idx = self._stack.currentIndex()
        
        # Stack'i tamamen boşalt
        while self._stack.count() > 0:
            widget = self._stack.widget(0)
            self._stack.removeWidget(widget)
            widget.deleteLater()
            
        self._build_pages()
        if current_idx >= 0 and current_idx < self._stack.count():
            self._stack.setCurrentIndex(current_idx)
            # Aktif sayfayı yenile
            current_widget = self._stack.currentWidget()
            if hasattr(current_widget, "refresh"):
                current_widget.refresh()

    def _switch_page(self, page_id: str) -> None:
        if page_id == "__back__":
            self.back_requested.emit()
            return
        page = self._pages.get(page_id)
        if page:
            self._stack.setCurrentWidget(page)
            if hasattr(page, "refresh"):
                page.refresh()

    def activate(self) -> None:
        """Admin sayfasına geçişte dashboard'u sıfırla."""
        self._switch_page("dashboard")
