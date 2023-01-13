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

from bot import MessageError, Plugin, views

from .converters import MessageTransformer


class Utilities(Plugin):
    embed = app.Group(
        name="embed",
        description="The base command for creating/managing embeds.",
        default_permissions=discord.Permissions(manage_messages=True),
    )

    @embed.command()
    @app.describe(channel="The channel you want to post the embed to.")
    @app.describe(mention="The role to mention when the embed is posted.")
    async def create(
        self,
        interaction: discord.Interaction,
        channel: discord.TextChannel | None = None,
        mention: discord.Role | None = None,
    ) -> None:
        """Create and post an embed with the help of an interactive menu."""
        view = views.CreateEmbed(interaction, channel=channel, mention=mention)
        embed = view.sync_embed_sections(discord.Embed())

        await interaction.response.send_message(content=getattr(mention, "mention", None), embed=embed, view=view)
        view.message = await interaction.original_response()

    @embed.command()
    @app.describe(message="The message url containing the embed you want to edit.")
    async def edit(
        self, interaction: discord.Interaction, message: app.Transform[discord.Message, MessageTransformer]
    ) -> None:
        """Edit an embed already posted by me with the help of an interactive menu."""
        if not message.embeds:
            raise MessageError("There was no embed found in the message to edit.")
        if not message.author == interaction.client.user:
            raise MessageError("I can only edit embeds posted by me.")

        embed = message.embeds[0]
        if embed.author:
            author = views.embed.Author(name=embed.author.name, icon=embed.author.icon_url)
        else:
            author = views.embed.Author(toggled=False)

        if embed.title:
            title = views.embed.Title(title=embed.title, url=embed.url)
        else:
            title = views.embed.Title(toggled=False)

        if embed.description:
            description = views.embed.Description(description=embed.description)
        else:
            description = views.embed.Description(toggled=False)

        if embed.thumbnail.url:
            thumbnail = views.embed.Thumbnail(thumbnail=embed.thumbnail.url)
        else:
            thumbnail = views.embed.Thumbnail(toggled=False)

        if embed.image.url:
            image = views.embed.Image(image=embed.image.url)
        else:
            image = views.embed.Image(toggled=False)

        if embed.footer.text:
            footer = views.embed.Footer(text=embed.footer.text)
        else:
            footer = views.embed.Footer(toggled=False)

        if embed.footer.icon_url:
            footer_icon = views.embed.FooterIcon(icon=embed.footer.icon_url)
        else:
            footer_icon = views.embed.FooterIcon(toggled=False)

        fields = [views.embed.Field(name=field.name, value=field.value, inline=field.inline) for field in embed.fields]  # type: ignore

        assert isinstance(message.channel, discord.TextChannel)
        view = views.CreateEmbed(
            interaction,
            channel=message.channel,
            to_edit=message,
            author=author,
            title=title,
            description=description,
            thumbnail=thumbnail,
            image=image,
            footer=footer,
            footer_icon=footer_icon,
            fields=fields,
        )
        view.color = embed.color

        embed = view.sync_embed_sections(discord.Embed())
        if hasattr(message.embeds[0], "_fields"):
            embed._fields = message.embeds[0]._fields

        await interaction.response.send_message(embed=embed, view=view)
        view.message = await interaction.original_response()
