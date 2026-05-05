"""presentation/admin/pages/experience_page.py — İş deneyimi CRUD sayfası."""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QScrollArea, QFrame, QDialog, QLineEdit, QFormLayout,
    QSpinBox, QTextEdit, QCheckBox
)
from PySide6.QtCore import Qt

from styles.constants import COLORS, FONTS
from controllers.experience_controller import ExperienceController
from domain.models.experience import Experience
from presentation.shared.confirm_dialog import confirm
from presentation.shared.toast import show_toast, Toast


class ExperiencePage(QWidget):
    """Admin iş deneyimi yönetim sayfası."""

    def __init__(self, controller: ExperienceController, parent=None):
        super().__init__(parent)
        self._ctrl = controller
        self._ctrl.experience_changed.connect(self.refresh)
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

        title = QLabel("İş Deneyimi")
        title.setStyleSheet(
            f"color: {COLORS['text_primary']};"
            f"font-size: {FONTS['size_lg']}px;"
            f"font-weight: 700;"
            f"border: none; background: transparent;"
        )
        h_layout.addWidget(title)
        h_layout.addStretch()

        add_btn = QPushButton("+ Deneyim Ekle")
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
        """Deneyim listesini yeniler."""
        while self._list_layout.count():
            item = self._list_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        records = self._ctrl.get_all()
        if not records:
            empty = QLabel("Henüz iş deneyimi kaydı eklenmemiş.")
            empty.setStyleSheet(
                f"color: {COLORS['text_muted']}; font-size: 14px; "
                f"border: none; background: transparent;"
            )
            self._list_layout.addWidget(empty)
            return

        for exp in records:
            card = ExpCard(exp, self._open_edit_dialog, self._delete)
            self._list_layout.addWidget(card)

    def _open_create_dialog(self) -> None:
        dlg = ExpDialog(self)
        if dlg.exec() == QDialog.Accepted:
            self._ctrl.create(dlg.get_data())

    def _open_edit_dialog(self, exp: Experience) -> None:
        dlg = ExpDialog(self, exp)
        if dlg.exec() == QDialog.Accepted:
            self._ctrl.update(exp.id, dlg.get_data())

    def _delete(self, exp: Experience) -> None:
        if confirm(self, f'"{exp.company}" deneyim kaydını silmek istiyor musunuz?', danger=True):
            self._ctrl.delete(exp.id)


class ExpCard(QFrame):
    """Tek deneyim kaydı kartı."""

    def __init__(self, exp: Experience, on_edit, on_delete, parent=None):
        super().__init__(parent)
        self._exp = exp
        self._on_edit = on_edit
        self._on_delete = on_delete
        self._build_ui()

    def _build_ui(self) -> None:
        self.setObjectName("exp_card")
        self.setStyleSheet(f"""
            QFrame#exp_card {{
                background: {COLORS['bg_card']};
                border: 1px solid {COLORS['border']};
                border-radius: 10px;
            }}
            QFrame#exp_card:hover {{
                border-color: {COLORS['accent_blue']};
            }}
        """)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(20, 16, 16, 16)
        layout.setSpacing(16)

        # Sol: İkon
        icon_lbl = QLabel("💼")
        icon_lbl.setStyleSheet("font-size: 32px; background: transparent; border: none;")
        icon_lbl.setFixedWidth(48)
        layout.addWidget(icon_lbl)

        # Orta: Bilgiler
        info = QWidget()
        info.setStyleSheet("background: transparent; border: none;")
        info_layout = QVBoxLayout(info)
        info_layout.setContentsMargins(0, 0, 0, 0)
        info_layout.setSpacing(2)

        company_lbl = QLabel(self._exp.company)
        company_lbl.setStyleSheet(
            f"color: {COLORS['text_primary']}; font-size: {FONTS['size_base']}px; "
            f"font-weight: 700; background: transparent; border: none;"
        )
        info_layout.addWidget(company_lbl)

        pos_lbl = QLabel(self._exp.position)
        pos_lbl.setStyleSheet(
            f"color: {COLORS['accent_blue']}; font-size: {FONTS['size_sm']}px; "
            f"background: transparent; border: none;"
        )
        info_layout.addWidget(pos_lbl)

        date_text = self._exp.start_date
        if self._exp.is_current:
            date_text += " — Devam ediyor"
        elif self._exp.end_date:
            date_text += f" — {self._exp.end_date}"
        date_lbl = QLabel(date_text)
        date_lbl.setStyleSheet(
            f"color: {COLORS['text_muted']}; font-size: {FONTS['size_xs']}px; "
            f"background: transparent; border: none;"
        )
        info_layout.addWidget(date_lbl)

        if self._exp.description:
            desc_lbl = QLabel(self._exp.description[:150] + "..." if len(self._exp.description) > 150 else self._exp.description)
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
        edit_btn.clicked.connect(lambda: self._on_edit(self._exp))

        del_btn = QPushButton("Sil")
        del_btn.setObjectName("btn_danger")
        del_btn.setCursor(Qt.PointingHandCursor)
        del_btn.setFixedWidth(80)
        del_btn.clicked.connect(lambda: self._on_delete(self._exp))

        btn_layout.addWidget(edit_btn)
        btn_layout.addWidget(del_btn)
        layout.addWidget(btn_widget)


