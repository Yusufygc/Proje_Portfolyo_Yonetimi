"""styles/theme_manager.py — Uygulama tema yöneticisi."""

from typing import Dict, Any
from PySide6.QtCore import QObject, Signal, QCoreApplication
from PySide6.QtWidgets import QApplication, QWidget

class ThemeSignals(QObject):
    theme_changed = Signal(str)

class Theme:
    def __init__(self, name: str, colors: Dict[str, str]):
        self.name = name
        self.colors = colors

# --- DARK THEME (Varsayılan GitHub Dark) ---
DARK_COLORS = {
    "bg_primary":    "#0D1117",
    "bg_secondary":  "#161B22",
    "bg_card":       "#161B22",
    "bg_glass":      "rgba(22, 27, 34, 0.7)",
    "bg_input":      "#0D1117",
    "bg_hover":      "#1C2128",
    "bg_active":     "#21262D",
    "bg_sidebar":    "#010409",
    "bg_navbar":     "#010409",

    "accent_blue":   "#2F81F7",
    "accent_blue_dark": "#388BFD",
    "accent_silver": "#B0BEC5",
    "text_primary":  "#E6EDF3",
    "text_secondary": "#8B949E",
    "text_muted":    "#484F58",
    "white":         "#FFFFFF",

    "border":        "#30363D",
    "border_light":  "#21262D",
    "border_focus":  "#2F81F7",

    "grad_about":    "qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #0D1117, stop:1 #161B22)",
    "grad_projects": "qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #161B22, stop:1 #0D1117)",
    "grad_vision":   "qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #0D1117, stop:1 #161B22)",
    "grad_certs":    "qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #161B22, stop:1 #0D1117)",
    "grad_hero":     "qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #0D1117, stop:0.5 #161B22, stop:1 #0D1117)",
    "grad_button":   "qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #388BFD, stop:1 #2F81F7)",
    "grad_sidebar":  "qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #0D1117, stop:1 #161B22)",

    "success":       "#3FB950",
    "success_dark":  "#2EA043",
    "warning":       "#D29922",
    "warning_dark":  "#BB8009",
    "error":         "#EF4444",
    "error_dark":    "#DC2626",
    "info":          "#2F81F7",

    "tag_bg":        "rgba(47, 129, 247, 0.1)",
    "tag_border":    "rgba(47, 129, 247, 0.3)",
    "tag_text":      "#79C0FF",
}

# --- LIGHT THEME (GitHub Light) ---
LIGHT_COLORS = {
    "bg_primary":    "#F6F8FA",
    "bg_secondary":  "#FFFFFF",
    "bg_card":       "#FFFFFF",
    "bg_glass":      "rgba(255, 255, 255, 0.7)",
    "bg_input":      "#F6F8FA",
    "bg_hover":      "#F3F4F6",
    "bg_active":     "#E5E7EB",
    "bg_sidebar":    "#FFFFFF",
    "bg_navbar":     "#FFFFFF",

    "accent_blue":   "#0969DA",
    "accent_blue_dark": "#0349B4",
    "accent_silver": "#6E7781",
    "text_primary":  "#24292F",
    "text_secondary": "#57606A",
    "text_muted":    "#8C959F",
    "white":         "#FFFFFF",

    "border":        "#D0D7DE",
    "border_light":  "#E1E4E8",
    "border_focus":  "#0969DA",

    "grad_about":    "qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #F6F8FA, stop:1 #FFFFFF)",
    "grad_projects": "qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #FFFFFF, stop:1 #F6F8FA)",
    "grad_vision":   "qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #F6F8FA, stop:1 #FFFFFF)",
    "grad_certs":    "qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #FFFFFF, stop:1 #F6F8FA)",
    "grad_hero":     "qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #F6F8FA, stop:0.5 #FFFFFF, stop:1 #F6F8FA)",
    "grad_button":   "qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #0349B4, stop:1 #0969DA)",
    "grad_sidebar":  "qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #F6F8FA, stop:1 #FFFFFF)",

    "success":       "#2DA44E",
    "success_dark":  "#2C974B",
    "warning":       "#BF8700",
    "warning_dark":  "#9E6A03",
    "error":         "#CF222E",
    "error_dark":    "#A40E26",
    "info":          "#0969DA",

    "tag_bg":        "rgba(9, 105, 218, 0.1)",
    "tag_border":    "rgba(9, 105, 218, 0.3)",
    "tag_text":      "#0969DA",
}


class ThemeManager:
    _themes: Dict[str, Theme] = {
        "dark": Theme("dark", DARK_COLORS),
        "light": Theme("light", LIGHT_COLORS)
    }
    _current_theme_name: str = "dark"
    signals = ThemeSignals()

    @classmethod
    def register_theme(cls, theme: Theme):
        """Yeni bir tema eklemek için kullanılır."""
        cls._themes[theme.name] = theme

    @classmethod
    def load_saved_theme(cls):
        from utils.settings_manager import get_setting
        saved = get_setting("theme", "dark")
        if saved in cls._themes:
            cls._current_theme_name = saved

    @classmethod
    def set_theme(cls, name: str):
        """Aktif temayı değiştirir ve kaydeder."""
        if name in cls._themes:
            cls._current_theme_name = name
            from utils.settings_manager import set_setting
            set_setting("theme", name)
        else:
            raise ValueError(f"Bilinmeyen tema: {name}")

    @classmethod
    def toggle_theme(cls):
        """Temayı değiştirir ve restart atmadan arayüzü anlık günceller."""
        from resources.icon_manager import IconManager
        
        current = cls._current_theme_name
        new_theme = "light" if current == "dark" else "dark"
        cls.set_theme(new_theme)
        
        # İkon cache temizle (yeni metin renklerine göre üretilecek)
        IconManager.clear_cache()
        
        # Sinyali fırlat (custom event için dinleyenler olabilir)
        cls.signals.theme_changed.emit(new_theme)
        
        # Global ağaç taraması ile apply_theme çağrısı
        app = QApplication.instance()
        if app:
            for top_widget in app.topLevelWidgets():
                cls._refresh_widget_tree(top_widget)

    @classmethod
    def _refresh_widget_tree(cls, widget: QWidget):
        """Recursive widget tree taraması yaparak apply_theme metodu olanları tetikler."""
        if hasattr(widget, "apply_theme") and callable(widget.apply_theme):
            widget.apply_theme()
            
        for child in widget.findChildren(QWidget):
            if hasattr(child, "apply_theme") and callable(child.apply_theme):
                child.apply_theme()

    @classmethod
    def toggle_theme_and_restart(cls):
        """(Eski metod) Temayı değiştirir ve uygulamayı yeniden başlatır."""
        import sys
        from PySide6.QtCore import QProcess
        
        current = cls._current_theme_name
        new_theme = "light" if current == "dark" else "dark"
        cls.set_theme(new_theme)
        
        QProcess.startDetached(sys.executable, sys.argv)
        QCoreApplication.quit()

    @classmethod
    def get_current_theme(cls) -> Theme:
        return cls._themes[cls._current_theme_name]

    @classmethod
    def get_color(cls, color_key: str) -> str:
        """Aktif temanın istenen renk kodunu döndürür."""
        colors = cls.get_current_theme().colors
        return colors.get(color_key, "#FF00FF") # Hata ayıklama rengi (Magenta)
