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

from bot import Winston, models


class Miscellaneous(models.Plugin):
    @app.command()
    async def ping(self, interaction: discord.Interaction) -> None:
        """Measures the latency and response time of the bot"""
        embed = discord.Embed(
            description=f"\N{HEAVY BLACK HEART} **Hearbeat:** {self.bot.latency * 1000:.2f}ms", color=discord.Color.blurple()
        )

        start = time.perf_counter()

        await interaction.response.send_message(embed=embed)

        duration = time.perf_counter() - start

        assert embed.description is not None
        embed.description += f" **|** \N{SATELLITE ANTENNA} **Ping:** {duration * 1000:.2f}ms"

        await interaction.edit_original_response(embed=embed)


async def setup(bot: Winston) -> None:
    await bot.add_cog(Miscellaneous(bot))
