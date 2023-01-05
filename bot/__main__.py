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
import sys
from contextlib import suppress

import discord

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


async def start() -> None:
    # Setup Logging
    discord.utils.setup_logging(level=logging.INFO)

    logging.getLogger("discord").setLevel(logging.WARNING)
    logging.getLogger("discord.http").setLevel(logging.WARNING)

    # Setup Bot Instance
    loop: asyncio.AbstractEventLoop = asyncio.get_event_loop()

    try:
        bot = Winston(loop=loop)
    except Exception as exc:
        return __log__.warn("Failed to instantiate Winston", exc_info=exc)

    # Launching the Bot
    async with bot:
        await bot.start(config.TOKEN)


with suppress(KeyboardInterrupt):
    asyncio.run(start())
