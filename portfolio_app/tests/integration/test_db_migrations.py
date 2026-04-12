"""tests/integration/test_db_migrations.py — Migration sistemi integration testleri."""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../"))

import pytest
from infrastructure.database.db_manager import DBManager


def test_migrations_run_on_init(test_db):
    """Migration tablosu oluşturulmuş olmalı."""
    row = test_db.fetch_one("SELECT * FROM schema_migrations WHERE version='001'")
    assert row is not None


def test_tables_exist(test_db):
    """Tüm tablolar oluşturulmuş olmalı."""
    tables = [
        "personal_info", "projects", "project_images",
        "project_tags", "project_tasks", "certificates", "resources",
    ]
    for table in tables:
        row = test_db.fetch_one(
            "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
            (table,),
        )
        assert row is not None, f"Tablo eksik: {table}"


def test_personal_info_initial_row(test_db):
    """Başlangıç kişisel bilgi satırı mevcut olmalı."""
    row = test_db.fetch_one("SELECT * FROM personal_info WHERE id=1")
    assert row is not None


def test_foreign_keys_enabled(test_db):
    """Foreign key kısıtları aktif olmalı."""
    result = test_db.fetch_one("PRAGMA foreign_keys")
    assert result[0] == 1
