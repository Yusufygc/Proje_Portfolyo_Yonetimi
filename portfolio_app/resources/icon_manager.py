"""resources/icon_manager.py — SVG ikon cache yöneticisi (offline, bundled)."""

import logging
from PySide6.QtGui import QIcon, QPixmap, QPainter, QColor
from PySide6.QtCore import QSize, QByteArray
from PySide6.QtSvg import QSvgRenderer

from config import get_resource_path
from styles.constants import COLORS

logger = logging.getLogger(__name__)


class IconManager:
    """İkonları dosyadan yükler ve cache'ler. İnternet bağlantısı gerekmez."""

    _cache: dict[str, QIcon] = {}

    @classmethod
    def get(cls, name: str, fallback: str = "", color: str = None) -> QIcon:
        """
        SVG ikonunu döner. Bulunamazsa fallback döner.
        color verilmezse, aktif temanın 'text_primary' rengini kullanır.
        """
        if color is None:
            color = COLORS["text_primary"]

        cache_key = f"{name}_{color}"
        
        if cache_key not in cls._cache:
            icon = cls._load_colored_svg(name, color)
            if icon.isNull() and fallback:
                icon = cls._load_colored_svg(fallback, color)
            cls._cache[cache_key] = icon
            
        return cls._cache[cache_key]

    @classmethod
    def _load_colored_svg(cls, name: str, color: str) -> QIcon:
        path = get_resource_path(f"resources/icons/{name}.svg")
        try:
            with open(path, "r", encoding="utf-8") as f:
                svg_content = f.read()
                
            # SVG içindeki currentColor'ı ve varsayılan siyah rengi hedef renge çevir
            svg_content = svg_content.replace('currentColor', color)
            svg_content = svg_content.replace('stroke="#000000"', f'stroke="{color}"')
            svg_content = svg_content.replace('fill="#000000"', f'fill="{color}"')
            
            # UI için yeterli yüksek çözünürlükte (64x64) render et
            renderer = QSvgRenderer(QByteArray(svg_content.encode('utf-8')))
            if not renderer.isValid():
                return QIcon()
                
            pixmap = QPixmap(64, 64)
            pixmap.fill(QColor(0, 0, 0, 0)) # şeffaf
            
            painter = QPainter(pixmap)
            painter.setRenderHint(QPainter.Antialiasing)
            painter.setRenderHint(QPainter.SmoothPixmapTransform)
            renderer.render(painter)
            painter.end()
            
            return QIcon(pixmap)
            
        except Exception as e:
            logger.error(f"İkon yüklenirken hata ({name}): {e}")
            return QIcon()

    @classmethod
    def get_pixmap(cls, name: str, size: int = 24, color: str = None) -> QPixmap:
        """İkonu QPixmap olarak döner."""
        icon = cls.get(name, color=color)
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
    SETTINGS    = "settings"
    SUN         = "sun"
    MOON        = "moon"
    PIN         = "map-pin"
