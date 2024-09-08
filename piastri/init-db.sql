\c f1_db;
SET search_path TO sessions;

CREATE SCHEMA IF NOT EXISTS sessions;

CREATE TABLE IF NOT EXISTS events_denormalized (
    year SMALLINT NOT NULL,
    round SMALLINT NOT NULL,
    name_circuit TEXT NOT NULL,
    country_circuit TEXT NOT NULL,
    id_driver TEXT NOT NULL,
    name_driver_last TEXT NOT NULL,
    name_driver_first TEXT NOT NULL,
    name_team TEXT NOT NULL,
    session TEXT NOT NULL,
    position TEXT NOT NULL,
    time INTERVAL NULL, 
    PRIMARY KEY (year, round, id_driver, session)
);

CREATE TABLE IF NOT EXISTS events (
    year SMALLINT NOT NULL,
    round SMALLINT NOT NULL,
    name_circuit TEXT NOT NULL,
    PRIMARY KEY (year, round)
);

CREATE TABLE IF NOT EXISTS drivers (
    id_driver TEXT PRIMARY KEY,
    name_driver_last TEXT NOT NULL,
    name_driver_first TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS teams (
    name_team TEXT NOT NULL,
    year SMALLINT NOT NULL,
    id_driver TEXT NOT NULL,
    PRIMARY KEY (name_team, year)
);

CREATE TABLE IF NOT EXISTS circuits (
    name_circuit TEXT PRIMARY KEY,
    country_circuit TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS results (
    year SMALLINT NOT NULL,
    round SMALLINT NOT NULL,
    id_driver TEXT NOT NULL,
    name_team TEXT NOT NULL,
    session TEXT NOT NULL,
    position TEXT NOT NULL,
    time INTERVAL NULL,
    PRIMARY KEY (year, round, id_driver, session)
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

CREATE INDEX IF NOT EXISTS idx_t_y
    ON sessions.teams (year);

CREATE INDEX IF NOT EXISTS idx_c_n
    ON sessions.circuits (name_circuit);

CREATE INDEX IF NOT EXISTS idx_r_y
    ON sessions.results (year);

CREATE INDEX IF NOT EXISTS idx_r_r
    ON sessions.results (round);

CREATE INDEX IF NOT EXISTS idx_r_i
    ON sessions.results (id_driver);