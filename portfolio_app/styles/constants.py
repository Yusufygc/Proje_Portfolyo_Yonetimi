"""
styles/constants.py — Tüm renk, font, spacing sabitleri.
Widget'larda hardcode renk YASAK — buradan al.
"""

COLORS = {
    # Arka planlar
    "bg_primary":    "#0F1923",   # Koyu lacivert-siyah
    "bg_secondary":  "#162030",
    "bg_card":       "#1C2A3A",
    "bg_glass":      "rgba(28, 42, 58, 0.7)",
    "bg_input":      "#1A2535",
    "bg_hover":      "#243447",
    "bg_active":     "#2A3D52",

    # Silver/Blue/White ton sistemi
    "accent_blue":   "#4A9EFF",
    "accent_blue_dark": "#2D7DD2",
    "accent_silver": "#B0BEC5",
    "text_primary":  "#E8EDF2",
    "text_secondary": "#8CA0B3",
    "text_muted":    "#4A5C6E",
    "white":         "#FFFFFF",

    # Border
    "border":        "#243447",
    "border_light":  "#2D4057",
    "border_focus":  "#4A9EFF",

    # Gradyanlar (vitrin bölüm geçişleri)
    "grad_about":    "qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #0F1923, stop:1 #162030)",
    "grad_projects": "qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #162030, stop:1 #0D1F2D)",
    "grad_vision":   "qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #0D1F2D, stop:1 #111827)",
    "grad_certs":    "qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #111827, stop:1 #0F1923)",
    "grad_hero":     "qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #0F1923, stop:0.5 #162030, stop:1 #0D1F2D)",
    "grad_button":   "qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #5AADFF, stop:1 #4A9EFF)",
    "grad_sidebar":  "qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #0D1620, stop:1 #0F1923)",

    # Durum renkleri
    "success":       "#4CAF7D",
    "success_dark":  "#3A8F61",
    "warning":       "#F59E0B",
    "warning_dark":  "#D97706",
    "error":         "#EF4444",
    "error_dark":    "#DC2626",
    "info":          "#4A9EFF",

    # Tag / chip renkleri
    "tag_bg":        "#1E3348",
    "tag_border":    "#2D5070",
    "tag_text":      "#7EB8FF",
}

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
