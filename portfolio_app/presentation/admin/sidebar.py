"""presentation/admin/sidebar.py — Açılır/kapanır admin sidebar."""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QLabel, QHBoxLayout, QSpacerItem, QSizePolicy
)
from PySide6.QtCore import Qt, Signal, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QFont

from styles.constants import COLORS, FONTS
from config import SIDEBAR_WIDTH_EXPANDED, SIDEBAR_WIDTH_COLLAPSED, ANIMATION_DURATION_MS


class AdminSidebar(QWidget):
    """
    Açılır/kapanır sidebar.
    - Genişletilmiş: 240px — ikon + metin
    - Daraltılmış: 56px — sadece ikon
    """

    page_requested = Signal(str)  # page_id

    PAGES = [
        ("dashboard",     "Dashboard",       "D"),
        ("projects",      "Projeler",        "P"),
        ("skills",        "Beceriler",       "B"),
        ("personal_info", "Kişisel Bilgi",   "K"),
        ("certificates",  "Sertifikalar",    "S"),
        ("resources",     "Kaynaklar",       "R"),
    ]

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("sidebar")
        self._expanded = True
        self._current_page = "dashboard"
        self._page_btns: dict[str, QPushButton] = {}
        self._build_ui()
        self.setFixedWidth(SIDEBAR_WIDTH_EXPANDED)

    def _build_ui(self) -> None:
        self.setStyleSheet(f"""
            QWidget#sidebar {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #0D1620, stop:1 #0F1923);
                border-right: 1px solid {COLORS['border']};
            }}
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 12, 8, 12)
        layout.setSpacing(2)

        # Üst: Logo + Toggle
        top_row = QHBoxLayout()
        top_row.setContentsMargins(8, 0, 8, 0)

        self._logo = QLabel("Admin")
        self._logo.setObjectName("sidebar_logo")
        self._logo.setStyleSheet(f"""
            color: {COLORS['accent_blue']};
            font-size: 18px;
            font-weight: 700;
            padding: 4px 0;
        """)
        top_row.addWidget(self._logo)
        top_row.addStretch()

        toggle_btn = QPushButton("☰")
        toggle_btn.setObjectName("sidebar_toggle")
        toggle_btn.setCursor(Qt.PointingHandCursor)
        toggle_btn.setFixedSize(32, 32)
        toggle_btn.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                border: none;
                border-radius: 6px;
                color: {COLORS['text_secondary']};
                font-size: 16px;
            }}
            QPushButton:hover {{ background: rgba(74, 158, 255, 0.1); }}
        """)
        toggle_btn.clicked.connect(self.toggle)
        top_row.addWidget(toggle_btn)

        layout.addLayout(top_row)
        layout.addSpacing(16)

        # Sayfa butonları
        for page_id, label, icon_char in self.PAGES:
            btn = self._make_page_btn(page_id, label, icon_char)
            self._page_btns[page_id] = btn
            layout.addWidget(btn)

        layout.addStretch()

        # Geri butonu (vitrine dön)
        self._back_btn = QPushButton("← Vitrine Dön")
        self._back_btn.setObjectName("sidebar_btn")
        self._back_btn.setCursor(Qt.PointingHandCursor)
        self._back_btn.setToolTip("Vitrine Dön")
        self._back_btn.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                border: none;
                border-radius: 8px;
                color: {COLORS['text_muted']};
                font-size: 13px;
                text-align: left;
                padding: 10px 12px;
            }}
            QPushButton:hover {{ color: {COLORS['text_secondary']}; background: rgba(74,158,255,0.05); }}
        """)
        self._back_btn.clicked.connect(lambda: self.page_requested.emit("__back__"))
        layout.addWidget(self._back_btn)

        self._set_active(self._current_page)

    def _make_page_btn(self, page_id: str, label: str, icon_char: str) -> QPushButton:
        btn = QPushButton(f"   {label}")
        btn.setObjectName("sidebar_btn")
        btn.setCursor(Qt.PointingHandCursor)
        btn.setCheckable(False)
        btn.clicked.connect(lambda: self._on_page_click(page_id))
        btn.setStyleSheet(self._btn_style(False))
        btn.setMinimumHeight(40)
        btn.setToolTip(label)
        return btn

    def _on_page_click(self, page_id: str) -> None:
        self._set_active(page_id)
        self.page_requested.emit(page_id)

    def _set_active(self, page_id: str) -> None:
        self._current_page = page_id
        for pid, btn in self._page_btns.items():
            btn.setStyleSheet(self._btn_style(pid == page_id))

    def _btn_style(self, active: bool) -> str:
        if self._expanded:
            padding = "10px 12px"
            align   = "left"
        else:
            padding = "10px 4px"
            align   = "center"

        if active:
            return f"""
                QPushButton {{
                    background: rgba(74, 158, 255, 0.15);
                    border: none;
                    border-left: 3px solid {COLORS['accent_blue']};
                    border-radius: 8px;
                    color: {COLORS['accent_blue']};
                    font-size: 14px;
                    font-weight: 600;
                    text-align: {align};
                    padding: {padding};
                }}
            """
        return f"""
            QPushButton {{
                background: transparent;
                border: none;
                border-radius: 8px;
                color: {COLORS['text_secondary']};
                font-size: 14px;
                text-align: {align};
                padding: {padding};
            }}
            QPushButton:hover {{
                background: rgba(74, 158, 255, 0.08);
                color: {COLORS['text_primary']};
            }}
        """

    def toggle(self) -> None:
        """Sidebar'ı genişlet veya daralt (animasyonlu)."""
        will_collapse = self._expanded
        target = SIDEBAR_WIDTH_COLLAPSED if will_collapse else SIDEBAR_WIDTH_EXPANDED

        self._anim = QPropertyAnimation(self, b"minimumWidth", self)
        self._anim.setStartValue(self.width())
        self._anim.setEndValue(target)
        self._anim.setDuration(ANIMATION_DURATION_MS)
        self._anim.setEasingCurve(QEasingCurve.OutCubic)

        anim2 = QPropertyAnimation(self, b"maximumWidth", self)
        anim2.setStartValue(self.width())
        anim2.setEndValue(target)
        anim2.setDuration(ANIMATION_DURATION_MS)
        anim2.setEasingCurve(QEasingCurve.OutCubic)
        anim2.start()
        self._anim.start()

        self._expanded = not self._expanded
        self._logo.setVisible(self._expanded)
        self._update_btn_labels()

    def _update_btn_labels(self) -> None:
        """Genisletilmis: tam yazi. Daraltilmis: sadece ikon harfi."""
        for (page_id, label, icon_char), btn in zip(self.PAGES, self._page_btns.values()):
            if self._expanded:
                btn.setText(f"   {label}")
            else:
                btn.setText(icon_char)

        # Stil de guncellenmeli (padding/hizalama degisiyor)
        self._set_active(self._current_page)

        if self._expanded:
            self._back_btn.setText("← Vitrine Dön")
        else:
            self._back_btn.setText("←")
