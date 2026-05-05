"""presentation/showcase/sections/experience_section.py"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QFrame
from PySide6.QtCore import Qt

from styles.constants import COLORS
from domain.models.experience import Experience


class ExperienceSection(QWidget):
    def __init__(self, experiences: list[Experience] = None, parent=None):
        super().__init__(parent)
        self.setObjectName("experience_section")
        self._experiences = experiences or []
        self.setStyleSheet(f"""
            QWidget#experience_section {{
                background: {COLORS['bg_secondary']};
                border-top: 1px solid {COLORS['border_light']};
            }}
        """)
        
        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(64, 80, 64, 80)
        self._layout.setSpacing(40)
        self.load_data(self._experiences)

    def load_data(self, experiences: list[Experience]) -> None:
        self._experiences = experiences
        
        while self._layout.count():
            item = self._layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                # delete layout contents
                while item.layout().count():
                    sub = item.layout().takeAt(0)
                    if sub.widget(): sub.widget().deleteLater()
                item.layout().deleteLater()

        header_col = QVBoxLayout()
        header_col.setSpacing(8)

        label = QLabel("// İŞ DENEYİMİ")
        label.setStyleSheet(f"""
            color: {COLORS['accent_blue']};
            font-size: 12px;
            font-weight: 600;
            letter-spacing: 3px;
        """)
        header_col.addWidget(label)

        title = QLabel("İş Deneyimi")
        title.setStyleSheet(f"""
            color: {COLORS['text_primary']};
            font-size: 36px;
            font-weight: 700;
        """)
        header_col.addWidget(title)
        
        subtitle = QLabel("Kariyer yolculuğum ve çalıştığım projeler")
        subtitle.setStyleSheet(f"""
            color: {COLORS['text_secondary']};
            font-size: 15px;
        """)
        header_col.addWidget(subtitle)
        
        self._layout.addLayout(header_col)

        if not self._experiences:
            empty = QLabel("Henüz deneyim eklenmemiş.")
            empty.setStyleSheet(f"color: {COLORS['text_muted']};")
            self._layout.addWidget(empty)
            return

        for exp in sorted(self._experiences, key=lambda x: x.start_date or "", reverse=True):
            card = self._create_card(exp)
            self._layout.addWidget(card)

    def _create_card(self, exp: Experience) -> QFrame:
        card = QFrame()
        card.setObjectName("exp_card")
        card.setStyleSheet(f"""
            QFrame#exp_card {{
                background: {COLORS['bg_card']};
                border: 1px solid {COLORS['border']};
                border-radius: 12px;
                padding: 20px;
            }}
            QFrame#exp_card:hover {{
                border-color: {COLORS['accent_blue']};
            }}
        """)
        c_layout = QVBoxLayout(card)
        c_layout.setContentsMargins(20, 20, 20, 20)
        c_layout.setSpacing(8)

        company = QLabel(exp.company)
        company.setStyleSheet(f"font-size: 18px; font-weight: bold; color: {COLORS['text_primary']};")
        c_layout.addWidget(company)

        pos_date = f"{exp.position}"
        date_str = exp.start_date or ""
        if exp.is_current:
            date_str += " — Devam ediyor"
        elif exp.end_date:
            date_str += f" — {exp.end_date}"
            
        if date_str:
            pos_date += f" | {date_str}"
            
        pd_lbl = QLabel(pos_date)
        pd_lbl.setStyleSheet(f"font-size: 14px; color: {COLORS['accent_blue']};")
        c_layout.addWidget(pd_lbl)

        desc = exp.description or ""
        if desc:
            desc_lbl = QLabel(desc)
            desc_lbl.setWordWrap(True)
            desc_lbl.setStyleSheet(f"font-size: 14px; color: {COLORS['text_secondary']}; margin-top: 8px;")
            c_layout.addWidget(desc_lbl)

        return card
