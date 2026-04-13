"""
styles/constants.py — Tüm renk, font, spacing sabitleri.
Widget'larda hardcode renk YASAK — buradan al.
"""

COLORS = {
    # Arka planlar — GitHub dark tema
    "bg_primary":    "#0D1117",
    "bg_secondary":  "#161B22",
    "bg_card":       "#161B22",
    "bg_glass":      "rgba(22, 27, 34, 0.7)",
    "bg_input":      "#0D1117",
    "bg_hover":      "#1C2128",
    "bg_active":     "#21262D",

    # Renk paleti
    "accent_blue":   "#2F81F7",
    "accent_blue_dark": "#388BFD",
    "accent_silver": "#B0BEC5",
    "text_primary":  "#E6EDF3",
    "text_secondary": "#8B949E",
    "text_muted":    "#484F58",
    "white":         "#FFFFFF",

    # Border
    "border":        "#30363D",
    "border_light":  "#21262D",
    "border_focus":  "#2F81F7",

    # Gradyanlar (vitrin bölüm geçişleri)
    "grad_about":    "qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #0D1117, stop:1 #161B22)",
    "grad_projects": "qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #161B22, stop:1 #0D1117)",
    "grad_vision":   "qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #0D1117, stop:1 #161B22)",
    "grad_certs":    "qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #161B22, stop:1 #0D1117)",
    "grad_hero":     "qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #0D1117, stop:0.5 #161B22, stop:1 #0D1117)",
    "grad_button":   "qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #388BFD, stop:1 #2F81F7)",
    "grad_sidebar":  "qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #0D1117, stop:1 #161B22)",

    # Durum renkleri
    "success":       "#3FB950",
    "success_dark":  "#2EA043",
    "warning":       "#D29922",
    "warning_dark":  "#BB8009",
    "error":         "#EF4444",
    "error_dark":    "#DC2626",
    "info":          "#2F81F7",

    # Tag / chip renkleri
    "tag_bg":        "rgba(47, 129, 247, 0.1)",
    "tag_border":    "rgba(47, 129, 247, 0.3)",
    "tag_text":      "#79C0FF",
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
