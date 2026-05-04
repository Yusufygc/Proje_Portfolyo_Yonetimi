"""presentation/showcase/sections/certificates_section.py — Sertifikalarım bölümü."""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QGridLayout
)
from PySide6.QtCore import Qt

from styles.constants import COLORS
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
                background: {COLORS['bg_secondary']};
                border-top: 1px solid {COLORS['border_light']};
            }}
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(64, 80, 64, 80)
        layout.setSpacing(40)

        # Section header
        header_col = QVBoxLayout()
        header_col.setSpacing(8)

        label = QLabel("// SERTİFİKALAR")
        label.setStyleSheet(f"""
            color: {COLORS['accent_blue']};
            font-size: 12px;
            font-weight: 600;
            letter-spacing: 3px;
        """)
        header_col.addWidget(label)

        title = QLabel("Sertifikalarım")
        title.setStyleSheet(f"""
            color: {COLORS['text_primary']};
            font-size: 36px;
            font-weight: 700;
        """)
        header_col.addWidget(title)

        subtitle = QLabel("Aldığım eğitimler ve başarı sertifikaları")
        subtitle.setStyleSheet(f"""
            color: {COLORS['text_secondary']};
            font-size: 15px;
        """)
        header_col.addWidget(subtitle)

        layout.addLayout(header_col)

        self._grid_widget = QWidget()
        self._grid_widget.setStyleSheet("background: transparent;")
        self._grid = QGridLayout(self._grid_widget)
        self._grid.setSpacing(16)
        self._grid.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self._grid_widget)

        self._empty_label = QLabel("Henüz sertifika eklenmemiş.")
        self._empty_label.setAlignment(Qt.AlignCenter)
        self._empty_label.setStyleSheet(f"color: {COLORS['text_muted']}; font-size: 15px;")
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
        cols = 3 if len(certs) >= 3 else (2 if len(certs) == 2 else 1)
        for i, cert in enumerate(certs):
            card = CertCard(cert)
            self._grid.addWidget(card, i // cols, i % cols)

        # Son sütundan sonrasını stretch et — kartlar sola yaslanır
        self._grid.setColumnStretch(cols, 1)
