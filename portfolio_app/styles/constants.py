"""
styles/constants.py — Tüm renk, font, spacing sabitleri.
Widget'larda hardcode renk YASAK — buradan al.
"""

from styles.theme_manager import ThemeManager

class ActiveThemeProxy:
    """
    Tüm arayüzlerin COLORS['key'] şeklinde kullandığı yapıya dinamik yanıt verir.
    Tema değiştiğinde otomatik olarak güncel rengi döndürür.
    """
    def __getitem__(self, key: str) -> str:
        return ThemeManager.get_color(key)
        
    def get(self, key: str, default: str = None) -> str:
        color = ThemeManager.get_color(key)
        if color == "#FF00FF":  # theme_manager'daki fallback rengi ise
            return default if default is not None else color
        return color

    def items(self):
        return ThemeManager.get_current_theme().colors.items()

    def get_dict(self) -> dict:
        return ThemeManager.get_current_theme().colors

COLORS = ActiveThemeProxy()

FONTS = {
    "family_primary": "Segoe UI",
    "family_mono":    "Consolas",
    "family_heading": "Segoe UI",

    "size_xs":   10,
    "size_sm":   12,
    "size_base": 14,
    "size_md":   16,
    "size_lg":   20,
    "size_xl":   24,
    "size_2xl":  32,
    "size_3xl":  48,

    "weight_normal": 400,
    "weight_medium": 500,
    "weight_bold":   700,
}

SPACING = {
    "xs":  4,
    "sm":  8,
    "md":  16,
    "lg":  24,
    "xl":  32,
    "2xl": 48,
    "3xl": 64,
}

RADIUS = {
    "sm":  4,
    "md":  8,
    "lg":  12,
    "xl":  16,
    "full": 999,
}

SHADOWS = {
    "card":   "0 4px 24px rgba(0,0,0,0.4)",
    "glass":  "0 8px 32px rgba(0,0,0,0.5)",
    "button": "0 2px 8px rgba(74,158,255,0.3)",
}
