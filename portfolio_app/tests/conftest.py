"""tests/conftest.py — Paylaşılan test fixture'ları."""

import pytest

from infrastructure.database.db_manager import DBManager


@pytest.fixture
def test_db():
    """Her test için temiz in-memory SQLite veritabanı."""
    # Singleton sıfırla (test izolasyonu)
    DBManager._instance = None
    manager = DBManager.initialize(":memory:")
    yield manager
    manager.close()
    DBManager._instance = None


@pytest.fixture
def project_repo(test_db):
    from infrastructure.repositories.project_repository import ProjectRepository
    return ProjectRepository(test_db)


@pytest.fixture
def task_repo(test_db):
    from infrastructure.repositories.task_repository import TaskRepository
    return TaskRepository(test_db)


@pytest.fixture
def cert_repo(test_db):
    from infrastructure.repositories.certificate_repository import CertificateRepository
    return CertificateRepository(test_db)


@pytest.fixture
def personal_info_repo(test_db):
    from infrastructure.repositories.personal_info_repository import PersonalInfoRepository
    return PersonalInfoRepository(test_db)


@pytest.fixture
def resource_repo(test_db):
    from infrastructure.repositories.resource_repository import ResourceRepository
    return ResourceRepository(test_db)
