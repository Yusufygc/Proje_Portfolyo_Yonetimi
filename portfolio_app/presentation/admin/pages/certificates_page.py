"""presentation/admin/pages/certificates_page.py — Sertifika CRUD."""

import os

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QScrollArea, QFrame, QDialog, QLineEdit, QFormLayout,
    QFileDialog, QSpinBox, QGridLayout, QSizePolicy
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap

from config import get_data_path
from styles.constants import COLORS, FONTS
from controllers.certificate_controller import CertificateController
from domain.models.certificate import Certificate
from presentation.shared.confirm_dialog import confirm
from presentation.shared.toast import show_toast, Toast

GRID_COLUMNS = 3
CARD_WIDTH   = 260
IMG_HEIGHT   = 160


class CertificatesPage(QWidget):
    """Admin sertifika yönetim sayfası — grid görünüm."""

    def __init__(self, controller: CertificateController, parent=None):
        super().__init__(parent)
        self._ctrl = controller
        self._ctrl.certificates_changed.connect(self.refresh)
        self._ctrl.error_occurred.connect(lambda msg: show_toast(self, msg, Toast.ERROR))
        self._build_ui()
        self.refresh()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Üst bar
        header = QWidget()
        header.setStyleSheet(
            f"background: {COLORS['bg_secondary']};"
            f"border-bottom: 1px solid {COLORS['border']};"
        )
        h_layout = QHBoxLayout(header)
        h_layout.setContentsMargins(24, 16, 24, 16)

        title = QLabel("Sertifikalar")
        title.setStyleSheet(
            f"color: {COLORS['text_primary']};"
            f"font-size: {FONTS['size_lg']}px;"
            f"font-weight: 700;"
            f"border: none; background: transparent;"
        )
        h_layout.addWidget(title)
        h_layout.addStretch()

        add_btn = QPushButton("+ Sertifika Ekle")
        add_btn.setCursor(Qt.PointingHandCursor)
        add_btn.clicked.connect(self._open_create_dialog)
        h_layout.addWidget(add_btn)
        layout.addWidget(header)

        # Scroll + Grid
        self._scroll = QScrollArea()
        self._scroll.setWidgetResizable(True)
        self._scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")

        self._container = QWidget()
        self._container.setStyleSheet(f"background: {COLORS['bg_primary']};")

        self._grid_layout = QGridLayout(self._container)
        self._grid_layout.setContentsMargins(24, 24, 24, 24)
        self._grid_layout.setSpacing(16)
        self._grid_layout.setAlignment(Qt.AlignTop | Qt.AlignLeft)

        self._scroll.setWidget(self._container)
        layout.addWidget(self._scroll)

    def refresh(self) -> None:
        # Grid'i temizle
        while self._grid_layout.count():
            item = self._grid_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        certs = self._ctrl.get_all()
        if not certs:
            empty = QLabel("Henüz sertifika eklenmemiş.")
            empty.setStyleSheet(
                f"color: {COLORS['text_muted']}; font-size: 14px; border: none; background: transparent;"
            )
            self._grid_layout.addWidget(empty, 0, 0)
            return

        for i, cert in enumerate(certs):
            row = i // GRID_COLUMNS
            col = i % GRID_COLUMNS
            card = CertAdminCard(cert, self._open_edit_dialog, self._delete)
            self._grid_layout.addWidget(card, row, col)

        # Boş hücreleri stretch ile doldur (son satır boşlukları)
        self._grid_layout.setColumnStretch(GRID_COLUMNS, 1)

    def _open_create_dialog(self) -> None:
        dlg = CertDialog(self)
        if dlg.exec() == QDialog.Accepted:
            self._ctrl.create(dlg.get_data())

    def _open_edit_dialog(self, cert: Certificate) -> None:
        dlg = CertDialog(self, cert)
        if dlg.exec() == QDialog.Accepted:
            self._ctrl.update(cert.id, dlg.get_data())

    def _delete(self, cert: Certificate) -> None:
        if confirm(self, f'"{cert.name}" sertifikasını silmek istediğinizden emin misiniz?', danger=True):
            self._ctrl.delete(cert.id)


