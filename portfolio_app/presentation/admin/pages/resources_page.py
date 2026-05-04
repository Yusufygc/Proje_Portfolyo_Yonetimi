"""presentation/admin/pages/resources_page.py — Kaynak yönetim merkezi."""

import webbrowser
from datetime import datetime

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QScrollArea, QFrame, QDialog, QLineEdit, QGridLayout, QSizePolicy,
    QGraphicsDropShadowEffect
)
from PySide6.QtCore import Qt, QSize, QTimer
from PySide6.QtGui import QColor

from styles.constants import COLORS, FONTS, SPACING
from controllers.resource_controller import ResourceController
from controllers.resource_type_controller import ResourceTypeController
from controllers.project_controller import ProjectController
from domain.models.resource import Resource
from domain.enums.resource_type import ResourceStatus, ResourcePriority
from presentation.shared.confirm_dialog import confirm
from presentation.shared.toast import show_toast, Toast
from presentation.admin.pages.resource_dialog import ResourceDialog
from presentation.admin.pages.resource_type_dialog import ResourceTypeDialog
from resources.icon_manager import IconManager, Icons

GRID_COLS = 3


class ResourcesPage(QWidget):
    def __init__(self, ctrl: ResourceController,
                 type_ctrl: ResourceTypeController,
                 project_ctrl: ProjectController, parent=None):
        super().__init__(parent)
        self._ctrl = ctrl
        self._type_ctrl = type_ctrl
        self._project_ctrl = project_ctrl
        self._filter_type: str | None = None
        self._filter_status: str | None = None
        self._search_query: str = ""
        self._sort_by: str = "created_at"
        self._sort_dir: str = "DESC"
        self._resources: list[Resource] = []
        self._ctrl.resources_changed.connect(self.refresh)
        self._type_ctrl.types_changed.connect(self.refresh)
        self._ctrl.error_occurred.connect(lambda m: show_toast(self, m, Toast.ERROR))
        self._search_timer = QTimer(); self._search_timer.setSingleShot(True)
        self._search_timer.timeout.connect(self._do_search)
        self._build_ui()
        self.refresh()

    def _build_ui(self):
        root = QVBoxLayout(self); root.setContentsMargins(0,0,0,0); root.setSpacing(0)

        # Header
        hdr = QWidget(); hdr.setFixedHeight(52)
        hdr.setStyleSheet(f"background:{COLORS['bg_secondary']};border-bottom:1px solid {COLORS['border']};")
        hl = QHBoxLayout(hdr); hl.setContentsMargins(24,0,24,0); hl.setSpacing(16)
        
        title_box = QVBoxLayout(); title_box.setSpacing(0); title_box.setAlignment(Qt.AlignVCenter)
        t = QLabel("Kaynaklar")
        t.setStyleSheet(f"color:{COLORS['text_primary']};font-size:18px;font-weight:600;background:transparent;border:none;")
        title_box.addWidget(t)
        
        self._header_subtitle = QLabel("Yükleniyor...")
        self._header_subtitle.setStyleSheet(f"color:{COLORS['text_muted']};font-size:11px;background:transparent;border:none;")
        title_box.addWidget(self._header_subtitle)
        hl.addLayout(title_box); hl.addStretch()

        self._search = QLineEdit(); self._search.setPlaceholderText("🔍  Kaynaklarda ara...")
        self._search.setFixedWidth(280); self._search.setFixedHeight(32)
        self._search.setStyleSheet(f"background:{COLORS['bg_input']};color:{COLORS['text_primary']};border:1px solid {COLORS['border']};border-radius:16px;padding:0 14px;font-size:13px;")
        self._search.textChanged.connect(lambda: (self._search_timer.stop(), self._search_timer.start(300)))
        hl.addWidget(self._search)

        add_btn = QPushButton(" + Yeni"); add_btn.setCursor(Qt.PointingHandCursor); add_btn.setFixedHeight(32)
        add_btn.setStyleSheet(f"QPushButton{{background:{COLORS['text_primary']};color:{COLORS['bg_primary']};border:none;border-radius:16px;font-size:13px;font-weight:600;padding:0 16px;}}QPushButton:hover{{background:{COLORS['text_secondary']};}}")
        add_btn.clicked.connect(self._open_create_dialog); hl.addWidget(add_btn)
        root.addWidget(hdr)
        
        # Filter bar
        fb = QWidget(); fb.setFixedHeight(56)
        fb.setStyleSheet(f"background:{COLORS['bg_secondary']};border-bottom:1px solid {COLORS['border']};")
        fl = QHBoxLayout(fb); fl.setContentsMargins(24,0,24,0); fl.setSpacing(8)

        lbl_type = QLabel("Tür:"); lbl_type.setStyleSheet(f"color:{COLORS['text_muted']};font-size:10px;font-weight:700;text-transform:uppercase;")
        fl.addWidget(lbl_type)
        
        type_mgr_btn = QPushButton(); type_mgr_btn.setIcon(IconManager.get(Icons.SETTINGS)); type_mgr_btn.setIconSize(QSize(14,14))
        type_mgr_btn.setFixedSize(24, 24); type_mgr_btn.setCursor(Qt.PointingHandCursor)
        type_mgr_btn.setStyleSheet(f"QPushButton{{background:transparent;border:none;border-radius:4px;}}QPushButton:hover{{background:{COLORS['bg_hover']};}}")
        type_mgr_btn.setToolTip("Türleri Yönet")
        type_mgr_btn.clicked.connect(self._open_type_manager)
        fl.addWidget(type_mgr_btn)

        self._type_btns = {}
        fl.addWidget(self._make_filter_btn("Tümü", None, True, self._type_btns, self._set_type_filter))
        
        fl.addSpacing(16)

        # Durum filtreleri
        lbl_status = QLabel("Durum:"); lbl_status.setStyleSheet(f"color:{COLORS['text_muted']};font-size:10px;font-weight:700;text-transform:uppercase;")
        fl.addWidget(lbl_status)
        
        self._status_btns = {}
        fl.addWidget(self._make_filter_btn("Tümü", None, True, self._status_btns, self._set_status_filter))
        for s in ResourceStatus:
            fl.addWidget(self._make_filter_btn(s.label(), s.value, False, self._status_btns, self._set_status_filter))
        fl.addStretch()

        # Sıralama
        from PySide6.QtWidgets import QComboBox
        self._sort_combo = QComboBox(); self._sort_combo.setFixedHeight(28); self._sort_combo.setFixedWidth(150)
        self._sort_combo.setStyleSheet(f"QComboBox{{background:{COLORS['bg_input']};color:{COLORS['text_primary']};border:1px solid {COLORS['border']};border-radius:6px;padding:0 8px;font-size:12px;}}")
        for label, val in [("Tarih ↓","created_at|DESC"),("Tarih ↑","created_at|ASC"),("Başlık A→Z","title|ASC"),("Öncelik","priority|DESC")]:
            self._sort_combo.addItem(label, val)
        self._sort_combo.currentIndexChanged.connect(self._on_sort_changed)
        fl.addWidget(self._sort_combo)
        root.addWidget(fb)

        # Grid
        self._scroll = QScrollArea(); self._scroll.setWidgetResizable(True)
        self._scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self._scroll.setStyleSheet(f"QScrollArea{{border:none;background:{COLORS['bg_primary']};}}")
        self._gc = QWidget(); self._gc.setStyleSheet(f"background:{COLORS['bg_primary']};")
        self._grid = QGridLayout(self._gc); self._grid.setContentsMargins(24,20,24,24); self._grid.setSpacing(16)
        self._grid.setAlignment(Qt.AlignTop|Qt.AlignLeft)
        self._scroll.setWidget(self._gc); root.addWidget(self._scroll)

    def _make_filter_btn(self, label, val, active, btn_dict, handler):
        b = QPushButton(label); b.setCursor(Qt.PointingHandCursor); b.setFixedHeight(28)
        b.setCheckable(True); b.setChecked(active)
        b.setStyleSheet(self._fbtn_style(active))
        b.clicked.connect(lambda: handler(val)); btn_dict[val] = b; return b

    def _set_type_filter(self, v):
        self._filter_type = v
        for k, b in self._type_btns.items(): b.setChecked(k==v); b.setStyleSheet(self._fbtn_style(k==v))
        self._render_grid()

    def _set_status_filter(self, v):
        self._filter_status = v
        for k, b in self._status_btns.items(): b.setChecked(k==v); b.setStyleSheet(self._fbtn_style(k==v))
        self._render_grid()

    def _on_sort_changed(self):
        d = self._sort_combo.currentData()
        if d:
            parts = d.split("|"); self._sort_by = parts[0]; self._sort_dir = parts[1]
            self.refresh()

    def _do_search(self):
        self._search_query = self._search.text().strip(); self._render_grid()

    def refresh(self):
        self._resources = self._ctrl.get_all(self._sort_by, self._sort_dir)
        self._rebuild_type_filters()
        self._update_stats()
        self._render_grid()

    def _rebuild_type_filters(self):
        types = self._type_ctrl.get_all()
        # Sadece ilk sefer oluştur veya tür değiştiğinde
        existing_keys = set(self._type_btns.keys()) - {None}
        new_keys = {rt.name for rt in types}
        if existing_keys != new_keys:
            # Type butonlarını filter bar'a ekle — basit çözüm: mevcut butonları sil, yeniden oluştur
            fb_layout = None
            for i in range(self.layout().count()):
                w = self.layout().itemAt(i).widget()
                if w and w.layout():
                    for j in range(w.layout().count()):
                        item = w.layout().itemAt(j)
                        if item and item.widget() and item.widget() in self._type_btns.values():
                            fb_layout = w.layout()
                            break
            if fb_layout:
                for k in list(self._type_btns.keys()):
                    if k is not None:
                        btn = self._type_btns.pop(k)
                        fb_layout.removeWidget(btn); btn.deleteLater()
                insert_pos = 3  # After "Tür:", settings btn, and "Tümü" button
                for rt in types:
                    b = self._make_filter_btn(f"{rt.name}", rt.name,
                                              rt.name == self._filter_type, self._type_btns, self._set_type_filter)
                    fb_layout.insertWidget(insert_pos, b); insert_pos += 1

    def _update_stats(self):
        stats = self._ctrl.get_stats()
        total = stats.get("total", 0)
        
        if hasattr(self, '_header_subtitle'):
            self._header_subtitle.setText(f"{total} kaynak · Yönetim Merkezi")

    def _render_grid(self):
        while self._grid.count():
            item = self._grid.takeAt(0)
            if item.widget(): item.widget().deleteLater()
            
        for r in range(self._grid.rowCount()):
            self._grid.setRowStretch(r, 0)

        filtered = self._resources
        if self._filter_type:
            filtered = [r for r in filtered if r.type == self._filter_type]
        if self._filter_status:
            filtered = [r for r in filtered if r.status.value == self._filter_status]
        if self._search_query:
            q = self._search_query.lower()
            filtered = [r for r in filtered if q in r.title.lower() or q in (r.notes or "").lower()]

        if not filtered:
            ew = QWidget(); el = QVBoxLayout(ew); el.setAlignment(Qt.AlignCenter); el.setSpacing(12)
            
            ic = QLabel(); ic.setAlignment(Qt.AlignCenter)
            ic_px = IconManager.get(Icons.RESOURCES).pixmap(56, 56)
            ic.setPixmap(ic_px); ic.setStyleSheet("background:transparent;border:none;opacity:0.6;")
            el.addWidget(ic)
            
            msg = QLabel("Kaynak bulunamadı." if self._resources else "Kaynak koleksiyonunuz boş")
            msg.setAlignment(Qt.AlignCenter)
            msg.setStyleSheet(f"color:{COLORS['text_primary']};font-size:16px;font-weight:700;background:transparent;border:none;")
            el.addWidget(msg)
            
            submsg = QLabel("Arama veya filtre kriterlerini değiştirin." if self._resources else "Kurslarınızı, notlarınızı ve repolarınızı buradan yönetin.")
            submsg.setAlignment(Qt.AlignCenter)
            submsg.setStyleSheet(f"color:{COLORS['text_muted']};font-size:13px;background:transparent;border:none;")
            el.addWidget(submsg)
            
            if not self._resources:
                el.addSpacing(16)
                cta = QPushButton("+ İlk Kaynağı Ekle"); cta.setCursor(Qt.PointingHandCursor)
                cta.setFixedSize(180, 40)
                cta.setStyleSheet(f"QPushButton{{background:{COLORS['accent_blue']};color:#fff;border:none;border-radius:20px;font-size:14px;font-weight:600;}}QPushButton:hover{{background:{COLORS['accent_blue_dark']};}}")
                cta.clicked.connect(self._open_create_dialog); el.addWidget(cta, alignment=Qt.AlignCenter)
                
            self._grid.addWidget(ew, 0, 0, 1, GRID_COLS, Qt.AlignTop)
            self._grid.setRowStretch(1, 1)
            return

        for i, res in enumerate(filtered):
            self._grid.addWidget(self._build_card(res), i // GRID_COLS, i % GRID_COLS)
            
        for c in range(GRID_COLS): self._grid.setColumnStretch(c, 1)
        
        # En alt satıra boşluk ekleyerek kartların dikeyde esnemesini engelle
        row_count = (len(filtered) - 1) // GRID_COLS + 1
        self._grid.setRowStretch(row_count, 1)

    def _build_card(self, res: Resource):
        color = res.type_color
        card = QFrame(); card.setMinimumSize(280, 180)

        # Öncelik çizgisi rengi
        prio_color = res.priority.color() if hasattr(res.priority, 'color') else COLORS['accent_blue']

        card.setStyleSheet(f"""
            QFrame {{
                background: {COLORS['bg_card']};
                border: 1px solid rgba{self._hex_rgba(color, 0.6)};
                border-radius: 12px;
            }}
            QFrame:hover {{
                border: 1px solid {color};
            }}
        """)
        
        shadow = QGraphicsDropShadowEffect(card)
        shadow.setBlurRadius(24)
        shadow.setColor(QColor(0, 0, 0, 12))  # %5 opacity siyah gölge
        shadow.setOffset(0, 8)
        card.setGraphicsEffect(shadow)
        
        outer = QVBoxLayout(card); outer.setContentsMargins(0,0,0,0); outer.setSpacing(0)

        body = QWidget(); body.setStyleSheet("background:transparent;")
        bl = QVBoxLayout(body); bl.setContentsMargins(20,18,20,18); bl.setSpacing(10)

        # Üst: badge + pin + durum
        br = QHBoxLayout(); br.setSpacing(8)
        badge = QLabel(f" {res.type} ")
        badge.setFixedHeight(22)
        badge.setStyleSheet(f"QLabel{{background:rgba{self._hex_rgba(color,0.08)};color:{color};font-size:11px;font-weight:600;border-radius:11px;padding:0 10px;}}")
        br.addWidget(badge)

        br.addStretch()

        sc, st = self._status_meta(res.status)
        sp = QLabel(f"● {st}"); sp.setStyleSheet(f"color:{sc};font-size:11px;font-weight:500;background:transparent;border:none;")
        br.addWidget(sp)
        bl.addLayout(br)

        # Başlık
        tl = QLabel(res.title); tl.setWordWrap(True)
        tl.setStyleSheet(f"color:{COLORS['text_primary']};font-size:16px;font-weight:700;background:transparent;border:none;")
        bl.addWidget(tl)

        # Not önizlemesi
        if res.notes and res.notes.strip():
            preview = res.notes.strip().replace("\n"," ")
            if len(preview) > 90: preview = preview[:90] + "…"
            nl = QLabel(preview); nl.setWordWrap(True)
            nl.setStyleSheet(f"color:{COLORS['text_secondary']};font-size:12px;font-weight:400;background:transparent;border:none;")
            bl.addWidget(nl)

        # İlerleme barı
        if res.progress > 0:
            pb_bg = QFrame(); pb_bg.setFixedHeight(6); pb_bg.setStyleSheet(f"background:{COLORS['bg_active']};border-radius:3px;border:none;")
            pb_fg = QFrame(); pb_fg.setFixedHeight(6); pb_fg.setStyleSheet(f"background:{COLORS['accent_blue']};border-radius:3px;border:none;")
            pbl = QHBoxLayout(pb_bg); pbl.setContentsMargins(0,0,0,0); pbl.setSpacing(0)
            pbl.addWidget(pb_fg, stretch=max(res.progress,1)); pbl.addStretch(max(100-res.progress,1))
            pr = QHBoxLayout(); pr.setSpacing(4)
            pr.addWidget(pb_bg, stretch=1)
            pl = QLabel(f"%{res.progress}"); pl.setStyleSheet(f"color:{COLORS['accent_blue']};font-size:10px;font-weight:bold;background:transparent;border:none;")
            pr.addWidget(pl)
            bl.addLayout(pr)

        # Etiketler
        if res.tags:
            tr = QHBoxLayout(); tr.setSpacing(6)
            for tag in res.tags[:4]:
                tg = QLabel(tag); tg.setStyleSheet(f"background:{COLORS['tag_bg']};border:1px solid {COLORS['tag_border']};border-radius:10px;color:{COLORS['tag_text']};font-size:11px;padding:2px 8px;")
                tr.addWidget(tg)
            if len(res.tags) > 4:
                ml = QLabel(f"+{len(res.tags)-4}"); ml.setStyleSheet(f"color:{COLORS['text_muted']};font-size:11px;background:transparent;border:none;")
                tr.addWidget(ml)
            tr.addStretch(); bl.addLayout(tr)

        bl.addStretch()

        # Meta (Tarih + Proje)
        meta_parts = []
        if res.created_at:
            meta_parts.append(self._relative_date(res.created_at))
        if res.related_project_title:
            meta_parts.append(f"📂 {res.related_project_title}")
        
        if meta_parts:
            dl = QLabel(" · ".join(meta_parts)); dl.setStyleSheet(f"color:rgba{self._hex_rgba(COLORS['text_muted'],0.6)};font-size:11px;background:transparent;border:none;")
            bl.addWidget(dl)

        # Eylem butonları
        ar = QHBoxLayout(); ar.setSpacing(8); ar.setContentsMargins(0,8,0,0)
        
        if res.url and res.url.strip():
            ob = QPushButton(" Aç"); ob.setCursor(Qt.PointingHandCursor); ob.setFixedHeight(28)
            ob.setIcon(IconManager.get(Icons.LINK)); ob.setIconSize(QSize(14,14))
            ob.setStyleSheet(self._act_style(color)); url=res.url
            ob.clicked.connect(lambda:webbrowser.open(url)); ar.addWidget(ob)

        ar.addStretch()

        # Pin toggle
        pb = QPushButton(); pb.setCursor(Qt.PointingHandCursor); pb.setFixedSize(28, 28)
        pb.setIcon(IconManager.get(Icons.PIN)); pb.setIconSize(QSize(14,14))
        # Eğer pinliyse butonu vurgulu göster
        pb.setStyleSheet(self._ghost_style(active=res.is_pinned)); rid=res.id
        pb.clicked.connect(lambda:self._toggle_pin(rid)); ar.addWidget(pb)

        eb = QPushButton(); eb.setCursor(Qt.PointingHandCursor); eb.setFixedSize(28, 28)
        eb.setIcon(IconManager.get(Icons.EDIT)); eb.setIconSize(QSize(14,14))
        eb.setStyleSheet(self._ghost_style()); eb.clicked.connect(lambda:self._open_edit_dialog(res)); ar.addWidget(eb)
        
        db = QPushButton(); db.setCursor(Qt.PointingHandCursor); db.setFixedSize(28, 28)
        db.setIcon(IconManager.get(Icons.DELETE)); db.setIconSize(QSize(14,14))
        db.setStyleSheet(self._danger_style()); db.clicked.connect(lambda:self._delete(res)); ar.addWidget(db)
        
        bl.addLayout(ar)

        outer.addWidget(body); return card

    # Stiller
    @staticmethod
    def _hex_rgba(hc, a):
        try:
            h = hc.lstrip("#")
            if len(h)==6: return f"({int(h[0:2],16)},{int(h[2:4],16)},{int(h[4:6],16)},{a})"
        except (ValueError, AttributeError):
            pass
        return f"(80,130,200,{a})"

    @staticmethod
    def _status_meta(s):
        return {ResourceStatus.PLANLI:(COLORS['text_muted'],"Planlı"),ResourceStatus.DEVAM_EDIYOR:(COLORS['accent_blue'],"Devam Ediyor"),ResourceStatus.TAMAMLANDI:(COLORS['success'],"Tamamlandı")}.get(s,(COLORS['text_muted'],s.label()))

    @staticmethod
    def _relative_date(dt_str):
        try:
            dt = datetime.fromisoformat(dt_str)
            diff = datetime.now() - dt
            if diff.days == 0: return "Bugün"
            if diff.days == 1: return "Dün"
            if diff.days < 7: return f"{diff.days} gün önce"
            if diff.days < 30: return f"{diff.days//7} hafta önce"
            return dt.strftime("%d %b %Y")
        except: return dt_str[:10] if len(dt_str)>=10 else dt_str

    @staticmethod
    def _fbtn_style(active):
        if active: return f"QPushButton{{background:{COLORS['text_primary']};color:{COLORS['bg_primary']};border:none;border-radius:14px;font-size:12px;font-weight:600;padding:0 16px;margin:0px;}}"
        return f"QPushButton{{background:transparent;color:{COLORS['text_secondary']};border:1px solid {COLORS['border']};border-radius:14px;font-size:12px;font-weight:500;padding:0 16px;margin:0px;}}QPushButton:hover{{background:{COLORS['bg_hover']};color:{COLORS['text_primary']};}}"

    @staticmethod
    def _act_style(c): return f"QPushButton{{background:transparent;color:{c};border:1px solid {c};border-radius:6px;font-size:12px;font-weight:600;padding:0 12px;}}QPushButton:hover{{background:rgba{ResourcesPage._hex_rgba(c,0.1)};}}"
    
    @staticmethod
    def _ghost_style(active=False): 
        color = COLORS['accent_blue'] if active else COLORS['text_secondary']
        bg = f"rgba{ResourcesPage._hex_rgba(COLORS['accent_blue'],0.1)}" if active else "transparent"
        border = f"1px solid {color}" if active else f"1px solid {COLORS['border']}"
        return f"QPushButton{{background:{bg};border:{border};border-radius:6px;padding:6px;}}QPushButton:hover{{background:{COLORS['bg_hover']};border-color:{COLORS['text_secondary']};}}"
    
    @staticmethod
    def _danger_style(): return f"QPushButton{{background:transparent;border:1px solid {COLORS['border']};border-radius:6px;padding:6px;}}QPushButton:hover{{background:rgba(239,68,68,0.1);border-color:{COLORS['error']};}}"

    # Eylemler
    def _open_type_manager(self):
        dlg = ResourceTypeDialog(self._type_ctrl, self)
        dlg.exec()
        
    def _open_create_dialog(self):
        types = self._type_ctrl.get_all()
        projects = self._project_ctrl.get_all()
        dlg = ResourceDialog(self, resource_types=types, projects=projects)
        if dlg.exec() == QDialog.Accepted: self._ctrl.create(dlg.get_data())

    def _open_edit_dialog(self, res):
        types = self._type_ctrl.get_all()
        projects = self._project_ctrl.get_all()
        dlg = ResourceDialog(self, res, resource_types=types, projects=projects)
        if dlg.exec() == QDialog.Accepted: self._ctrl.update(res.id, dlg.get_data())

    def _delete(self, res):
        if confirm(self, f'"{res.title}" kaynağını silmek istediğinizden emin misiniz?', danger=True):
            self._ctrl.delete(res.id)

    def _toggle_pin(self, rid):
        self._ctrl.toggle_pin(rid)
