"""presentation/admin/pages/education_page.py — Eğitim geçmişi CRUD sayfası."""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QScrollArea, QFrame, QDialog, QLineEdit, QFormLayout,
    QSpinBox, QTextEdit, QSizePolicy
)
from PySide6.QtCore import Qt

from styles.constants import COLORS, FONTS
from controllers.education_controller import EducationController
from domain.models.education import Education
from presentation.shared.confirm_dialog import confirm
from presentation.shared.toast import show_toast, Toast


class EducationPage(QWidget):
    """Admin eğitim geçmişi yönetim sayfası."""

    def __init__(self, controller: EducationController, parent=None):
        super().__init__(parent)
        self._ctrl = controller
        self._ctrl.education_changed.connect(self.refresh)
        self._ctrl.error_occurred.connect(lambda msg: show_toast(self, msg, Toast.ERROR))
        self._build_ui()
        self.refresh()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Üst bar
        header = QWidget()
        header.setStyleSheet(
            f"background: {COLORS['bg_secondary']};"
            f"border-bottom: 1px solid {COLORS['border']};"
        )
        h_layout = QHBoxLayout(header)
        h_layout.setContentsMargins(24, 16, 24, 16)

        title = QLabel("Eğitim Geçmişi")
        title.setStyleSheet(
            f"color: {COLORS['text_primary']};"
            f"font-size: {FONTS['size_lg']}px;"
            f"font-weight: 700;"
            f"border: none; background: transparent;"
        )
        h_layout.addWidget(title)
        h_layout.addStretch()

        add_btn = QPushButton("+ Eğitim Ekle")
        add_btn.setCursor(Qt.PointingHandCursor)
        add_btn.clicked.connect(self._open_create_dialog)
        h_layout.addWidget(add_btn)
        layout.addWidget(header)

        # Scroll + Liste
        self._scroll = QScrollArea()
        self._scroll.setWidgetResizable(True)
        self._scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")

        self._container = QWidget()
        self._container.setStyleSheet(f"background: {COLORS['bg_primary']};")

        self._list_layout = QVBoxLayout(self._container)
        self._list_layout.setContentsMargins(24, 24, 24, 24)
        self._list_layout.setSpacing(12)
        self._list_layout.setAlignment(Qt.AlignTop)

        self._scroll.setWidget(self._container)
        layout.addWidget(self._scroll)

    def refresh(self) -> None:
        """Eğitim listesini yeniler."""
        while self._list_layout.count():
            item = self._list_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        records = self._ctrl.get_all()
        if not records:
            empty = QLabel("Henüz eğitim kaydı eklenmemiş.")
            empty.setStyleSheet(
                f"color: {COLORS['text_muted']}; font-size: 14px; "
                f"border: none; background: transparent;"
            )
            self._list_layout.addWidget(empty)
            return

        for edu in records:
            card = EduCard(edu, self._open_edit_dialog, self._delete)
            self._list_layout.addWidget(card)

    def _open_create_dialog(self) -> None:
        dlg = EduDialog(self)
        if dlg.exec() == QDialog.Accepted:
            self._ctrl.create(dlg.get_data())

    def _open_edit_dialog(self, edu: Education) -> None:
        dlg = EduDialog(self, edu)
        if dlg.exec() == QDialog.Accepted:
            self._ctrl.update(edu.id, dlg.get_data())

    def _delete(self, edu: Education) -> None:
        if confirm(self, f'"{edu.institution}" eğitim kaydını silmek istiyor musunuz?', danger=True):
            self._ctrl.delete(edu.id)