class CertAdminCard(QFrame):
    """Admin grid'de gösterilen sertifika kartı."""

    def __init__(self, cert: Certificate, on_edit, on_delete, parent=None):
        super().__init__(parent)
        self._cert = cert
        self._on_edit = on_edit
        self._on_delete = on_delete
        self.setFixedWidth(CARD_WIDTH)
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Minimum)
        self._build_ui()

    def _build_ui(self) -> None:
        self.setObjectName("cert_admin_card")
        self.setStyleSheet(f"""
            QFrame#cert_admin_card {{
                background: {COLORS['bg_card']};
                border: 1px solid {COLORS['border']};
                border-radius: 12px;
            }}
            QFrame#cert_admin_card:hover {{
                border-color: {COLORS['accent_blue']};
            }}
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # ── Görsel alanı ─────────────────────────────────────────────────
        img_frame = QFrame()
        img_frame.setFixedHeight(IMG_HEIGHT)
        img_frame.setStyleSheet(f"""
            QFrame {{
                background: {COLORS['bg_secondary']};
                border-top-left-radius: 12px;
                border-top-right-radius: 12px;
                border-bottom-left-radius: 0px;
                border-bottom-right-radius: 0px;
                border: none;
            }}
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
                Qt.SmoothTransformation
            )
            img_lbl.setPixmap(scaled)
        else:
            # Fallback: büyük emoji / placeholder
            img_lbl.setText("🏆")
            img_lbl.setStyleSheet(
                f"font-size: 56px; background: transparent; border: none;"
                f"color: {COLORS['warning']};"
            )

        img_layout.addWidget(img_lbl)
        layout.addWidget(img_frame)

        # ── Bilgi alanı ──────────────────────────────────────────────────
        info_widget = QWidget()
        info_widget.setStyleSheet("background: transparent; border: none;")
        info_layout = QVBoxLayout(info_widget)
        info_layout.setContentsMargins(14, 12, 14, 4)
        info_layout.setSpacing(4)

        name_lbl = QLabel(self._cert.name)
        name_lbl.setWordWrap(True)
        name_lbl.setStyleSheet(
            f"color: {COLORS['text_primary']};"
            f"font-size: {FONTS['size_base']}px;"
            f"font-weight: 700;"
            f"background: transparent; border: none;"
        )
        info_layout.addWidget(name_lbl)

        if self._cert.issuer:
            issuer_lbl = QLabel(self._cert.issuer)
            issuer_lbl.setStyleSheet(
                f"color: {COLORS['accent_blue']};"
                f"font-size: {FONTS['size_sm']}px;"
                f"background: transparent; border: none;"
            )
            info_layout.addWidget(issuer_lbl)

        if self._cert.date:
            date_lbl = QLabel(self._cert.date)
            date_lbl.setStyleSheet(
                f"color: {COLORS['text_muted']};"
                f"font-size: {FONTS['size_xs']}px;"
                f"background: transparent; border: none;"
            )
            info_layout.addWidget(date_lbl)

        layout.addWidget(info_widget)

        # ── Ayırıcı ──────────────────────────────────────────────────────
        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setStyleSheet(f"color: {COLORS['border']}; border: none; background: {COLORS['border']}; max-height: 1px;")
        sep.setFixedHeight(1)
        layout.addWidget(sep)

        # ── Aksiyon butonları ─────────────────────────────────────────────
        btn_widget = QWidget()
        btn_widget.setStyleSheet("background: transparent; border: none;")
        btn_layout = QHBoxLayout(btn_widget)
        btn_layout.setContentsMargins(10, 8, 10, 10)
        btn_layout.setSpacing(8)

        edit_btn = QPushButton("Düzenle")
        edit_btn.setObjectName("btn_flat")
        edit_btn.setCursor(Qt.PointingHandCursor)
        edit_btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        edit_btn.clicked.connect(lambda: self._on_edit(self._cert))

        del_btn = QPushButton("Sil")
        del_btn.setObjectName("btn_danger")
        del_btn.setCursor(Qt.PointingHandCursor)
        del_btn.setFixedWidth(56)
        del_btn.clicked.connect(lambda: self._on_delete(self._cert))

        btn_layout.addWidget(edit_btn)
        btn_layout.addWidget(del_btn)
        layout.addWidget(btn_widget)

    def _load_pixmap(self):
        """Sertifika görselini yükle; yoksa None döner."""
        if not self._cert.image_path:
            return None
        # image_path data/ altında relatif ya da mutlak olabilir
        if os.path.isabs(self._cert.image_path):
            full_path = self._cert.image_path
        else:
            full_path = os.path.join(get_data_path(), self._cert.image_path)
        if not os.path.exists(full_path):
            return None
        px = QPixmap(full_path)
        return px if not px.isNull() else None


