-- portfolio_app/infrastructure/database/migrations/004_add_hobbies.sql
ALTER TABLE personal_info ADD COLUMN hobbies TEXT DEFAULT '';
