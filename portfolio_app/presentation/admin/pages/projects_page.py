"""presentation/admin/pages/projects_page.py — Proje CRUD + task yönetimi."""

import json

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QScrollArea, QFrame, QDialog, QLineEdit, QTextEdit,
    QComboBox, QCheckBox, QFormLayout, QSpinBox, QSplitter,
    QListWidget, QListWidgetItem, QSizePolicy
)
from PySide6.QtCore import Qt, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QFont

from styles.constants import COLORS, FONTS
from controllers.project_controller import ProjectController
from domain.models.project import Project
from domain.enums.project_status import ProjectStatus
from domain.enums.task_type import TaskType, TaskStatus
from presentation.shared.confirm_dialog import confirm
from presentation.shared.toast import show_toast, Toast


# ── Todo yardımcıları ────────────────────────────────────────────────────────

def todos_to_json(todos: list[dict]) -> str:
    return json.dumps(todos, ensure_ascii=False)


def json_to_todos(text: str) -> list[dict]:
    if not text:
        return []
    try:
        data = json.loads(text)
        if isinstance(data, list):
            return [t for t in data if isinstance(t, dict) and "text" in t]
    except (json.JSONDecodeError, ValueError):
        pass
    if text.strip():
        return [{"text": text.strip(), "done": False}]
    return []


# ── Ana sayfa ────────────────────────────────────────────────────────────────

