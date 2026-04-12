"""presentation/admin/pages/resources_page.py — Kaynak (kurs/video/repo/not/plan) yönetimi."""

import webbrowser
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QScrollArea, QFrame, QDialog, QLineEdit, QTextEdit,
    QFormLayout, QComboBox, QTabWidget
)
from PySide6.QtCore import Qt

from styles.constants import COLORS, FONTS
from controllers.resource_controller import ResourceController
from domain.models.resource import Resource
from domain.enums.resource_type import ResourceType, ResourceStatus
from presentation.shared.confirm_dialog import confirm
from presentation.shared.toast import show_toast, Toast


class ResourcesPage(QWidget):
    """Admin kaynak yönetim sayfası — tab'lara ayrılmış türler."""

    def __init__(self, controller: ResourceController, parent=None):
        super().__init__(parent)
        self._ctrl = controller
        self._ctrl.resources_changed.connect(self.refresh)
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

        title = QLabel("Kaynaklar")
        title.setStyleSheet(f"color: {COLORS['text_primary']}; font-size: {FONTS['size_lg']}px; font-weight: 700;")
        h_layout.addWidget(title)
        h_layout.addStretch()

        add_btn = QPushButton("+ Kaynak Ekle")
        add_btn.setCursor(Qt.PointingHandCursor)
        add_btn.clicked.connect(self._open_create_dialog)
        h_layout.addWidget(add_btn)
        layout.addWidget(header)

        # Tab widget — türe göre filtreleme
        self._tabs = QTabWidget()
        self._tabs.setStyleSheet(f"""
            QTabWidget::pane {{
                background: {COLORS['bg_primary']};
                border: none;
            }}
            QTabBar::tab {{
                background: {COLORS['bg_secondary']};
                color: {COLORS['text_secondary']};
                padding: 8px 20px;
                border: none;
                font-size: 13px;
            }}
            QTabBar::tab:selected {{
                background: {COLORS['bg_primary']};
                color: {COLORS['accent_blue']};
                border-bottom: 2px solid {COLORS['accent_blue']};
            }}
        """)

        self._tab_widgets: dict[str, QWidget] = {}
        self._tab_layouts: dict[str, QVBoxLayout] = {}

        tabs = [
            ("Tümü",   None),
            ("Kurs",   ResourceType.KURS),
            ("Video",  ResourceType.VIDEO),
            ("Repo",   ResourceType.REPO),
            ("Not",    ResourceType.NOT),
            ("Plan",   ResourceType.PLAN),
        ]
        for tab_label, resource_type in tabs:
            scroll = QScrollArea()
            scroll.setWidgetResizable(True)
            scroll.setStyleSheet("QScrollArea { border: none; }")
            inner = QWidget()
            inner.setStyleSheet(f"background: {COLORS['bg_primary']};")
            inner_layout = QVBoxLayout(inner)
            inner_layout.setContentsMargins(24, 16, 24, 16)
            inner_layout.setSpacing(10)
            scroll.setWidget(inner)

            key = tab_label
            self._tab_widgets[key] = scroll
            self._tab_layouts[key] = inner_layout
            self._tabs.addTab(scroll, tab_label)

        layout.addWidget(self._tabs)

    def refresh(self) -> None:
        all_resources = self._ctrl.get_all()

        for key, lyt in self._tab_layouts.items():
            while lyt.count():
                item = lyt.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()

            if key == "Tümü":
                filtered = all_resources
            else:
                type_map = {
                    "Kurs": ResourceType.KURS,
                    "Video": ResourceType.VIDEO,
                    "Repo": ResourceType.REPO,
                    "Not": ResourceType.NOT,
                    "Plan": ResourceType.PLAN,
                }
                rtype = type_map.get(key)
                filtered = [r for r in all_resources if r.type == rtype]

            if not filtered:
                empty = QLabel("Kayıt yok.")
                empty.setStyleSheet(f"color: {COLORS['text_muted']}; font-size: 14px;")
                lyt.addWidget(empty)
            else:
                for resource in filtered:
                    lyt.addWidget(self._make_resource_row(resource))

            lyt.addStretch()

    def _make_resource_row(self, res: Resource) -> QFrame:
        frame = QFrame()
        type_color = {
            ResourceType.KURS:  COLORS["accent_blue"],
            ResourceType.VIDEO: COLORS["error"],
            ResourceType.REPO:  COLORS["success"],
            ResourceType.NOT:   COLORS["warning"],
            ResourceType.PLAN:  COLORS["accent_silver"],
        }.get(res.type, COLORS["accent_silver"])

        frame.setStyleSheet(f"""
            QFrame {{
                background: {COLORS['bg_card']};
                border: 1px solid {COLORS['border']};
                border-left: 3px solid {type_color};
                border-radius: 8px;
            }}
        """)
        row = QHBoxLayout(frame)
        row.setContentsMargins(14, 10, 14, 10)
        row.setSpacing(12)

        type_lbl = QLabel(res.type.label())
        type_lbl.setFixedWidth(50)
        type_lbl.setStyleSheet(f"color: {type_color}; font-size: 11px; font-weight: 600;")
        row.addWidget(type_lbl)

        info_col = QVBoxLayout()
        title_lbl = QLabel(res.title)
        title_lbl.setStyleSheet(f"color: {COLORS['text_primary']}; font-size: 14px; font-weight: 600;")
        info_col.addWidget(title_lbl)

        if res.notes:
            notes_lbl = QLabel(res.notes[:100] + ("..." if len(res.notes) > 100 else ""))
            notes_lbl.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 12px;")
            info_col.addWidget(notes_lbl)
        row.addLayout(info_col, stretch=1)

        status_lbl = QLabel(res.status.label())
        status_lbl.setStyleSheet(f"color: {COLORS['text_muted']}; font-size: 11px;")
        row.addWidget(status_lbl)

        if res.url:
            open_btn = QPushButton("Aç")
            open_btn.setObjectName("btn_flat")
            open_btn.setCursor(Qt.PointingHandCursor)
            url = res.url
            open_btn.clicked.connect(lambda: webbrowser.open(url))
            row.addWidget(open_btn)

        edit_btn = QPushButton("Düzenle")
        edit_btn.setObjectName("btn_flat")
        edit_btn.setCursor(Qt.PointingHandCursor)
        edit_btn.clicked.connect(lambda: self._open_edit_dialog(res))
        row.addWidget(edit_btn)

        del_btn = QPushButton("Sil")
        del_btn.setObjectName("btn_danger")
        del_btn.setCursor(Qt.PointingHandCursor)
        del_btn.clicked.connect(lambda: self._delete(res))
        row.addWidget(del_btn)

        return frame

    def _open_create_dialog(self) -> None:
        dlg = ResourceDialog(self)
        if dlg.exec() == QDialog.Accepted:
            self._ctrl.create(dlg.get_data())

    def _open_edit_dialog(self, res: Resource) -> None:
        dlg = ResourceDialog(self, res)
        if dlg.exec() == QDialog.Accepted:
            self._ctrl.update(res.id, dlg.get_data())

    def _delete(self, res: Resource) -> None:
        if confirm(self, f'"{res.title}" kaynağını silmek istediğinizden emin misiniz?', danger=True):
            self._ctrl.delete(res.id)


