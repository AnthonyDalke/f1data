CREATE TABLE IF NOT EXISTS sessions.events_denormalized (
    year SMALLINT NOT NULL,
    round SMALL INT NOT NULL,
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
    year SMALLINT PRIMARY KEY,
    round SMALL INT PRIMARY KEY,
    circuit_name TEXT NOT NULL
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