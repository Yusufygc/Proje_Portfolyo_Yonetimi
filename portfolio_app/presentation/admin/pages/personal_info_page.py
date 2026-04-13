"""presentation/admin/pages/personal_info_page.py — Kişisel bilgi düzenleme."""

import os
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QTextEdit, QFormLayout, QFileDialog, QScrollArea
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap

from styles.constants import COLORS, FONTS
from controllers.personal_info_controller import PersonalInfoController
from presentation.shared.toast import show_toast, Toast
from config import get_data_path


class PersonalInfoPage(QWidget):
    """Admin kişisel bilgi sayfası."""

    def __init__(self, controller: PersonalInfoController, parent=None):
        super().__init__(parent)
        self._ctrl = controller
        self._avatar_source_path: str | None = None
        self._ctrl.info_changed.connect(self.refresh)
        self._ctrl.error_occurred.connect(lambda msg: show_toast(self, msg, Toast.ERROR))
        self._build_ui()
        self.refresh()

    def _build_ui(self) -> None:
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; }")

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(scroll)

        content = QWidget()
        scroll.setWidget(content)
        layout = QVBoxLayout(content)
        layout.setContentsMargins(32, 32, 32, 32)
        layout.setSpacing(24)

        # Başlık
        title = QLabel("Kişisel Bilgiler")
        title.setStyleSheet(f"color: {COLORS['text_primary']}; font-size: {FONTS['size_lg']}px; font-weight: 700;")
        layout.addWidget(title)

        # Avatar
        avatar_row = QHBoxLayout()
        self._avatar_lbl = QLabel("YG")
        self._avatar_lbl.setFixedSize(100, 130)
        self._avatar_lbl.setAlignment(Qt.AlignCenter)
        self._avatar_lbl.setStyleSheet(f"""
            background: {COLORS['bg_card']};
            border: 2px solid {COLORS['accent_blue']};
            border-radius: 8px;
            color: {COLORS['text_primary']};
            font-size: 28px;
            font-weight: 700;
        """)
        avatar_row.addWidget(self._avatar_lbl)

        avatar_btn = QPushButton("Fotoğraf Seç")
        avatar_btn.setObjectName("btn_flat")
        avatar_btn.setCursor(Qt.PointingHandCursor)
        avatar_btn.clicked.connect(self._pick_avatar)
        avatar_row.addWidget(avatar_btn)
        avatar_row.addStretch()
        layout.addLayout(avatar_row)

        # Form
        form = QFormLayout()
        form.setSpacing(12)
        form.setLabelAlignment(Qt.AlignRight | Qt.AlignVCenter)

        self._name_input     = QLineEdit()
        self._title_input    = QLineEdit()
        self._bio_input      = QTextEdit()
        self._bio_input.setMaximumHeight(100)
        self._github_input   = QLineEdit()
        self._linkedin_input = QLineEdit()
        self._website_input  = QLineEdit()
        self._email_input    = QLineEdit()
        self._vision_input   = QTextEdit()
        self._vision_input.setMaximumHeight(100)
        self._mission_input  = QTextEdit()
        self._mission_input.setMaximumHeight(100)

        fields = [
            ("Ad Soyad *",   self._name_input),
            ("Unvan",        self._title_input),
            ("Hakkımda",     self._bio_input),
            ("GitHub URL",   self._github_input),
            ("LinkedIn URL", self._linkedin_input),
            ("Website URL",  self._website_input),
            ("E-posta",      self._email_input),
            ("Vizyonum",     self._vision_input),
            ("Misyonum",     self._mission_input),
        ]
        for label, widget in fields:
            form.addRow(label, widget)

        layout.addLayout(form)

        # Kaydet butonu
        save_btn = QPushButton("Kaydet")
        save_btn.setCursor(Qt.PointingHandCursor)
        save_btn.clicked.connect(self._save)
        layout.addWidget(save_btn, alignment=Qt.AlignLeft)
        layout.addStretch()

    def refresh(self) -> None:
        info = self._ctrl.get()
        self._name_input.setText(info.full_name)
        self._title_input.setText(info.title)
        self._bio_input.setPlainText(info.bio)
        self._github_input.setText(info.github_url or "")
        self._linkedin_input.setText(info.linkedin_url or "")
        self._website_input.setText(info.website_url or "")
        self._email_input.setText(info.email or "")
        self._vision_input.setPlainText(info.vision_text)
        self._mission_input.setPlainText(info.mission_text)

        if info.avatar_path:
            full = os.path.join(get_data_path(), info.avatar_path)
            if os.path.exists(full):
                self._avatar_lbl.setPixmap(_fit_pixmap(QPixmap(full), 100, 130))
                self._avatar_lbl.setText("")

    def _pick_avatar(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self, "Avatar Seç", "", "Görseller (*.jpg *.jpeg *.png *.webp)"
        )
        if path:
            self._avatar_source_path = path
            self._avatar_lbl.setPixmap(_fit_pixmap(QPixmap(path), 100, 130))
            self._avatar_lbl.setText("")

    def _save(self) -> None:
        data = {
            "full_name":    self._name_input.text(),
            "title":        self._title_input.text(),
            "bio":          self._bio_input.toPlainText(),
            "github_url":   self._github_input.text(),
            "linkedin_url": self._linkedin_input.text(),
            "website_url":  self._website_input.text(),
            "email":        self._email_input.text(),
            "vision_text":  self._vision_input.toPlainText(),
            "mission_text": self._mission_input.toPlainText(),
        }
        if self._avatar_source_path:
            data["avatar_source_path"] = self._avatar_source_path
        result = self._ctrl.update(data)
        if result:
            show_toast(self, "Kişisel bilgiler kaydedildi.", Toast.SUCCESS)
            self._avatar_source_path = None


def _fit_pixmap(source: QPixmap, w: int, h: int) -> QPixmap:
    """Pixmap'i çerçeveye tam dolduracak şekilde ölçekler ve ortadan kırpar."""
    scaled = source.scaled(w, h, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
    x = (scaled.width() - w) // 2
    y = (scaled.height() - h) // 2
    return scaled.copy(x, y, w, h)
