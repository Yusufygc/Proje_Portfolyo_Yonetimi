"""domain/models/personal_info.py — Kişisel bilgi entity (tek satır, id=1)."""

from dataclasses import dataclass
from typing import Optional


@dataclass
class PersonalInfo:
    id: int = 1
    full_name: str = ""
    title: str = ""
    bio: str = ""
    avatar_path: Optional[str] = None
    github_url: Optional[str] = None
    linkedin_url: Optional[str] = None
    website_url: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    vision_text: str = ""
    mission_text: str = ""
    hobbies: str = ""
    updated_at: str = ""
