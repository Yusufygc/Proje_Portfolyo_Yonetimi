"""
infrastructure/logger.py — Merkezi logger kurulumu.
Her modülde: logger = logging.getLogger(__name__)
"""

import logging
from logging.handlers import RotatingFileHandler

from config import get_log_path


def setup_logger(name: str) -> logging.Logger:
    """Modül adıyla çağrılan logger döner; console + dosya handler ekler."""
    logger = logging.getLogger(name)

    if logger.handlers:
        # Aynı logger ikinci kez kurulmasın
        return logger

    logger.setLevel(logging.DEBUG)

    # ── Konsol handler (geliştirme) ──────────────────────────────────────────
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)

    # ── Dosya handler (production) — max 5 MB, 3 yedek ──────────────────────
    try:
        file_handler = RotatingFileHandler(
            get_log_path(),
            maxBytes=5_000_000,
            backupCount=3,
            encoding="utf-8",
        )
        file_handler.setLevel(logging.DEBUG)
    except OSError as e:
        logging.warning(f"Log dosyası açılamadı: {e}")
        file_handler = None

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    console.setFormatter(formatter)
    logger.addHandler(console)

    if file_handler:
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger
