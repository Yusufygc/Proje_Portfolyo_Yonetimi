"""presentation/showcase/sections/certificates_section.py — Sertifikalarım bölümü."""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QGridLayout
)
from PySide6.QtCore import Qt

from styles.constants import COLORS, FONTS
from domain.models.certificate import Certificate
from presentation.showcase.widgets.cert_card import CertCard


class CertificatesSection(QWidget):
    """Sertifikalar ızgarası."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("certificates_section")
        self._build_ui()

    def _build_ui(self) -> None:
        self.setStyleSheet(f"""
            QWidget#certificates_section {{
                background: {COLORS['grad_certs']};
            }}
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(64, 80, 64, 80)
        layout.setSpacing(40)

        # Başlık
        title = QLabel("Sertifikalarım")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet(f"""
            color: {COLORS['text_primary']};
            font-size: {FONTS['size_2xl']}px;
            font-weight: 700;
        """)
        layout.addWidget(title)

        subtitle = QLabel("Aldığım eğitimler ve başarı sertifikaları")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: {FONTS['size_md']}px;")
        layout.addWidget(subtitle)

        self._grid_widget = QWidget()
        self._grid_widget.setStyleSheet("background: transparent;")
        self._grid = QGridLayout(self._grid_widget)
        self._grid.setSpacing(20)
        layout.addWidget(self._grid_widget)

        self._empty_label = QLabel("Henüz sertifika eklenmemiş.")
        self._empty_label.setAlignment(Qt.AlignCenter)
        self._empty_label.setStyleSheet(f"color: {COLORS['text_muted']}; font-size: {FONTS['size_md']}px;")
        self._empty_label.setVisible(False)
        layout.addWidget(self._empty_label)

    def load_data(self, certs: list[Certificate]) -> None:
        while self._grid.count():
            item = self._grid.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        if not certs:
            self._empty_label.setVisible(True)
            return

        self._empty_label.setVisible(False)
        cols = 4
        for i, cert in enumerate(certs):
            card = CertCard(cert)
            self._grid.addWidget(card, i // cols, i % cols)
