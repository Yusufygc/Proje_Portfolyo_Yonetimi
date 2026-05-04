"""presentation/admin/pages/resource_dialog.py — Kaynak ekleme/düzenleme dialog'u."""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QTextEdit, QFormLayout, QComboBox, QSpinBox
)
from PySide6.QtCore import Qt, QSize

from styles.constants import COLORS, FONTS
from domain.models.resource import Resource
from domain.enums.resource_type import ResourceStatus, ResourcePriority
from resources.icon_manager import IconManager, Icons


class ResourceDialog(QDialog):
    def __init__(self, parent=None, resource: Resource = None,
                 resource_types=None, projects=None):
        super().__init__(parent)
        self._resource = resource
        self._resource_types = resource_types or []
        self._projects = projects or []
        self.setWindowTitle("Kaynak Ekle" if not resource else "Kaynak Düzenle")
        self.setMinimumWidth(520)
        self.setModal(True)
        self._build_ui()
        if resource:
            self._populate(resource)

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 28, 28, 24)
        layout.setSpacing(20)

        self.setStyleSheet(f"""
            QDialog {{ background: {COLORS['bg_secondary']}; }}
            QLabel {{ color: {COLORS['text_secondary']}; font-size: 13px; background: transparent; border: none; }}
            QLineEdit, QTextEdit, QComboBox, QSpinBox {{
                background: {COLORS['bg_input']};
                color: {COLORS['text_primary']};
                border: 1px solid {COLORS['border']};
                border-radius: 8px;
                padding: 8px 12px;
                font-size: 13px;
            }}
            QLineEdit:focus, QTextEdit:focus, QComboBox:focus, QSpinBox:focus {{
                border-color: {COLORS['border_focus']};
            }}
        """)

        dlg_title = QLabel("Kaynak Ekle" if not self._resource else "Kaynağı Düzenle")
        dlg_title.setStyleSheet(
            f"color: {COLORS['text_primary']}; font-size: 17px; font-weight: 700;"
            f"background: transparent; border: none;"
        )
        layout.addWidget(dlg_title)

        form = QFormLayout()
        form.setSpacing(14)
        form.setLabelAlignment(Qt.AlignRight | Qt.AlignVCenter)
        form.setFieldGrowthPolicy(QFormLayout.ExpandingFieldsGrow)

        # Tür (dinamik)
        self._type_combo = QComboBox()
        for rt in self._resource_types:
            self._type_combo.addItem(f"{rt.emoji}  {rt.name}", rt.name)
        form.addRow("Tür", self._type_combo)

        self._title_input = QLineEdit()
        self._title_input.setPlaceholderText("Kaynak başlığı")
        form.addRow("Başlık *", self._title_input)

        self._url_input = QLineEdit()
        self._url_input.setPlaceholderText("https://...")
        form.addRow("URL", self._url_input)

        self._notes_input = QTextEdit()
        self._notes_input.setPlaceholderText("Notlar, açıklamalar…")
        self._notes_input.setFixedHeight(90)
        form.addRow("Notlar", self._notes_input)

        self._status_combo = QComboBox()
        for s in ResourceStatus:
            self._status_combo.addItem(s.label(), s.value)
        form.addRow("Durum", self._status_combo)

        self._priority_combo = QComboBox()
        for p in ResourcePriority:
            self._priority_combo.addItem(p.label(), p.value)
        self._priority_combo.setCurrentIndex(1)  # MEDIUM
        form.addRow("Öncelik", self._priority_combo)

        self._progress_spin = QSpinBox()
        self._progress_spin.setRange(0, 100)
        self._progress_spin.setSuffix(" %")
        form.addRow("İlerleme", self._progress_spin)

        # Proje ilişkisi
        self._project_combo = QComboBox()
        self._project_combo.addItem("— Bağlı proje yok —", None)
        for p in self._projects:
            self._project_combo.addItem(p.title, p.id)
        form.addRow("İlişkili Proje", self._project_combo)

        # Etiketler
        self._tags_input = QLineEdit()
        self._tags_input.setPlaceholderText("virgülle ayırın: python, web, api")
        form.addRow("Etiketler", self._tags_input)

        layout.addLayout(form)

        # Butonlar
        btn_row = QHBoxLayout()
        btn_row.addStretch()

        cancel = QPushButton(" İptal")
        cancel.setIcon(IconManager.get(Icons.CLOSE))
        cancel.setIconSize(QSize(16, 16))
        cancel.setFixedHeight(36)
        cancel.setCursor(Qt.PointingHandCursor)
        cancel.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                color: {COLORS['text_secondary']};
                border: 1px solid {COLORS['border']};
                border-radius: 8px; font-size: 13px; padding: 0 20px;
            }}
            QPushButton:hover {{ background: {COLORS['bg_hover']}; }}
        """)
        cancel.clicked.connect(self.reject)
        btn_row.addWidget(cancel)

        save = QPushButton(" Kaydet")
        save.setIcon(IconManager.get(Icons.CHECK))
        save.setIconSize(QSize(16, 16))
        save.setFixedHeight(36)
        save.setCursor(Qt.PointingHandCursor)
        save.setStyleSheet(f"""
            QPushButton {{
                background: {COLORS['accent_blue']}; color: #fff;
                border: none; border-radius: 8px;
                font-size: 13px; font-weight: 600; padding: 0 24px;
            }}
            QPushButton:hover {{ background: {COLORS['accent_blue_dark']}; }}
        """)
        save.clicked.connect(self.accept)
        btn_row.addWidget(save)
        layout.addLayout(btn_row)

    def _populate(self, res: Resource) -> None:
        idx = self._type_combo.findData(res.type)
        if idx >= 0:
            self._type_combo.setCurrentIndex(idx)
        self._title_input.setText(res.title)
        self._url_input.setText(res.url or "")
        self._notes_input.setPlainText(res.notes or "")
        idx = self._status_combo.findData(res.status.value)
        if idx >= 0:
            self._status_combo.setCurrentIndex(idx)
        idx = self._priority_combo.findData(res.priority.value)
        if idx >= 0:
            self._priority_combo.setCurrentIndex(idx)
        self._progress_spin.setValue(res.progress)
        if res.related_project_id:
            idx = self._project_combo.findData(res.related_project_id)
            if idx >= 0:
                self._project_combo.setCurrentIndex(idx)
        if res.tags:
            self._tags_input.setText(", ".join(res.tags))

    def get_data(self) -> dict:
        tags_text = self._tags_input.text()
        tags = [t.strip() for t in tags_text.split(",") if t.strip()] if tags_text else []
        return {
            "type":               self._type_combo.currentData(),
            "title":              self._title_input.text(),
            "url":                self._url_input.text(),
            "notes":              self._notes_input.toPlainText(),
            "status":             self._status_combo.currentData(),
            "priority":           self._priority_combo.currentData(),
            "progress":           self._progress_spin.value(),
            "related_project_id": self._project_combo.currentData(),
            "tags":               tags,
        }
