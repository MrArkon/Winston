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
import re

import discord
from discord import app_commands as app

from bot import MessageError

MESSAGE_URL = re.compile(r"https:\/\/discord(?:app)?.com\/channels\/(\d+|@me)\/(\d+)\/(\d+)")


class MessageTransformer(app.Transformer):
    async def transform(self, interaction: discord.Interaction, value: str, /) -> discord.Message:
        match = re.match(MESSAGE_URL, value)
        error = MessageError(
            "I couldn't find the message with the link you provided. Please make sure the link you provided is valid."
        )

        if match:
            guild_id, channel_id, message_id = match.groups()

            if interaction.guild.id != int(guild_id):
                raise error

            channel = interaction.guild.get_channel(int(channel_id))
            assert isinstance(channel, discord.TextChannel)

            try:
                message = await channel.fetch_message(int(message_id))
            except (discord.NotFound, discord.Forbidden, discord.HTTPException):
                raise error

            return message

        raise error
