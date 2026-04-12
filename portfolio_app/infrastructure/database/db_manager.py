"""
infrastructure/database/db_manager.py — SQLite bağlantı + migration runner.
Singleton pattern: tek bağlantı, her açılışta migration kontrol.
"""

import sqlite3
import os
import logging

logger = logging.getLogger(__name__)


class DBManager:
    """SQLite bağlantı yöneticisi ve migration runner."""

    _instance: "DBManager | None" = None

    def __init__(self, db_path: str):
        self._db_path = db_path
        self._connection: sqlite3.Connection | None = None
        self._migrations_dir = os.path.join(
            os.path.dirname(__file__), "migrations"
        )

    # ── Singleton ────────────────────────────────────────────────────────────

    @classmethod
    def get_instance(cls) -> "DBManager":
        if cls._instance is None:
            raise RuntimeError("DBManager başlatılmamış. Önce DBManager(path) çağırın.")
        return cls._instance

    @classmethod
    def initialize(cls, db_path: str) -> "DBManager":
        if cls._instance is None:
            cls._instance = cls(db_path)
            cls._instance.connect()
            cls._instance.run_migrations()
            logger.info(f"DBManager başlatıldı: {db_path}")
        return cls._instance

    # ── Bağlantı ────────────────────────────────────────────────────────────

    def connect(self) -> None:
        parent = os.path.dirname(self._db_path)
        if parent:
            os.makedirs(parent, exist_ok=True)
        self._connection = sqlite3.connect(self._db_path, check_same_thread=False)
        self._connection.row_factory = sqlite3.Row
        self._connection.execute("PRAGMA foreign_keys=ON")
        self._connection.execute("PRAGMA journal_mode=WAL")
        logger.debug("Veritabanı bağlantısı açıldı.")

    def close(self) -> None:
        if self._connection:
            self._connection.close()
            self._connection = None
            logger.debug("Veritabanı bağlantısı kapatıldı.")

    @property
    def connection(self) -> sqlite3.Connection:
        if self._connection is None:
            raise RuntimeError("Veritabanı bağlantısı yok.")
        return self._connection

    # ── Migration runner ─────────────────────────────────────────────────────

    def run_migrations(self) -> None:
        """migrations/ klasöründeki eksik SQL dosyalarını sırayla uygular."""
        self._ensure_migration_table()
        applied = self._get_applied_versions()
        migration_files = sorted(
            f for f in os.listdir(self._migrations_dir)
            if f.endswith(".sql")
        )
        for filename in migration_files:
            version = filename.split("_")[0]
            if version not in applied:
                self._apply_migration(filename, version)

    def _ensure_migration_table(self) -> None:
        self.connection.execute("""
            CREATE TABLE IF NOT EXISTS schema_migrations (
                version    TEXT PRIMARY KEY,
                applied_at TEXT NOT NULL DEFAULT (datetime('now'))
            )
        """)
        self.connection.commit()

    def _get_applied_versions(self) -> set[str]:
        cursor = self.connection.execute("SELECT version FROM schema_migrations")
        return {row["version"] for row in cursor.fetchall()}

    def _apply_migration(self, filename: str, version: str) -> None:
        filepath = os.path.join(self._migrations_dir, filename)
        with open(filepath, encoding="utf-8") as f:
            sql = f.read()
        try:
            self.connection.executescript(sql)
            self.connection.commit()
            logger.info(f"Migration uygulandı: {filename}")
        except Exception:
            logger.exception(f"Migration başarısız: {filename}")
            raise

    # ── Yardımcı sorgular ───────────────────────────────────────────────────

    def execute(self, sql: str, params: tuple = ()) -> sqlite3.Cursor:
        cursor = self.connection.execute(sql, params)
        self.connection.commit()
        return cursor

    def fetch_one(self, sql: str, params: tuple = ()) -> sqlite3.Row | None:
        cursor = self.connection.execute(sql, params)
        return cursor.fetchone()

    def fetch_all(self, sql: str, params: tuple = ()) -> list[sqlite3.Row]:
        cursor = self.connection.execute(sql, params)
        return cursor.fetchall()
