"""presentation/showcase/sections/skills_section.py — Yetenekler bölümü."""

import os
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QGridLayout, QFrame, QSizePolicy
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap

from styles.constants import COLORS
from domain.models.skill import Skill
from config import get_data_path

class SkillsSection(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("skills_section")
        self._build_ui()

    def _build_ui(self) -> None:
        self.setStyleSheet(f"""
            QWidget#skills_section {{
                background: {COLORS['bg_primary']};
                border-top: 1px solid {COLORS['border_light']};
            }}
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(64, 80, 64, 80)
        layout.setSpacing(40)

        # Section header
        header_col = QVBoxLayout()
        header_col.setSpacing(8)

        label = QLabel("// YETENEKLER & BECERİLER")
        label.setStyleSheet(f"""
            color: {COLORS['accent_blue']};
            font-size: 12px;
            font-weight: 600;
            letter-spacing: 3px;
        """)
        header_col.addWidget(label)

        title = QLabel("Yeteneklerim")
        title.setStyleSheet(f"""
            color: {COLORS['text_primary']};
            font-size: 36px;
            font-weight: 700;
        """)
        header_col.addWidget(title)

        subtitle = QLabel("Kullandığım teknolojiler ve yetkinlik seviyelerim")
        subtitle.setStyleSheet(f"""
            color: {COLORS['text_secondary']};
            font-size: 15px;
        """)
        header_col.addWidget(subtitle)

        layout.addLayout(header_col)

        # Kart ızgarası — 3 sütun
        self._grid_widget = QWidget()
        self._grid_widget.setStyleSheet("background: transparent;")
        self._grid = QGridLayout(self._grid_widget)
        self._grid.setSpacing(24)
        self._grid.setContentsMargins(0, 0, 0, 0)
        self._grid.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        layout.addWidget(self._grid_widget)

        self._empty_label = QLabel("Henüz yetenek eklenmemiş.")
        self._empty_label.setAlignment(Qt.AlignCenter)
        self._empty_label.setStyleSheet(f"color: {COLORS['text_muted']}; font-size: 15px;")
        self._empty_label.setVisible(False)
        layout.addWidget(self._empty_label)

    def load_data(self, skills: list[Skill]) -> None:
        while self._grid.count():
            item = self._grid.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        if not skills:
            self._empty_label.setVisible(True)
            self.setVisible(False)
            return

        self.setVisible(True)
        self._empty_label.setVisible(False)
        cols = 3
        for i, skill in enumerate(skills):
            card = self._build_skill_card(skill)
            self._grid.addWidget(card, i // cols, i % cols)
        
        for c in range(cols):
            self._grid.setColumnStretch(c, 1)

    def _build_skill_card(self, skill: Skill) -> QWidget:
        card = QFrame()
        card.setMinimumWidth(280)
        card.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        card.setStyleSheet(f"""
            QFrame {{
                background: {COLORS['bg_card']};
                border: 1px solid {COLORS['border']};
                border-radius: 8px;
            }}
            QFrame:hover {{
                border: 1px solid {COLORS['text_secondary']};
            }}
        """)
        lay = QVBoxLayout(card)
        lay.setContentsMargins(16, 16, 16, 16)
        lay.setSpacing(12)

        # Baslik Satiri
        top_row = QHBoxLayout()
        icon_lbl = QLabel()
        icon_lbl.setFixedSize(48, 48)
        icon_lbl.setStyleSheet("background: transparent; border: none;")
        if skill.icon_path:
            full_path = os.path.join(get_data_path(), skill.icon_path)
            if os.path.exists(full_path):
                pixmap = QPixmap(full_path)
                icon_lbl.setPixmap(pixmap.scaled(48, 48, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        top_row.addWidget(icon_lbl)

        txt_col = QVBoxLayout()
        name_lbl = QLabel(skill.name)
        name_lbl.setStyleSheet(f"color: {COLORS['text_primary']}; font-size: 18px; font-weight: 700; border: none; background: transparent;")
        txt_col.addWidget(name_lbl)
        
        if skill.category:
            cat_lbl = QLabel(skill.category)
            cat_lbl.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 13px; border: none; background: transparent;")
            txt_col.addWidget(cat_lbl)
        
        top_row.addLayout(txt_col)
        top_row.addStretch()
        lay.addLayout(top_row)

        # Progress Bar
        prog_lay = QVBoxLayout()
        prog_lay.setSpacing(4)
        
        perc_row = QHBoxLayout()
        perc_row.addStretch()
        perc_lbl = QLabel(f"%{skill.rating}")
        perc_lbl.setStyleSheet(f"color: {COLORS['accent_blue']}; font-size: 13px; font-weight: bold; border: none; background: transparent;")
        perc_row.addWidget(perc_lbl)
        prog_lay.addLayout(perc_row)

        # Bar cizgisi
        bar_bg = QFrame()
        bar_bg.setFixedHeight(8)
        bar_bg.setObjectName("bar_bg")
        bar_bg.setStyleSheet(f"QFrame#bar_bg {{ background: {COLORS['bg_active']}; border-radius: 4px; border: none; }}")

        bar_fg = QFrame()
        bar_fg.setFixedHeight(8)
        bar_fg.setObjectName("bar_fg")
        bar_fg.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        bar_fg.setStyleSheet(f"QFrame#bar_fg {{ background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 {COLORS['accent_blue']}, stop:1 {COLORS['accent_blue_dark']}); border-radius: 4px; border: none; }}")

        inner_lay = QHBoxLayout(bar_bg)
        inner_lay.setContentsMargins(0, 0, 0, 0)
        inner_lay.setSpacing(0)
        inner_lay.addWidget(bar_fg, stretch=max(skill.rating, 1))
        inner_lay.addStretch(max(100 - skill.rating, 1))
        
        prog_lay.addWidget(bar_bg)
        lay.addLayout(prog_lay)

        return card
