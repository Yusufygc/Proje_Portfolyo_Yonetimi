"""presentation/admin/pages/certificates_page.py — Sertifika CRUD."""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QScrollArea, QFrame, QDialog, QLineEdit, QFormLayout,
    QFileDialog, QSpinBox
)
from PySide6.QtCore import Qt

from styles.constants import COLORS, FONTS
from controllers.certificate_controller import CertificateController
from domain.models.certificate import Certificate
from presentation.shared.confirm_dialog import confirm
from presentation.shared.toast import show_toast, Toast


class CertificatesPage(QWidget):
    """Admin sertifika yönetim sayfası."""

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
        header.setStyleSheet(f"background: {COLORS['bg_secondary']}; border-bottom: 1px solid {COLORS['border']};")
        h_layout = QHBoxLayout(header)
        h_layout.setContentsMargins(24, 16, 24, 16)

        title = QLabel("Sertifikalar")
        title.setStyleSheet(f"color: {COLORS['text_primary']}; font-size: {FONTS['size_lg']}px; font-weight: 700;")
        h_layout.addWidget(title)
        h_layout.addStretch()

        add_btn = QPushButton("+ Sertifika Ekle")
        add_btn.setCursor(Qt.PointingHandCursor)
        add_btn.clicked.connect(self._open_create_dialog)
        h_layout.addWidget(add_btn)
        layout.addWidget(header)

        # Liste
        self._scroll = QScrollArea()
        self._scroll.setWidgetResizable(True)
        self._scroll.setStyleSheet("QScrollArea { border: none; }")
        self._list_widget = QWidget()
        self._list_widget.setStyleSheet(f"background: {COLORS['bg_primary']};")
        self._list_layout = QVBoxLayout(self._list_widget)
        self._list_layout.setContentsMargins(24, 16, 24, 16)
        self._list_layout.setSpacing(12)
        self._scroll.setWidget(self._list_widget)
        layout.addWidget(self._scroll)

    def refresh(self) -> None:
        while self._list_layout.count():
            item = self._list_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        certs = self._ctrl.get_all()
        if not certs:
            empty = QLabel("Henüz sertifika eklenmemiş.")
            empty.setStyleSheet(f"color: {COLORS['text_muted']}; font-size: 14px;")
            self._list_layout.addWidget(empty)
        else:
            for cert in certs:
                self._list_layout.addWidget(self._make_cert_row(cert))

        self._list_layout.addStretch()

    def _make_cert_row(self, cert: Certificate) -> QFrame:
        frame = QFrame()
        frame.setStyleSheet(f"""
            QFrame {{
                background: {COLORS['bg_card']};
                border: 1px solid {COLORS['border']};
                border-radius: 10px;
            }}
        """)
        row = QHBoxLayout(frame)
        row.setContentsMargins(16, 12, 16, 12)
        row.setSpacing(16)

        icon = QLabel("🏆")
        icon.setFixedWidth(32)
        icon.setStyleSheet("background: transparent; font-size: 22px;")
        row.addWidget(icon)

        info_col = QVBoxLayout()
        name_lbl = QLabel(cert.name)
        name_lbl.setStyleSheet(f"color: {COLORS['text_primary']}; font-size: 14px; font-weight: 600;")
        info_col.addWidget(name_lbl)

        meta_parts = []
        if cert.issuer:
            meta_parts.append(cert.issuer)
        if cert.date:
            meta_parts.append(cert.date)
        if meta_parts:
            meta = QLabel(" · ".join(meta_parts))
            meta.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 12px;")
            info_col.addWidget(meta)

        row.addLayout(info_col, stretch=1)

        edit_btn = QPushButton("Düzenle")
        edit_btn.setObjectName("btn_flat")
        edit_btn.setCursor(Qt.PointingHandCursor)
        edit_btn.clicked.connect(lambda: self._open_edit_dialog(cert))
        row.addWidget(edit_btn)

        del_btn = QPushButton("Sil")
        del_btn.setObjectName("btn_danger")
        del_btn.setCursor(Qt.PointingHandCursor)
        del_btn.clicked.connect(lambda: self._delete(cert))
        row.addWidget(del_btn)

        return frame

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


class CertDialog(QDialog):
    def __init__(self, parent=None, cert: Certificate = None):
        super().__init__(parent)
        self._cert = cert
        self._image_source: str | None = None
        self.setWindowTitle("Sertifika Ekle" if not cert else "Sertifika Düzenle")
        self.setMinimumWidth(440)
        self.setModal(True)
        self._build_ui()
        if cert:
            self._populate(cert)

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 20)
        layout.setSpacing(16)
        self.setStyleSheet(f"QDialog {{ background: {COLORS['bg_secondary']}; }}")

        form = QFormLayout()
        form.setSpacing(12)

        self._name_input    = QLineEdit()
        self._issuer_input  = QLineEdit()
        self._date_input    = QLineEdit()
        self._date_input.setPlaceholderText("YYYY-MM veya YYYY")
        self._url_input     = QLineEdit()
        self._url_input.setPlaceholderText("https://...")
        self._order_spin    = QSpinBox()
        self._order_spin.setRange(0, 999)

        form.addRow("Ad *",          self._name_input)
        form.addRow("Kurum",         self._issuer_input)
        form.addRow("Tarih",         self._date_input)
        form.addRow("Doğrulama URL", self._url_input)
        form.addRow("Sıralama",      self._order_spin)

        img_btn = QPushButton("Görsel Seç")
        img_btn.setObjectName("btn_flat")
        img_btn.clicked.connect(self._pick_image)
        self._img_label = QLabel("Görsel seçilmedi")
        self._img_label.setStyleSheet(f"color: {COLORS['text_muted']}; font-size: 12px;")
        img_row = QHBoxLayout()
        img_row.addWidget(img_btn)
        img_row.addWidget(self._img_label)
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

    def _pick_image(self) -> None:
        path, _ = QFileDialog.getOpenFileName(self, "Görsel Seç", "", "Görseller (*.jpg *.jpeg *.png)")
        if path:
            self._image_source = path
            import os
            self._img_label.setText(os.path.basename(path))

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