class ResourceDialog(QDialog):
    def __init__(self, parent=None, resource: Resource = None):
        super().__init__(parent)
        self._resource = resource
        self.setWindowTitle("Kaynak Ekle" if not resource else "Kaynak Düzenle")
        self.setMinimumWidth(460)
        self.setModal(True)
        self._build_ui()
        if resource:
            self._populate(resource)

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 20)
        layout.setSpacing(16)
        self.setStyleSheet(f"QDialog {{ background: {COLORS['bg_secondary']}; }}")

        form = QFormLayout()
        form.setSpacing(12)

        self._type_combo = QComboBox()
        for t in ResourceType:
            self._type_combo.addItem(t.label(), t.value)
        form.addRow("Tür", self._type_combo)

        self._title_input = QLineEdit()
        self._title_input.setPlaceholderText("Kaynak başlığı")
        form.addRow("Başlık *", self._title_input)

        self._url_input = QLineEdit()
        self._url_input.setPlaceholderText("https://...")
        form.addRow("URL", self._url_input)

        self._notes_input = QTextEdit()
        self._notes_input.setPlaceholderText("Notlar, açıklamalar...")
        self._notes_input.setMaximumHeight(100)
        form.addRow("Notlar", self._notes_input)

        self._status_combo = QComboBox()
        for s in ResourceStatus:
            self._status_combo.addItem(s.label(), s.value)
        form.addRow("Durum", self._status_combo)

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

    def _populate(self, res: Resource) -> None:
        idx = self._type_combo.findData(res.type.value)
        if idx >= 0:
            self._type_combo.setCurrentIndex(idx)
        self._title_input.setText(res.title)
        self._url_input.setText(res.url or "")
        self._notes_input.setPlainText(res.notes)
        idx = self._status_combo.findData(res.status.value)
        if idx >= 0:
            self._status_combo.setCurrentIndex(idx)

    def get_data(self) -> dict:
        return {
            "type":   self._type_combo.currentData(),
            "title":  self._title_input.text(),
            "url":    self._url_input.text(),
            "notes":  self._notes_input.toPlainText(),
            "status": self._status_combo.currentData(),
        }
