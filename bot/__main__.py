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
import sys
from contextlib import suppress

import aiohttp
import discord
import tomli

from bot import Winston, config

try:
    import uvloop  # type: ignore
except ImportError:
    pass
else:
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

__log__ = logging.getLogger(__name__)


if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

discord.VoiceClient.warn_nacl = False

os.environ["JISHAKU_NO_UNDERSCORE"] = "True"
os.environ["JISHAKU_NO_DM_TRACEBACK"] = "True"


async def start() -> None:
    # Setup Logging
    discord.utils.setup_logging(level=logging.INFO)

    logging.getLogger("discord").setLevel(logging.WARNING)
    logging.getLogger("discord.http").setLevel(logging.WARNING)

    # Setup Bot Instance
    loop = asyncio.get_event_loop()

    with open("./pyproject.toml", "rb") as f:
        version = tomli.load(f)["tool"]["poetry"]["version"]

    session = aiohttp.ClientSession(headers={"User-Agent": f"Winston/{version} (https://github.com/MrArkon/Winston)"})

    try:
        bot = Winston(loop=loop, session=session)
    except Exception as exc:
        return __log__.warn("Failed to instantiate Winston", exc_info=exc)

    bot.version = version

    # Launching the Bot
    async with bot, session:
        await bot.start(config.TOKEN)


with suppress(KeyboardInterrupt):
    asyncio.run(start())
