"""presentation/admin/pages/resource_type_dialog.py — Kaynak türü yönetim ekranı."""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QLineEdit, QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox, QWidget
)
from PySide6.QtCore import Qt

from styles.constants import COLORS

class ResourceTypeDialog(QDialog):
    def __init__(self, type_ctrl, parent=None):
        super().__init__(parent)
        self._ctrl = type_ctrl
        self.setWindowTitle("Kaynak Türü Yönetimi")
        self.resize(500, 400)
        self.setStyleSheet(f"background:{COLORS['bg_primary']};")
        
        self._editing_id = None
        
        self._build_ui()
        self._load_data()
        
        self._ctrl.error_occurred.connect(self._on_error)
        self._ctrl.types_changed.connect(self._load_data)

    def _build_ui(self):
        lay = QVBoxLayout(self)
        lay.setContentsMargins(24, 24, 24, 24)
        lay.setSpacing(16)
        
        # Başlık
        self._title = QLabel("Yeni Tür Ekle")
        self._title.setStyleSheet(f"color:{COLORS['text_primary']};font-size:14px;font-weight:700;")
        lay.addWidget(self._title)
        
        # Form
        fl = QHBoxLayout()
        self._name = QLineEdit(); self._name.setPlaceholderText("Ad (örn: Video)")
        self._color = QLineEdit(); self._color.setPlaceholderText("Renk (örn: #ef4444)")
        
        self._name.setStyleSheet(self._input_style())
        self._color.setStyleSheet(self._input_style()); self._color.setFixedWidth(100)
        
        self._submit_btn = QPushButton("Ekle")
        self._submit_btn.setCursor(Qt.PointingHandCursor)
        self._submit_btn.setStyleSheet(f"QPushButton{{background:{COLORS['accent_blue']};color:#fff;border:none;border-radius:4px;padding:8px 16px;font-weight:bold;}}QPushButton:hover{{opacity:0.8;}}")
        self._submit_btn.clicked.connect(self._submit)
        
        self._cancel_btn = QPushButton("İptal")
        self._cancel_btn.setCursor(Qt.PointingHandCursor)
        self._cancel_btn.setStyleSheet(f"QPushButton{{background:transparent;color:{COLORS['text_muted']};border:1px solid {COLORS['border']};border-radius:4px;padding:8px 16px;font-weight:bold;}}QPushButton:hover{{background:{COLORS['bg_hover']};}}")
        self._cancel_btn.clicked.connect(self._reset_form)
        self._cancel_btn.hide()
        
        fl.addWidget(self._name)
        fl.addWidget(self._color)
        fl.addWidget(self._cancel_btn)
        fl.addWidget(self._submit_btn)
        lay.addLayout(fl)
        
        # Tablo
        self._table = QTableWidget()
        self._table.setColumnCount(3)
        self._table.setHorizontalHeaderLabels(["Tür Adı", "Renk", "İşlemler"])
        self._table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self._table.setColumnWidth(1, 100)
        self._table.setColumnWidth(2, 90)
        self._table.verticalHeader().setVisible(False)
        self._table.setEditTriggers(QTableWidget.NoEditTriggers)
        self._table.setSelectionMode(QTableWidget.NoSelection)
        self._table.setShowGrid(False)
        
        self._table.setStyleSheet(f"""
            QTableWidget {{
                background: {COLORS['bg_card']};
                color: {COLORS['text_primary']};
                border: 1px solid {COLORS['border']};
                border-radius: 8px;
            }}
            QHeaderView::section {{
                background: {COLORS['bg_secondary']};
                color: {COLORS['text_muted']};
                border: none;
                border-bottom: 1px solid {COLORS['border']};
                padding: 4px;
                font-weight: 600;
            }}
        """)
        lay.addWidget(self._table)

    def _input_style(self):
        return f"background:{COLORS['bg_input']};color:{COLORS['text_primary']};border:1px solid {COLORS['border']};border-radius:4px;padding:8px;"

    def _load_data(self):
        types = self._ctrl.get_all()
        self._table.setRowCount(len(types))
        for i, t in enumerate(types):
            self._table.setItem(i, 0, QTableWidgetItem(t.name))
            
            c_item = QTableWidgetItem(t.color)
            c_item.setForeground(Qt.white if t.color != "#ffffff" else Qt.black)
            self._table.setItem(i, 1, c_item)
            
            # İşlemler
            db_w = QWidget(); db_l = QHBoxLayout(db_w); db_l.setContentsMargins(0,0,0,0); db_l.setSpacing(4)
            
            eb = QPushButton("✏")
            eb.setCursor(Qt.PointingHandCursor)
            eb.setStyleSheet(f"color:{COLORS['text_primary']};background:transparent;border:none;font-size:14px;")
            eb.clicked.connect(lambda _, tid=t.id, nm=t.name, clr=t.color: self._start_edit(tid, nm, clr))
            db_l.addWidget(eb)
            
            db = QPushButton("🗑")
            db.setCursor(Qt.PointingHandCursor)
            db.setStyleSheet(f"color:{COLORS['error']};background:transparent;border:none;font-size:14px;")
            db.clicked.connect(lambda _, tid=t.id: self._delete(tid))
            db_l.addWidget(db)
            
            db_l.setAlignment(Qt.AlignCenter)
            self._table.setCellWidget(i, 2, db_w)

    def _start_edit(self, tid, name, color):
        self._editing_id = tid
        self._name.setText(name)
        self._color.setText(color)
        self._title.setText("Türü Düzenle")
        self._submit_btn.setText("Güncelle")
        self._submit_btn.setStyleSheet(f"QPushButton{{background:{COLORS['success']};color:#fff;border:none;border-radius:4px;padding:8px 16px;font-weight:bold;}}QPushButton:hover{{opacity:0.8;}}")
        self._cancel_btn.show()

    def _reset_form(self):
        self._editing_id = None
        self._name.clear()
        self._color.clear()
        self._title.setText("Yeni Tür Ekle")
        self._submit_btn.setText("Ekle")
        self._submit_btn.setStyleSheet(f"QPushButton{{background:{COLORS['accent_blue']};color:#fff;border:none;border-radius:4px;padding:8px 16px;font-weight:bold;}}QPushButton:hover{{opacity:0.8;}}")
        self._cancel_btn.hide()

    def _submit(self):
        if not self._name.text().strip(): return
        data = {
            "name": self._name.text().strip(),
            "color": self._color.text().strip() or "#888888",
            "emoji": "📁" # veritabanı boş emoji ile hata vermemesi için varsayılan
        }
        
        if self._editing_id:
            self._ctrl.update(self._editing_id, data)
        else:
            self._ctrl.create(data)
            
        self._reset_form()

    def _delete(self, tid):
        self._ctrl.delete(tid)

    def _on_error(self, msg):
        QMessageBox.warning(self, "Hata", msg)
