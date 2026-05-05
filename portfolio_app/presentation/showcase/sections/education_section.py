"""presentation/showcase/sections/education_section.py"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QFrame
from PySide6.QtCore import Qt

from styles.constants import COLORS
from domain.models.education import Education


class EducationSection(QWidget):
    def __init__(self, educations: list[Education] = None, parent=None):
        super().__init__(parent)
        self.setObjectName("education_section")
        self._educations = educations or []
        self.setStyleSheet(f"""
            QWidget#education_section {{
                background: {COLORS['bg_primary']};
                border-top: 1px solid {COLORS['border_light']};
            }}
        """)
        
        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(64, 80, 64, 80)
        self._layout.setSpacing(40)
        self.load_data(self._educations)

    def load_data(self, educations: list[Education]) -> None:
        self._educations = educations
        
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

        label = QLabel("// EĞİTİM GEÇMİŞİ")
        label.setStyleSheet(f"""
            color: {COLORS['accent_blue']};
            font-size: 12px;
            font-weight: 600;
            letter-spacing: 3px;
        """)
        header_col.addWidget(label)

        title = QLabel("Eğitim Geçmişi")
        title.setStyleSheet(f"""
            color: {COLORS['text_primary']};
            font-size: 36px;
            font-weight: 700;
        """)
        header_col.addWidget(title)
        
        subtitle = QLabel("Akademik eğitimim ve derecelerim")
        subtitle.setStyleSheet(f"""
            color: {COLORS['text_secondary']};
            font-size: 15px;
        """)
        header_col.addWidget(subtitle)
        
        self._layout.addLayout(header_col)

        if not self._educations:
            empty = QLabel("Henüz eğitim eklenmemiş.")
            empty.setStyleSheet(f"color: {COLORS['text_muted']};")
            self._layout.addWidget(empty)
            return

        for edu in self._educations:
            card = self._create_card(edu)
            self._layout.addWidget(card)

    def _create_card(self, edu: Education) -> QFrame:
        card = QFrame()
        card.setObjectName("edu_card")
        card.setStyleSheet(f"""
            QFrame#edu_card {{
                background: {COLORS['bg_card']};
                border: 1px solid {COLORS['border']};
                border-radius: 12px;
                padding: 20px;
            }}
            QFrame#edu_card:hover {{
                border-color: {COLORS['accent_blue']};
            }}
        """)
        c_layout = QVBoxLayout(card)
        c_layout.setContentsMargins(20, 20, 20, 20)
        c_layout.setSpacing(8)

        inst = QLabel(edu.institution)
        inst.setStyleSheet(f"font-size: 18px; font-weight: bold; color: {COLORS['text_primary']};")
        c_layout.addWidget(inst)

        deg_field = edu.degree
        if edu.field:
            deg_field += f", {edu.field}"
            
        date_str = edu.start_date or ""
        if edu.end_date:
            date_str += f" — {edu.end_date}"
            
        if date_str:
            deg_field += f" | {date_str}"

        df_lbl = QLabel(deg_field)
        df_lbl.setStyleSheet(f"font-size: 14px; color: {COLORS['accent_blue']};")
        c_layout.addWidget(df_lbl)

        desc = edu.description or ""
        if desc:
            desc_lbl = QLabel(desc)
            desc_lbl.setWordWrap(True)
            desc_lbl.setStyleSheet(f"font-size: 14px; color: {COLORS['text_secondary']}; margin-top: 8px;")
            c_layout.addWidget(desc_lbl)

        return card
