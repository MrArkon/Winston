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
import asyncio
import logging
import os
import pathlib

import aiohttp
import discord
from discord.ext import commands

from bot import Plural, config, database, models

__log__ = logging.getLogger(__name__)


class Winston(commands.Bot):
    """
    Represents the main bot instance, subclasses :class:`commands.Bot` for utility functions shared between plugins.

    Parameters
    ----------
    loop: :class:`asyncio.AbstractEventLoop`
        The main running event loop.
    session: :class:`aiohttp.ClientSession`
        A seperate client session used for querying other APIs.
    """

    version: str

    def __init__(self, loop: asyncio.AbstractEventLoop, session: aiohttp.ClientSession) -> None:
        self.loop = loop
        self.session = session

        intents = discord.Intents(members=True, guilds=True, guild_messages=True, message_content=True)
        allowed_mentions = discord.AllowedMentions(everyone=False, users=True, roles=False, replied_user=False)
        activity = discord.Activity(name="the Tomfoolery Olympics", type=discord.ActivityType.competing)

        super().__init__(
            command_prefix=commands.when_mentioned,
            intents=intents,
            allowed_mentions=allowed_mentions,
            activity=activity,
            owner_ids=set(config.OWNER_IDS),
            help_command=None,
            max_messages=None,
            tree_cls=models.CommandTree,
        )

        self.ERRORS_WEBHOOK = discord.Webhook.from_url(config.ERRORS_WEBHOOK_URL, session=self.session)

    # Overrides
    async def setup_hook(self) -> None:
        await database.Manager.init(**config.DATABASE)

        plugins = ["jishaku"]

        # Load Files
        for f in os.listdir(f"./bot/plugins"):
            if f.endswith(".py"):
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
            f"Loaded {Plural(len(plugins) - failed):Plugin}"
            + (f" | Failed to load {Plural(failed):Plugin}" if failed else "")
        )

        return await super().setup_hook()

    async def close(self) -> None:
        try:
            await super().close()
        finally:
            await self.session.close()

    # Events
    async def on_ready(self) -> None:
        message = "Reconnected"

        if not hasattr(self, "uptime"):
            message = "Logged in"
            self.uptime = discord.utils.utcnow()

        assert self.user is not None
        __log__.info(f"{message} as {self.user} [ID: {self.user.id}] | Running Winston [Version: {self.version}]")
