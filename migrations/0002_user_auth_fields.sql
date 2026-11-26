-- Apply once after 0001 to each database lacking these columns.
-- Existing accounts keep NULL hashes until a password is set.
BEGIN;
ALTER TABLE users
    ADD COLUMN password_hash TEXT,
    ADD COLUMN disabled BOOLEAN NOT NULL DEFAULT FALSE;
COMMIT;
