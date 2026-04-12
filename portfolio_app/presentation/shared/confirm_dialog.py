"""presentation/shared/confirm_dialog.py — Silme/işlem onay dialog'u."""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QWidget
)
from PySide6.QtCore import Qt

from styles.constants import COLORS


class ConfirmDialog(QDialog):
    """Evet/Hayır onay dialog'u."""

    def __init__(
        self,
        parent: QWidget,
        title: str = "Onay",
        message: str = "Bu işlemi yapmak istediğinizden emin misiniz?",
        confirm_text: str = "Evet",
        cancel_text: str = "İptal",
        danger: bool = False,
    ):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setModal(True)
        self.setMinimumWidth(360)
        self._build_ui(message, confirm_text, cancel_text, danger)

    def _build_ui(self, message: str, confirm_text: str, cancel_text: str, danger: bool) -> None:
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(24, 24, 24, 20)

        msg_label = QLabel(message)
        msg_label.setWordWrap(True)
        msg_label.setStyleSheet(f"color: {COLORS['text_primary']}; font-size: 14px;")
        layout.addWidget(msg_label)

        btn_row = QHBoxLayout()
        btn_row.setSpacing(12)
        btn_row.addStretch()

        cancel_btn = QPushButton(cancel_text)
        cancel_btn.setObjectName("btn_flat")
        cancel_btn.clicked.connect(self.reject)
        btn_row.addWidget(cancel_btn)

        confirm_btn = QPushButton(confirm_text)
        if danger:
            confirm_btn.setObjectName("btn_danger")
        confirm_btn.clicked.connect(self.accept)
        btn_row.addWidget(confirm_btn)

        layout.addLayout(btn_row)

        self.setStyleSheet(f"""
            QDialog {{
                background: {COLORS['bg_secondary']};
                border: 1px solid {COLORS['border']};
                border-radius: 12px;
            }}
        """)


def confirm(parent: QWidget, message: str, danger: bool = False) -> bool:
    """Kısayol — True döner ise kullanıcı onayladı."""
    dialog = ConfirmDialog(parent, message=message, danger=danger)
    return dialog.exec() == QDialog.Accepted
