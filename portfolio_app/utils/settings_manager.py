"""utils/settings_manager.py — Basit uygulama ayarları yöneticisi."""
import json
import os
from config import get_resource_path

SETTINGS_FILE = get_resource_path("settings.json")

def load_settings() -> dict:
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def save_settings(settings: dict):
    with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
        json.dump(settings, f, indent=4)

def get_setting(key: str, default=None):
    return load_settings().get(key, default)

def set_setting(key: str, value):
    settings = load_settings()
    settings[key] = value
    save_settings(settings)
