CREATE TABLE IF NOT EXISTS economy (
    User text PRIMARY KEY,
    Credits integer DEFAULT 100,
    Lock text DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO economy (User, Credits, Lock) VALUES ("bank", 0, NULL) ON CONFLICT DO NOTHING;
