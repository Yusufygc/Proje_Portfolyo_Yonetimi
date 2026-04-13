"""presentation/admin/pages/resources_page.py — Kaynak yönetimi (grid kart görünümü)."""

import webbrowser

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QScrollArea, QFrame, QDialog, QLineEdit, QTextEdit,
    QFormLayout, QComboBox, QGridLayout, QSizePolicy
)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QFont, QCursor

from styles.constants import COLORS, FONTS, SPACING
from controllers.resource_controller import ResourceController
from domain.models.resource import Resource
from domain.enums.resource_type import ResourceType, ResourceStatus
from presentation.shared.confirm_dialog import confirm
from presentation.shared.toast import show_toast, Toast


# Tür → (renk, emoji)
TYPE_META: dict[ResourceType, tuple[str, str]] = {
    ResourceType.KURS:  (COLORS["accent_blue"], "📚"),
    ResourceType.VIDEO: ("#FF6B6B",             "🎬"),
    ResourceType.REPO:  (COLORS["success"],     "🗂"),
    ResourceType.NOT:   (COLORS["warning"],     "📝"),
    ResourceType.PLAN:  (COLORS["accent_silver"],"🗺"),
}

GRID_COLS = 3
CARD_MIN_W = 280
CARD_MIN_H = 170


class ResourcesPage(QWidget):
    """Admin kaynak yönetim sayfası — grid kart görünümü."""

    def __init__(self, controller: ResourceController, parent=None):
        super().__init__(parent)
        self._ctrl = controller
        self._filter: ResourceType | None = None   # None = tümü
        self._resources: list[Resource] = []
        self._ctrl.resources_changed.connect(self.refresh)
        self._ctrl.error_occurred.connect(lambda msg: show_toast(self, msg, Toast.ERROR))
        self._build_ui()
        self.refresh()

    # ── UI inşası ───────────────────────────────────────────────────────────

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ── Üst bar ─────────────────────────────────────────────────────────
        header = QWidget()
        header.setFixedHeight(60)
        header.setStyleSheet(
            f"background: {COLORS['bg_secondary']};"
            f"border-bottom: 1px solid {COLORS['border']};"
        )
        h_lay = QHBoxLayout(header)
        h_lay.setContentsMargins(24, 0, 24, 0)

        title_lbl = QLabel("Kaynaklar")
        title_lbl.setStyleSheet(
            f"color: {COLORS['text_primary']};"
            f"font-size: {FONTS['size_lg']}px;"
            f"font-weight: 700;"
        )
        h_lay.addWidget(title_lbl)
        h_lay.addStretch()

        add_btn = QPushButton("＋  Kaynak Ekle")
        add_btn.setCursor(Qt.PointingHandCursor)
        add_btn.setFixedHeight(36)
        add_btn.setStyleSheet(self._primary_btn_style())
        add_btn.clicked.connect(self._open_create_dialog)
        h_lay.addWidget(add_btn)
        root.addWidget(header)

        # ── Filter + stats bar ──────────────────────────────────────────────
        filter_bar = QWidget()
        filter_bar.setFixedHeight(52)
        filter_bar.setStyleSheet(
            f"background: {COLORS['bg_secondary']};"
            f"border-bottom: 1px solid {COLORS['border']};"
        )
        f_lay = QHBoxLayout(filter_bar)
        f_lay.setContentsMargins(24, 0, 24, 0)
        f_lay.setSpacing(8)

        self._filter_btns: dict[str | None, QPushButton] = {}

        filters = [
            (None,               "Tümü"),
            (ResourceType.KURS,  "📚  Kurs"),
            (ResourceType.VIDEO, "🎬  Video"),
            (ResourceType.REPO,  "🗂  Repo"),
            (ResourceType.NOT,   "📝  Not"),
            (ResourceType.PLAN,  "🗺  Plan"),
        ]
        for rtype, label in filters:
            btn = QPushButton(label)
            btn.setCursor(Qt.PointingHandCursor)
            btn.setFixedHeight(30)
            btn.setCheckable(True)
            btn.setChecked(rtype is None)
            btn.setStyleSheet(self._filter_btn_style(rtype is None))
            btn.clicked.connect(lambda checked, t=rtype: self._set_filter(t))
            self._filter_btns[rtype] = btn
            f_lay.addWidget(btn)

        f_lay.addStretch()

        # Stats label
        self._stats_lbl = QLabel("")
        self._stats_lbl.setStyleSheet(
            f"color: {COLORS['text_muted']}; font-size: 12px;"
        )
        f_lay.addWidget(self._stats_lbl)

        root.addWidget(filter_bar)

        # ── Grid scroll area ─────────────────────────────────────────────────
        self._scroll = QScrollArea()
        self._scroll.setWidgetResizable(True)
        self._scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self._scroll.setStyleSheet(
            f"QScrollArea {{ border: none; background: {COLORS['bg_primary']}; }}"
        )

        self._grid_container = QWidget()
        self._grid_container.setStyleSheet(f"background: {COLORS['bg_primary']};")
        self._grid_layout = QGridLayout(self._grid_container)
        self._grid_layout.setContentsMargins(24, 20, 24, 24)
        self._grid_layout.setSpacing(16)
        self._grid_layout.setAlignment(Qt.AlignTop | Qt.AlignLeft)

        self._scroll.setWidget(self._grid_container)
        root.addWidget(self._scroll)

    # ── Filtre ──────────────────────────────────────────────────────────────

    def _set_filter(self, rtype: ResourceType | None) -> None:
        self._filter = rtype
        for t, btn in self._filter_btns.items():
            active = (t == rtype)
            btn.setChecked(active)
            btn.setStyleSheet(self._filter_btn_style(active))
        self._render_grid()

    # ── Veri ────────────────────────────────────────────────────────────────

    def refresh(self) -> None:
        self._resources = self._ctrl.get_all()
        self._update_stats()
        self._render_grid()

    def _update_stats(self) -> None:
        total = len(self._resources)
        self._stats_lbl.setText(f"{total} kaynak")

    def _render_grid(self) -> None:
        # Eski kartları temizle
        while self._grid_layout.count():
            item = self._grid_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        filtered = (
            self._resources if self._filter is None
            else [r for r in self._resources if r.type == self._filter]
        )

        if not filtered:
            empty_w = QWidget()
            empty_lay = QVBoxLayout(empty_w)
            empty_lay.setAlignment(Qt.AlignCenter)

            icon = QLabel("🔍")
            icon.setAlignment(Qt.AlignCenter)
            icon.setStyleSheet("font-size: 40px; background: transparent;")
            empty_lay.addWidget(icon)

            msg = QLabel("Bu filtrede kayıt yok.")
            msg.setAlignment(Qt.AlignCenter)
            msg.setStyleSheet(
                f"color: {COLORS['text_muted']}; font-size: 14px; background: transparent;"
            )
            empty_lay.addWidget(msg)
            self._grid_layout.addWidget(empty_w, 0, 0, 1, GRID_COLS)
            return

        for i, res in enumerate(filtered):
            card = self._build_card(res)
            row, col = divmod(i, GRID_COLS)
            self._grid_layout.addWidget(card, row, col)

        # Sütunları eşit genişlikte tut
        for c in range(GRID_COLS):
            self._grid_layout.setColumnStretch(c, 1)

    # ── Kart ────────────────────────────────────────────────────────────────

    def _build_card(self, res: Resource) -> QFrame:
        color, emoji = TYPE_META.get(res.type, (COLORS["accent_silver"], "📄"))

        card = QFrame()
        card.setMinimumSize(CARD_MIN_W, CARD_MIN_H)
        card.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        card.setStyleSheet(f"""
            QFrame {{
                background: {COLORS['bg_card']};
                border: 1px solid {COLORS['border']};
                border-radius: 12px;
            }}
            QFrame:hover {{
                border: 1px solid {color};
            }}
        """)

        outer = QVBoxLayout(card)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        # Renkli üst şerit
        top_bar = QWidget()
        top_bar.setFixedHeight(4)
        top_bar.setStyleSheet(
            f"background: {color};"
            f"border-radius: 12px 12px 0 0;"
        )
        outer.addWidget(top_bar)

        # İçerik
        body = QWidget()
        body.setStyleSheet("background: transparent;")
        body_lay = QVBoxLayout(body)
        body_lay.setContentsMargins(16, 12, 16, 14)
        body_lay.setSpacing(8)

        # Tür badge + durum pill
        badge_row = QHBoxLayout()
        badge_row.setSpacing(8)

        type_badge = QLabel(f"{emoji}  {res.type.label()}")
        type_badge.setFixedHeight(22)
        type_badge.setStyleSheet(f"""
            QLabel {{
                background: rgba{self._hex_to_rgba(color, 0.15)};
                color: {color};
                font-size: 11px;
                font-weight: 600;
                border-radius: 11px;
                padding: 0 10px;
            }}
        """)
        badge_row.addWidget(type_badge)
        badge_row.addStretch()

        status_color, status_text = self._status_meta(res.status)
        status_pill = QLabel(f"● {status_text}")
        status_pill.setStyleSheet(
            f"color: {status_color}; font-size: 11px; font-weight: 500;"
        )
        badge_row.addWidget(status_pill)
        body_lay.addLayout(badge_row)

        # Başlık
        title_lbl = QLabel(res.title)
        title_lbl.setStyleSheet(
            f"color: {COLORS['text_primary']};"
            f"font-size: 15px;"
            f"font-weight: 700;"
        )
        title_lbl.setWordWrap(True)
        body_lay.addWidget(title_lbl)

        # Notlar önizlemesi
        if res.notes and res.notes.strip():
            preview = res.notes.strip().replace("\n", " ")
            if len(preview) > 90:
                preview = preview[:90] + "…"
            notes_lbl = QLabel(preview)
            notes_lbl.setStyleSheet(
                f"color: {COLORS['text_secondary']}; font-size: 12px;"
            )
            notes_lbl.setWordWrap(True)
            body_lay.addWidget(notes_lbl)

        body_lay.addStretch()

        # Ayraç çizgisi
        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setStyleSheet(f"background: {COLORS['border']}; margin: 0 0;")
        sep.setFixedHeight(1)
        body_lay.addWidget(sep)

        # Eylem butonları
        action_row = QHBoxLayout()
        action_row.setSpacing(6)
        action_row.setContentsMargins(0, 6, 0, 0)

        if res.url and res.url.strip():
            open_btn = QPushButton("↗  Aç")
            open_btn.setCursor(Qt.PointingHandCursor)
            open_btn.setFixedHeight(28)
            open_btn.setStyleSheet(self._action_btn_style(color))
            url = res.url
            open_btn.clicked.connect(lambda: webbrowser.open(url))
            action_row.addWidget(open_btn)

        action_row.addStretch()

        edit_btn = QPushButton("Düzenle")
        edit_btn.setCursor(Qt.PointingHandCursor)
        edit_btn.setFixedHeight(28)
        edit_btn.setStyleSheet(self._ghost_btn_style())
        edit_btn.clicked.connect(lambda: self._open_edit_dialog(res))
        action_row.addWidget(edit_btn)

        del_btn = QPushButton("Sil")
        del_btn.setCursor(Qt.PointingHandCursor)
        del_btn.setFixedHeight(28)
        del_btn.setStyleSheet(self._danger_btn_style())
        del_btn.clicked.connect(lambda: self._delete(res))
        action_row.addWidget(del_btn)

        body_lay.addLayout(action_row)

        outer.addWidget(body)
        return card

    # ── Stil yardımcıları ────────────────────────────────────────────────────

    @staticmethod
    def _hex_to_rgba(hex_color: str, alpha: float) -> str:
        """'#RRGGBB' → '(R, G, B, A)' string (QSS rgba formatı için)."""
        h = hex_color.lstrip("#")
        if len(h) == 6:
            r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
            return f"({r}, {g}, {b}, {alpha})"
        return f"(80, 130, 200, {alpha})"

    @staticmethod
    def _status_meta(status: ResourceStatus) -> tuple[str, str]:
        return {
            ResourceStatus.PLANLI:       (COLORS["text_muted"],  "Planlı"),
            ResourceStatus.DEVAM_EDIYOR: (COLORS["accent_blue"], "Devam Ediyor"),
            ResourceStatus.TAMAMLANDI:   (COLORS["success"],     "Tamamlandı"),
        }.get(status, (COLORS["text_muted"], status.label()))

    @staticmethod
    def _primary_btn_style() -> str:
        return f"""
            QPushButton {{
                background: {COLORS['accent_blue']};
                color: #fff;
                border: none;
                border-radius: 8px;
                font-size: 13px;
                font-weight: 600;
                padding: 0 16px;
            }}
            QPushButton:hover {{ background: {COLORS['accent_blue_dark']}; }}
        """

    @staticmethod
    def _filter_btn_style(active: bool) -> str:
        if active:
            return f"""
                QPushButton {{
                    background: rgba(47, 129, 247, 0.15);
                    color: {COLORS['accent_blue']};
                    border: 1px solid rgba(47, 129, 247, 0.4);
                    border-radius: 15px;
                    font-size: 12px;
                    font-weight: 600;
                    padding: 0 14px;
                }}
            """
        return f"""
            QPushButton {{
                background: transparent;
                color: {COLORS['text_secondary']};
                border: 1px solid {COLORS['border']};
                border-radius: 15px;
                font-size: 12px;
                padding: 0 14px;
            }}
            QPushButton:hover {{
                background: {COLORS['bg_hover']};
                color: {COLORS['text_primary']};
            }}
        """

    @staticmethod
    def _action_btn_style(color: str) -> str:
        return f"""
            QPushButton {{
                background: transparent;
                color: {color};
                border: 1px solid {color};
                border-radius: 6px;
                font-size: 11px;
                font-weight: 600;
                padding: 0 10px;
            }}
            QPushButton:hover {{ background: rgba(80,130,200,0.1); }}
        """

    @staticmethod
    def _ghost_btn_style() -> str:
        return f"""
            QPushButton {{
                background: transparent;
                color: {COLORS['text_secondary']};
                border: 1px solid {COLORS['border']};
                border-radius: 6px;
                font-size: 11px;
                padding: 0 10px;
            }}
            QPushButton:hover {{
                background: {COLORS['bg_hover']};
                color: {COLORS['text_primary']};
            }}
        """

    @staticmethod
    def _danger_btn_style() -> str:
        return f"""
            QPushButton {{
                background: transparent;
                color: {COLORS['error']};
                border: 1px solid rgba(239,68,68,0.4);
                border-radius: 6px;
                font-size: 11px;
                padding: 0 10px;
            }}
            QPushButton:hover {{
                background: rgba(239,68,68,0.1);
                border-color: {COLORS['error']};
            }}
        """

    # ── Eylemler ────────────────────────────────────────────────────────────

    def _open_create_dialog(self) -> None:
        dlg = ResourceDialog(self)
        if dlg.exec() == QDialog.Accepted:
            self._ctrl.create(dlg.get_data())

    def _open_edit_dialog(self, res: Resource) -> None:
        dlg = ResourceDialog(self, res)
        if dlg.exec() == QDialog.Accepted:
            self._ctrl.update(res.id, dlg.get_data())

    def _delete(self, res: Resource) -> None:
        if confirm(self, f'"{res.title}" kaynağını silmek istediğinizden emin misiniz?', danger=True):
            self._ctrl.delete(res.id)


