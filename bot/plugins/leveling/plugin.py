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
import random

import discord
from discord import app_commands as app
from discord.ext import commands

from bot import Manager, Plugin, Winston

from .render import render


class Leveling(Plugin):
    def __init__(self, bot: Winston) -> None:
        super().__init__(bot)

        self.message_cooldown = commands.CooldownMapping.from_cooldown(1, 60, commands.BucketType.member)

    @Plugin.listener()
    async def on_message(self, message: discord.Message) -> None:
        # Message is not present in a guild or author is a bot
        if message.guild is None or message.author.bot:
            return

        # Mentions any bot
        if any(user.bot for user in message.mentions):
            return

        # Content length less than equal to 3
        if len(message.content) <= 3:
            return

        bucket = self.message_cooldown.get_bucket(message)
        retry_after = bucket.update_rate_limit()

        # You are on cooldown
        if retry_after:
            return

        level_config = await Manager.get_level_config(message.author.id, message.guild.id)
        await level_config.set_messages(Manager.pool, level_config.messages + 1)
        await level_config.set_experience(Manager.pool, level_config.experience + random.randint(7, 13))

    @app.command()
    @app.describe(member="The member you want to see the rank card for.")
    async def rank(self, interaction: discord.Interaction, member: discord.Member | None = None) -> None:
        """View yours or someone else's rank card."""
        await interaction.response.defer()

        assert isinstance(interaction.user, discord.Member)
        member = member or interaction.user

        level_config = await Manager.get_level_config(member.id, member.guild.id)

        card = await render(
            await member.display_avatar.read(),
            member,
            level_config.level,
            level_config.experience - level_config.get_experience(level_config.level),
            level_config.get_needed(level_config.level),
            await level_config.get_rank(Manager.pool),
            sum(not member.bot for member in interaction.guild.members),
            level_config.messages,
        )
        await interaction.followup.send(file=card)
