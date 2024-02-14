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