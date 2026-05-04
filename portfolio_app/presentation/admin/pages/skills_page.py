"""presentation/admin/pages/skills_page.py — Yetenekler (Skills) yönetimi."""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QScrollArea, QFrame, QDialog, QLineEdit, QFormLayout, QSpinBox, 
    QGridLayout, QSizePolicy
)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QPixmap

from styles.constants import COLORS, FONTS
from controllers.skill_controller import SkillController
from domain.models.skill import Skill
from presentation.shared.confirm_dialog import confirm
from presentation.shared.toast import show_toast, Toast
from config import get_data_path
import os
from resources.icon_manager import IconManager, Icons

GRID_COLS = 3
CARD_MIN_W = 200
CARD_MIN_H = 100

class SkillsPage(QWidget):
    def __init__(self, controller: SkillController, parent=None):
        super().__init__(parent)
        self._ctrl = controller
        self._skills: list[Skill] = []
        self._build_ui()
        self.refresh()

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ── Üst bar ──
        header = QWidget()
        header.setFixedHeight(60)
        header.setStyleSheet(
            f"background: {COLORS['bg_secondary']};"
            f"border-bottom: 1px solid {COLORS['border']};"
        )
        h_lay = QHBoxLayout(header)
        h_lay.setContentsMargins(24, 0, 24, 0)

        title_lbl = QLabel("Beceriler & Yetenekler")
        title_lbl.setStyleSheet(
            f"color: {COLORS['text_primary']}; font-size: {FONTS['size_lg']}px;"
            f"font-weight: 700; background: transparent; border: none;"
        )
        h_lay.addWidget(title_lbl)
        h_lay.addStretch()

        add_btn = QPushButton(" Yetenek Ekle")
        add_btn.setIcon(IconManager.get(Icons.ADD))
        add_btn.setIconSize(QSize(18, 18))
        add_btn.setCursor(Qt.PointingHandCursor)
        add_btn.setFixedHeight(36)
        add_btn.setStyleSheet(self._primary_btn_style())
        add_btn.clicked.connect(self._open_create_dialog)
        h_lay.addWidget(add_btn)
        root.addWidget(header)

        # ── Scroll area ──
        self._scroll = QScrollArea()
        self._scroll.setWidgetResizable(True)
        self._scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self._scroll.setStyleSheet(f"QScrollArea {{ border: none; background: {COLORS['bg_primary']}; }}")

        self._grid_container = QWidget()
        self._grid_container.setStyleSheet(f"background: {COLORS['bg_primary']};")
        self._grid_layout = QGridLayout(self._grid_container)
        self._grid_layout.setContentsMargins(24, 20, 24, 24)
        self._grid_layout.setSpacing(16)
        self._grid_layout.setAlignment(Qt.AlignTop | Qt.AlignLeft)

        self._scroll.setWidget(self._grid_container)
        root.addWidget(self._scroll)

    def refresh(self) -> None:
        try:
            self._skills = self._ctrl.get_all()
            self._render_grid()
        except Exception as e:
            show_toast(self, f"Yetenekler yüklenemedi: {e}", Toast.ERROR)

    def _render_grid(self) -> None:
        while self._grid_layout.count():
            item = self._grid_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        for i, skill in enumerate(self._skills):
            card = self._build_card(skill)
            row, col = divmod(i, GRID_COLS)
            self._grid_layout.addWidget(card, row, col)

        for c in range(GRID_COLS):
            self._grid_layout.setColumnStretch(c, 1)

    def _build_card(self, skill: Skill) -> QFrame:
        card = QFrame()
        card.setMinimumSize(CARD_MIN_W, CARD_MIN_H)
        card.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        card.setStyleSheet(f"""
            QFrame {{
                background: {COLORS['bg_card']};
                border: 1px solid {COLORS['border']};
                border-radius: 12px;
            }}
            QFrame:hover {{ border: 1px solid {COLORS['accent_blue']}; }}
        """)

        layout = QVBoxLayout(card)
        layout.setContentsMargins(16, 16, 16, 16)
        
        # Üst Kısım: İkon ve İsim
        top_row = QHBoxLayout()
        icon_lbl = QLabel()
        icon_lbl.setFixedSize(32, 32)
        icon_lbl.setStyleSheet("background: transparent; border: none;")
        if skill.icon_path:
            full_path = os.path.join(get_data_path(), skill.icon_path)
            if os.path.exists(full_path):
                pixmap = QPixmap(full_path)
                icon_lbl.setPixmap(pixmap.scaled(32, 32, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        top_row.addWidget(icon_lbl)
        
        title_lbl = QLabel(skill.name)
        title_lbl.setStyleSheet(f"color: {COLORS['text_primary']}; font-size: 15px; font-weight: 700; border: none;")
        top_row.addWidget(title_lbl)
        top_row.addStretch()
        layout.addLayout(top_row)

        # İlerleme (Rating)
        rating_lbl = QLabel(f"Seviye: %{skill.rating}")
        rating_lbl.setStyleSheet(f"color: {COLORS['text_muted']}; font-size: 12px; border: none;")
        layout.addWidget(rating_lbl)

        # Butonlar
        action_row = QHBoxLayout()
        action_row.addStretch()

        edit_btn = QPushButton(" Düzenle")
        edit_btn.setIcon(IconManager.get(Icons.EDIT))
        edit_btn.setIconSize(QSize(14, 14))
        edit_btn.setCursor(Qt.PointingHandCursor)
        edit_btn.setStyleSheet(self._ghost_btn_style())
        edit_btn.clicked.connect(lambda: self._open_edit_dialog(skill))
        action_row.addWidget(edit_btn)

        del_btn = QPushButton(" Sil")
        del_btn.setIcon(IconManager.get(Icons.DELETE))
        del_btn.setIconSize(QSize(14, 14))
        del_btn.setCursor(Qt.PointingHandCursor)
        del_btn.setStyleSheet(self._danger_btn_style())
        del_btn.clicked.connect(lambda: self._delete(skill))
        action_row.addWidget(del_btn)

        layout.addLayout(action_row)
        return card

    def _open_create_dialog(self) -> None:
        dlg = SkillDialog(self)
        if dlg.exec() == QDialog.Accepted:
            data = dlg.get_data()
            try:
                self._ctrl.create(data["name"], data["category"], data["rating"])
                self.refresh()
                show_toast(self, "Yetenek eklendi", Toast.SUCCESS)
            except Exception as e:
                show_toast(self, f"Hata: {e}", Toast.ERROR)

    def _open_edit_dialog(self, skill: Skill) -> None:
        dlg = SkillDialog(self, skill)
        if dlg.exec() == QDialog.Accepted:
            data = dlg.get_data()
            skill.name = data["name"]
            skill.category = data["category"]
            skill.rating = data["rating"]
            try:
                self._ctrl.update(skill)
                self.refresh()
                show_toast(self, "Yetenek güncellendi", Toast.SUCCESS)
            except Exception as e:
                show_toast(self, f"Hata: {e}", Toast.ERROR)

    def _delete(self, skill: Skill) -> None:
        if confirm(self, f'"{skill.name}" silinecek, emin misiniz?', danger=True):
            try:
                self._ctrl.delete(skill.id)
                self.refresh()
                show_toast(self, "Yetenek silindi", Toast.SUCCESS)
            except Exception as e:
                show_toast(self, f"Hata: {e}", Toast.ERROR)

    @staticmethod
    def _primary_btn_style() -> str:
        return f"""
            QPushButton {{
                background: {COLORS['accent_blue']}; color: #fff; border: none;
                border-radius: 8px; font-size: 13px; font-weight: 600; padding: 0 16px;
            }}
            QPushButton:hover {{ background: {COLORS['accent_blue_dark']}; }}
        """

    @staticmethod
    def _ghost_btn_style() -> str:
        return f"""
            QPushButton {{
                background: transparent; color: {COLORS['text_secondary']};
                border: 1px solid {COLORS['border']}; border-radius: 6px; padding: 4px 8px; font-size: 11px;
            }}
            QPushButton:hover {{ background: {COLORS['bg_hover']}; color: {COLORS['text_primary']}; }}
        """

    @staticmethod
    def _danger_btn_style() -> str:
        return f"""
            QPushButton {{
                background: transparent; color: {COLORS['error']};
                border: 1px solid rgba(239,68,68,0.4); border-radius: 6px; padding: 4px 8px; font-size: 11px;
            }}
            QPushButton:hover {{ background: rgba(239,68,68,0.1); border-color: {COLORS['error']}; }}
        """

class SkillDialog(QDialog):
    def __init__(self, parent=None, skill: Skill = None):
        super().__init__(parent)
        self._skill = skill
        self.setWindowTitle("Yetenek Ekle" if not skill else "Yetenek Düzenle")
        self.setMinimumWidth(350)
        self.setModal(True)
        self._build_ui()
        if skill:
            self._populate(skill)

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        self.setStyleSheet(f"""
            QDialog {{ background: {COLORS['bg_secondary']}; }}
            QLabel {{ color: {COLORS['text_secondary']}; }}
            QLineEdit, QSpinBox {{
                background: {COLORS['bg_input']}; color: {COLORS['text_primary']};
                border: 1px solid {COLORS['border']}; border-radius: 6px; padding: 6px;
            }}
        """)
        
        form = QFormLayout()
        
        self._name_input = QLineEdit()
        self._name_input.setPlaceholderText("Örn: Python")
        form.addRow("Yeteneğin Adı:", self._name_input)
        
        self._category_input = QLineEdit()
        self._category_input.setPlaceholderText("Örn: Programlama Dilleri")
        form.addRow("Kategori:", self._category_input)

        self._rating_input = QSpinBox()
        self._rating_input.setRange(0, 100)
        self._rating_input.setValue(50)
        self._rating_input.setSingleStep(5)
        self._rating_input.setSuffix(" %")
        form.addRow("Derece:", self._rating_input)
        
        layout.addLayout(form)

        btn_row = QHBoxLayout()
        btn_row.addStretch()
        save_btn = QPushButton(" Kaydet")
        save_btn.setIcon(IconManager.get(Icons.CHECK))
        save_btn.setIconSize(QSize(16, 16))
        save_btn.clicked.connect(self.accept)
        save_btn.setStyleSheet(f"background: {COLORS['accent_blue']}; color: white; padding: 6px 12px; border-radius: 6px;")
        btn_row.addWidget(save_btn)
        layout.addLayout(btn_row)

    def _populate(self, skill: Skill) -> None:
        self._name_input.setText(skill.name)
        self._category_input.setText(skill.category)
        self._rating_input.setValue(skill.rating)

    def get_data(self) -> dict:
        return {
            "name": self._name_input.text(),
            "category": self._category_input.text(),
            "rating": self._rating_input.value()
        }
