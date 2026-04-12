-- 001_initial.sql — İlk şema
-- Tüm tablolar burada oluşturulur.

PRAGMA journal_mode=WAL;
PRAGMA foreign_keys=ON;

-- Migration takibi
CREATE TABLE IF NOT EXISTS schema_migrations (
    version    TEXT PRIMARY KEY,
    applied_at TEXT NOT NULL DEFAULT (datetime('now'))
);

-- Kişisel bilgiler (tek satır, id=1)
CREATE TABLE IF NOT EXISTS personal_info (
    id            INTEGER PRIMARY KEY,
    full_name     TEXT NOT NULL DEFAULT '',
    title         TEXT NOT NULL DEFAULT '',
    bio           TEXT NOT NULL DEFAULT '',
    avatar_path   TEXT,
    github_url    TEXT,
    linkedin_url  TEXT,
    website_url   TEXT,
    email         TEXT,
    vision_text   TEXT NOT NULL DEFAULT '',
    mission_text  TEXT NOT NULL DEFAULT '',
    updated_at    TEXT NOT NULL DEFAULT (datetime('now'))
);

-- Başlangıç kişisel bilgi satırı
INSERT OR IGNORE INTO personal_info (id, full_name, title, bio, vision_text, mission_text)
VALUES (1, 'Ad Soyad', 'Yazılım Geliştirici', 'Hakkımda kısa açıklama.', 'Vizyon metni.', 'Misyon metni.');

-- Projeler
CREATE TABLE IF NOT EXISTS projects (
    id                INTEGER PRIMARY KEY AUTOINCREMENT,
    title             TEXT NOT NULL,
    short_description TEXT NOT NULL DEFAULT '',
    full_description  TEXT NOT NULL DEFAULT '',
    status            TEXT NOT NULL DEFAULT 'DEVAM_EDIYOR',
    github_url        TEXT,
    demo_url          TEXT,
    start_date        TEXT,
    end_date          TEXT,
    is_featured       INTEGER NOT NULL DEFAULT 0,
    display_order     INTEGER NOT NULL DEFAULT 0,
    created_at        TEXT NOT NULL DEFAULT (datetime('now'))
);

-- Proje görselleri
CREATE TABLE IF NOT EXISTS project_images (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id    INTEGER NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    image_path    TEXT NOT NULL,
    caption       TEXT,
    display_order INTEGER NOT NULL DEFAULT 0
);

-- Proje teknoloji etiketleri
CREATE TABLE IF NOT EXISTS project_tags (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    tag_name   TEXT NOT NULL
);

-- Proje task'leri
CREATE TABLE IF NOT EXISTS project_tasks (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id    INTEGER NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    type          TEXT NOT NULL DEFAULT 'GOREV',
    title         TEXT NOT NULL,
    description   TEXT,
    status        TEXT NOT NULL DEFAULT 'BEKLIYOR',
    display_order INTEGER NOT NULL DEFAULT 0,
    created_at    TEXT NOT NULL DEFAULT (datetime('now'))
);

-- Sertifikalar
CREATE TABLE IF NOT EXISTS certificates (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    name             TEXT NOT NULL,
    issuer           TEXT NOT NULL DEFAULT '',
    date             TEXT,
    verification_url TEXT,
    image_path       TEXT,
    display_order    INTEGER NOT NULL DEFAULT 0
);

-- Kaynaklar
CREATE TABLE IF NOT EXISTS resources (
    id                 INTEGER PRIMARY KEY AUTOINCREMENT,
    type               TEXT NOT NULL DEFAULT 'KURS',
    title              TEXT NOT NULL,
    url                TEXT,
    notes              TEXT,
    status             TEXT NOT NULL DEFAULT 'PLANLI',
    related_project_id INTEGER REFERENCES projects(id) ON DELETE SET NULL,
    created_at         TEXT NOT NULL DEFAULT (datetime('now'))
);

-- Bu migration'ı kayıt et
INSERT OR IGNORE INTO schema_migrations (version) VALUES ('001');