# ── Kaynak Dialog ─────────────────────────────────────────────────────────────

class ResourceDialog(QDialog):
    def __init__(self, parent=None, resource: Resource = None):
        super().__init__(parent)
        self._resource = resource
        self.setWindowTitle("Kaynak Ekle" if not resource else "Kaynak Düzenle")
        self.setMinimumWidth(480)
        self.setModal(True)
        self._build_ui()
        if resource:
            self._populate(resource)

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 28, 28, 24)
        layout.setSpacing(20)

        self.setStyleSheet(f"""
            QDialog {{ background: {COLORS['bg_secondary']}; }}
            QLabel {{ color: {COLORS['text_secondary']}; font-size: 13px; }}
            QLineEdit, QTextEdit, QComboBox {{
                background: {COLORS['bg_input']};
                color: {COLORS['text_primary']};
                border: 1px solid {COLORS['border']};
                border-radius: 8px;
                padding: 8px 12px;
                font-size: 13px;
            }}
            QLineEdit:focus, QTextEdit:focus, QComboBox:focus {{
                border-color: {COLORS['border_focus']};
            }}
        """)

        # Dialog başlık
        dlg_title = QLabel("Kaynak Ekle" if not self._resource else "Kaynağı Düzenle")
        dlg_title.setStyleSheet(
            f"color: {COLORS['text_primary']}; font-size: 17px; font-weight: 700;"
        )
        layout.addWidget(dlg_title)

        form = QFormLayout()
        form.setSpacing(14)
        form.setLabelAlignment(Qt.AlignRight | Qt.AlignVCenter)
        form.setFieldGrowthPolicy(QFormLayout.ExpandingFieldsGrow)

        self._type_combo = QComboBox()
        for t in ResourceType:
            self._type_combo.addItem(t.label(), t.value)
        form.addRow("Tür", self._type_combo)

        self._title_input = QLineEdit()
        self._title_input.setPlaceholderText("Kaynak başlığı")
        form.addRow("Başlık *", self._title_input)

        self._url_input = QLineEdit()
        self._url_input.setPlaceholderText("https://...")
        form.addRow("URL", self._url_input)

        self._notes_input = QTextEdit()
        self._notes_input.setPlaceholderText("Notlar, açıklamalar, önemli linkler…")
        self._notes_input.setFixedHeight(110)
        form.addRow("Notlar", self._notes_input)

        self._status_combo = QComboBox()
        for s in ResourceStatus:
            self._status_combo.addItem(s.label(), s.value)
        form.addRow("Durum", self._status_combo)

        layout.addLayout(form)

        # Butonlar
        btn_row = QHBoxLayout()
        btn_row.addStretch()

        cancel = QPushButton("İptal")
        cancel.setFixedHeight(36)
        cancel.setCursor(Qt.PointingHandCursor)
        cancel.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                color: {COLORS['text_secondary']};
                border: 1px solid {COLORS['border']};
                border-radius: 8px;
                font-size: 13px;
                padding: 0 20px;
            }}
            QPushButton:hover {{ background: {COLORS['bg_hover']}; }}
        """)
        cancel.clicked.connect(self.reject)
        btn_row.addWidget(cancel)

        save = QPushButton("Kaydet")
        save.setFixedHeight(36)
        save.setCursor(Qt.PointingHandCursor)
        save.setStyleSheet(f"""
            QPushButton {{
                background: {COLORS['accent_blue']};
                color: #fff;
                border: none;
                border-radius: 8px;
                font-size: 13px;
                font-weight: 600;
                padding: 0 24px;
            }}
            QPushButton:hover {{ background: {COLORS['accent_blue_dark']}; }}
        """)
        save.clicked.connect(self.accept)
        btn_row.addWidget(save)

        layout.addLayout(btn_row)

    def _populate(self, res: Resource) -> None:
        idx = self._type_combo.findData(res.type.value)
        if idx >= 0:
            self._type_combo.setCurrentIndex(idx)
        self._title_input.setText(res.title)
        self._url_input.setText(res.url or "")
        self._notes_input.setPlainText(res.notes or "")
        idx = self._status_combo.findData(res.status.value)
        if idx >= 0:
            self._status_combo.setCurrentIndex(idx)

    def get_data(self) -> dict:
        return {
            "type":   self._type_combo.currentData(),
            "title":  self._title_input.text(),
            "url":    self._url_input.text(),
            "notes":  self._notes_input.toPlainText(),
            "status": self._status_combo.currentData(),
        }
