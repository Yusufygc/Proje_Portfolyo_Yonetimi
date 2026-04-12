"""presentation/shared/toast.py — Geçici bildirim popup'ı."""

from PySide6.QtWidgets import QLabel, QWidget, QHBoxLayout
from PySide6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, QPoint
from PySide6.QtGui import QColor

from styles.constants import COLORS


class Toast(QWidget):
    """Ekranın sağ altında 3 saniye görünen bildirim."""

    SUCCESS = "success"
    ERROR   = "error"
    WARNING = "warning"
    INFO    = "info"

    def __init__(self, parent: QWidget, message: str, kind: str = INFO):
        super().__init__(parent)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.SubWindow)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self._build_ui(message, kind)
        self._position()
        self._animate_in()
        QTimer.singleShot(3000, self._animate_out)

    def _build_ui(self, message: str, kind: str) -> None:
        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)

        self._label = QLabel(message)
        self._label.setWordWrap(True)
        layout.addWidget(self._label)

        color_map = {
            self.SUCCESS: (COLORS["success"], "#1A3528"),
            self.ERROR:   (COLORS["error"],   "#3A1A1A"),
            self.WARNING: (COLORS["warning"], "#3A2E10"),
            self.INFO:    (COLORS["accent_blue"], "#1A2840"),
        }
        border_color, bg_color = color_map.get(kind, color_map[self.INFO])

        self.setStyleSheet(f"""
            QWidget {{
                background: {bg_color};
                border: 1px solid {border_color};
                border-radius: 8px;
            }}
            QLabel {{
                color: {COLORS['text_primary']};
                font-size: 13px;
                background: transparent;
                border: none;
            }}
        """)
        self.setMaximumWidth(380)
        self.adjustSize()

    def _position(self) -> None:
        parent = self.parent()
        if parent:
            x = parent.width() - self.width() - 24
            y = parent.height() - self.height() - 24
            self.move(x, y)

    def _animate_in(self) -> None:
        self.show()
        anim = QPropertyAnimation(self, b"pos", self)
        start = self.pos() + QPoint(0, 20)
        anim.setStartValue(start)
        anim.setEndValue(self.pos())
        anim.setDuration(200)
        anim.setEasingCurve(QEasingCurve.OutCubic)
        anim.start()

    def _animate_out(self) -> None:
        anim = QPropertyAnimation(self, b"pos", self)
        anim.setStartValue(self.pos())
        anim.setEndValue(self.pos() + QPoint(0, 20))
        anim.setDuration(200)
        anim.setEasingCurve(QEasingCurve.InCubic)
        anim.finished.connect(self.deleteLater)
        anim.start()


def show_toast(parent: QWidget, message: str, kind: str = Toast.INFO) -> None:
    """Kısayol fonksiyon — her yerden çağrılabilir."""
    Toast(parent, message, kind)
