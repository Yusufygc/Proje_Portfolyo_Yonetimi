"""presentation/admin/pages/projects_page.py — Proje CRUD + task yönetimi."""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QScrollArea, QFrame, QDialog, QLineEdit, QTextEdit,
    QComboBox, QCheckBox, QFormLayout, QSpinBox, QSplitter,
    QListWidget, QListWidgetItem
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont

from styles.constants import COLORS, FONTS
from controllers.project_controller import ProjectController
from domain.models.project import Project
from domain.enums.project_status import ProjectStatus
from domain.enums.task_type import TaskType, TaskStatus
from presentation.shared.confirm_dialog import confirm
from presentation.shared.toast import show_toast, Toast


class ProjectsPage(QWidget):
    """Admin proje yönetim sayfası."""

    def __init__(self, controller: ProjectController, parent=None):
        super().__init__(parent)
        self._ctrl = controller
        self._selected_project: Project | None = None
        self._ctrl.projects_changed.connect(self.refresh)
        self._ctrl.error_occurred.connect(lambda msg: show_toast(self, msg, Toast.ERROR))
        self._build_ui()
        self.refresh()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Üst bar
        header = QWidget()
        header.setStyleSheet(f"background: {COLORS['bg_secondary']}; border-bottom: 1px solid {COLORS['border']};")
        h_layout = QHBoxLayout(header)
        h_layout.setContentsMargins(24, 16, 24, 16)

        title = QLabel("Projeler")
        title.setStyleSheet(f"color: {COLORS['text_primary']}; font-size: {FONTS['size_lg']}px; font-weight: 700;")
        h_layout.addWidget(title)
        h_layout.addStretch()

        add_btn = QPushButton("+ Yeni Proje")
        add_btn.setCursor(Qt.PointingHandCursor)
        add_btn.clicked.connect(self._open_create_dialog)
        h_layout.addWidget(add_btn)

        layout.addWidget(header)

        # İçerik: sol liste, sağ detay/task
        splitter = QSplitter(Qt.Horizontal)
        splitter.setStyleSheet(f"QSplitter {{ background: {COLORS['bg_primary']}; }}")

        # Sol: Proje listesi
        left = QWidget()
        left.setMinimumWidth(280)
        left.setMaximumWidth(380)
        left_layout = QVBoxLayout(left)
        left_layout.setContentsMargins(12, 12, 6, 12)
        left_layout.setSpacing(8)

        self._project_list = QListWidget()
        self._project_list.setStyleSheet(f"""
            QListWidget {{
                background: {COLORS['bg_secondary']};
                border: 1px solid {COLORS['border']};
                border-radius: 8px;
            }}
            QListWidget::item {{
                padding: 12px;
                border-bottom: 1px solid {COLORS['border']};
                color: {COLORS['text_primary']};
            }}
            QListWidget::item:selected {{
                background: rgba(74, 158, 255, 0.15);
                color: {COLORS['accent_blue']};
            }}
            QListWidget::item:hover {{
                background: {COLORS['bg_hover']};
            }}
        """)
        self._project_list.currentRowChanged.connect(self._on_project_selected)
        left_layout.addWidget(self._project_list)
        splitter.addWidget(left)

        # Sağ: Detay + task'lar
        right = QWidget()
        right_layout = QVBoxLayout(right)
        right_layout.setContentsMargins(6, 12, 12, 12)
        right_layout.setSpacing(16)

        self._detail_area = QScrollArea()
        self._detail_area.setWidgetResizable(True)
        self._detail_area.setStyleSheet("QScrollArea { border: none; }")
        self._detail_widget = QWidget()
        self._detail_layout = QVBoxLayout(self._detail_widget)
        self._detail_layout.setContentsMargins(0, 0, 0, 0)
        self._detail_area.setWidget(self._detail_widget)
        right_layout.addWidget(self._detail_area)

        splitter.addWidget(right)
        splitter.setSizes([300, 700])
        layout.addWidget(splitter)

    def refresh(self) -> None:
        projects = self._ctrl.get_all()
        self._project_list.clear()
        self._projects_cache = projects
        for p in projects:
            item = QListWidgetItem(p.title)
            item.setData(Qt.UserRole, p.id)
            self._project_list.addItem(item)

    def _on_project_selected(self, row: int) -> None:
        if row < 0 or row >= len(self._projects_cache):
            return
        project = self._projects_cache[row]
        self._selected_project = project
        self._render_detail(project)

    def _render_detail(self, project: Project) -> None:
        # Temizle
        while self._detail_layout.count():
            item = self._detail_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # Üst bilgi
        info_frame = QFrame()
        info_frame.setStyleSheet(f"""
            QFrame {{
                background: {COLORS['bg_card']};
                border: 1px solid {COLORS['border']};
                border-radius: 12px;
            }}
        """)
        info_col = QVBoxLayout(info_frame)
        info_col.setContentsMargins(20, 16, 20, 16)
        info_col.setSpacing(8)

        title_row = QHBoxLayout()
        title_lbl = QLabel(project.title)
        title_lbl.setStyleSheet(f"color: {COLORS['text_primary']}; font-size: {FONTS['size_lg']}px; font-weight: 700;")
        title_row.addWidget(title_lbl)
        title_row.addStretch()

        edit_btn = QPushButton("Düzenle")
        edit_btn.setObjectName("btn_flat")
        edit_btn.setCursor(Qt.PointingHandCursor)
        edit_btn.clicked.connect(lambda: self._open_edit_dialog(project))
        title_row.addWidget(edit_btn)

        del_btn = QPushButton("Sil")
        del_btn.setObjectName("btn_danger")
        del_btn.setCursor(Qt.PointingHandCursor)
        del_btn.clicked.connect(lambda: self._delete_project(project))
        title_row.addWidget(del_btn)

        info_col.addLayout(title_row)

        status_lbl = QLabel(f"Durum: {project.status.label()}")
        status_lbl.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 13px;")
        info_col.addWidget(status_lbl)

        if project.short_description:
            desc_lbl = QLabel(project.short_description)
            desc_lbl.setWordWrap(True)
            desc_lbl.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 13px;")
            info_col.addWidget(desc_lbl)

        if project.tags:
            tags_str = "  ".join(f"#{t.tag_name}" for t in project.tags)
            tags_lbl = QLabel(tags_str)
            tags_lbl.setStyleSheet(f"color: {COLORS['accent_blue']}; font-size: 12px;")
            info_col.addWidget(tags_lbl)

        self._detail_layout.addWidget(info_frame)

        # Task bölümü
        task_header = QHBoxLayout()
        task_title = QLabel("Görevler / Fikirler / Tasarımlar")
        task_title.setStyleSheet(f"color: {COLORS['text_primary']}; font-size: 15px; font-weight: 600;")
        task_header.addWidget(task_title)
        task_header.addStretch()

        add_task_btn = QPushButton("+ Task Ekle")
        add_task_btn.setObjectName("btn_flat")
        add_task_btn.setCursor(Qt.PointingHandCursor)
        add_task_btn.clicked.connect(lambda: self._open_task_dialog(project.id))
        task_header.addWidget(add_task_btn)
        self._detail_layout.addLayout(task_header)

        tasks = self._ctrl.get_tasks(project.id)
        if tasks:
            for task in tasks:
                task_card = self._make_task_card(task)
                self._detail_layout.addWidget(task_card)
        else:
            no_task = QLabel("Henüz task eklenmemiş.")
            no_task.setStyleSheet(f"color: {COLORS['text_muted']}; font-size: 13px;")
            self._detail_layout.addWidget(no_task)

        self._detail_layout.addStretch()

    def _make_task_card(self, task) -> QFrame:
        frame = QFrame()
        frame.setStyleSheet(f"""
            QFrame {{
                background: {COLORS['bg_card']};
                border: 1px solid {COLORS['border']};
                border-left: 3px solid {self._task_color(task.type)};
                border-radius: 8px;
            }}
        """)
        row = QHBoxLayout(frame)
        row.setContentsMargins(12, 8, 12, 8)
        row.setSpacing(12)

        type_lbl = QLabel(task.type.label())
        type_lbl.setFixedWidth(70)
        type_lbl.setStyleSheet(f"color: {self._task_color(task.type)}; font-size: 11px; font-weight: 600;")
        row.addWidget(type_lbl)

        title_lbl = QLabel(task.title)
        title_lbl.setStyleSheet(f"color: {COLORS['text_primary']}; font-size: 13px;")
        title_lbl.setWordWrap(True)
        row.addWidget(title_lbl, stretch=1)

        status_lbl = QLabel(task.status.label())
        status_lbl.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 11px;")
        row.addWidget(status_lbl)

        del_btn = QPushButton("✕")
        del_btn.setObjectName("btn_icon")
        del_btn.setCursor(Qt.PointingHandCursor)
        del_btn.setFixedSize(28, 28)
        task_id = task.id
        del_btn.clicked.connect(lambda: self._delete_task(task_id))
        row.addWidget(del_btn)

        return frame

    @staticmethod
    def _task_color(task_type) -> str:
        return {
            TaskType.GOREV:   COLORS["accent_blue"],
            TaskType.FIKIR:   COLORS["warning"],
            TaskType.TASARIM: COLORS["success"],
        }.get(task_type, COLORS["accent_silver"])

    def _open_create_dialog(self) -> None:
        dlg = ProjectDialog(self)
        if dlg.exec() == QDialog.Accepted:
            self._ctrl.create(dlg.get_data())

    def _open_edit_dialog(self, project: Project) -> None:
        dlg = ProjectDialog(self, project)
        if dlg.exec() == QDialog.Accepted:
            self._ctrl.update(project.id, dlg.get_data())

    def _delete_project(self, project: Project) -> None:
        if confirm(self, f'"{project.title}" projesini silmek istediğinizden emin misiniz?', danger=True):
            self._ctrl.delete(project.id)
            self._selected_project = None
            while self._detail_layout.count():
                item = self._detail_layout.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()

    def _open_task_dialog(self, project_id: int) -> None:
        dlg = TaskDialog(self)
        if dlg.exec() == QDialog.Accepted:
            self._ctrl.create_task(project_id, dlg.get_data())
            if self._selected_project and self._selected_project.id == project_id:
                proj = self._ctrl.get_by_id(project_id)
                self._render_detail(proj)

    def _delete_task(self, task_id: int) -> None:
        self._ctrl.delete_task(task_id)
        if self._selected_project:
            proj = self._ctrl.get_by_id(self._selected_project.id)
            self._render_detail(proj)


