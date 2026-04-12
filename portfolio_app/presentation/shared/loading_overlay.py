"""presentation/shared/loading_overlay.py — Yükleniyor overlay'i."""

from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QPainter, QColor

from styles.constants import COLORS


class LoadingOverlay(QWidget):
    """Ebeveyn widget'ın üzerini kaplayan yarı-saydam yükleniyor ekranı."""

    def __init__(self, parent: QWidget, message: str = "Yükleniyor..."):
        super().__init__(parent)
        self.setAttribute(Qt.WA_TransparentForMouseEvents, False)
        self.setGeometry(parent.rect())

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)

        self._label = QLabel(message)
        self._label.setAlignment(Qt.AlignCenter)
        self._label.setStyleSheet(f"""
            color: {COLORS['text_primary']};
            font-size: 16px;
            font-weight: 600;
            background: transparent;
        """)
        layout.addWidget(self._label)

        self._dots = 0
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._animate)
        self._timer.start(500)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor(15, 25, 35, 200))

    def _animate(self):
        self._dots = (self._dots + 1) % 4
        self._label.setText(self._label.text().rstrip(".") + "." * self._dots)

    def resizeEvent(self, event):
        parent = self.parent()
        if parent:
            self.setGeometry(parent.rect())

    def show(self):
        self._timer.start()
        super().show()
        self.raise_()

    def hide(self):
        self._timer.stop()
        super().hide()
