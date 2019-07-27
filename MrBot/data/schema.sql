CREATE TABLE IF NOT EXISTS user_config(
    key BIGINT PRIMARY KEY,
    background TEXT,
    timezone TIMESTAMPTZ,
    vote_time BIGINT,
    vote_count BIGINT,
    cash BIGINT,
    bank BIGINT
);

CREATE TABLE IF NOT EXISTS guild_config(
    key BIGINT PRIMARY KEY,
    logging_channel BIGINT,
    logging_enabled BOOLEAN,
    member_activity BOOLEAN,
    member_join BOOLEAN,
    member_leave BOOLEAN,
    member_nickname BOOLEAN,
    member_role BOOLEAN,
    member_status BOOLEAN,
    message_delete BOOLEAN,
    message_edit BOOLEAN,
    message_pin BOOLEAN,
    user_avatar BOOLEAN,
    user_discriminator BOOLEAN,
    user_username BOOLEAN,
    guild_name BOOLEAN,
    guild_region BOOLEAN,
    guild_afk_timeout BOOLEAN,
    guild_afk_channel BOOLEAN,
    guild_system_channel BOOLEAN,
    guild_icon BOOLEAN,
    guild_default_notifications BOOLEAN,
    guild_description BOOLEAN,
    guild_mfa_level BOOLEAN,
    guild_verification_level BOOLEAN,
    guild_explicit_content_filter BOOLEAN,
    guild_splash BOOLEAN
);

CREATE TABLE IF NOT EXISTS bot_stats(
    key BIGINT PRIMARY KEY,
    messages_seen BIGINT,
    messages_sent BIGINT,
    commands_run BIGINT
);



