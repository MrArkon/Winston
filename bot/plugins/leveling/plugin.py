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

from bot import Manager, MessageError, Plugin, Winston

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

        experience = level_config.experience + random.randint(7, 13)
        leveled_up = experience - level_config.get_experience(level_config.level) >= level_config.get_required(
            level_config.level
        )
        await level_config.set_experience(Manager.pool, experience)

        if leveled_up:
            await message.reply(f"Congratulations {message.author.mention}! You leveled up to level {level_config.level}!")

    @app.command()
    @app.describe(member="The member you want to see the rank card for.")
    async def rank(self, interaction: discord.Interaction, member: discord.Member | None = None) -> None:
        """View yours or someone else's rank card."""
        assert isinstance(interaction.user, discord.Member)
        member = member or interaction.user

        if member.bot:
            raise MessageError("Bots don't have any experience.")

        await interaction.response.defer()

        level_config = await Manager.get_level_config(member.id, member.guild.id)

        card = await render(
            await member.display_avatar.read(),
            member,
            level_config.level,
            level_config.experience - level_config.get_experience(level_config.level),
            level_config.get_required(level_config.level),
            await level_config.get_rank(Manager.pool),
            sum(not member.bot for member in interaction.guild.members),
            level_config.messages,
        )
        await interaction.followup.send(file=card)

    @app.command()
    @app.default_permissions(administrator=True)
    @app.describe(target="The member you want to set/add XP to.")
    @app.describe(level="The amount of levels you want to set/add. Takes priority over xp if both provided.")
    @app.describe(xp="The amount of XP you want to set/add.")
    @app.describe(add="Whether to add to the target's experience or overwrite it.")
    async def setlevel(
        self,
        interaction: discord.Interaction,
        target: discord.Member,
        xp: app.Range[int, 0, 125052000] | None = None,
        level: app.Range[int, 0, 500] | None = None,
        add: bool = False,
    ) -> None:
        """Set/Add a member's experience or level."""
        if target.bot:
            raise MessageError("Bots don't have any experience.")

        if xp is None and level is None:
            raise MessageError("You must provide either xp or level to add/set.")
        if level is not None and xp is not None:
            xp = None

        level_config = await Manager.get_level_config(target.id, target.guild.id)

        experience = 0
        if level:
            experience = level_config.get_experience(level) + (level_config.experience if add else 0)
        elif xp:
            experience = xp + (level_config.experience if add else 0)

        if experience > level_config.get_experience(500):
            raise MessageError("Too much amount of experience to set/add.")

        await interaction.response.defer()

        await level_config.set_experience(Manager.pool, experience)
        await interaction.followup.send(
            f"{target.mention} is now level {level_config.level} with {level_config.experience:,} total experience."
        )
