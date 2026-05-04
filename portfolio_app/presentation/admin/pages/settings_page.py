"""presentation/admin/pages/settings_page.py — Uygulama Ayarları Sayfası."""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout
from PySide6.QtCore import Qt
from styles.constants import COLORS, FONTS
from styles.theme_manager import ThemeManager

class SettingsPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(24)

        title = QLabel("Ayarlar")
        title.setStyleSheet(f"font-size: {FONTS['size_xl']}px; font-weight: bold; color: {COLORS['text_primary']};")
        layout.addWidget(title)

        desc = QLabel("Uygulama ayarlarınızı buradan yönetebilirsiniz. Tema değişikliği, uygulama yeniden başlatılmasını gerektirir.")
        desc.setStyleSheet(f"color: {COLORS['text_secondary']};")
        desc.setWordWrap(True)
        layout.addWidget(desc)

        # Tema Ayarı
        theme_row = QHBoxLayout()
        theme_lbl = QLabel("Arayüz Teması:")
        theme_lbl.setStyleSheet(f"color: {COLORS['text_primary']}; font-weight: 500;")
        theme_row.addWidget(theme_lbl)

        theme_btn = QPushButton("Temayı Değiştir (Restart)")
        theme_btn.setCursor(Qt.PointingHandCursor)
        theme_btn.setFixedWidth(200)
        theme_btn.setFixedHeight(40)
        theme_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['accent_blue']};
                color: {COLORS['white']};
                border-radius: 6px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {COLORS['accent_blue_dark']};
            }}
        """)
        theme_btn.clicked.connect(ThemeManager.toggle_theme_and_restart)
        theme_row.addWidget(theme_btn)
        theme_row.addStretch()

        layout.addLayout(theme_row)
        layout.addStretch()
