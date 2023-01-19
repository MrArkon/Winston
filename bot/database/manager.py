"""
Winston: Utilities & Moderation Tools for Discord
Copyright (C) 2023 MrArkon

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published
by the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""
from __future__ import annotations

import logging

import asyncpg

from .objects import LevelConfig, LevelRecord

__log__ = logging.getLogger(__name__)


class Manager:
    """
    Represents a database manager for the postgresql database. Contains
    various utilities and caching for obtaining data.
    """

    pool: asyncpg.Pool
    levels_cache: dict[int, LevelConfig] = {}

    @classmethod
    async def init(cls, host: str, user: str, database: str, password: str) -> None:
        try:
            pool = await asyncpg.create_pool(host=host, user=user, database=database, password=password)
        except Exception as exc:
            return __log__.error("Failed to instantiate the database manager.", exc_info=exc)

        assert pool is not None
        cls.pool = pool

        __log__.info("Instantiated database manager successfully.")

    @classmethod
    async def fetch_level_config(cls, user_id: int, guild_id: int) -> LevelConfig:
        record: LevelRecord = await cls.pool.fetchrow(
            """
            INSERT INTO levels (user_id, guild_id) 
            VALUES ($1, $2)
            ON CONFLICT (user_id, guild_id) DO UPDATE 
            SET user_id = excluded.user_id, guild_id = excluded.guild_id
            RETURNING *""",
            user_id,
            guild_id,
        )
        level_config = LevelConfig(record=record)

        cls.levels_cache[int(str(user_id) + str(guild_id))] = level_config
        return level_config

    @classmethod
    async def get_level_config(cls, user_id: int, guild_id: int) -> LevelConfig:

        if not (level_config := cls.levels_cache.get(int(str(user_id) + str(guild_id)))):
            level_config = await cls.fetch_level_config(user_id, guild_id)

        return level_config
