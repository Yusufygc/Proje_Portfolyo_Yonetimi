"""presentation/admin/pages/export_page.py — CV/PDF export sayfası."""

import os

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QScrollArea, QFrame, QComboBox, QTextEdit, QFileDialog,
    QProgressBar, QSizePolicy
)
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QPixmap

from config import get_data_path
from styles.constants import COLORS, FONTS
from controllers.export_controller import ExportController
from services.dto.export_config import ExportConfig
from presentation.shared.toast import show_toast, Toast


class ExportWorker(QThread):
    """Arka planda export işlemini yürüten thread."""
    
    finished_export = Signal(bytes, str)
    error = Signal(str)

    def __init__(self, controller: ExportController, format_key: str, config: ExportConfig):
        super().__init__()
        self._ctrl = controller
        self._format_key = format_key
        self._config = config

    def run(self):
        # controller.export() asenkron değil ama sinyal yayıyor.
        # QThread içinde signal/slot bağlantısını manuel simüle etmek veya 
        # doğrudan servisi çağırmak mantıklı olabilir. Fakat biz controller
        # sinyallerini dinleyip QThread'den emit edeceğiz.
        
        def on_completed(data, ext):
            self.finished_export.emit(data, ext)
            
        def on_error(msg):
            self.error.emit(msg)
            
        self._ctrl.export_completed.connect(on_completed)
        self._ctrl.error_occurred.connect(on_error)
        
        self._ctrl.export(self._format_key, self._config)
        
        self._ctrl.export_completed.disconnect(on_completed)
        self._ctrl.error_occurred.disconnect(on_error)


