import os
import urllib.request
import logging

logging.basicConfig(level=logging.INFO)

ICONS = [
    "layout-dashboard", "folder-open", "user", "award", "book-open",
    "plus", "edit-2", "trash-2", "x", "menu", "chevron-left", "chevron-right",
    "github", "external-link", "image", "check", "check-square", "lightbulb",
    "pen-tool", "arrow-left", "filter", "search", "refresh-cw", "alert-triangle",
    "info", "check-circle", "x-circle", "eye", "eye-off"
]

BASE_URL = "https://unpkg.com/lucide-static@latest/icons/{}.svg"

def download_icons():
    # portfolio_app/resources/icons dizinini bul
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    icons_dir = os.path.join(base_dir, "resources", "icons")
    os.makedirs(icons_dir, exist_ok=True)
    
    logging.info(f"Downloading icons to: {icons_dir}")
    
    for icon in ICONS:
        url = BASE_URL.format(icon)
        dest = os.path.join(icons_dir, f"{icon}.svg")
        try:
            urllib.request.urlretrieve(url, dest)
            logging.info(f"Downloaded: {icon}.svg")
        except Exception as e:
            logging.error(f"Failed to download {icon}.svg: {e}")

if __name__ == "__main__":
    download_icons()