class ProjectsPage(QWidget):
    """Admin proje yönetim sayfası."""

    def __init__(self, controller: ProjectController, parent=None):
        super().__init__(parent)
        self._ctrl = controller
        self._selected_project: Project | None = None
        self._projects_cache: list[Project] = []
        self._ctrl.projects_changed.connect(self.refresh)
        self._ctrl.error_occurred.connect(lambda msg: show_toast(self, msg, Toast.ERROR))
        self._build_ui()
        self.refresh()

    # ── UI inşası ───────────────────────────────────────────────────────────

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # Üst bar
        header = QWidget()
        header.setFixedHeight(60)
        header.setStyleSheet(
            f"background: {COLORS['bg_secondary']};"
            f"border-bottom: 1px solid {COLORS['border']};"
        )
        h_lay = QHBoxLayout(header)
        h_lay.setContentsMargins(24, 0, 24, 0)

        title = QLabel("Projeler")
        title.setStyleSheet(
            f"color: {COLORS['text_primary']};"
            f"font-size: {FONTS['size_lg']}px;"
            f"font-weight: 700;"
            f"background: transparent; border: none;"
        )
        h_lay.addWidget(title)
        h_lay.addStretch()

        add_btn = QPushButton("+ Yeni Proje")
        add_btn.setCursor(Qt.PointingHandCursor)
        add_btn.clicked.connect(self._open_create_dialog)
        h_lay.addWidget(add_btn)

        root.addWidget(header)

        # Splitter: sol liste | sağ detay
        splitter = QSplitter(Qt.Horizontal)
        splitter.setStyleSheet(f"QSplitter {{ background: {COLORS['bg_primary']}; }}")

        # Sol — proje listesi
        left_wrap = QWidget()
        left_wrap.setMinimumWidth(220)
        left_wrap.setMaximumWidth(340)
        left_lay = QVBoxLayout(left_wrap)
        left_lay.setContentsMargins(12, 12, 6, 12)
        left_lay.setSpacing(0)

        self._project_list = QListWidget()
        self._project_list.setStyleSheet(f"""
            QListWidget {{
                background: {COLORS['bg_secondary']};
                border: 1px solid {COLORS['border']};
                border-radius: 8px;
                outline: none;
            }}
            QListWidget::item {{
                padding: 14px 16px;
                border-bottom: 1px solid {COLORS['border']};
                color: {COLORS['text_primary']};
                font-size: 14px;
            }}
            QListWidget::item:last {{
                border-bottom: none;
            }}
            QListWidget::item:selected {{
                background: rgba(74, 158, 255, 0.15);
                color: {COLORS['accent_blue']};
                font-weight: 600;
            }}
            QListWidget::item:hover:!selected {{
                background: {COLORS['bg_hover']};
            }}
        """)
        self._project_list.currentRowChanged.connect(self._on_project_selected)
        left_lay.addWidget(self._project_list)

        splitter.addWidget(left_wrap)

        # Sağ — detay + tasklar
        self._detail_scroll = QScrollArea()
        self._detail_scroll.setWidgetResizable(True)
        self._detail_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self._detail_scroll.setStyleSheet(
            "QScrollArea { border: none; background: transparent; }"
        )
        self._detail_scroll.setWidget(self._build_empty_detail())

        splitter.addWidget(self._detail_scroll)
        splitter.setSizes([260, 740])

        root.addWidget(splitter)

    def _build_empty_detail(self) -> QWidget:
        w = QWidget()
        w.setStyleSheet(f"background: {COLORS['bg_primary']};")
        lay = QVBoxLayout(w)
        lay.setAlignment(Qt.AlignCenter)
        lbl = QLabel("Soldaki listeden bir proje seçin.")
        lbl.setStyleSheet(f"color: {COLORS['text_muted']}; font-size: 14px;")
        lay.addWidget(lbl)
        return w

    # ── Veri ────────────────────────────────────────────────────────────────

    def refresh(self) -> None:
        selected_id = self._selected_project.id if self._selected_project else None
        self._projects_cache = self._ctrl.get_all()

        self._project_list.blockSignals(True)
        self._project_list.clear()
        restore_row = -1
        for i, p in enumerate(self._projects_cache):
            item = QListWidgetItem(p.title)
            item.setData(Qt.UserRole, p.id)
            self._project_list.addItem(item)
            if p.id == selected_id:
                restore_row = i
        self._project_list.blockSignals(False)

        if restore_row >= 0:
            self._project_list.setCurrentRow(restore_row)
        elif self._projects_cache:
            self._project_list.setCurrentRow(0)
        else:
            self._selected_project = None
            self._detail_scroll.setWidget(self._build_empty_detail())

    def _on_project_selected(self, row: int) -> None:
        if row < 0 or row >= len(self._projects_cache):
            return
        self._selected_project = self._projects_cache[row]
        self._render_detail(self._selected_project)

    # ── Detay render ────────────────────────────────────────────────────────

    def _render_detail(self, project: Project) -> None:
        content = QWidget()
        content.setStyleSheet(f"background: {COLORS['bg_primary']};")
        lay = QVBoxLayout(content)
        lay.setContentsMargins(16, 16, 16, 16)
        lay.setSpacing(16)

        lay.addWidget(self._build_info_card(project))

        # Task başlık satırı
        task_hdr = QHBoxLayout()
        task_hdr.setContentsMargins(0, 0, 0, 0)
        task_lbl = QLabel("Görevler / Fikirler / Tasarımlar")
        task_lbl.setStyleSheet(
            f"color: {COLORS['text_primary']}; font-size: 15px; font-weight: 600;"
            f"background: transparent; border: none;"
        )
        task_hdr.addWidget(task_lbl)
        task_hdr.addStretch()

        add_task_btn = QPushButton("+ Task Ekle")
        add_task_btn.setObjectName("btn_flat")
        add_task_btn.setCursor(Qt.PointingHandCursor)
        add_task_btn.clicked.connect(lambda: self._open_task_dialog(project.id))
        task_hdr.addWidget(add_task_btn)

        task_hdr_widget = QWidget()
        task_hdr_widget.setStyleSheet("background: transparent;")
        task_hdr_widget.setLayout(task_hdr)
        lay.addWidget(task_hdr_widget)

        # Task kartları
        tasks = self._ctrl.get_tasks(project.id)
        if tasks:
            for task in tasks:
                card = TaskCardWidget(task, self._ctrl, self._refresh_detail)
                lay.addWidget(card)
        else:
            no_lbl = QLabel("Henüz task eklenmemiş.")
            no_lbl.setStyleSheet(
                f"color: {COLORS['text_muted']}; font-size: 13px; padding: 8px 0;"
            )
            lay.addWidget(no_lbl)

        lay.addStretch()

        old = self._detail_scroll.takeWidget()
        if old:
            old.deleteLater()
        self._detail_scroll.setWidget(content)

    def _refresh_detail(self) -> None:
        if self._selected_project:
            proj = self._ctrl.get_by_id(self._selected_project.id)
            if proj:
                self._selected_project = proj
                self._render_detail(proj)

    def _build_info_card(self, project: Project) -> QFrame:
        frame = QFrame()
        frame.setStyleSheet(f"""
            QFrame {{
                background: {COLORS['bg_card']};
                border: 1px solid {COLORS['border']};
                border-radius: 12px;
            }}
        """)
        col = QVBoxLayout(frame)
        col.setContentsMargins(20, 16, 20, 16)
        col.setSpacing(10)

        title_row = QHBoxLayout()
        title_lbl = QLabel(project.title)
        title_lbl.setStyleSheet(
            f"color: {COLORS['text_primary']};"
            f"font-size: {FONTS['size_lg']}px; font-weight: 700;"
            f"background: transparent; border: none;"
        )
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

        col.addLayout(title_row)

        status_lbl = QLabel(f"Durum: {project.status.label()}")
        status_lbl.setStyleSheet(
            f"color: {COLORS['text_secondary']}; font-size: 13px;"
            f"background: transparent; border: none;"
        )
        col.addWidget(status_lbl)

        if project.short_description:
            desc_lbl = QLabel(project.short_description)
            desc_lbl.setWordWrap(True)
            desc_lbl.setStyleSheet(
                f"color: {COLORS['text_secondary']}; font-size: 13px;"
                f"background: transparent; border: none;"
            )
            col.addWidget(desc_lbl)

        if project.tags:
            tags_str = "  ".join(f"#{t.tag_name}" for t in project.tags)
            tags_lbl = QLabel(tags_str)
            tags_lbl.setStyleSheet(
                f"color: {COLORS['accent_blue']}; font-size: 12px;"
                f"background: transparent; border: none;"
            )
            col.addWidget(tags_lbl)

        return frame

    # ── Eylemler ────────────────────────────────────────────────────────────

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

    def _open_task_dialog(self, project_id: int) -> None:
        dlg = TaskDialog(self)
        if dlg.exec() == QDialog.Accepted:
            self._ctrl.create_task(project_id, dlg.get_data())
            self._refresh_detail()


