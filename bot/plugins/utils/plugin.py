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
import discord
from discord import app_commands as app

from bot import CreateEmbed, Plugin


class Utilities(Plugin):
    embed = app.Group(
        name="embed",
        description="The base command for creating/managing embeds.",
        default_permissions=discord.Permissions(manage_messages=True),
    )

    @embed.command()
    @app.default_permissions()
    @app.describe(channel="The channel you want to post the embed to.")
    @app.describe(mention="The role to mention when the embed is posted.")
    async def create(
        self,
        interaction: discord.Interaction,
        channel: discord.TextChannel | None = None,
        mention: discord.Role | None = None,
    ) -> None:
        """Create and post an embed with the help of an interactive menu."""
        view = CreateEmbed(interaction, channel=channel, mention=mention)
        embed = view.sync_embed_sections(discord.Embed())

        await interaction.response.send_message(content=getattr(mention, "mention", None), embed=embed, view=view)
        view.message = await interaction.original_response()
