CREATE TABLE IF NOT EXISTS economy (
    User text PRIMARY KEY,
    Credits integer DEFAULT 100,
    Lock text DEFAULT CURRENT_TIMESTAMP
);
