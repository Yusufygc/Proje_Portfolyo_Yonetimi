"""presentation/showcase/navbar.py — Sabit vitrin navbar'ı."""

from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel, QPushButton, QFrame
from PySide6.QtCore import Qt, Signal, QEasingCurve
from PySide6.QtGui import QFont

from styles.constants import COLORS, FONTS


class ShowcaseNavbar(QWidget):
    """Vitrin üstünde sabit duran navbar. Tıklama → scroll sinyali."""

    scroll_requested = Signal(str)  # section_id: "about", "projects", "vision", "certificates"

    SECTIONS = [
        ("about",        "Hakkımda"),
        ("projects",     "Projelerim"),
        ("vision",       "Vizyon & Misyon"),
        ("certificates", "Sertifikalarım"),
    ]

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("navbar")
        self.setFixedHeight(64)
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QHBoxLayout(self)
        layout.setContentsMargins(32, 0, 32, 0)
        layout.setSpacing(0)

        # Brand
        brand = QLabel("YG")
        brand.setObjectName("nav_brand")
        font = QFont(FONTS["family_heading"], FONTS["size_xl"], QFont.Bold)
        brand.setFont(font)
        layout.addWidget(brand)
        layout.addStretch()

        # Nav butonları
        for section_id, label in self.SECTIONS:
            btn = QPushButton(label)
            btn.setObjectName("nav_btn")
            btn.setCursor(Qt.PointingHandCursor)
            btn.clicked.connect(lambda _, sid=section_id: self.scroll_requested.emit(sid))
            layout.addWidget(btn)
            layout.addSpacing(4)

        self.setStyleSheet(f"""
            QWidget#navbar {{
                background: rgba(15, 25, 35, 0.95);
                border-bottom: 1px solid rgba(74, 158, 255, 0.2);
            }}
            QLabel#nav_brand {{
                color: {COLORS['accent_blue']};
                font-size: {FONTS['size_xl']}px;
                font-weight: 700;
            }}
            QPushButton#nav_btn {{
                background: transparent;
                border: none;
                color: {COLORS['text_secondary']};
                font-size: {FONTS['size_base']}px;
                font-weight: 500;
                padding: 8px 16px;
                border-radius: 6px;
            }}
            QPushButton#nav_btn:hover {{
                color: {COLORS['accent_blue']};
                background: rgba(74, 158, 255, 0.08);
            }}
        """)
