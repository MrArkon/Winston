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
from contextlib import suppress

import discord


class View(discord.ui.View):
    """
    Represents a UI View.

    This object is meant to be inherited from to create Views this
    class is created to add various helper methods to the default :class:`discord.ui.View`

    Parameters
    ----------
    interaction: :class:`discord.Interaction`
        The app command interaction.
    timeout: :class:`float` | ``None``, default=180
        Timeout in seconds from last interaction with the UI before no longer accepting input.
        If ``None`` then there is no timeout.
    delete_after: bool, default=False
        Decides what to do when the View timeouts. If set to True, the message will be deleted
        otherwise all the children will be disabled.
    """

    def __init__(self, interaction: discord.Interaction, *, timeout: float | None = 180, delete_after: bool = False):
        self.interaction = interaction
        self.delete_after = delete_after

        super().__init__(timeout=timeout)

        self.message: discord.Message | None = None

    async def interaction_check(self, interaction: discord.Interaction, /) -> bool:
        return interaction.user == self.interaction.user

    async def on_error(self, interaction: discord.Interaction, error: Exception, item: discord.ui.Item, /) -> None:
        send = interaction.followup.send if interaction.response.is_done() else interaction.response.send_message

        embed = discord.Embed(
            description="Something went wrong while trying to process your request. I have notified my developers. "
            f"\n\n```python\n{error.__class__.__name__}: {error}```",
            color=discord.Color.red(),
        )

        embed.set_author(name=str(interaction.user), icon_url=interaction.user.display_avatar.url)

        with suppress(discord.HTTPException, discord.Forbidden):
            await send(embed=embed)

        await super().on_error(interaction, error, item)

    async def on_timeout(self) -> None:
        if self.message is None:
            return

        if self.delete_after:
            with suppress(discord.NotFound, discord.HTTPException):
                await self.message.delete()
        else:
            for item in self.children:
                if isinstance(item, (discord.ui.Button, discord.ui.Select)):
                    item.disabled = True

            with suppress(discord.NotFound, discord.HTTPException):
                await self.message.edit(view=self)


class DismissButton(discord.ui.Button["View"]):
    def __init__(
        self,
        *,
        style: discord.ButtonStyle = discord.ButtonStyle.red,
        label: str = "Dismiss",
        emoji: str | discord.Emoji | discord.PartialEmoji | None = None,
    ):
        super().__init__(style=style, label=label, emoji=emoji)

    async def callback(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer()

        await self.view.on_timeout()
        self.view.stop()
