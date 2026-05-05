-- 005_add_phone_role_edu_exp.sql
-- PersonalInfo'ya phone, Project'e role_in_project,
-- Education ve Experience tabloları eklenir.

PRAGMA foreign_keys=ON;

-- PersonalInfo: phone alanı ekle
ALTER TABLE personal_info ADD COLUMN phone TEXT;

-- Projects: role_in_project alanı ekle
ALTER TABLE projects ADD COLUMN role_in_project TEXT NOT NULL DEFAULT '';

-- Eğitim tablosu
CREATE TABLE IF NOT EXISTS education (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    institution  TEXT NOT NULL,
    degree       TEXT NOT NULL DEFAULT '',
    field        TEXT NOT NULL DEFAULT '',
    start_date   TEXT NOT NULL DEFAULT '',
    end_date     TEXT,
    description  TEXT,
    display_order INTEGER NOT NULL DEFAULT 0,
    created_at   TEXT NOT NULL DEFAULT (datetime('now'))
);

-- İş deneyimi tablosu
CREATE TABLE IF NOT EXISTS experience (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    company      TEXT NOT NULL,
    position     TEXT NOT NULL DEFAULT '',
    start_date   TEXT NOT NULL DEFAULT '',
    end_date     TEXT,
    description  TEXT,
    is_current   INTEGER NOT NULL DEFAULT 0,
    display_order INTEGER NOT NULL DEFAULT 0,
    created_at   TEXT NOT NULL DEFAULT (datetime('now'))
);

