"""presentation/showcase/widgets/cert_card.py — Vitrin sertifika kartı."""

import webbrowser
from PySide6.QtWidgets import QFrame, QVBoxLayout, QLabel, QPushButton
from PySide6.QtCore import Qt

from styles.constants import COLORS, FONTS
from domain.models.certificate import Certificate


class CertCard(QFrame):
    """Vitrin'de gösterilen sertifika kartı."""

    def __init__(self, cert: Certificate, parent=None):
        super().__init__(parent)
        self.setObjectName("card")
        self._cert = cert
        self._build_ui()

    def _build_ui(self) -> None:
        self.setStyleSheet(f"""
            QFrame#card {{
                background: {COLORS['bg_card']};
                border: 1px solid {COLORS['border']};
                border-radius: 12px;
            }}
            QFrame#card:hover {{
                border-color: {COLORS['accent_blue']};
            }}
        """)
        self.setMinimumWidth(200)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(8)

        # İkon placeholder
        icon_lbl = QLabel("🏆")
        icon_lbl.setAlignment(Qt.AlignCenter)
        icon_lbl.setStyleSheet(f"font-size: 32px; background: transparent;")
        layout.addWidget(icon_lbl)

        name_lbl = QLabel(self._cert.name)
        name_lbl.setAlignment(Qt.AlignCenter)
        name_lbl.setWordWrap(True)
        name_lbl.setStyleSheet(f"""
            color: {COLORS['text_primary']};
            font-size: 13px;
            font-weight: 700;
        """)
        layout.addWidget(name_lbl)

        issuer_lbl = QLabel(self._cert.issuer)
        issuer_lbl.setAlignment(Qt.AlignCenter)
        issuer_lbl.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 11px;")
        layout.addWidget(issuer_lbl)

        if self._cert.date:
            date_lbl = QLabel(self._cert.date)
            date_lbl.setAlignment(Qt.AlignCenter)
            date_lbl.setStyleSheet(f"color: {COLORS['text_muted']}; font-size: 11px;")
            layout.addWidget(date_lbl)

        if self._cert.verification_url:
            verify_btn = QPushButton("Doğrula")
            verify_btn.setObjectName("btn_flat")
            verify_btn.setCursor(Qt.PointingHandCursor)
            url = self._cert.verification_url
            verify_btn.clicked.connect(lambda: webbrowser.open(url))
            layout.addWidget(verify_btn)
