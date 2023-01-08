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

from bot import Plugin, Plural, Winston, config


class Miscellaneous(Plugin):
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
    @app.describe(user="The user you want information about. Defaults to you if nothing is provided.")
    @app.describe(ephemeral="Setting this to True makes it so that only you can see it. Default is False.")
    async def user(
        self, interaction: discord.Interaction, user: discord.Member | discord.User | None = None, ephemeral: bool = False
    ):
        """Obtain information about a specified user or yourself."""
        user = user or interaction.user

        embed = discord.Embed(color=user.color if user.color != discord.Color.default() else discord.Color.blurple())
        embed.set_author(name=str(user), icon_url=user.display_avatar.url)

        embed.description = f"{user.mention} " + " ".join(
            str(config.BADGES.get(name, "")) for name, value in user.public_flags if value
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

    @info.command()
    @app.describe(ephemeral="Setting this to True makes it so that only you can see it. Default is False.")
    async def server(self, interaction: discord.Interaction, ephemeral: bool = False) -> None:
        """Obtain information about this server."""
        embed = discord.Embed(color=discord.Color.blurple())
        embed.set_author(name=str(interaction.guild), icon_url=getattr(interaction.guild.icon, "url", None))

        embed.add_field(name="Owner", value=interaction.guild.owner.mention)

        embed.add_field(
            name="Created At",
            value="\n".join(discord.utils.format_dt(interaction.guild.created_at, style=f) for f in ["D", "R"]),  # type: ignore
        )

        assert interaction.guild.member_count is not None
        bots = sum(member.bot for member in interaction.guild.members)
        embed.add_field(
            name="Members",
            value=f"{interaction.guild.member_count} Total\n"
            f"{Plural(interaction.guild.member_count - bots):Human} | "
            f"{Plural(bots):Bot}\n",
        )

        text_channels = [0, 0]
        voice_channels = [0, 0]

        for channel in interaction.guild.channels:
            allowed, denied = channel.overwrites_for(interaction.guild.default_role).pair()
            permissions = discord.Permissions(
                (interaction.guild.default_role.permissions.value & ~denied.value) | allowed.value
            )

            if isinstance(channel, discord.TextChannel):
                text_channels[0] += 1
                text_channels[1] += 1 if not permissions.read_messages else 0
            elif isinstance(channel, (discord.VoiceChannel, discord.StageChannel)):
                voice_channels[0] += 1
                voice_channels[1] += 1 if not permissions.connect else 0

        embed.add_field(
            name="Channels",
            value=f"{config.TEXT_CHANNEL} {text_channels[0]}"
            + ("\n" if not text_channels[1] else f" ({text_channels[1]} Locked)\n")
            + f"{config.VOICE_CHANNEL} {voice_channels[0]}"
            + ("" if not voice_channels[1] else f" ({voice_channels[1]} Locked)\n"),
        )

        embed.add_field(
            name="Moderation",
            value=f"2FA: {'Enabled' if interaction.guild.mfa_level.value else 'Disabled'}\n"
            f"Explicit Media Filter: {['Disabled', 'Medium', 'High'][interaction.guild.explicit_content_filter.value]}\n"
            f"Verification: {str(interaction.guild.verification_level).title()}",
        )

        last_boost = max(interaction.guild.members, key=lambda member: member.premium_since or interaction.guild.created_at)
        embed.add_field(
            name="Boosts",
            value=f"Level {interaction.guild.premium_tier} ({interaction.guild.premium_subscription_count} Boosts)"
            + (
                f"Last Boost: {last_boost} ({discord.utils.format_dt(last_boost.premium_since, style='R')})"
                if last_boost.premium_since is not None
                else ""
            ),
        )

        embed.add_field(
            name="Server Limits",
            value=f"Emojis: {len(interaction.guild.emojis)}/{interaction.guild.emoji_limit}\n"
            f"Bitrate: {int(interaction.guild.bitrate_limit / 1000)} Kbps\n"
            f"File Size Limit: {int(interaction.guild.filesize_limit / 1048576)} MB\n"
            f"Maximum Members: {interaction.guild.max_members:,}",
            inline=False,
        )

        embed.set_footer(text=f"ID: {interaction.guild.id}")

        await interaction.response.send_message(embed=embed, ephemeral=ephemeral)

    @info.command()
    @app.describe(role="The role you want information about. Defaults to your top role if nothing is provided.")
    @app.describe(ephemeral="Setting this to True makes it so that only you can see it. Default is False.")
    async def role(
        self, interaction: discord.Interaction, role: discord.Role | None = None, ephemeral: bool = False
    ) -> None:
        """Obtain information about a role."""
        assert isinstance(interaction.user, discord.Member)

        role = role or interaction.user.top_role

        embed = discord.Embed(
            description=role.mention if not role.is_default() else role.name,
            color=role.color if role.color != discord.Color.default() else discord.Color.blurple(),
        )
        embed.set_author(
            name=role.name,
            icon_url=role.display_icon if not isinstance(role.display_icon, discord.Asset) else role.display_icon.url,
        )

        embed.add_field(
            name="Created At",
            value="\n".join(discord.utils.format_dt(role.created_at, style=f) for f in ["D", "R"]),  # type: ignore
        )

        features = []
        if role.hoist:
            features.append("Displayed Separately")
        if role.managed:
            features.append("Managed by " + (f"<@{role.tags.bot_id}>" if role.is_bot_managed() else "an integration"))
        if role.mentionable:
            features.append("Mentionable by Anyone")
        if role.is_premium_subscriber():
            features.append("Premium/Booster Role")
        if role.is_default():
            features.append("Default Role")

        embed.add_field(name="Features", value="\n".join(features) if features else "None")

        embed.add_field(name="Color", value=str(role.color).upper())

        embed.add_field(
            name="Key Permissions",
            value=", ".join(
                f"{permission.replace('_', ' ').title()}"
                for permission, value in role.permissions & discord.Permissions(27812569150)
                if value
            )
            if not role.permissions.administrator
            else "Administrator",
            inline=False,
        )

        await interaction.response.send_message(embed=embed, ephemeral=ephemeral)


async def setup(bot: Winston) -> None:
    await bot.add_cog(Miscellaneous(bot))