class CertDialog(QDialog):
    def __init__(self, parent=None, cert: Certificate = None):
        super().__init__(parent)
        self._cert = cert
        self._image_source: str | None = None
        self.setWindowTitle("Sertifika Ekle" if not cert else "Sertifika Düzenle")
        self.setMinimumWidth(460)
        self.setModal(True)
        self._build_ui()
        if cert:
            self._populate(cert)

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 20)
        layout.setSpacing(16)
        self.setStyleSheet(f"""
            QDialog {{ background: {COLORS['bg_secondary']}; }}
            QLabel  {{ color: {COLORS['text_secondary']}; background: transparent; border: none; }}
            QLineEdit, QSpinBox {{
                background: {COLORS['bg_input']};
                color: {COLORS['text_primary']};
                border: 1px solid {COLORS['border']};
                border-radius: 6px;
                padding: 6px 10px;
                font-size: 13px;
            }}
            QLineEdit:focus, QSpinBox:focus {{
                border-color: {COLORS['border_focus']};
            }}
        """)

        form = QFormLayout()
        form.setSpacing(12)
        form.setLabelAlignment(Qt.AlignRight)

        self._name_input   = QLineEdit()
        self._issuer_input = QLineEdit()
        self._date_input   = QLineEdit()
        self._date_input.setPlaceholderText("YYYY-MM veya YYYY")
        self._url_input    = QLineEdit()
        self._url_input.setPlaceholderText("https://...")
        self._order_spin   = QSpinBox()
        self._order_spin.setRange(0, 999)

        form.addRow("Ad *",          self._name_input)
        form.addRow("Kurum",         self._issuer_input)
        form.addRow("Tarih",         self._date_input)
        form.addRow("Doğrulama URL", self._url_input)
        form.addRow("Sıralama",      self._order_spin)

        # Görsel seçici
        img_btn = QPushButton("Görsel Seç")
        img_btn.setObjectName("btn_flat")
        img_btn.clicked.connect(self._pick_image)

        self._img_preview = QLabel()
        self._img_preview.setFixedSize(80, 56)
        self._img_preview.setAlignment(Qt.AlignCenter)
        self._img_preview.setStyleSheet(
            f"background: {COLORS['bg_input']}; border: 1px solid {COLORS['border']}; border-radius: 6px;"
        )
        self._img_preview.setText("—")

        self._img_name_lbl = QLabel("Görsel seçilmedi")
        self._img_name_lbl.setStyleSheet(f"color: {COLORS['text_muted']}; font-size: 12px; border: none;")

        img_row = QHBoxLayout()
        img_row.addWidget(img_btn)
        img_row.addWidget(self._img_preview)
        img_row.addWidget(self._img_name_lbl)
        img_row.addStretch()
        form.addRow("Görsel", img_row)

        layout.addLayout(form)

        btn_row = QHBoxLayout()
        btn_row.addStretch()
        cancel = QPushButton("İptal")
        cancel.setObjectName("btn_flat")
        cancel.clicked.connect(self.reject)
        btn_row.addWidget(cancel)
        save = QPushButton("Kaydet")
        save.clicked.connect(self.accept)
        btn_row.addWidget(save)
        layout.addLayout(btn_row)

    def _populate(self, cert: Certificate) -> None:
        self._name_input.setText(cert.name)
        self._issuer_input.setText(cert.issuer)
        self._date_input.setText(cert.date or "")
        self._url_input.setText(cert.verification_url or "")
        self._order_spin.setValue(cert.display_order)

        # Mevcut görseli önizlemeye yükle
        if cert.image_path:
            if os.path.isabs(cert.image_path):
                full_path = cert.image_path
            else:
                full_path = os.path.join(get_data_path(), cert.image_path)
            if os.path.exists(full_path):
                px = QPixmap(full_path)
                if not px.isNull():
                    self._img_preview.setPixmap(
                        px.scaled(80, 56, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                    )
                    self._img_name_lbl.setText(os.path.basename(full_path))

    def _pick_image(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self, "Görsel Seç", "", "Görseller (*.jpg *.jpeg *.png *.webp)"
        )
        if path:
            self._image_source = path
            self._img_name_lbl.setText(os.path.basename(path))
            px = QPixmap(path)
            if not px.isNull():
                self._img_preview.setPixmap(
                    px.scaled(80, 56, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                )

    def get_data(self) -> dict:
        data = {
            "name":             self._name_input.text(),
            "issuer":           self._issuer_input.text(),
            "date":             self._date_input.text(),
            "verification_url": self._url_input.text(),
            "display_order":    self._order_spin.value(),
        }
        if self._image_source:
            data["image_source_path"] = self._image_source
        return data
