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

import contextlib
import logging
import traceback
from typing import TYPE_CHECKING

import discord
from discord import app_commands as app

if TYPE_CHECKING:
    from bot import Winston

__log__ = logging.getLogger(__name__)


class CommandTree(app.CommandTree):
    """
    Represents the command tree, subclasses :class:`app.CommandTree` for
    applying global checks on slash commands and handle errors.
    """

    client: Winston

    async def interaction_check(self, interaction: discord.Interaction, /) -> bool:
        if interaction.guild is None:
            return False
        return True

    async def on_error(self, interaction: discord.Interaction, error: app.AppCommandError, /) -> None:
        """
        This callback that is called when any app command raises an error.

        This callback handles that error and sends an appropriate response
        or logs it in the error webhook if it is an unknown error.
        """
        send = interaction.followup.send if interaction.response.is_done() else interaction.response.send_message
        error = getattr(error, "original")

        # Unknown Error
        __log__.error(
            f"Something went wrong while trying to process command '{getattr(interaction.command, 'name', 'N/A')}'",
            exc_info=error,
        )

        embed = discord.Embed(color=discord.Color.red())
        embed.description = (
            "Something went wrong while trying to process your request. I have notified my developers. "
            f"\n\n```python\n{error.__class__.__name__}: {error}```"
        )

        embed.set_author(name=str(interaction.user), icon_url=interaction.user.display_avatar.url)

        with contextlib.suppress(discord.HTTPException, discord.Forbidden):
            await send(embed=embed)  # Send information to the app command invoker

        embed.remove_author()
        embed.title = f"Unexpected error in command {getattr(interaction.command, 'name', 'N/A')}"

        embed.description = (
            f"**User:** {interaction.user} | {interaction.user.id}\n"
            f"**Guild:** {interaction.guild} | {interaction.guild.id}\n\n"
            f"**Traceback:**\n```python\n{''.join(traceback.format_exception(error))}```"
        )

        with contextlib.suppress(discord.HTTPException, discord.Forbidden):
            await self.client.ERRORS_WEBHOOK.send(embed=embed)
