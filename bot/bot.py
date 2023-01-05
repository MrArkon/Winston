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
import os
import pathlib

import discord
import tomli
from discord.ext import commands

from bot import config, models

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

        intents = discord.Intents(guilds=True, guild_messages=True)
        allowed_mentions = discord.AllowedMentions(everyone=False, users=True, roles=False, replied_user=False)

        super().__init__(
            command_prefix=commands.when_mentioned,
            intents=intents,
            allowed_mentions=allowed_mentions,
            owner_ids=set(config.OWNER_IDS),
            help_command=None,
            max_messages=None,
            tree_cls=models.CommandTree,
        )

    # Overrides
    async def setup_hook(self) -> None:
        plugins = ["jishaku"]

        # Load Files
        for f in os.listdir(f"./bot/plugins"):
            plugins.append(f"bot.plugins.{f[:-3]}")

        # Load Folders
        for path in pathlib.Path("./bot/plugins").glob("*/__init__.py"):
            plugins.append(str(path.parent).replace("/", ".").replace("\\", "."))

        __log__.debug(f"Plugins Detected: {', '.join(plugins)}")

        failed = 0
        for plugin in plugins:
            try:
                await self.load_extension(plugin)
            except Exception as exc:
                failed += 1
                __log__.error(f"Failed to load plugin '{plugin}'", exc_info=exc)

        __log__.info(
            f"Loaded {len(plugins) - failed} plugin(s)" + (f" | Failed to load {failed} plugin(s)" if failed else "")
        )

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
