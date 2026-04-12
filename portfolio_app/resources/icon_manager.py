"""resources/icon_manager.py — SVG ikon cache yöneticisi (offline, bundled)."""

import logging
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtCore import QSize

from config import get_resource_path

logger = logging.getLogger(__name__)


class IconManager:
    """İkonları dosyadan yükler ve cache'ler. İnternet bağlantısı gerekmez."""

    _cache: dict[str, QIcon] = {}

    @classmethod
    def get(cls, name: str, fallback: str = "") -> QIcon:
        """SVG ikonunu döner. Bulunamazsa boş QIcon döner."""
        if name not in cls._cache:
            path = get_resource_path(f"resources/icons/{name}.svg")
            icon = QIcon(path)
            if icon.isNull() and fallback:
                path = get_resource_path(f"resources/icons/{fallback}.svg")
                icon = QIcon(path)
            cls._cache[name] = icon
        return cls._cache[name]

    @classmethod
    def get_pixmap(cls, name: str, size: int = 24) -> QPixmap:
        """İkonu QPixmap olarak döner."""
        icon = cls.get(name)
        return icon.pixmap(QSize(size, size))

    @classmethod
    def clear_cache(cls) -> None:
        cls._cache.clear()


# Sık kullanılan ikon adları — resources/icons/*.svg ile eşleşmeli
class Icons:
    DASHBOARD   = "layout-dashboard"
    PROJECTS    = "folder-open"
    PERSON      = "user"
    CERTIFICATE = "award"
    RESOURCES   = "book-open"
    ADD         = "plus"
    EDIT        = "edit-2"
    DELETE      = "trash-2"
    CLOSE       = "x"
    MENU        = "menu"
    ARROW_LEFT  = "chevron-left"
    ARROW_RIGHT = "chevron-right"
    GITHUB      = "github"
    LINK        = "external-link"
    IMAGE       = "image"
    CHECK       = "check"
    TASK        = "check-square"
    IDEA        = "lightbulb"
    DESIGN      = "pen-tool"
    BACK        = "arrow-left"
    FILTER      = "filter"
    SEARCH      = "search"
    REFRESH     = "refresh-cw"
    WARNING     = "alert-triangle"
    INFO        = "info"
    SUCCESS     = "check-circle"
    ERROR       = "x-circle"
    EYE         = "eye"
    EYE_OFF     = "eye-off"
