"""presentation/showcase/sections/about_section.py — Hakkımda bölümü."""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QPixmap

from styles.constants import COLORS, FONTS, SPACING
from domain.models.personal_info import PersonalInfo
from config import get_data_path
import os


class AboutSection(QWidget):
    """Hakkımda — avatar, ad, unvan, bio, sosyal linkler."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("about_section")
        self._build_ui()

    def _build_ui(self) -> None:
        self.setStyleSheet(f"""
            QWidget#about_section {{
                background: {COLORS['grad_about']};
            }}
        """)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(64, 80, 64, 80)
        outer.setAlignment(Qt.AlignCenter)

        content_row = QHBoxLayout()
        content_row.setSpacing(64)
        content_row.setAlignment(Qt.AlignCenter)

        # Sol: Avatar
        self._avatar_label = QLabel()
        self._avatar_label.setFixedSize(180, 180)
        self._avatar_label.setAlignment(Qt.AlignCenter)
        self._avatar_label.setStyleSheet(f"""
            QLabel {{
                background: {COLORS['bg_card']};
                border: 3px solid {COLORS['accent_blue']};
                border-radius: 90px;
                color: {COLORS['text_secondary']};
                font-size: {FONTS['size_2xl']}px;
                font-weight: 700;
            }}
        """)
        self._avatar_label.setText("YG")
        content_row.addWidget(self._avatar_label)

        # Sağ: Metin
        text_col = QVBoxLayout()
        text_col.setSpacing(16)
        text_col.setAlignment(Qt.AlignVCenter)

        self._name_label = QLabel("Ad Soyad")
        self._name_label.setStyleSheet(f"""
            color: {COLORS['text_primary']};
            font-size: {FONTS['size_3xl']}px;
            font-weight: 700;
        """)
        text_col.addWidget(self._name_label)

        self._title_label = QLabel("Yazılım Geliştirici")
        self._title_label.setStyleSheet(f"""
            color: {COLORS['accent_blue']};
            font-size: {FONTS['size_lg']}px;
            font-weight: 500;
        """)
        text_col.addWidget(self._title_label)

        # Ayırıcı çizgi
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setStyleSheet(f"color: {COLORS['border']};")
        line.setFixedWidth(300)
        text_col.addWidget(line)

        self._bio_label = QLabel("Hakkımda açıklama...")
        self._bio_label.setWordWrap(True)
        self._bio_label.setMaximumWidth(500)
        self._bio_label.setStyleSheet(f"""
            color: {COLORS['text_secondary']};
            font-size: {FONTS['size_md']}px;
            line-height: 1.6;
        """)
        text_col.addWidget(self._bio_label)

        # Sosyal linkler
        links_row = QHBoxLayout()
        links_row.setSpacing(12)

        self._github_btn = QPushButton("GitHub")
        self._github_btn.setObjectName("btn_flat")
        self._github_btn.setCursor(Qt.PointingHandCursor)
        self._github_btn.setVisible(False)
        links_row.addWidget(self._github_btn)

        self._linkedin_btn = QPushButton("LinkedIn")
        self._linkedin_btn.setObjectName("btn_flat")
        self._linkedin_btn.setCursor(Qt.PointingHandCursor)
        self._linkedin_btn.setVisible(False)
        links_row.addWidget(self._linkedin_btn)

        self._website_btn = QPushButton("Website")
        self._website_btn.setObjectName("btn_flat")
        self._website_btn.setCursor(Qt.PointingHandCursor)
        self._website_btn.setVisible(False)
        links_row.addWidget(self._website_btn)

        links_row.addStretch()
        text_col.addLayout(links_row)

        content_row.addLayout(text_col)
        outer.addLayout(content_row)

    def load_data(self, info: PersonalInfo) -> None:
        """Kişisel bilgilerle bölümü günceller."""
        self._name_label.setText(info.full_name or "Ad Soyad")
        self._title_label.setText(info.title or "Geliştirici")
        self._bio_label.setText(info.bio or "")

        # Avatar
        if info.avatar_path:
            full = os.path.join(get_data_path(), info.avatar_path)
            if os.path.exists(full):
                pix = QPixmap(full).scaled(
                    180, 180, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation
                )
                self._avatar_label.setPixmap(pix)
                self._avatar_label.setText("")
        else:
            initials = "".join(w[0].upper() for w in (info.full_name or "YG").split()[:2])
            self._avatar_label.setText(initials)

        # Sosyal linkler
        import webbrowser
        if info.github_url:
            self._github_btn.setVisible(True)
            self._github_btn.clicked.connect(lambda: webbrowser.open(info.github_url))
        if info.linkedin_url:
            self._linkedin_btn.setVisible(True)
            self._linkedin_btn.clicked.connect(lambda: webbrowser.open(info.linkedin_url))
        if info.website_url:
            self._website_btn.setVisible(True)
            self._website_btn.clicked.connect(lambda: webbrowser.open(info.website_url))
