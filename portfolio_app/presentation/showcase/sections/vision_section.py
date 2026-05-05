"""presentation/showcase/sections/vision_section.py — Vizyon & Misyon bölümü."""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame
)
from PySide6.QtCore import Qt

from styles.constants import COLORS
from domain.models.personal_info import PersonalInfo


class VisionSection(QWidget):
    """Vizyon ve Misyon — iki sütun kartlar."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("vision_section")
        self._build_ui()

    def _build_ui(self) -> None:
        self._label = QLabel("// VİZYON & MİSYON")
        self._title = QLabel("Vizyon & Misyon")
        self._subtitle = QLabel("Hedeflerim ve yazılım geliştirme felsefem")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(64, 80, 64, 80)
        layout.setSpacing(40)

        # Section header
        header_col = QVBoxLayout()
        header_col.setSpacing(8)

        header_col.addWidget(self._label)

        header_col.addWidget(self._title)

        header_col.addWidget(self._subtitle)

        layout.addLayout(header_col)

        # İki sütun kartlar
        cards_row = QHBoxLayout()
        cards_row.setSpacing(20)

        self._vision_card = self._make_card(
            icon="🎯",
            label="Vizyonum",
            title_color=COLORS['accent_blue'],
            border_color=COLORS['accent_blue'],
            accent_color=COLORS['accent_blue'],
        )
        self._mission_card = self._make_card(
            icon="⚡",
            label="Misyonum",
            title_color=COLORS['success'],
            border_color=COLORS['success'],
            accent_color=COLORS['success'],
        )
        cards_row.addWidget(self._vision_card["widget"])
        cards_row.addWidget(self._mission_card["widget"])

        layout.addLayout(cards_row)
        
        self.apply_theme()

    def _make_card(self, icon: str, label: str, title_color: str,
                   border_color: str, accent_color: str) -> dict:
        frame = QFrame()
        frame.setObjectName("vision_card")
        frame.setStyleSheet(f"""
            QFrame#vision_card {{
                background: {COLORS['bg_card']};
                border: 1px solid {COLORS['border']};
                border-left: 3px solid {border_color};
                border-radius: 12px;
            }}
        """)

        col = QVBoxLayout(frame)
        col.setContentsMargins(32, 32, 32, 32)
        col.setSpacing(0)

        # Başlık satırı: ikon + yazı
        title_row = QHBoxLayout()
        title_row.setSpacing(10)

        icon_lbl = QLabel(icon)
        icon_lbl.setStyleSheet("font-size: 20px; background: transparent; border: none;")
        title_row.addWidget(icon_lbl)

        title_lbl = QLabel(label)
        title_lbl.setStyleSheet(f"""
            color: {title_color};
            font-size: 20px;
            font-weight: 600;
            background: transparent;
            border: none;
        """)
        title_row.addWidget(title_lbl)
        title_row.addStretch()
        col.addLayout(title_row)

        # Alt divider çizgisi
        divider = QFrame()
        divider.setFixedHeight(2)
        divider.setFixedWidth(40)
        divider.setStyleSheet(f"""
            background: {accent_color};
            border: none;
            margin-top: 12px;
            margin-bottom: 20px;
        """)
        col.addWidget(divider)
        col.addSpacing(20)

        # İçerik metni — veri admin panelden gelir, dokunma
        text_lbl = QLabel("")
        text_lbl.setWordWrap(True)
        col.addWidget(text_lbl)
        col.addStretch()

        return {"widget": frame, "text_label": text_lbl, "icon_lbl": icon_lbl, "title_lbl": title_lbl, "divider": divider, "title_color": title_color, "border_color": border_color, "accent_color": accent_color}

    def load_data(self, info: PersonalInfo) -> None:
        self._vision_card["text_label"].setText(info.vision_text or "")
        self._mission_card["text_label"].setText(info.mission_text or "")

    def apply_theme(self):
        self.setStyleSheet(f"""
            QWidget#vision_section {{
                background: {COLORS['bg_primary']};
                border-top: 1px solid {COLORS['border_light']};
            }}
        """)
        self._label.setStyleSheet(f"color: {COLORS['accent_blue']}; font-size: 12px; font-weight: 600; letter-spacing: 3px;")
        self._title.setStyleSheet(f"color: {COLORS['text_primary']}; font-size: 36px; font-weight: 700;")
        self._subtitle.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 15px;")
        
        for c in [self._vision_card, self._mission_card]:
            c["widget"].setStyleSheet(f"""
                QFrame#vision_card {{
                    background: {COLORS['bg_card']};
                    border: 1px solid {COLORS['border']};
                    border-left: 3px solid {COLORS['accent_blue'] if c == self._vision_card else COLORS['success']};
                    border-radius: 12px;
                }}
            """)
            c["icon_lbl"].setStyleSheet("font-size: 20px; background: transparent; border: none;")
            c["title_lbl"].setStyleSheet(f"color: {COLORS['accent_blue'] if c == self._vision_card else COLORS['success']}; font-size: 20px; font-weight: 600; background: transparent; border: none;")
            c["divider"].setStyleSheet(f"background: {COLORS['accent_blue'] if c == self._vision_card else COLORS['success']}; border: none; margin-top: 12px; margin-bottom: 20px;")
            c["text_label"].setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 15px; background: transparent; border: none;")
