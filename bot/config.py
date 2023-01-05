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
import tomli

with open("config.toml", "rb") as f:
    f = tomli.load(f)

TOKEN = f["bot"]["settings"]["token"]
OWNER_IDS = f["bot"]["settings"]["owner_ids"]

EMOJIS: dict[str, discord.PartialEmoji] = {}
for name, id in f["bot"]["emojis"].items():
    EMOJIS[name] = discord.PartialEmoji(name=name, id=id)
