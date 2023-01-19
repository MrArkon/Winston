CREATE TABLE IF NOT EXISTS levels (
    user_id BIGINT NOT NULL,
    guild_id BIGINT NOT NULL,

    PRIMARY KEY (user_id, guild_id),

    messages INT DEFAULT 0,
    experience INT DEFAULT 0
);

CREATE INDEX IF NOT EXISTS levels_guild_id_user_id_idx ON levels (user_id, guild_id);