# ── Proje Dialog ─────────────────────────────────────────────────────────────

class ProjectDialog(QDialog):
    def __init__(self, parent=None, project: Project = None):
        super().__init__(parent)
        self._project = project
        self.setWindowTitle("Proje Ekle" if not project else "Proje Düzenle")
        self.setMinimumWidth(520)
        self.setModal(True)
        self._build_ui()
        if project:
            self._populate(project)

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 20)
        layout.setSpacing(16)

        self.setStyleSheet(f"""
            QDialog {{ background: {COLORS['bg_secondary']}; border-radius: 12px; }}
            QLabel {{ color: {COLORS['text_secondary']}; font-size: 13px; }}
        """)

        form = QFormLayout()
        form.setSpacing(12)
        form.setLabelAlignment(Qt.AlignRight | Qt.AlignVCenter)

        self._title_input    = QLineEdit()
        self._title_input.setPlaceholderText("Proje başlığı")
        form.addRow("Başlık *", self._title_input)

        self._short_desc     = QLineEdit()
        self._short_desc.setPlaceholderText("Kısa açıklama (kart özeti)")
        form.addRow("Kısa Açıklama", self._short_desc)

        self._full_desc      = QTextEdit()
        self._full_desc.setPlaceholderText("Detaylı açıklama...")
        self._full_desc.setMaximumHeight(120)
        form.addRow("Detay", self._full_desc)

        self._status_combo   = QComboBox()
        for s in ProjectStatus:
            self._status_combo.addItem(s.label(), s.value)
        form.addRow("Durum", self._status_combo)

        self._github_input   = QLineEdit()
        self._github_input.setPlaceholderText("https://github.com/...")
        form.addRow("GitHub URL", self._github_input)

        self._demo_input     = QLineEdit()
        self._demo_input.setPlaceholderText("https://...")
        form.addRow("Demo URL", self._demo_input)

        self._tags_input     = QLineEdit()
        self._tags_input.setPlaceholderText("Python, PySide6, SQLite (virgülle ayır)")
        form.addRow("Etiketler", self._tags_input)

        self._featured_check = QCheckBox("Öne Çıkan")
        form.addRow("", self._featured_check)

        self._order_spin     = QSpinBox()
        self._order_spin.setRange(0, 999)
        form.addRow("Sıralama", self._order_spin)

        layout.addLayout(form)

        btn_row = QHBoxLayout()
        btn_row.addStretch()
        cancel = QPushButton("İptal")
        cancel.setObjectName("btn_flat")
        cancel.clicked.connect(self.reject)
        btn_row.addWidget(cancel)

        save = QPushButton("Kaydet")
        save.clicked.connect(self.accept)
        btn_row.addWidget(save)
        layout.addLayout(btn_row)

    def _populate(self, p: Project) -> None:
        self._title_input.setText(p.title)
        self._short_desc.setText(p.short_description)
        self._full_desc.setPlainText(p.full_description)
        idx = self._status_combo.findData(p.status.value)
        if idx >= 0:
            self._status_combo.setCurrentIndex(idx)
        self._github_input.setText(p.github_url or "")
        self._demo_input.setText(p.demo_url or "")
        self._tags_input.setText(", ".join(t.tag_name for t in p.tags))
        self._featured_check.setChecked(p.is_featured)
        self._order_spin.setValue(p.display_order)

    def get_data(self) -> dict:
        tags = [t.strip() for t in self._tags_input.text().split(",") if t.strip()]
        return {
            "title":             self._title_input.text(),
            "short_description": self._short_desc.text(),
            "full_description":  self._full_desc.toPlainText(),
            "status":            self._status_combo.currentData(),
            "github_url":        self._github_input.text(),
            "demo_url":          self._demo_input.text(),
            "tags":              tags,
            "is_featured":       self._featured_check.isChecked(),
            "display_order":     self._order_spin.value(),
        }


