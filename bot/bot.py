"""
Winston: Discord Utility Bot
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
import asyncio
import logging

import discord
import tomli
from discord.ext import commands

__log__ = logging.getLogger(__name__)


class Winston(commands.Bot):
    """
    Represents the main bot instance, subclasses :class:`commands.Bot` for utility functions shared between plugins.

    Parameters
    ----------
    loop: :class:`AbstractEventLoop`
        The main running event loop.
    """

    def __init__(self, loop: asyncio.AbstractEventLoop) -> None:
        self.loop = loop

        intents = discord.Intents(guilds=True)
        allowed_mentions = discord.AllowedMentions(everyone=False, users=True, roles=False, replied_user=False)

        super().__init__(
            command_prefix=commands.when_mentioned,
            intents=intents,
            allowed_mentions=allowed_mentions,
            help_command=None,
            max_messages=None,
        )

    # Overrides
    async def setup_hook(self) -> None:
        with open("./pyproject.toml", "rb") as f:
            self.version = tomli.load(f)["tool"]["poetry"]["version"]

        return await super().setup_hook()

    # Events
    async def on_ready(self) -> None:
        message = "Reconnected"

        if not hasattr(self, "uptime"):
            message = "Logged in"
            self.uptime = discord.utils.utcnow()

        assert self.user is not None
        __log__.info(f"{message} as {self.user} [ID: {self.user.id}] | Running Winston [Version: {self.version}]")