class ExportPage(QWidget):
    """CV / PDF oluşturma sayfası."""

    def __init__(self, controller: ExportController, parent=None):
        super().__init__(parent)
        self._ctrl = controller
        self._config = ExportConfig()
        self._worker = None
        
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # ── Header ───────────────────────────────────────────────────────────
        header = QWidget()
        header.setStyleSheet(
            f"background: {COLORS['bg_secondary']};"
            f"border-bottom: 1px solid {COLORS['border']};"
        )
        h_layout = QHBoxLayout(header)
        h_layout.setContentsMargins(24, 16, 24, 16)

        title = QLabel("CV / PDF Çıktı")
        title.setStyleSheet(
            f"color: {COLORS['text_primary']};"
            f"font-size: {FONTS['size_lg']}px;"
            f"font-weight: 700;"
            f"border: none; background: transparent;"
        )
        h_layout.addWidget(title)
        h_layout.addStretch()
        layout.addWidget(header)

        # ── Main Content ─────────────────────────────────────────────────────
        content = QWidget()
        content.setStyleSheet(f"background: {COLORS['bg_primary']};")
        c_layout = QHBoxLayout(content)
        c_layout.setContentsMargins(24, 24, 24, 24)
        c_layout.setSpacing(24)

        # ── Sol Panel (Ayarlar) ──────────────────────────────────────────────
        left_panel = QFrame()
        left_panel.setFixedWidth(360)
        left_panel.setStyleSheet(f"""
            QFrame {{
                background: {COLORS['bg_card']};
                border: 1px solid {COLORS['border']};
                border-radius: 12px;
            }}
            QLabel {{ border: none; background: transparent; color: {COLORS['text_primary']}; }}
        """)
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(20, 20, 20, 20)
        left_layout.setSpacing(16)
        
        settings_lbl = QLabel("Çıktı Ayarları")
        settings_lbl.setStyleSheet(f"font-size: {FONTS['size_md']}px; font-weight: 700;")
        left_layout.addWidget(settings_lbl)

        # Format seçimi
        format_lbl = QLabel("Format:")
        left_layout.addWidget(format_lbl)
        self._format_combo = QComboBox()
        self._format_combo.setStyleSheet(f"""
            QComboBox {{
                background: {COLORS['bg_input']};
                color: {COLORS['text_primary']};
                border: 1px solid {COLORS['border']};
                border-radius: 6px;
                padding: 6px;
            }}
        """)
        formats = self._ctrl.get_available_formats()
        for f in formats:
            self._format_combo.addItem(f["name"], f["key"])
        left_layout.addWidget(self._format_combo)

        # Dil seçimi
        lang_lbl = QLabel("Dil:")
        left_layout.addWidget(lang_lbl)
        self._lang_combo = QComboBox()
        self._lang_combo.setStyleSheet(self._format_combo.styleSheet())
        self._lang_combo.addItem("İngilizce (English)", "en")
        self._lang_combo.addItem("Türkçe", "tr")
        left_layout.addWidget(self._lang_combo)

        left_layout.addSpacing(16)

        # Öneriler kutusu
        sugg_lbl = QLabel("Sistem Önerileri:")
        sugg_lbl.setStyleSheet(f"font-weight: 600; color: {COLORS['warning']};")
        left_layout.addWidget(sugg_lbl)
        
        self._sugg_box = QTextEdit()
        self._sugg_box.setReadOnly(True)
        self._sugg_box.setStyleSheet(f"""
            QTextEdit {{
                background: rgba(245, 158, 11, 0.1);
                color: {COLORS['text_secondary']};
                border: 1px solid rgba(245, 158, 11, 0.3);
                border-radius: 6px;
                font-size: 12px;
                padding: 8px;
            }}
        """)
        left_layout.addWidget(self._sugg_box)

        left_layout.addStretch()

        # İlerleme Çubuğu ve Buton
        self._progress = QProgressBar()
        self._progress.setFixedHeight(4)
        self._progress.setTextVisible(False)
        self._progress.setRange(0, 0)
        self._progress.setVisible(False)
        self._progress.setStyleSheet(f"""
            QProgressBar {{
                background: {COLORS['bg_input']};
                border: none;
                border-radius: 2px;
            }}
            QProgressBar::chunk {{
                background: {COLORS['accent_blue']};
                border-radius: 2px;
            }}
        """)
        left_layout.addWidget(self._progress)

        self._export_btn = QPushButton("Dosyayı Oluştur")
        self._export_btn.setCursor(Qt.PointingHandCursor)
        self._export_btn.setFixedHeight(40)
        self._export_btn.setStyleSheet(f"""
            QPushButton {{
                background: {COLORS['accent_blue']};
                color: white;
                border: none;
                border-radius: 6px;
                font-size: 14px;
                font-weight: 600;
            }}
            QPushButton:hover {{
                background: #3b82f6;
            }}
            QPushButton:disabled {{
                background: {COLORS['bg_input']};
                color: {COLORS['text_muted']};
            }}
        """)
        self._export_btn.clicked.connect(self._on_export_clicked)
        left_layout.addWidget(self._export_btn)

        c_layout.addWidget(left_panel)

        # ── Sağ Panel (Açıklama / Boş Alan) ──────────────────────────────────
        right_panel = QFrame()
        right_panel.setStyleSheet(f"background: {COLORS['bg_secondary']}; border-radius: 12px;")
        right_layout = QVBoxLayout(right_panel)
        right_layout.setAlignment(Qt.AlignCenter)
        
        icon_lbl = QLabel("📄")
        icon_lbl.setStyleSheet("font-size: 64px; background: transparent; border: none;")
        icon_lbl.setAlignment(Qt.AlignCenter)
        right_layout.addWidget(icon_lbl)
        
        info_lbl = QLabel("Sol taraftan ayarları seçip\nçıktı oluşturabilirsiniz.")
        info_lbl.setAlignment(Qt.AlignCenter)
        info_lbl.setStyleSheet(f"color: {COLORS['text_muted']}; font-size: 14px; background: transparent; border: none;")
        right_layout.addWidget(info_lbl)
        
        c_layout.addWidget(right_panel, stretch=1)

        layout.addWidget(content)

    def refresh(self) -> None:
        """Sayfa açıldığında önerileri günceller."""
        suggestions = self._ctrl.get_suggestions()
        if suggestions:
            self._sugg_box.setPlainText("• " + "\n• ".join(suggestions))
        else:
            self._sugg_box.setPlainText("Tüm bilgileriniz eksiksiz görünüyor. Harika!")

    def _on_export_clicked(self) -> None:
        format_key = self._format_combo.currentData()
        self._config.language = self._lang_combo.currentData()
        
        if "portfolio" in format_key:
            self._config.mode = "portfolio_pdf"
        elif "docx" in format_key:
            self._config.mode = "ats_docx"
        else:
            self._config.mode = "ats_pdf"

        self._export_btn.setEnabled(False)
        self._export_btn.setText("Oluşturuluyor...")
        self._progress.setVisible(True)

        self._worker = ExportWorker(self._ctrl, format_key, self._config)
        self._worker.finished_export.connect(self._on_export_finished)
        self._worker.error.connect(self._on_export_error)
        self._worker.start()

    def _on_export_finished(self, data: bytes, ext: str) -> None:
        self._reset_button()
        
        default_name = "CV" + ext
        # Masaüstüne kaydetme varsayılanı için expanduser kullanabiliriz
        default_path = os.path.join(os.path.expanduser("~"), "Desktop", default_name)
        
        path, _ = QFileDialog.getSaveFileName(
            self, "Dosyayı Kaydet", default_path, f"Dosyalar (*{ext})"
        )
        if path:
            try:
                with open(path, "wb") as f:
                    f.write(data)
                show_toast(self, "Dosya başarıyla kaydedildi.", Toast.SUCCESS)
            except Exception as e:
                show_toast(self, f"Kaydetme hatası: {e}", Toast.ERROR)

    def _on_export_error(self, msg: str) -> None:
        self._reset_button()
        show_toast(self, f"Hata: {msg}", Toast.ERROR)

    def _reset_button(self) -> None:
        self._export_btn.setEnabled(True)
        self._export_btn.setText("Dosyayı Oluştur")
        self._progress.setVisible(False)
        self._worker = None
