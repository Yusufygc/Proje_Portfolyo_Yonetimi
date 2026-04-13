"""presentation/showcase/navbar.py — Sabit vitrin navbar'ı."""

from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel, QPushButton
from PySide6.QtCore import Qt, Signal, QEvent
from PySide6.QtGui import QFont

from styles.constants import COLORS, FONTS


class ShowcaseNavbar(QWidget):
    """Vitrin üstünde sabit duran navbar. Tıklama → scroll sinyali."""

    scroll_requested = Signal(str)   # section_id
    admin_requested  = Signal()      # gizli logo tıklaması

    SECTIONS = [
        ("about",        "Hakkımda"),
        ("projects",     "Projelerim"),
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
        self._brand.setText('<span style="color:#2F81F7;font-weight:700;letter-spacing:2px;">M</span>'
                            '<span style="color:#E6EDF3;font-weight:700;letter-spacing:2px;">Y</span>'
                            '<span style="color:#2F81F7;font-weight:700;letter-spacing:2px;">Y</span>')
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

        self.setStyleSheet("""
            QWidget#navbar {
                background: rgba(13, 17, 23, 0.95);
                border-bottom: 1px solid #30363D;
            }
            QLabel#nav_brand {
                border: 1px solid #30363D;
                border-radius: 6px;
                padding: 6px 10px;
                font-size: 18px;
            }
            QPushButton#nav_btn {
                background: transparent;
                border: none;
                border-bottom: 1px solid transparent;
                color: #FFFFFF;
                font-size: 16px;
                font-weight: 500;
                padding: 8px 4px;
            }
            QPushButton#nav_btn:hover {
                color: #2F81F7;
                border-bottom: 1px solid #2F81F7;
            }
        """)

    # ── Event filter — logo tıklaması ────────────────────────────────────────

    def eventFilter(self, obj, event) -> bool:
        if obj is self._brand and event.type() == QEvent.MouseButtonPress:
            self.admin_requested.emit()
            return True
        return super().eventFilter(obj, event)
