"""tests/unit/test_project_service.py — Proje servisi unit testleri."""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../"))

import pytest
from unittest.mock import MagicMock

from services.project_service import ProjectService
from domain.models.project import Project, ProjectTag
from domain.enums.project_status import ProjectStatus
from domain.exceptions.domain_exceptions import ValidationError


@pytest.fixture
def project_service(project_repo, task_repo):
    storage = MagicMock()
    return ProjectService(project_repo, task_repo, storage)


def test_create_project_success(project_service):
    data = {"title": "Test Proje", "short_description": "Açıklama", "tags": ["Python", "PySide6"]}
    project = project_service.create(data)
    assert project.id is not None
    assert project.title == "Test Proje"
    assert len(project.tags) == 2


def test_create_project_empty_title_raises(project_service):
    with pytest.raises(ValidationError):
        project_service.create({"title": "  "})


def test_get_all_returns_list(project_service):
    project_service.create({"title": "Proje 1"})
    project_service.create({"title": "Proje 2"})
    projects = project_service.get_all()
    assert len(projects) >= 2


def test_update_project(project_service):
    project = project_service.create({"title": "Eski Başlık"})
    updated = project_service.update(project.id, {"title": "Yeni Başlık"})
    assert updated.title == "Yeni Başlık"


def test_delete_project(project_service):
    from domain.exceptions.domain_exceptions import NotFoundError
    project = project_service.create({"title": "Silinecek"})
    project_service.delete(project.id)
    with pytest.raises(NotFoundError):
        project_service.get_by_id(project.id)


def test_create_task(project_service):
    project = project_service.create({"title": "Proje"})
    task = project_service.create_task(project.id, {"title": "Task 1", "type": "GOREV"})
    assert task.id is not None
    assert task.title == "Task 1"


def test_create_task_empty_title_raises(project_service):
    project = project_service.create({"title": "Proje"})
    with pytest.raises(ValidationError):
        project_service.create_task(project.id, {"title": ""})


def test_featured_projects(project_service):
    project_service.create({"title": "Normal", "is_featured": False})
    project_service.create({"title": "Öne Çıkan", "is_featured": True})
    featured = project_service.get_featured()
    assert all(p.is_featured for p in featured)
