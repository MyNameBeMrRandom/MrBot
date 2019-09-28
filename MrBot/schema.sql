CREATE TABLE IF NOT EXISTS user_config(
    key BIGINT PRIMARY KEY,
    background TEXT,
    voted BOOLEAN,
    vote_claimed BOOLEAN,
    vote_count BIGINT,
    cash BIGINT,
    bank BIGINT
);

CREATE TABLE IF NOT EXISTS guild_config(
    key BIGINT PRIMARY KEY
);

CREATE TABLE IF NOT EXISTS kross_config(
    key TEXT PRIMARY KEY,
    points BIGINT
);

CREATE TABLE IF NOT EXISTS user_blacklist(
    id BIGINT PRIMARY KEY,
    reason TEXT
);

CREATE TABLE IF NOT EXISTS guild_blacklist(
    id BIGINT PRIMARY KEY,
    reason TEXT
);