# ── Task Kart Widget (accordion + todo list) ──────────────────────────────────

class TaskCardWidget(QFrame):
    """Tıklanınca açılan/kapanan task kartı. İçinde todo listesi."""

    def __init__(self, task, controller: ProjectController, refresh_cb, parent=None):
        super().__init__(parent)
        self._task = task
        self._ctrl = controller
        self._refresh_cb = refresh_cb
        self._expanded = False
        self._todos: list[dict] = json_to_todos(task.description)

        self.setStyleSheet(f"""
            TaskCardWidget {{
                background: {COLORS['bg_card']};
                border: 1px solid {COLORS['border']};
                border-left: 3px solid {self._type_color()};
                border-radius: 8px;
            }}
        """)
        self._build_ui()

    def _type_color(self) -> str:
        return {
            TaskType.GOREV:   COLORS["accent_blue"],
            TaskType.FIKIR:   COLORS["warning"],
            TaskType.TASARIM: COLORS["success"],
        }.get(self._task.type, COLORS["accent_silver"])

    def _build_ui(self) -> None:
        self._root = QVBoxLayout(self)
        self._root.setContentsMargins(0, 0, 0, 0)
        self._root.setSpacing(0)

        # ── Header ──────────────────────────────────────────────────────────
        self._header = QWidget()
        self._header.setStyleSheet("background: transparent;")
        self._header.setCursor(Qt.PointingHandCursor)
        self._header.mousePressEvent = self._toggle_expand

        h_lay = QHBoxLayout(self._header)
        h_lay.setContentsMargins(12, 10, 12, 10)
        h_lay.setSpacing(10)

        # Ok işareti
        self._arrow_lbl = QLabel("▶")
        self._arrow_lbl.setFixedWidth(14)
        self._arrow_lbl.setStyleSheet(
            f"color: {COLORS['text_muted']}; font-size: 10px;"
            f"background: transparent; border: none;"
        )
        h_lay.addWidget(self._arrow_lbl)

        # Tür etiketi
        type_lbl = QLabel(self._task.type.label())
        type_lbl.setFixedWidth(70)
        type_lbl.setStyleSheet(
            f"color: {self._type_color()}; font-size: 11px; font-weight: 600;"
            f"background: transparent; border: none;"
        )
        h_lay.addWidget(type_lbl)

        # Başlık
        self._title_lbl = QLabel(self._task.title)
        self._title_lbl.setStyleSheet(
            f"color: {COLORS['text_primary']}; font-size: 13px;"
            f"background: transparent; border: none;"
        )
        self._title_lbl.setWordWrap(False)
        h_lay.addWidget(self._title_lbl, stretch=1)

        # Durum
        self._status_lbl = QLabel(self._task.status.label())
        self._status_lbl.setStyleSheet(
            f"color: {COLORS['text_secondary']}; font-size: 11px;"
            f"background: transparent; border: none;"
        )
        h_lay.addWidget(self._status_lbl)

        # Todo sayacı
        self._counter_lbl = QLabel()
        self._counter_lbl.setStyleSheet(
            f"color: {COLORS['accent_blue']}; font-size: 11px;"
            f"background: transparent; border: none;"
        )
        h_lay.addWidget(self._counter_lbl)
        self._update_counter()

        # Düzenle butonu
        edit_btn = QPushButton("✎")
        edit_btn.setObjectName("btn_icon")
        edit_btn.setCursor(Qt.PointingHandCursor)
        edit_btn.setFixedSize(28, 28)
        edit_btn.setToolTip("Düzenle")
        edit_btn.clicked.connect(self._open_edit)
        h_lay.addWidget(edit_btn)

        # Sil butonu
        del_btn = QPushButton("✕")
        del_btn.setObjectName("btn_icon")
        del_btn.setCursor(Qt.PointingHandCursor)
        del_btn.setFixedSize(28, 28)
        del_btn.setToolTip("Sil")
        del_btn.clicked.connect(self._delete_task)
        h_lay.addWidget(del_btn)

        self._root.addWidget(self._header)

        # ── Body (todo listesi) ──────────────────────────────────────────────
        self._body = QWidget()
        self._body.setStyleSheet(
            f"background: {COLORS['bg_secondary']};"
            f"border-top: 1px solid {COLORS['border_light']};"
        )
        self._body.setVisible(False)

        self._body_lay = QVBoxLayout(self._body)
        self._body_lay.setContentsMargins(48, 10, 12, 12)
        self._body_lay.setSpacing(4)

        self._rebuild_todo_list()

        self._root.addWidget(self._body)

    # ── Todo listesi ────────────────────────────────────────────────────────

    def _rebuild_todo_list(self) -> None:
        """Body layout içindeki todo öğelerini sıfırdan yeniden çizer."""
        # Eski öğeleri temizle (add-input satırı dahil)
        while self._body_lay.count():
            item = self._body_lay.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        if not self._todos:
            placeholder = QLabel("Henüz görev eklenmemiş. Aşağıdan ekleyebilirsin.")
            placeholder.setStyleSheet(
                f"color: {COLORS['text_muted']}; font-size: 12px;"
                f"background: transparent; border: none; padding: 4px 0;"
            )
            self._body_lay.addWidget(placeholder)

        for idx, todo in enumerate(self._todos):
            self._body_lay.addWidget(self._build_todo_row(idx, todo))

        # Ayırıcı
        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setStyleSheet(f"color: {COLORS['border_light']};")
        self._body_lay.addWidget(sep)

        # Yeni todo girdi satırı
        add_row = QWidget()
        add_row.setStyleSheet("background: transparent;")
        add_lay = QHBoxLayout(add_row)
        add_lay.setContentsMargins(0, 4, 0, 0)
        add_lay.setSpacing(8)

        self._todo_input = QLineEdit()
        self._todo_input.setPlaceholderText("Yeni görev ekle...")
        self._todo_input.setStyleSheet(
            f"background: {COLORS['bg_input']}; color: {COLORS['text_primary']};"
            f"border: 1px solid {COLORS['border']}; border-radius: 4px;"
            f"padding: 4px 8px; font-size: 12px;"
        )
        self._todo_input.returnPressed.connect(self._add_todo)
        add_lay.addWidget(self._todo_input, stretch=1)

        add_btn = QPushButton("+ Ekle")
        add_btn.setObjectName("btn_flat")
        add_btn.setCursor(Qt.PointingHandCursor)
        add_btn.setFixedHeight(28)
        add_btn.clicked.connect(self._add_todo)
        add_lay.addWidget(add_btn)

        self._body_lay.addWidget(add_row)

    def _build_todo_row(self, idx: int, todo: dict) -> QWidget:
        row = QWidget()
        row.setStyleSheet("background: transparent;")
        lay = QHBoxLayout(row)
        lay.setContentsMargins(0, 2, 0, 2)
        lay.setSpacing(8)

        done = todo.get("done", False)

        # Checkbox görseli
        check_lbl = QLabel("✓" if done else "○")
        check_lbl.setFixedWidth(16)
        check_lbl.setStyleSheet(
            f"color: {COLORS['success'] if done else COLORS['text_muted']};"
            f"font-size: 12px; font-weight: 700;"
            f"background: transparent; border: none;"
        )
        lay.addWidget(check_lbl)

        # Metin
        text_lbl = QLabel(todo["text"])
        if done:
            text_lbl.setStyleSheet(
                f"color: {COLORS['text_muted']}; font-size: 12px; "
                f"text-decoration: line-through;"
                f"background: transparent; border: none;"
            )
        else:
            text_lbl.setStyleSheet(
                f"color: {COLORS['text_primary']}; font-size: 12px;"
                f"background: transparent; border: none;"
            )
        text_lbl.setCursor(Qt.PointingHandCursor)
        text_lbl.mousePressEvent = lambda e, i=idx: self._toggle_todo(i)
        lay.addWidget(text_lbl, stretch=1)

        # Sil butonu
        del_btn = QPushButton("✕")
        del_btn.setObjectName("btn_icon")
        del_btn.setCursor(Qt.PointingHandCursor)
        del_btn.setFixedSize(22, 22)
        del_btn.clicked.connect(lambda checked=False, i=idx: self._remove_todo(i))
        lay.addWidget(del_btn)

        return row

    def _add_todo(self) -> None:
        text = self._todo_input.text().strip()
        if not text:
            return
        self._todos.append({"text": text, "done": False})
        self._save_todos()
        self._rebuild_todo_list()
        self._update_counter()
        self._todo_input.clear()
        self._todo_input.setFocus()

    def _toggle_todo(self, idx: int) -> None:
        if 0 <= idx < len(self._todos):
            self._todos[idx]["done"] = not self._todos[idx].get("done", False)
            self._save_todos()
            self._rebuild_todo_list()
            self._update_counter()

    def _remove_todo(self, idx: int) -> None:
        if 0 <= idx < len(self._todos):
            del self._todos[idx]
            self._save_todos()
            self._rebuild_todo_list()
            self._update_counter()

    def _save_todos(self) -> None:
        # blockSignals: todo değişikliği küçük bir micro-update — tüm sayfayı yeniden
        # render etmeden sadece DB'ye yaz, UI'ı yerel olarak güncelle.
        self._ctrl.blockSignals(True)
        self._ctrl.update_task(self._task.id, {
            "type":        self._task.type.value,
            "title":       self._task.title,
            "description": todos_to_json(self._todos),
            "status":      self._task.status.value,
        })
        self._ctrl.blockSignals(False)

    def _update_counter(self) -> None:
        if not self._todos:
            self._counter_lbl.setText("")
            return
        done_count = sum(1 for t in self._todos if t.get("done"))
        self._counter_lbl.setText(f"{done_count}/{len(self._todos)}")

    # ── Akordiyon ───────────────────────────────────────────────────────────

    def _toggle_expand(self, event=None) -> None:
        self._expanded = not self._expanded
        self._arrow_lbl.setText("▼" if self._expanded else "▶")
        self._body.setVisible(self._expanded)
        if self._expanded and hasattr(self, "_todo_input"):
            self._todo_input.setFocus()

    # ── Task düzenleme / silme ───────────────────────────────────────────────

    def _open_edit(self) -> None:
        dlg = TaskDialog(self, task=self._task, todos=self._todos)
        if dlg.exec() == QDialog.Accepted:
            data = dlg.get_data()
            # projects_changed sinyali tüm detay panelini yeniden render eder —
            # bu widget silineceği için sonrasında yerel state güncelleme yapma.
            self._ctrl.update_task(self._task.id, data)

    def _delete_task(self) -> None:
        self._ctrl.delete_task(self._task.id)
        self._refresh_cb()


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
            QLabel {{ color: {COLORS['text_secondary']}; font-size: 13px; background: transparent; border: none; }}
        """)

        form = QFormLayout()
        form.setSpacing(12)
        form.setLabelAlignment(Qt.AlignRight | Qt.AlignVCenter)

        self._title_input = QLineEdit()
        self._title_input.setPlaceholderText("Proje başlığı")
        form.addRow("Başlık *", self._title_input)

        self._short_desc = QLineEdit()
        self._short_desc.setPlaceholderText("Kısa açıklama (kart özeti)")
        form.addRow("Kısa Açıklama", self._short_desc)

        self._full_desc = QTextEdit()
        self._full_desc.setPlaceholderText("Detaylı açıklama...")
        self._full_desc.setMaximumHeight(120)
        form.addRow("Detay", self._full_desc)

        self._status_combo = QComboBox()
        for s in ProjectStatus:
            self._status_combo.addItem(s.label(), s.value)
        form.addRow("Durum", self._status_combo)

        self._github_input = QLineEdit()
        self._github_input.setPlaceholderText("https://github.com/...")
        form.addRow("GitHub URL", self._github_input)

        self._demo_input = QLineEdit()
        self._demo_input.setPlaceholderText("https://...")
        form.addRow("Demo URL", self._demo_input)

        self._tags_input = QLineEdit()
        self._tags_input.setPlaceholderText("Python, PySide6, SQLite (virgülle ayır)")
        form.addRow("Etiketler", self._tags_input)

        self._featured_check = QCheckBox("Öne Çıkan")
        form.addRow("", self._featured_check)

        self._order_spin = QSpinBox()
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
        self._short_desc.setText(p.short_description or "")
        self._full_desc.setPlainText(p.full_description or "")
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


# ── Task Dialog (ekle / düzenle) ──────────────────────────────────────────────

class TaskDialog(QDialog):
    """Task ekleme ve düzenleme diyaloğu.
    Açıklama alanı yerine todo-list editörü içerir.
    """

    def __init__(self, parent=None, task=None, todos: list[dict] | None = None):
        super().__init__(parent)
        self._task = task
        self._todos: list[dict] = list(todos) if todos else []
        self.setWindowTitle("Task Ekle" if not task else "Task Düzenle")
        self.setMinimumWidth(440)
        self.setModal(True)
        self._build_ui()
        if task:
            self._populate(task)

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 20)
        layout.setSpacing(14)

        self.setStyleSheet(f"""
            QDialog {{ background: {COLORS['bg_secondary']}; }}
            QLabel {{ color: {COLORS['text_secondary']}; font-size: 13px;
                      background: transparent; border: none; }}
        """)

        form = QFormLayout()
        form.setSpacing(12)
        form.setLabelAlignment(Qt.AlignRight | Qt.AlignVCenter)

        self._type_combo = QComboBox()
        for t in TaskType:
            self._type_combo.addItem(t.label(), t.value)
        form.addRow("Tür", self._type_combo)

        self._title_input = QLineEdit()
        self._title_input.setPlaceholderText("Task başlığı")
        form.addRow("Başlık *", self._title_input)

        self._status_combo = QComboBox()
        for s in TaskStatus:
            self._status_combo.addItem(s.label(), s.value)
        form.addRow("Durum", self._status_combo)

        layout.addLayout(form)

        # ── Todo listesi editörü ─────────────────────────────────────────────
        todo_header = QLabel("Görev Listesi")
        todo_header.setStyleSheet(
            f"color: {COLORS['text_primary']}; font-size: 13px; font-weight: 600;"
            f"background: transparent; border: none;"
        )
        layout.addWidget(todo_header)

        # Kapsayıcı frame
        self._todo_frame = QFrame()
        self._todo_frame.setStyleSheet(f"""
            QFrame {{
                background: {COLORS['bg_input']};
                border: 1px solid {COLORS['border']};
                border-radius: 6px;
            }}
        """)
        self._todo_frame_lay = QVBoxLayout(self._todo_frame)
        self._todo_frame_lay.setContentsMargins(10, 8, 10, 8)
        self._todo_frame_lay.setSpacing(4)

        # Giriş satırı
        input_row = QWidget()
        input_row.setStyleSheet("background: transparent;")
        input_lay = QHBoxLayout(input_row)
        input_lay.setContentsMargins(0, 0, 0, 0)
        input_lay.setSpacing(8)

        self._todo_input = QLineEdit()
        self._todo_input.setPlaceholderText("Yeni görev yaz, Enter'a bas...")
        self._todo_input.setStyleSheet(
            f"background: {COLORS['bg_secondary']}; color: {COLORS['text_primary']};"
            f"border: 1px solid {COLORS['border']}; border-radius: 4px;"
            f"padding: 4px 8px; font-size: 12px;"
        )
        self._todo_input.returnPressed.connect(self._add_todo_item)
        input_lay.addWidget(self._todo_input, stretch=1)

        add_btn = QPushButton("Ekle")
        add_btn.setObjectName("btn_flat")
        add_btn.setCursor(Qt.PointingHandCursor)
        add_btn.clicked.connect(self._add_todo_item)
        input_lay.addWidget(add_btn)

        self._todo_frame_lay.addWidget(input_row)

        # Todo öğe listesi
        self._todo_list_widget = QWidget()
        self._todo_list_widget.setStyleSheet("background: transparent;")
        self._todo_list_lay = QVBoxLayout(self._todo_list_widget)
        self._todo_list_lay.setContentsMargins(0, 0, 0, 0)
        self._todo_list_lay.setSpacing(2)
        self._todo_frame_lay.addWidget(self._todo_list_widget)

        self._render_todo_items()

        layout.addWidget(self._todo_frame)

        # ── Butonlar ─────────────────────────────────────────────────────────
        btn_row = QHBoxLayout()
        btn_row.addStretch()
        cancel = QPushButton("İptal")
        cancel.setObjectName("btn_flat")
        cancel.clicked.connect(self.reject)
        btn_row.addWidget(cancel)
        save = QPushButton("Ekle" if not self._task else "Kaydet")
        save.clicked.connect(self._on_accept)
        btn_row.addWidget(save)
        layout.addLayout(btn_row)

    def _populate(self, task) -> None:
        idx = self._type_combo.findData(task.type.value)
        if idx >= 0:
            self._type_combo.setCurrentIndex(idx)
        self._title_input.setText(task.title)
        idx2 = self._status_combo.findData(task.status.value)
        if idx2 >= 0:
            self._status_combo.setCurrentIndex(idx2)

    def _render_todo_items(self) -> None:
        while self._todo_list_lay.count():
            item = self._todo_list_lay.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        for idx, todo in enumerate(self._todos):
            row = QWidget()
            row.setStyleSheet("background: transparent;")
            r_lay = QHBoxLayout(row)
            r_lay.setContentsMargins(0, 0, 0, 0)
            r_lay.setSpacing(6)

            bullet = QLabel("•")
            bullet.setFixedWidth(12)
            bullet.setStyleSheet(
                f"color: {COLORS['accent_blue']}; font-size: 14px;"
                f"background: transparent; border: none;"
            )
            r_lay.addWidget(bullet)

            lbl = QLabel(todo["text"])
            lbl.setStyleSheet(
                f"color: {COLORS['text_primary']}; font-size: 12px;"
                f"background: transparent; border: none;"
            )
            lbl.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
            r_lay.addWidget(lbl, stretch=1)

            del_btn = QPushButton("✕")
            del_btn.setObjectName("btn_icon")
            del_btn.setCursor(Qt.PointingHandCursor)
            del_btn.setFixedSize(20, 20)
            del_btn.clicked.connect(lambda checked=False, i=idx: self._remove_todo_item(i))
            r_lay.addWidget(del_btn)

            self._todo_list_lay.addWidget(row)

    def _add_todo_item(self) -> None:
        text = self._todo_input.text().strip()
        if not text:
            return
        self._todos.append({"text": text, "done": False})
        self._todo_input.clear()
        self._render_todo_items()

    def _remove_todo_item(self, idx: int) -> None:
        if 0 <= idx < len(self._todos):
            del self._todos[idx]
            self._render_todo_items()

    def _on_accept(self) -> None:
        if not self._title_input.text().strip():
            self._title_input.setFocus()
            return
        self.accept()

    def get_data(self) -> dict:
        return {
            "type":        self._type_combo.currentData(),
            "title":       self._title_input.text().strip(),
            "description": todos_to_json(self._todos),
            "status":      self._status_combo.currentData(),
        }
