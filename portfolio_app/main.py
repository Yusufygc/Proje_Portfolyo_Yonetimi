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

logger = setup_logger("main")


def main() -> None:
    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setApplicationVersion(APP_VERSION)

    app.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

    try:
        stylesheet = ThemeEngine.get_full_stylesheet()
        app.setStyleSheet(stylesheet)
    except Exception as e:
        logger.warning(f"Tema yüklenemedi (devam ediliyor): {e}")

    db = DBManager.initialize(get_db_path())
    logger.info(f"{APP_NAME} v{APP_VERSION} başlatılıyor")

    container = DIContainer(db)

    # Tek pencere — vitrin + admin stack içinde
    win = ShowcaseWindow(container)

    # Gizli klavye kısayolu: Ctrl+Shift+A
    shortcut = QShortcut(QKeySequence(ADMIN_KEY_SEQUENCE), win)
    shortcut.activated.connect(win.switch_to_admin)

    win.show()
    logger.info("Uygulama başlatıldı")

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
