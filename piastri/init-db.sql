CREATE SCHEMA sessions;

CREATE TABLE IF NOT EXISTS sessions.events_denormalized (
    year SMALLINT NOT NULL,
    round SMALLINT NOT NULL,
    circuit_name TEXT NOT NULL,
    circuit_country TEXT NOT NULL,
    id_driver TEXT NOT NULL,
    name_driver_last TEXT NOT NULL,
    name_driver_first TEXT NOT NULL,
    name_team TEXT NOT NULL,
    session TEXT NOT NULL,
    position TEXT NOT NULL,
    time INTERVAL NULL
);

CREATE TABLE IF NOT EXISTS sessions.events (
    year SMALLINT NOT NULL,
    round SMALLINT NOT NULL,
    circuit_name TEXT NOT NULL,
    PRIMARY KEY (year, round)
);

CREATE TABLE IF NOT EXISTS sessions.drivers (
    id_driver TEXT PRIMARY KEY,
    name_last TEXT NOT NULL,
    name_first TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS sessions.teams (
    name_team TEXT PRIMARY KEY,
    year SMALLINT NOT NULL,
    id_driver TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS sessions.circuits (
    circuit_name TEXT PRIMARY KEY,
    circuit_country TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS sessions.results (
    year SMALLINT NOT NULL,
    round SMALLINT NOT NULL,
    id_driver TEXT NOT NULL,
    name_team TEXT NOT NULL,
    session TEXT NOT NULL,
    position TEXT NOT NULL,
    time INTERVAL NULL
);

CREATE INDEX IF NOT EXISTS idx_ed_y
    ON sessions.events_denormalized (year);

CREATE INDEX IF NOT EXISTS idx_ed_r
    ON sessions.events_denormalized (round);

CREATE INDEX IF NOT EXISTS idx_ed_d
    ON sessions.events_denormalized (id_driver);

CREATE INDEX IF NOT EXISTS idx_ed_t
    ON sessions.events_denormalized (name_team);

CREATE INDEX IF NOT EXISTS idx_ed_s
    ON sessions.events_denormalized (session);

CREATE INDEX IF NOT EXISTS idx_e_y
    ON sessions.events (year);

CREATE INDEX IF NOT EXISTS idx_e_r
    ON sessions.events (round);

CREATE INDEX IF NOT EXISTS idx_d_i
    ON sessions.drivers (id_driver);

CREATE INDEX IF NOT EXISTS idx_t_n
    ON sessions.teams (name_team);

CREATE INDEX IF NOT EXISTS idx_c_n
    ON sessions.circuits (circuit_name);