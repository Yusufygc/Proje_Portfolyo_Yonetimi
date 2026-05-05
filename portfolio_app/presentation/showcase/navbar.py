"""presentation/showcase/navbar.py — Sabit vitrin navbar'ı."""

from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel, QPushButton
from PySide6.QtCore import Qt, Signal, QEvent, QSize
from PySide6.QtGui import QFont

from styles.constants import COLORS, FONTS
from resources.icon_manager import IconManager, Icons
from styles.theme_manager import ThemeManager


class ShowcaseNavbar(QWidget):
    """Vitrin üstünde sabit duran navbar. Tıklama → scroll sinyali."""

    scroll_requested = Signal(str)   # section_id
    admin_requested  = Signal()      # gizli logo tıklaması

    SECTIONS = [
        ("about",        "Hakkımda"),
        ("skills",       "Yeteneklerim"),
        ("projects",     "Projelerim"),
        ("experience",   "Deneyim"),
        ("education",    "Eğitim"),
        ("vision",       "Vizyon & Misyon"),
        ("certificates", "Sertifikalarım"),
    ]

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("navbar")
        self.setFixedHeight(69)
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QHBoxLayout(self)
        layout.setContentsMargins(32, 10, 32, 10)
        layout.setSpacing(0)

        # Brand — "Y" mavi, "G" beyaz, bordered box
        # İmleç değişmeden (ArrowCursor) tıklanabilir — event filter ile
        self._brand = QLabel()
        self._brand.setObjectName("nav_brand")
        self._brand.setText(f'<span style="color:{COLORS["accent_blue"]};font-weight:700;letter-spacing:2px;">M</span>'
                            f'<span style="color:{COLORS["text_primary"]};font-weight:700;letter-spacing:2px;">Y</span>'
                            f'<span style="color:{COLORS["accent_blue"]};font-weight:700;letter-spacing:2px;">Y</span>')
        self._brand.setTextFormat(Qt.RichText)
        self._brand.setCursor(Qt.ArrowCursor)   # imleç değişmesin
        self._brand.installEventFilter(self)
        layout.addWidget(self._brand)
        layout.addStretch()

        # Nav butonları — aralarında 32px boşluk
        for i, (section_id, label) in enumerate(self.SECTIONS):
            if i > 0:
                layout.addSpacing(32)
            btn = QPushButton(label)
            btn.setObjectName("nav_btn")
            btn.setCursor(Qt.PointingHandCursor)
            btn.clicked.connect(lambda _, sid=section_id: self.scroll_requested.emit(sid))
            layout.addWidget(btn)

        # Tema değiştirme butonu
        layout.addSpacing(32)
        is_dark = ThemeManager.get_current_theme().name == "dark"
        theme_icon = Icons.SUN if is_dark else Icons.MOON
        self._theme_btn = QPushButton("")
        self._theme_btn.setIcon(IconManager.get(theme_icon))
        self._theme_btn.setIconSize(QSize(20, 20))
        self._theme_btn.setObjectName("theme_btn")
        self._theme_btn.setCursor(Qt.PointingHandCursor)
        self._theme_btn.setToolTip("Temayı Değiştir (Restart)")
        self._theme_btn.clicked.connect(ThemeManager.toggle_theme_and_restart)
        layout.addWidget(self._theme_btn)

        self.setStyleSheet(f"""
            QWidget#navbar {{
                background: {COLORS['bg_primary']};
                border-bottom: 1px solid {COLORS['border']};
            }}
            QLabel#nav_brand {{
                border: 1px solid {COLORS['border']};
                border-radius: 6px;
                padding: 6px 10px;
                font-size: 18px;
            }}
            QPushButton#nav_btn, QPushButton#theme_btn {{
                background: transparent;
                border: none;
                border-bottom: 1px solid transparent;
                color: {COLORS['text_primary']};
                font-size: 16px;
                font-weight: 500;
                padding: 8px 4px;
            }}
            QPushButton#nav_btn:hover, QPushButton#theme_btn:hover {{
                color: {COLORS['accent_blue']};
                border-bottom: 1px solid {COLORS['accent_blue']};
            }}
        """)

    # ── Event filter — logo tıklaması ────────────────────────────────────────

    def eventFilter(self, obj, event) -> bool:
        if obj is self._brand and event.type() == QEvent.MouseButtonPress:
            self.admin_requested.emit()
            return True
        return super().eventFilter(obj, event)
