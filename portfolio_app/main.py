"""
main.py — Uygulama giriş noktası.
DI Container kurulumu, gizli admin trigger, pencere akışı.

Gizli Admin Erişim Yöntemleri:
  1. Ctrl+Shift+A klavye kısayolu
  2. Vitrin penceresinde başlık çubuğuna 5 kez çift tıklama
"""

import sys
import os

# portfolio_app/ dizinini Python path'e ekle
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QKeySequence, QShortcut
from PySide6.QtCore import Qt

from config import get_db_path, APP_NAME, APP_VERSION, ADMIN_KEY_SEQUENCE
from infrastructure.database.db_manager import DBManager
from infrastructure.logger import setup_logger
from styles.theme_engine import ThemeEngine
from di_container import DIContainer
from presentation.showcase.main_window import ShowcaseWindow
from presentation.admin.admin_window import AdminWindow

logger = setup_logger("main")


def main() -> None:
    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setApplicationVersion(APP_VERSION)

    # Yüksek DPI desteği
    app.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

    # Tema
    try:
        stylesheet = ThemeEngine.get_full_stylesheet()
        app.setStyleSheet(stylesheet)
    except Exception as e:
        logger.warning(f"Tema yüklenemedi (devam ediliyor): {e}")

    # Veritabanı başlat
    db = DBManager.initialize(get_db_path())
    logger.info(f"{APP_NAME} v{APP_VERSION} başlatılıyor")

    # DI Container
    container = DIContainer(db)

    # ── Pencere yönetimi ─────────────────────────────────────────────────────

    showcase_win = ShowcaseWindow(container.showcase_controller)
    admin_win: AdminWindow | None = None

    def open_admin() -> None:
        nonlocal admin_win
        logger.info("Admin panel açılıyor")
        if admin_win is None or not admin_win.isVisible():
            admin_win = AdminWindow(container)
            admin_win.closed.connect(on_admin_closed)
        admin_win.show()
        admin_win.raise_()
        admin_win.activateWindow()

    def on_admin_closed() -> None:
        """Admin kapanınca vitrini yenile."""
        showcase_win.reload()
        showcase_win.show()
        showcase_win.raise_()

    # Vitrin → admin callback
    showcase_win.admin_requested = open_admin

    # Gizli klavye kısayolu: Ctrl+Shift+A
    shortcut = QShortcut(QKeySequence(ADMIN_KEY_SEQUENCE), showcase_win)
    shortcut.activated.connect(open_admin)

    showcase_win.show()
    logger.info("Vitrin penceresi açıldı")

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
