"""domain/models/certificate.py — Sertifika entity."""

from dataclasses import dataclass
from typing import Optional


@dataclass
class Certificate:
    id: Optional[int]
    name: str
    issuer: str = ""
    date: Optional[str] = None
    verification_url: Optional[str] = None
    image_path: Optional[str] = None
    display_order: int = 0
