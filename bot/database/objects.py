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
from typing import TypedDict

import asyncpg

from bot import database


class LevelRecord(TypedDict):
    user_id: int
    guild_id: int
    messages: int
    experience: int


class LevelConfig:
    def __init__(self, record: LevelRecord) -> None:
        self.user_id = record["user_id"]
        self.guild_id = record["guild_id"]
        self.messages = record["messages"]
        self.experience = record["experience"]

    @property
    def level(self) -> int:
        """Returns the current level of a user from their total experience."""
        level = 0

        while (self.experience - self.get_experience(level)) >= self.get_required(level):
            level += 1

        return level

    def get_experience(self, level: int) -> int:
        """Returns the total experience required for reaching a certain level."""
        return (level**3) + (104 * level)

    def get_required(self, level: int) -> int:
        """Returns the experience required for reaching the next level."""
        return (3 * level**2) + (3 * level) + 105

    async def get_rank(self, pool: asyncpg.Pool) -> int:
        data = await pool.fetchrow(
            """
            SELECT * FROM ( 
                SELECT user_id, guild_id, row_number() OVER (ORDER BY experience DESC) AS rank 
                FROM levels
                WHERE guild_id = $2
            ) AS x 
            WHERE user_id = $1 AND guild_id = $2
            """,
            self.user_id,
            self.guild_id,
        )
        return data["rank"]

    async def set_experience(self, pool: asyncpg.Pool, experience: int) -> None:
        record: LevelRecord = await pool.fetchrow(
            "UPDATE levels SET experience = $1 WHERE user_id = $2 AND guild_id = $3 RETURNING experience",
            experience,
            self.user_id,
            self.guild_id,
        )

        self.experience = record["experience"]

        database.Manager.levels_cache[int(str(self.user_id) + str(self.guild_id))] = self

    async def set_messages(self, pool: asyncpg.Pool, messages: int) -> None:
        record: LevelRecord = await pool.fetchrow(
            "UPDATE levels SET messages = $1 WHERE user_id = $2 AND guild_id = $3 RETURNING messages",
            messages,
            self.user_id,
            self.guild_id,
        )

        self.messages = record["messages"]

        database.Manager.levels_cache[int(str(self.user_id) + str(self.guild_id))] = self
