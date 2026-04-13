"""presentation/showcase/widgets/cert_card.py — Vitrin sertifika kartı."""

import os
import webbrowser

from PySide6.QtWidgets import (
    QFrame, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QSizePolicy
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap

from config import get_data_path
from domain.models.certificate import Certificate

CARD_WIDTH = 280
IMG_HEIGHT = 170


class CertCard(QFrame):
    """Vitrin'de gösterilen sertifika kartı — dikey, gerçek görsel."""

    def __init__(self, cert: Certificate, parent=None):
        super().__init__(parent)
        self.setObjectName("cert_card")
        self._cert = cert
        self.setFixedWidth(CARD_WIDTH)
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Minimum)
        self._build_ui()

    def _build_ui(self) -> None:
        self.setStyleSheet("""
            QFrame#cert_card {
                background: #161B22;
                border: 1px solid #30363D;
                border-radius: 12px;
            }
            QFrame#cert_card:hover {
                border-color: #D29922;
            }
            QPushButton#verify_btn {
                background: transparent;
                border: 1px solid #30363D;
                color: #8B949E;
                padding: 4px 14px;
                border-radius: 6px;
                font-size: 12px;
            }
            QPushButton#verify_btn:hover {
                border-color: #2F81F7;
                color: #2F81F7;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # ── Görsel alanı ─────────────────────────────────────────────────────
        img_frame = QFrame()
        img_frame.setFixedHeight(IMG_HEIGHT)
        img_frame.setStyleSheet("""
            QFrame {
                background: #0D1117;
                border-top-left-radius: 12px;
                border-top-right-radius: 12px;
                border-bottom-left-radius: 0px;
                border-bottom-right-radius: 0px;
                border: none;
            }
        """)
        img_layout = QVBoxLayout(img_frame)
        img_layout.setContentsMargins(0, 0, 0, 0)
        img_layout.setAlignment(Qt.AlignCenter)

        img_lbl = QLabel()
        img_lbl.setAlignment(Qt.AlignCenter)
        img_lbl.setStyleSheet("background: transparent; border: none;")

        pixmap = self._load_pixmap()
        if pixmap:
            scaled = pixmap.scaled(
                CARD_WIDTH, IMG_HEIGHT,
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation,
            )
            img_lbl.setPixmap(scaled)
        else:
            img_lbl.setText(self._pick_icon())
            img_lbl.setStyleSheet(
                "font-size: 52px; background: transparent; border: none;"
            )

        img_layout.addWidget(img_lbl)
        layout.addWidget(img_frame)

        # ── Bilgi alanı ───────────────────────────────────────────────────────
        info_widget = QWidget()
        info_widget.setStyleSheet("background: transparent; border: none;")
        info_layout = QVBoxLayout(info_widget)
        info_layout.setContentsMargins(16, 14, 16, 6)
        info_layout.setSpacing(4)

        name_lbl = QLabel(self._cert.name)
        name_lbl.setWordWrap(True)
        name_lbl.setStyleSheet("""
            color: #E6EDF3;
            font-size: 15px;
            font-weight: 600;
            background: transparent;
            border: none;
        """)
        info_layout.addWidget(name_lbl)

        if self._cert.issuer:
            issuer_lbl = QLabel(self._cert.issuer)
            issuer_lbl.setStyleSheet("""
                color: #2F81F7;
                font-size: 13px;
                background: transparent;
                border: none;
            """)
            info_layout.addWidget(issuer_lbl)

        if self._cert.date:
            date_lbl = QLabel(self._cert.date)
            date_lbl.setStyleSheet("""
                color: #484F58;
                font-size: 12px;
                background: transparent;
                border: none;
            """)
            info_layout.addWidget(date_lbl)

        layout.addWidget(info_widget)

        # ── Doğrulama butonu ─────────────────────────────────────────────────
        if self._cert.verification_url:
            btn_widget = QWidget()
            btn_widget.setStyleSheet("background: transparent; border: none;")
            btn_layout = QHBoxLayout(btn_widget)
            btn_layout.setContentsMargins(16, 4, 16, 14)

            verify_btn = QPushButton("Doğrula →")
            verify_btn.setObjectName("verify_btn")
            verify_btn.setCursor(Qt.PointingHandCursor)
            url = self._cert.verification_url
            verify_btn.clicked.connect(lambda: webbrowser.open(url))
            btn_layout.addWidget(verify_btn)
            btn_layout.addStretch()

            layout.addWidget(btn_widget)
        else:
            # Alt padding
            spacer = QWidget()
            spacer.setFixedHeight(14)
            spacer.setStyleSheet("background: transparent; border: none;")
            layout.addWidget(spacer)

    def _load_pixmap(self):
        if not self._cert.image_path:
            return None
        if os.path.isabs(self._cert.image_path):
            full_path = self._cert.image_path
        else:
            full_path = os.path.join(get_data_path(), self._cert.image_path)
        if not os.path.exists(full_path):
            return None
        px = QPixmap(full_path)
        return px if not px.isNull() else None

    def _pick_icon(self) -> str:
        name_lower = (self._cert.name or "").lower()
        if any(k in name_lower for k in ("python", "java", "qt", "c++", "programm", "coding", "development")):
            return "🖥️"
        if any(k in name_lower for k in ("award", "ödül", "başarı", "achievement")):
            return "🏆"
        return "📜"
