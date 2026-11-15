-- Fresh databases only. Run once in both development and test databases.

CREATE TABLE users (
    id         SERIAL PRIMARY KEY,
    username   VARCHAR NOT NULL,
    email      VARCHAR NOT NULL UNIQUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);
ALTER TABLE users ADD CONSTRAINT uk_users_username UNIQUE (username);

CREATE TABLE posts (
    id         SERIAL PRIMARY KEY,
    title      VARCHAR NOT NULL,
    content    VARCHAR NOT NULL,
    published  BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    user_id    INT NOT NULL REFERENCES users(id)
);