class EduCard(QFrame):
    """Tek eğitim kaydı kartı."""

    def __init__(self, edu: Education, on_edit, on_delete, parent=None):
        super().__init__(parent)
        self._edu = edu
        self._on_edit = on_edit
        self._on_delete = on_delete
        self._build_ui()

    def _build_ui(self) -> None:
        self.setObjectName("edu_card")
        self.setStyleSheet(f"""
            QFrame#edu_card {{
                background: {COLORS['bg_card']};
                border: 1px solid {COLORS['border']};
                border-radius: 10px;
            }}
            QFrame#edu_card:hover {{
                border-color: {COLORS['accent_blue']};
            }}
        """)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(20, 16, 16, 16)
        layout.setSpacing(16)

        # Sol: İkon
        icon_lbl = QLabel("🎓")
        icon_lbl.setStyleSheet("font-size: 32px; background: transparent; border: none;")
        icon_lbl.setFixedWidth(48)
        layout.addWidget(icon_lbl)

        # Orta: Bilgiler
        info = QWidget()
        info.setStyleSheet("background: transparent; border: none;")
        info_layout = QVBoxLayout(info)
        info_layout.setContentsMargins(0, 0, 0, 0)
        info_layout.setSpacing(2)

        inst_lbl = QLabel(self._edu.institution)
        inst_lbl.setStyleSheet(
            f"color: {COLORS['text_primary']}; font-size: {FONTS['size_base']}px; "
            f"font-weight: 700; background: transparent; border: none;"
        )
        info_layout.addWidget(inst_lbl)

        degree_text = self._edu.degree
        if self._edu.field:
            degree_text += f", {self._edu.field}"
        degree_lbl = QLabel(degree_text)
        degree_lbl.setStyleSheet(
            f"color: {COLORS['accent_blue']}; font-size: {FONTS['size_sm']}px; "
            f"background: transparent; border: none;"
        )
        info_layout.addWidget(degree_lbl)

        date_text = self._edu.start_date
        if self._edu.end_date:
            date_text += f" — {self._edu.end_date}"
        elif self._edu.start_date:
            date_text += " — Devam ediyor"
        date_lbl = QLabel(date_text)
        date_lbl.setStyleSheet(
            f"color: {COLORS['text_muted']}; font-size: {FONTS['size_xs']}px; "
            f"background: transparent; border: none;"
        )
        info_layout.addWidget(date_lbl)

        if self._edu.description:
            desc_lbl = QLabel(self._edu.description)
            desc_lbl.setWordWrap(True)
            desc_lbl.setStyleSheet(
                f"color: {COLORS['text_secondary']}; font-size: {FONTS['size_sm']}px; "
                f"background: transparent; border: none; margin-top: 4px;"
            )
            info_layout.addWidget(desc_lbl)

        layout.addWidget(info)
        layout.addStretch()

        # Sağ: Butonlar
        btn_widget = QWidget()
        btn_widget.setStyleSheet("background: transparent; border: none;")
        btn_layout = QVBoxLayout(btn_widget)
        btn_layout.setContentsMargins(0, 0, 0, 0)
        btn_layout.setSpacing(6)

        edit_btn = QPushButton("Düzenle")
        edit_btn.setObjectName("btn_flat")
        edit_btn.setCursor(Qt.PointingHandCursor)
        edit_btn.setFixedWidth(80)
        edit_btn.clicked.connect(lambda: self._on_edit(self._edu))

        del_btn = QPushButton("Sil")
        del_btn.setObjectName("btn_danger")
        del_btn.setCursor(Qt.PointingHandCursor)
        del_btn.setFixedWidth(80)
        del_btn.clicked.connect(lambda: self._on_delete(self._edu))

        btn_layout.addWidget(edit_btn)
        btn_layout.addWidget(del_btn)
        layout.addWidget(btn_widget)


class EduDialog(QDialog):
    """Eğitim kaydı oluşturma / düzenleme diyaloğu."""

    def __init__(self, parent=None, edu: Education = None):
        super().__init__(parent)
        self._edu = edu
        self.setWindowTitle("Eğitim Ekle" if not edu else "Eğitim Düzenle")
        self.setMinimumWidth(480)
        self.setModal(True)
        self._build_ui()
        if edu:
            self._populate(edu)

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 20)
        layout.setSpacing(16)
        self.setStyleSheet(f"""
            QDialog {{ background: {COLORS['bg_secondary']}; }}
            QLabel  {{ color: {COLORS['text_secondary']}; background: transparent; border: none; }}
            QLineEdit, QTextEdit, QSpinBox {{
                background: {COLORS['bg_input']};
                color: {COLORS['text_primary']};
                border: 1px solid {COLORS['border']};
                border-radius: 6px;
                padding: 6px 10px;
                font-size: 13px;
            }}
            QLineEdit:focus, QTextEdit:focus, QSpinBox:focus {{
                border-color: {COLORS['border_focus']};
            }}
        """)

        form = QFormLayout()
        form.setSpacing(12)
        form.setLabelAlignment(Qt.AlignRight)

        self._institution_input = QLineEdit()
        self._institution_input.setPlaceholderText("Ör: İstanbul Teknik Üniversitesi")
        self._degree_input = QLineEdit()
        self._degree_input.setPlaceholderText("Ör: Lisans, Yüksek Lisans")
        self._field_input = QLineEdit()
        self._field_input.setPlaceholderText("Ör: Bilgisayar Mühendisliği")
        self._start_input = QLineEdit()
        self._start_input.setPlaceholderText("Ör: 2018")
        self._end_input = QLineEdit()
        self._end_input.setPlaceholderText("Ör: 2022 (boş bırak = devam ediyor)")
        self._desc_input = QTextEdit()
        self._desc_input.setPlaceholderText("Opsiyonel açıklama...")
        self._desc_input.setFixedHeight(80)
        self._order_spin = QSpinBox()
        self._order_spin.setRange(0, 999)

        form.addRow("Kurum *",   self._institution_input)
        form.addRow("Derece",    self._degree_input)
        form.addRow("Bölüm",     self._field_input)
        form.addRow("Başlangıç", self._start_input)
        form.addRow("Bitiş",     self._end_input)
        form.addRow("Açıklama",  self._desc_input)
        form.addRow("Sıralama",  self._order_spin)
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

    def _populate(self, edu: Education) -> None:
        self._institution_input.setText(edu.institution)
        self._degree_input.setText(edu.degree)
        self._field_input.setText(edu.field)
        self._start_input.setText(edu.start_date)
        self._end_input.setText(edu.end_date or "")
        self._desc_input.setPlainText(edu.description or "")
        self._order_spin.setValue(edu.display_order)

    def get_data(self) -> dict:
        return {
            "institution":  self._institution_input.text(),
            "degree":        self._degree_input.text(),
            "field":         self._field_input.text(),
            "start_date":    self._start_input.text(),
            "end_date":      self._end_input.text() or None,
            "description":   self._desc_input.toPlainText() or None,
            "display_order": self._order_spin.value(),
        }
