"""styles/theme_engine.py — QSS şablonlarını runtime'da işler."""

import os
import logging

from config import get_resource_path
from styles.constants import COLORS, FONTS, SPACING, RADIUS

logger = logging.getLogger(__name__)


class ThemeEngine:
    """QSS dosyalarını yükler ve COLORS/FONTS değişkenlerini enjekte eder."""

    _cache: dict[str, str] = {}

    @classmethod
    def load_theme(cls, theme_name: str = "silver_blue") -> str:
        """Ana tema QSS'ini döner."""
        if theme_name in cls._cache:
            return cls._cache[theme_name]
        path = get_resource_path(f"styles/themes/{theme_name}.qss")
        qss = cls._load_file(path)
        qss = cls._inject_variables(qss)
        cls._cache[theme_name] = qss
        return qss

    @classmethod
    def load_component(cls, component_name: str) -> str:
        """Bileşen QSS'ini döner (button, card, sidebar, navbar)."""
        key = f"component_{component_name}"
        if key in cls._cache:
            return cls._cache[key]
        path = get_resource_path(f"styles/components/{component_name}.qss")
        qss = cls._load_file(path)
        qss = cls._inject_variables(qss)
        cls._cache[key] = qss
        return qss

    @classmethod
    def get_full_stylesheet(cls) -> str:
        """Tüm QSS bileşenlerini birleştirip döner."""
        parts = [cls.load_theme()]
        for component in ["button", "card", "sidebar", "navbar"]:
            try:
                parts.append(cls.load_component(component))
            except FileNotFoundError:
                logger.warning(f"Component QSS bulunamadı: {component}")
        return "\n".join(parts)

    @staticmethod
    def _load_file(path: str) -> str:
        if not os.path.exists(path):
            raise FileNotFoundError(f"QSS dosyası bulunamadı: {path}")
        with open(path, encoding="utf-8") as f:
            return f.read()

    @staticmethod
    def _inject_variables(qss: str) -> str:
        """{{VAR_NAME}} kalıplarını constants.py değerleriyle değiştirir."""
        replacements = {}
        for k, v in COLORS.items():
            replacements[f"{{{{COLOR_{k.upper()}}}}}"] = v
        for k, v in FONTS.items():
            if isinstance(v, int):
                replacements[f"{{{{FONT_{k.upper()}}}}}"] = str(v)
            else:
                replacements[f"{{{{FONT_{k.upper()}}}}}"] = v
        for k, v in SPACING.items():
            replacements[f"{{{{SPACING_{k.upper()}}}}}"] = str(v)
        for k, v in RADIUS.items():
            replacements[f"{{{{RADIUS_{k.upper()}}}}}"] = str(v)
        for placeholder, value in replacements.items():
            qss = qss.replace(placeholder, value)
        return qss
