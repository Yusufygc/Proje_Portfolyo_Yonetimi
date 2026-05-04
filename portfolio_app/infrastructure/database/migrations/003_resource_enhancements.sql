-- 003_resource_enhancements.sql — Kaynak yönetim merkezi geliştirmeleri
-- Dinamik kaynak türleri, etiketler, öncelik, ilerleme, pin desteği

PRAGMA foreign_keys=ON;

-- ─── Dinamik Kaynak Türleri Tablosu ────────────────────────────────────────
CREATE TABLE IF NOT EXISTS resource_types (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    name          TEXT NOT NULL UNIQUE,
    color         TEXT NOT NULL DEFAULT '#2F81F7',
    emoji         TEXT NOT NULL DEFAULT '📄',
    display_order INTEGER NOT NULL DEFAULT 0,
    created_at    TEXT NOT NULL DEFAULT (datetime('now'))
);

-- Mevcut 5 türü seed olarak ekle
INSERT OR IGNORE INTO resource_types (name, color, emoji, display_order) VALUES
    ('Kurs',  '#2F81F7', '📚', 1),
    ('Video', '#FF6B6B', '🎬', 2),
    ('Repo',  '#3FB950', '🗂', 3),
    ('Not',   '#D29922', '📝', 4),
    ('Plan',  '#B0BEC5', '🗺', 5);

-- ─── Resources tablosuna yeni sütunlar ─────────────────────────────────────
ALTER TABLE resources ADD COLUMN priority TEXT NOT NULL DEFAULT 'MEDIUM';
ALTER TABLE resources ADD COLUMN progress INTEGER NOT NULL DEFAULT 0;
ALTER TABLE resources ADD COLUMN is_pinned INTEGER NOT NULL DEFAULT 0;

-- ─── Kaynak Etiketleri Tablosu ─────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS resource_tags (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    resource_id INTEGER NOT NULL REFERENCES resources(id) ON DELETE CASCADE,
    tag_name    TEXT NOT NULL
);

-- ─── Mevcut kaynakların tür adlarını güncelle (eski enum → yeni isim) ────
UPDATE resources SET type = 'Kurs'  WHERE type = 'KURS';
UPDATE resources SET type = 'Video' WHERE type = 'VIDEO';
UPDATE resources SET type = 'Repo'  WHERE type = 'REPO';
UPDATE resources SET type = 'Not'   WHERE type = 'NOT';
UPDATE resources SET type = 'Plan'  WHERE type = 'PLAN';

-- Bu migration'ı kayıt et
INSERT OR IGNORE INTO schema_migrations (version) VALUES ('003');
