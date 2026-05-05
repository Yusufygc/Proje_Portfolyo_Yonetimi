"""domain/models/project.py — Proje entity."""

from dataclasses import dataclass, field
from typing import Optional

from domain.enums.project_status import ProjectStatus


@dataclass
class ProjectTag:
    id: Optional[int]
    project_id: int
    tag_name: str


@dataclass
class ProjectImage:
    id: Optional[int]
    project_id: int
    image_path: str
    caption: str = ""
    display_order: int = 0


@dataclass
class Project:
    id: Optional[int]
    title: str
    short_description: str = ""
    full_description: str = ""
    status: ProjectStatus = ProjectStatus.DEVAM_EDIYOR
    github_url: Optional[str] = None
    demo_url: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    is_featured: bool = False
    display_order: int = 0
    role_in_project: str = ""
    created_at: str = ""
    tags: list[ProjectTag] = field(default_factory=list)
    images: list[ProjectImage] = field(default_factory=list)
