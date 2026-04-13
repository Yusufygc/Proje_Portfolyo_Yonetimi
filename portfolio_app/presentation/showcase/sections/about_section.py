"""presentation/showcase/sections/about_section.py — Hakkımda bölümü."""

import webbrowser
import os

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap

from styles.constants import COLORS, FONTS, SPACING
from domain.models.personal_info import PersonalInfo
from config import get_data_path


class AboutSection(QWidget):
    """Hakkımda — avatar, ad, unvan, bio, sosyal linkler."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("about_section")
        self._build_ui()

    def _build_ui(self) -> None:
        self.setStyleSheet("""
            QWidget#about_section {
                background: #0D1117;
            }
        """)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(60, 80, 60, 80)
        outer.setAlignment(Qt.AlignCenter)

        content_row = QHBoxLayout()
        content_row.setSpacing(48)
        content_row.setAlignment(Qt.AlignCenter)

        # Sol: Avatar — 160x210, dikdörtgen, yuvarlatılmış köşe
        self._avatar_label = QLabel()
        self._avatar_label.setFixedSize(160, 210)
        self._avatar_label.setAlignment(Qt.AlignCenter)
        self._avatar_label.setStyleSheet("""
            QLabel {
                background: #161B22;
                border: 2px solid #2F81F7;
                border-radius: 10px;
                color: #8B949E;
                font-size: 32px;
                font-weight: 700;
            }
        """)
        self._avatar_label.setText("YG")
        content_row.addWidget(self._avatar_label)

        # Sağ: Metin
        text_col = QVBoxLayout()
        text_col.setSpacing(12)
        text_col.setAlignment(Qt.AlignVCenter)

        self._name_label = QLabel("Ad Soyad")
        self._name_label.setStyleSheet("""
            color: #E6EDF3;
            font-size: 42px;
            font-weight: 700;
        """)
        text_col.addWidget(self._name_label)

        # Unvan — border-left çizgisi
        self._title_label = QLabel("Yazılım Geliştirici")
        self._title_label.setStyleSheet("""
            color: #2F81F7;
            font-size: 18px;
            font-weight: 500;
            border-left: 3px solid #2F81F7;
            padding-left: 12px;
        """)
        text_col.addWidget(self._title_label)

        # Bio
        self._bio_label = QLabel("")
        self._bio_label.setWordWrap(True)
        self._bio_label.setMaximumWidth(480)
        self._bio_label.setStyleSheet("""
            color: #8B949E;
            font-size: 15px;
        """)
        text_col.addWidget(self._bio_label)

        # Butonlar
        links_row = QHBoxLayout()
        links_row.setSpacing(12)

        self._github_btn = QPushButton("⊕  GitHub")
        self._github_btn.setObjectName("btn_primary")
        self._github_btn.setCursor(Qt.PointingHandCursor)
        self._github_btn.setVisible(False)
        links_row.addWidget(self._github_btn)

        self._contact_btn = QPushButton("İletişim")
        self._contact_btn.setObjectName("btn_secondary")
        self._contact_btn.setCursor(Qt.PointingHandCursor)
        self._contact_btn.setVisible(False)
        links_row.addWidget(self._contact_btn)

        self._linkedin_btn = QPushButton("LinkedIn")
        self._linkedin_btn.setObjectName("btn_secondary")
        self._linkedin_btn.setCursor(Qt.PointingHandCursor)
        self._linkedin_btn.setVisible(False)
        links_row.addWidget(self._linkedin_btn)

        self._website_btn = QPushButton("Website")
        self._website_btn.setObjectName("btn_secondary")
        self._website_btn.setCursor(Qt.PointingHandCursor)
        self._website_btn.setVisible(False)
        links_row.addWidget(self._website_btn)

        links_row.addStretch()
        text_col.addLayout(links_row)

        content_row.addLayout(text_col)
        outer.addLayout(content_row)

        # Buton stilleri
        self.setStyleSheet(self.styleSheet() + """
            QPushButton#btn_primary {
                background: #2F81F7;
                color: #FFFFFF;
                border: none;
                padding: 10px 20px;
                border-radius: 6px;
                font-size: 14px;
                font-weight: 600;
            }
            QPushButton#btn_primary:hover {
                background: #388BFD;
            }
            QPushButton#btn_secondary {
                background: transparent;
                color: #E6EDF3;
                border: 1px solid #30363D;
                padding: 10px 20px;
                border-radius: 6px;
                font-size: 14px;
            }
            QPushButton#btn_secondary:hover {
                border-color: #2F81F7;
                color: #2F81F7;
            }
        """)

    def load_data(self, info: PersonalInfo) -> None:
        """Kişisel bilgilerle bölümü günceller."""
        self._name_label.setText(info.full_name or "Ad Soyad")
        self._title_label.setText(info.title or "Geliştirici")
        self._bio_label.setText(info.bio or "")

        # Avatar
        if info.avatar_path:
            full = os.path.join(get_data_path(), info.avatar_path)
            if os.path.exists(full):
                self._avatar_label.setPixmap(
                    _fit_pixmap(QPixmap(full), 160, 210)
                )
                self._avatar_label.setText("")
        else:
            initials = "".join(w[0].upper() for w in (info.full_name or "YG").split()[:2])
            self._avatar_label.setText(initials)

        # Sosyal linkler
        if info.github_url:
            self._github_btn.setVisible(True)
            self._github_btn.clicked.connect(lambda: webbrowser.open(info.github_url))
        if info.email:
            self._contact_btn.setVisible(True)
            self._contact_btn.clicked.connect(lambda: webbrowser.open(f"mailto:{info.email}"))
        if info.linkedin_url:
            self._linkedin_btn.setVisible(True)
            self._linkedin_btn.clicked.connect(lambda: webbrowser.open(info.linkedin_url))
        if info.website_url:
            self._website_btn.setVisible(True)
            self._website_btn.clicked.connect(lambda: webbrowser.open(info.website_url))


def _fit_pixmap(source: QPixmap, w: int, h: int) -> QPixmap:
    """Pixmap'i çerçeveye tam dolduracak şekilde ölçekler ve ortadan kırpar."""
    scaled = source.scaled(w, h, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
    x = (scaled.width() - w) // 2
    y = (scaled.height() - h) // 2
    return scaled.copy(x, y, w, h)
