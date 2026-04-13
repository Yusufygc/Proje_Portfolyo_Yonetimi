"""presentation/showcase/sections/vision_section.py — Vizyon & Misyon bölümü."""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame
)
from PySide6.QtCore import Qt

from domain.models.personal_info import PersonalInfo


class VisionSection(QWidget):
    """Vizyon ve Misyon — iki sütun kartlar."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("vision_section")
        self._build_ui()

    def _build_ui(self) -> None:
        self.setStyleSheet("""
            QWidget#vision_section {
                background: #0D1117;
                border-top: 1px solid #21262D;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(64, 80, 64, 80)
        layout.setSpacing(40)

        # Section header
        header_col = QVBoxLayout()
        header_col.setSpacing(8)

        label = QLabel("// VİZYON & MİSYON")
        label.setStyleSheet("""
            color: #2F81F7;
            font-size: 12px;
            font-weight: 600;
            letter-spacing: 3px;
        """)
        header_col.addWidget(label)

        title = QLabel("Vizyon & Misyon")
        title.setStyleSheet("""
            color: #E6EDF3;
            font-size: 36px;
            font-weight: 700;
        """)
        header_col.addWidget(title)

        subtitle = QLabel("Hedeflerim ve yazılım geliştirme felsefem")
        subtitle.setStyleSheet("""
            color: #8B949E;
            font-size: 15px;
        """)
        header_col.addWidget(subtitle)

        layout.addLayout(header_col)

        # İki sütun kartlar
        cards_row = QHBoxLayout()
        cards_row.setSpacing(20)

        self._vision_card = self._make_card(
            icon="🎯",
            label="Vizyonum",
            title_color="#2F81F7",
            border_color="#2F81F7",
            accent_color="#2F81F7",
        )
        self._mission_card = self._make_card(
            icon="⚡",
            label="Misyonum",
            title_color="#3FB950",
            border_color="#3FB950",
            accent_color="#3FB950",
        )
        cards_row.addWidget(self._vision_card["widget"])
        cards_row.addWidget(self._mission_card["widget"])

        layout.addLayout(cards_row)

    def _make_card(self, icon: str, label: str, title_color: str,
                   border_color: str, accent_color: str) -> dict:
        frame = QFrame()
        frame.setObjectName("vision_card")
        frame.setStyleSheet(f"""
            QFrame#vision_card {{
                background: #161B22;
                border: 1px solid #30363D;
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
        text_lbl.setStyleSheet("""
            color: #8B949E;
            font-size: 15px;
            background: transparent;
            border: none;
        """)
        col.addWidget(text_lbl)
        col.addStretch()

        return {"widget": frame, "text_label": text_lbl}

    def load_data(self, info: PersonalInfo) -> None:
        self._vision_card["text_label"].setText(info.vision_text or "")
        self._mission_card["text_label"].setText(info.mission_text or "")