# ── Task Dialog ──────────────────────────────────────────────────────────────

class TaskDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Task Ekle")
        self.setMinimumWidth(400)
        self.setModal(True)
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 20)
        layout.setSpacing(16)

        self.setStyleSheet(f"QDialog {{ background: {COLORS['bg_secondary']}; }}")

        form = QFormLayout()
        form.setSpacing(12)

        self._type_combo = QComboBox()
        for t in TaskType:
            self._type_combo.addItem(t.label(), t.value)
        form.addRow("Tür", self._type_combo)

        self._title_input = QLineEdit()
        self._title_input.setPlaceholderText("Task başlığı")
        form.addRow("Başlık *", self._title_input)

        self._desc_input = QTextEdit()
        self._desc_input.setPlaceholderText("Açıklama...")
        self._desc_input.setMaximumHeight(80)
        form.addRow("Açıklama", self._desc_input)

        self._status_combo = QComboBox()
        for s in TaskStatus:
            self._status_combo.addItem(s.label(), s.value)
        form.addRow("Durum", self._status_combo)

        layout.addLayout(form)

        btn_row = QHBoxLayout()
        btn_row.addStretch()
        cancel = QPushButton("İptal")
        cancel.setObjectName("btn_flat")
        cancel.clicked.connect(self.reject)
        btn_row.addWidget(cancel)
        save = QPushButton("Ekle")
        save.clicked.connect(self.accept)
        btn_row.addWidget(save)
        layout.addLayout(btn_row)

    def get_data(self) -> dict:
        return {
            "type":        self._type_combo.currentData(),
            "title":       self._title_input.text(),
            "description": self._desc_input.toPlainText(),
            "status":      self._status_combo.currentData(),
        }
