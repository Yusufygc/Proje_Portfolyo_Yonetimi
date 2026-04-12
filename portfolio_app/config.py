"""
config.py — Uygulama sabitleri, path yönetimi, versiyon.
Tüm path'ler buradan geçer: get_resource_path() veya get_data_path().
"""

import sys
import os

# ─── Versiyon ────────────────────────────────────────────────────────────────
APP_NAME = "Portfolio Manager"
APP_VERSION = "1.0.0"

# ─── Admin erişim PIN'i ───────────────────────────────────────────────────────
# Gizli klavye sekansı: Ctrl+Shift+A tuş kombinasyonu
ADMIN_KEY_SEQUENCE = "Ctrl+Shift+A"
# Alternatif: başlık çubuğuna 5 kez çift tıklama
ADMIN_CLICK_COUNT = 5

# ─── DB ──────────────────────────────────────────────────────────────────────
DB_FILENAME = "portfolio.db"

# ─── Görsel limitleri ─────────────────────────────────────────────────────────
MAX_IMAGE_SIZE_MB = 10
SUPPORTED_IMAGE_FORMATS = [".jpg", ".jpeg", ".png", ".webp", ".gif"]
AVATAR_SIZE = (300, 300)
PROJECT_IMAGE_MAX_WIDTH = 1200

# ─── UI ──────────────────────────────────────────────────────────────────────
WINDOW_MIN_WIDTH = 1200
WINDOW_MIN_HEIGHT = 700
SIDEBAR_WIDTH_EXPANDED = 240
SIDEBAR_WIDTH_COLLAPSED = 56
NAVBAR_HEIGHT = 64
ANIMATION_DURATION_MS = 300


# ─── Path yönetimi ───────────────────────────────────────────────────────────

def get_resource_path(relative_path: str) -> str:
    """
    PyInstaller bundle veya normal çalışma için doğru resource path döner.
    resources/ ve styles/ için kullan.
    """
    if hasattr(sys, '_MEIPASS'):
        base = sys._MEIPASS  # PyInstaller temp dizini
    else:
        base = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base, relative_path)


def get_data_path(relative_path: str = "") -> str:
    """
    Kullanıcı verisi (DB, görseller) için path döner.
    EXE yanındaki data/ dizinine işaret eder.
    """
    if hasattr(sys, '_MEIPASS'):
        base = os.path.dirname(sys.executable)
    else:
        base = os.path.dirname(os.path.abspath(__file__))
    if relative_path:
        return os.path.join(base, "data", relative_path)
    return os.path.join(base, "data")


def get_log_path() -> str:
    """Log dizini path'i döner, yoksa oluşturur."""
    if hasattr(sys, '_MEIPASS'):
        base = os.path.dirname(sys.executable)
    else:
        base = os.path.dirname(os.path.abspath(__file__))
    log_dir = os.path.join(base, "logs")
    os.makedirs(log_dir, exist_ok=True)
    return os.path.join(log_dir, "app.log")


def get_db_path() -> str:
    """SQLite veritabanı path'i döner, data/ dizinini oluşturur."""
    data_dir = get_data_path()
    os.makedirs(data_dir, exist_ok=True)
    return os.path.join(data_dir, DB_FILENAME)