class ExpDialog(QDialog):
    """Deneyim kaydı oluşturma / düzenleme diyaloğu."""

    def __init__(self, parent=None, exp: Experience = None):
        super().__init__(parent)
        self._exp = exp
        self.setWindowTitle("Deneyim Ekle" if not exp else "Deneyim Düzenle")
        self.setMinimumWidth(480)
        self.setModal(True)
        self._build_ui()
        if exp:
            self._populate(exp)

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
            QCheckBox {{ color: {COLORS['text_secondary']}; }}
        """)

        form = QFormLayout()
        form.setSpacing(12)
        form.setLabelAlignment(Qt.AlignRight)

        self._company_input = QLineEdit()
        self._company_input.setPlaceholderText("Ör: Google, Startup Inc.")
        self._position_input = QLineEdit()
        self._position_input.setPlaceholderText("Ör: Senior Backend Developer")
        self._start_input = QLineEdit()
        self._start_input.setPlaceholderText("Ör: Ocak 2022 veya 2022-01")
        self._end_input = QLineEdit()
        self._end_input.setPlaceholderText("Boş bırak = devam ediyor")
        self._current_check = QCheckBox("Hâlâ burada çalışıyorum")
        self._desc_input = QTextEdit()
        self._desc_input.setPlaceholderText("Sorumluluklar, başarılar... Her madde ayrı satırda olsun.")
        self._desc_input.setFixedHeight(100)
        self._order_spin = QSpinBox()
        self._order_spin.setRange(0, 999)

        # Hâlâ çalışıyor işaretlenirse bitiş alanı pasifleşsin
        self._current_check.toggled.connect(
            lambda checked: self._end_input.setEnabled(not checked)
        )

        form.addRow("Şirket *",    self._company_input)
        form.addRow("Pozisyon",    self._position_input)
        form.addRow("Başlangıç",   self._start_input)
        form.addRow("Bitiş",       self._end_input)
        form.addRow("",            self._current_check)
        form.addRow("Açıklama",    self._desc_input)
        form.addRow("Sıralama",    self._order_spin)
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

    def _populate(self, exp: Experience) -> None:
        self._company_input.setText(exp.company)
        self._position_input.setText(exp.position)
        self._start_input.setText(exp.start_date)
        self._end_input.setText(exp.end_date or "")
        self._current_check.setChecked(exp.is_current)
        self._end_input.setEnabled(not exp.is_current)
        self._desc_input.setPlainText(exp.description or "")
        self._order_spin.setValue(exp.display_order)

    def get_data(self) -> dict:
        is_current = self._current_check.isChecked()
        return {
            "company":       self._company_input.text(),
            "position":      self._position_input.text(),
            "start_date":    self._start_input.text(),
            "end_date":      None if is_current else (self._end_input.text() or None),
            "is_current":    is_current,
            "description":   self._desc_input.toPlainText() or None,
            "display_order": self._order_spin.value(),
        }
