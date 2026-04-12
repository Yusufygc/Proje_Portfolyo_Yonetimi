"""infrastructure/storage/image_storage.py — Görsel kaydetme/okuma/silme."""

import os
import shutil
import logging
from pathlib import Path

from config import get_data_path, SUPPORTED_IMAGE_FORMATS, MAX_IMAGE_SIZE_MB
from domain.exceptions.domain_exceptions import StorageError, ValidationError

logger = logging.getLogger(__name__)


class ImageStorage:
    """Görselleri data/images/ altında saklar."""

    def __init__(self):
        self._base_dir = get_data_path("images")
        os.makedirs(self._base_dir, exist_ok=True)

    def save_project_image(self, source_path: str, project_id: int) -> str:
        """Proje görselini kopyalar; path döner."""
        return self._save(source_path, f"projects/project_{project_id}")

    def save_profile_image(self, source_path: str) -> str:
        """Profil görselini kopyalar; path döner."""
        return self._save(source_path, "profile")

    def save_cert_image(self, source_path: str, cert_id: int) -> str:
        """Sertifika görselini kopyalar; path döner."""
        return self._save(source_path, f"certificates/cert_{cert_id}")

    def delete(self, stored_path: str) -> None:
        """Görsel dosyasını siler (relatif veya mutlak path kabul eder)."""
        full_path = self._full_path(stored_path)
        if os.path.exists(full_path):
            os.remove(full_path)
            logger.info(f"Görsel silindi: {full_path}")

    def _save(self, source_path: str, subdir: str) -> str:
        self._validate(source_path)
        dest_dir = os.path.join(self._base_dir, subdir)
        os.makedirs(dest_dir, exist_ok=True)
        filename = Path(source_path).name
        dest_path = os.path.join(dest_dir, filename)
        # Çakışma önleme
        if os.path.exists(dest_path):
            stem = Path(filename).stem
            suffix = Path(filename).suffix
            import time
            dest_path = os.path.join(dest_dir, f"{stem}_{int(time.time())}{suffix}")
        shutil.copy2(source_path, dest_path)
        logger.info(f"Görsel kaydedildi: {dest_path}")
        # data/ altındaki relatif path döner
        return os.path.relpath(dest_path, get_data_path())

    def _validate(self, path: str) -> None:
        p = Path(path)
        if not p.exists():
            raise StorageError(f"Dosya bulunamadı: {path}")
        if p.suffix.lower() not in SUPPORTED_IMAGE_FORMATS:
            raise ValidationError(f"Desteklenmeyen format: {p.suffix}")
        size_mb = p.stat().st_size / 1_000_000
        if size_mb > MAX_IMAGE_SIZE_MB:
            raise ValidationError(f"Dosya çok büyük: {size_mb:.1f} MB (max {MAX_IMAGE_SIZE_MB} MB)")

    def _full_path(self, stored_path: str) -> str:
        if os.path.isabs(stored_path):
            return stored_path
        return os.path.join(get_data_path(), stored_path)
