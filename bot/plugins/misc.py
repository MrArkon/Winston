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
import time

import discord
from discord import app_commands as app

from bot import Winston, config, models


class Miscellaneous(models.Plugin):
    @app.command()
    async def ping(self, interaction: discord.Interaction) -> None:
        """Measures the latency and response time of the bot."""
        embed = discord.Embed(
            description=f"\N{HEAVY BLACK HEART} **Hearbeat:** {self.bot.latency * 1000:.2f}ms", color=discord.Color.blurple()
        )

        start = time.perf_counter()

        await interaction.response.send_message(embed=embed)

        duration = time.perf_counter() - start

        assert embed.description is not None
        embed.description += f" **|** \N{SATELLITE ANTENNA} **Ping:** {duration * 1000:.2f}ms"

        await interaction.edit_original_response(embed=embed)

    info = app.Group(name="info", description="Parent command for information based commands.")

    @info.command()
    @app.describe(user="The user you want information about.")
    @app.describe(ephemeral="Setting this to True makes it so that only you can see it. Default is False.")
    async def user(
        self, interaction: discord.Interaction, user: discord.Member | discord.User | None = None, ephemeral: bool = False
    ):
        """Obtain information about a specified user or yourself."""
        user = user or interaction.user

        embed = discord.Embed(color=user.color if user.color != discord.Color.default() else discord.Color.blurple())
        embed.set_author(name=str(user), icon_url=user.display_avatar.url)

        embed.description = f"{user.mention} " + " ".join(
            str(config.EMOJIS.get(name, "")) for name, value in user.public_flags if value
        )

        embed.add_field(
            name="Discord User Since", value="\n".join(discord.utils.format_dt(user.created_at, style=f) for f in ["D", "R"])  # type: ignore
        )

        if isinstance(user, discord.Member):
            embed.add_field(
                name="Server Member Since", value="\n".join(discord.utils.format_dt(user.joined_at, style=f) for f in ["D", "R"])  # type: ignore
            )

            sorted_members = sorted(interaction.guild.members, key=lambda member: member.joined_at or discord.utils.utcnow())
            embed.add_field(name="Join Position", value=f"{sorted_members.index(user) + 1}/{len(sorted_members)}")

            embed.add_field(
                name=f"Roles [{len(user.roles)}]:",
                value=", ".join(
                    role.mention if not role.is_default() else "@everyone"
                    for role in sorted(user.roles, key=lambda role: role.position, reverse=True)
                )
                + (
                    f"\n\n**Top Role:** {user.top_role.mention}\n**Top Role Color:** {user.top_role.color.__str__().upper()}"
                    if not user.top_role.is_default()
                    else ""
                ),
            )

            embed.add_field(
                name="Key Permissions",
                value=", ".join(
                    f"{permission.replace('_', ' ').title()}"
                    for permission, value in user.guild_permissions & discord.Permissions(27812569150)
                    if value
                )
                if not user.guild_permissions.administrator
                else "Administrator",
                inline=False,
            )

        embed.set_footer(
            text=f"ID: {user.id}"
            + (" | This user is not a member of this server." if not isinstance(user, discord.Member) else "")
        )

        await interaction.response.send_message(embed=embed, ephemeral=ephemeral)


async def setup(bot: Winston) -> None:
    await bot.add_cog(Miscellaneous(bot))
