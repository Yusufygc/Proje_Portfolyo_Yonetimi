"""presentation/showcase/sections/vision_section.py — Vizyon & Misyon bölümü."""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame
)
from PySide6.QtCore import Qt

from styles.constants import COLORS, FONTS
from domain.models.personal_info import PersonalInfo


class VisionSection(QWidget):
    """Vizyon ve Misyon — iki sütun kartlar."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("vision_section")
        self._build_ui()

    def _build_ui(self) -> None:
        self.setStyleSheet(f"""
            QWidget#vision_section {{
                background: {COLORS['grad_vision']};
            }}
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(64, 80, 64, 80)
        layout.setSpacing(48)

        # Başlık
        title = QLabel("Vizyon & Misyon")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet(f"""
            color: {COLORS['text_primary']};
            font-size: {FONTS['size_2xl']}px;
            font-weight: 700;
        """)
        layout.addWidget(title)

        # İki sütun
        cards_row = QHBoxLayout()
        cards_row.setSpacing(32)

        self._vision_card  = self._make_card("Vizyonum", "")
        self._mission_card = self._make_card("Misyonum", "")
        cards_row.addWidget(self._vision_card["widget"])
        cards_row.addWidget(self._mission_card["widget"])

        layout.addLayout(cards_row)

    def _make_card(self, label: str, text: str) -> dict:
        frame = QFrame()
        frame.setObjectName("glass_card")
        frame.setStyleSheet(f"""
            QFrame#glass_card {{
                background: rgba(28, 42, 58, 0.6);
                border: 1px solid rgba(74, 158, 255, 0.25);
                border-radius: 16px;
                padding: 0;
            }}
        """)
        col = QVBoxLayout(frame)
        col.setContentsMargins(32, 32, 32, 32)
        col.setSpacing(16)

        title_lbl = QLabel(label)
        title_lbl.setStyleSheet(f"""
            color: {COLORS['accent_blue']};
            font-size: {FONTS['size_lg']}px;
            font-weight: 700;
        """)
        col.addWidget(title_lbl)

        accent = QFrame()
        accent.setFixedHeight(2)
        accent.setFixedWidth(40)
        accent.setStyleSheet(f"background: {COLORS['accent_blue']}; border-radius: 1px;")
        col.addWidget(accent)

        text_lbl = QLabel(text)
        text_lbl.setWordWrap(True)
        text_lbl.setStyleSheet(f"""
            color: {COLORS['text_secondary']};
            font-size: {FONTS['size_md']}px;
            line-height: 1.7;
        """)
        col.addWidget(text_lbl)
        col.addStretch()

        return {"widget": frame, "text_label": text_lbl}

    def load_data(self, info: PersonalInfo) -> None:
        self._vision_card["text_label"].setText(info.vision_text or "Vizyon metni girilmemiş.")
        self._mission_card["text_label"].setText(info.mission_text or "Misyon metni girilmemiş.")
