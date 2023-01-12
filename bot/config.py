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

ERRORS_WEBHOOK_URL = f["bot"]["webhooks"]["error"]

MENU = discord.PartialEmoji(name="menu", id=f["bot"]["emojis"]["menu"])
EDIT = discord.PartialEmoji(name="edit", id=f["bot"]["emojis"]["edit"])
COLOR = discord.PartialEmoji(name="color", id=f["bot"]["emojis"]["color"])
IMAGE = discord.PartialEmoji(name="image", id=f["bot"]["emojis"]["image"])
ADD = discord.PartialEmoji(name="add", id=f["bot"]["emojis"]["add"])
REMOVE = discord.PartialEmoji(name="remove", id=f["bot"]["emojis"]["remove"])
TOGGLE_ON = discord.PartialEmoji(name="toggle_on", id=f["bot"]["emojis"]["toggle_on"])
TOGGLE_OFF = discord.PartialEmoji(name="toggle_off", id=f["bot"]["emojis"]["toggle_off"])
TEXT_CHANNEL = discord.PartialEmoji(name="text_channel", id=f["bot"]["emojis"]["text_channel"])
VOICE_CHANNEL = discord.PartialEmoji(name="voice_channel", id=f["bot"]["emojis"]["voice_channel"])

BADGES: dict[str, discord.PartialEmoji] = {}
for name, id in f["bot"]["badges"].items():
    BADGES[name] = discord.PartialEmoji(name=name, id=id)
