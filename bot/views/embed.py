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
from __future__ import annotations

import logging
from dataclasses import dataclass

import discord

from bot import config, views

__log__ = logging.getLogger(__name__)


@dataclass
class Author:
    name: str | None = None
    icon: str | None = None
    toggled: bool = True


@dataclass
class Title:
    title: str = "Title"
    url: str | None = None
    toggled: bool = True


@dataclass
class Description:
    description: str = "Description"
    toggled: bool = True


@dataclass
class Thumbnail:
    thumbnail: str = "https://i.imgur.com/uNJ2GWB.png"
    toggled: bool = True


@dataclass
class Image:
    image: str = "https://i.imgur.com/JKPjTUi.png"
    toggled: bool = True


@dataclass
class Footer:
    text: str = "Footer Text"
    toggled: bool = True


@dataclass
class FooterIcon:
    icon: str = "https://i.imgur.com/pswoA1x.png"
    toggled: bool = True


@dataclass
class Field:
    name: str
    value: str
    inline: bool = True


# The following UI elements are for customising different aspects of the embed.


class EditEmbedText(discord.ui.Modal):
    def __init__(self, view: CreateEmbed) -> None:
        super().__init__(title="Edit Embed Text", timeout=60)

        self.view = view

        if self.view.title.toggled:
            self.title_ = discord.ui.TextInput(label="Title", default=self.view.title.title, required=False, max_length=256)
            self.title_url = discord.ui.TextInput(
                label="Title URL", default=self.view.title.url, required=False, max_length=256
            )
            self.add_item(self.title_)
            self.add_item(self.title_url)

        if self.view.description.toggled:
            self.description = discord.ui.TextInput(
                label="Description",
                style=discord.TextStyle.long,
                default=self.view.description.description,
                required=False,
                max_length=4000,
            )
            self.add_item(self.description)

        if self.view.footer.toggled:
            self.footer = discord.ui.TextInput(
                label="Footer",
                style=discord.TextStyle.long,
                default=self.view.footer.text,
                required=False,
                max_length=2048,
            )
            self.add_item(self.footer)

    async def on_submit(self, interaction: discord.Interaction, /) -> None:
        await interaction.response.defer()

        embed = self.view.message.embeds[0]

        if hasattr(self, "title_"):
            self.view.title.title = embed.title = self.title_.value
            self.view.title.url = embed.url = self.title_url.value

        if hasattr(self, "description"):
            self.view.description.description = embed.description = self.description.value

        if hasattr(self, "footer"):
            self.view.footer.text = self.footer.value
            embed.set_footer(
                text=self.view.footer.text, icon_url=self.view.footer_icon.icon if self.view.footer_icon.toggled else None
            )

        await self.view.message.edit(embed=embed, view=self.view)


class SetEmbedColor(discord.ui.Modal):
    def __init__(self, view: CreateEmbed) -> None:
        super().__init__(title="Set Embed Color", timeout=30)

        self.view = view

        self.color = discord.ui.TextInput(label="Color", default=str(self.view.color), max_length=7)
        self.add_item(self.color)

    async def on_submit(self, interaction: discord.Interaction, /) -> None:
        await interaction.response.defer(ephemeral=True)

        try:
            color = discord.Color.from_str(("" if self.color.value.startswith("#") else "#") + self.color.value)
        except ValueError:
            return await interaction.followup.send(
                "You provided an invalid hex code. Reverting to the previous embed color.", ephemeral=True
            )

        embed = self.view.message.embeds[0]
        self.view.color = embed.color = color

        await self.view.message.edit(embed=embed, view=self.view)


class EditEmbedField(discord.ui.Modal):
    def __init__(self, view: CreateEmbed, title: str = "Add Field", field: Field | None = None) -> None:
        self.view = view
        self.field = field

        super().__init__(title=title, timeout=60)

        self.name = discord.ui.TextInput(label="Field Name", default=getattr(self.field, "name", None), max_length=256)
        self.value = discord.ui.TextInput(
            label="Field Value", style=discord.TextStyle.long, default=getattr(self.field, "value", None), max_length=1024
        )
        self.inline = discord.ui.TextInput(
            label="Inline (True or False)", default=str(getattr(self.field, "inline", True)), max_length=5
        )

        self.add_item(self.name)
        self.add_item(self.value)
        self.add_item(self.inline)

    async def on_submit(self, interaction: discord.Interaction, /) -> None:
        await interaction.response.defer()

        inline = False if self.inline.value.lower() == "false" else True
        field = Field(name=self.name.value, value=self.value.value, inline=inline)

        embed = self.view.message.embeds[0]

        if self.field:
            index = self.view.fields.index(self.field)
            self.view.fields[index] = field

            embed.set_field_at(index, name=field.name, value=field.value, inline=field.inline)
        else:
            self.view.fields.append(field)

            embed.add_field(name=field.name, value=field.value, inline=field.inline)

        self.view.sync_select_options()
        await self.view.message.edit(embed=embed, view=self.view)


class EditEmbedImage(discord.ui.Modal):
    def __init__(self, view: CreateEmbed, element: str) -> None:
        super().__init__(title=f"Edit {element}", timeout=30)

        self.view = view
        self.element = element

        self.image = discord.ui.TextInput(label=f"{element} URL", max_length=256)
        if self.element == "Thumbnail":
            self.image.default = self.view.thumbnail.thumbnail
        elif self.element == "Image":
            self.image.default = self.view.image.image
        elif self.element == "Footer Icon":
            self.image.default = self.view.footer_icon.icon

        self.add_item(self.image)

    async def on_submit(self, interaction: discord.Interaction, /) -> None:
        await interaction.response.defer()

        embed = self.view.message.embeds[0]

        if self.element == "Thumbnail":
            self.view.thumbnail.thumbnail = self.image.value
            embed.set_thumbnail(url=self.image.value)
        elif self.element == "Image":
            self.view.image.image = self.image.value
            embed.set_image(url=self.image.value)
        elif self.element == "Footer Icon":
            self.view.footer_icon.icon = self.image.value
            embed.set_footer(text=self.view.footer.text, icon_url=self.image.value)

        self.view.sync_select_options()
        await self.view.message.edit(embed=embed, view=self.view)


class SelectEmbedField(discord.ui.Select["views.View"]):
    def __init__(self, parent: CreateEmbed, remove: bool = False) -> None:
        self.parent = parent
        self.remove = remove

        options = [
            discord.SelectOption(label=field.name, value=str(index), description=field.value[:100])
            for index, field in enumerate(self.parent.fields)
        ]
        super().__init__(options=options, placeholder="Select a Field", max_values=len(options) if self.remove else 1)

    async def callback(self, interaction: discord.Interaction) -> None:
        if self.remove:
            await interaction.response.defer()

            embed = self.parent.message.embeds[0]

            embed._fields = [field for index, field in enumerate(embed._fields) if str(index) not in self.values]
            self.parent.fields = [field for index, field in enumerate(self.parent.fields) if str(index) not in self.values]

            self.parent.sync_select_options()
            await self.parent.message.edit(embed=embed, view=self.parent)
        else:
            field = self.parent.fields[int(self.values[0])]
            await interaction.response.send_modal(EditEmbedField(view=self.parent, title="Edit Field", field=field))

        await self.view.on_timeout()


# The following UI elements are part of the main embed creator UI.


class EditEmbedSections(discord.ui.Select["CreateEmbed"]):
    def __init__(self, view: CreateEmbed) -> None:
        super().__init__(options=self.get_options(view))

    def get_options(self, view: CreateEmbed) -> list[discord.SelectOption]:
        options = [discord.SelectOption(label="Edit Section", emoji=config.MENU, default=True)]

        if any([view.title.toggled, view.description.toggled, view.footer.toggled]):
            toggled: dict[str, bool] = {
                section: getattr(view, section).toggled for section in ("title", "description", "footer")
            }

            options.append(
                discord.SelectOption(
                    label=f"Edit Text ({', '.join(section.capitalize() for section, value in toggled.items() if value)})",
                    value="text",
                    description="Customise the text in the embed",
                    emoji=config.EDIT,
                )
            )

        if view.thumbnail.toggled:
            options.append(
                discord.SelectOption(
                    label="Edit Thumbnail",
                    value="thumbnail",
                    description="Edit the thumbnail of the embed",
                    emoji=config.IMAGE,
                )
            )
        if view.image.toggled:
            options.append(
                discord.SelectOption(
                    label="Edit Image", value="image", description="Edit the image of the embed", emoji=config.IMAGE
                )
            )
        if view.footer_icon.toggled:
            options.append(
                discord.SelectOption(
                    label="Edit Footer Icon",
                    value="footer_icon",
                    description="Edit the footer icon of the embed",
                    emoji=config.IMAGE,
                )
            )

        options.append(
            discord.SelectOption(
                label="Set Embed Color", value="color", description="Customise the color of the embed", emoji=config.COLOR
            )
        )

        options.append(
            discord.SelectOption(
                label="Add Field", value="add_field", description="Add a field to the embed", emoji=config.ADD
            )
        )

        if view.fields:
            options.append(
                discord.SelectOption(
                    label="Edit Field", value="edit_field", description="Edit a field in the embed", emoji=config.EDIT
                ),
            )
            options.append(
                discord.SelectOption(
                    label="Remove Field",
                    value="remove_field",
                    description="Remove a field in the embed",
                    emoji=config.REMOVE,
                )
            )

        return options

    async def callback(self, interaction: discord.Interaction) -> None:
        for index, option in enumerate(self.options):
            option.default = True if index == 0 else False
        await self.view.message.edit(view=self.view)

        assert self.view is not None

        if self.values[0] == "text":
            await interaction.response.send_modal(EditEmbedText(self.view))
        if self.values[0] == "color":
            await interaction.response.send_modal(SetEmbedColor(self.view))
        if self.values[0] == "add_field":
            await interaction.response.send_modal(EditEmbedField(self.view))
        if self.values[0] in ["thumbnail", "image", "footer_icon"]:
            await interaction.response.send_modal(
                EditEmbedImage(self.view, element=self.values[0].replace("_", " ").title())
            )
        if self.values[0] in ["edit_field", "remove_field"]:
            view = views.View(self.view.interaction, timeout=20, delete_after=True)
            view.add_item(SelectEmbedField(self.view, remove=True if self.values[0] == "remove_field" else False))
            view.add_item(views.DismissButton())

            await interaction.response.send_message(view=view, ephemeral=True)
            view.message = await interaction.original_response()


class ToggleEmbedSections(discord.ui.Select["CreateEmbed"]):
    def __init__(self, view: CreateEmbed) -> None:
        options = [
            discord.SelectOption(
                label=section.replace("_", " ").title(),
                value=section,
                description=f"To toggle ON/OFF {section.replace('_', ' ').title()}",
                emoji=config.TOGGLE_ON,
                default=getattr(view, section).toggled,
            )
            for section in ["author", "title", "description", "thumbnail", "image", "footer", "footer_icon"]
        ]

        super().__init__(options=options, min_values=1, max_values=len(options))

    async def callback(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer(ephemeral=True)

        for option in self.options:
            getattr(self.view, option.value).toggled = option.default = True if option.value in self.values else False
            option.emoji = config.TOGGLE_ON if option.value in self.values else config.TOGGLE_OFF

        # Disable footer icon if footer is disabled, This is due to a discord limitation.
        if self.view.footer_icon and not self.view.footer.toggled:
            self.view.footer_icon.toggled = self.options[6].default = False
            self.options[6].emoji = config.TOGGLE_OFF

        embed = self.view.sync_embed_sections(self.view.message.embeds[0])
        self.view.sync_select_options()

        await self.view.message.edit(embed=embed, view=self.view)


class CreateEmbed(views.View):
    def __init__(
        self,
        interaction: discord.Interaction,
        channel: discord.TextChannel | None = None,
        mention: discord.Role | None = None,
        to_edit: discord.Message | None = None,
        **kwargs,
    ):
        super().__init__(interaction, timeout=300, delete_after=True)

        assert isinstance(self.interaction.channel, discord.TextChannel)
        self.channel = channel or self.interaction.channel
        self.mention = mention
        self.to_edit = to_edit

        self.author = kwargs.get("author", Author())
        self.title = kwargs.get("title", Title())
        self.description = kwargs.get("description", Description())
        self.thumbnail = kwargs.get("thumbnail", Thumbnail())
        self.image = kwargs.get("image", Image())
        self.footer = kwargs.get("footer", Footer())
        self.footer_icon = kwargs.get("footer_icon", FooterIcon())
        self.fields: list[Field] = kwargs.get("fields", [])
        self.color = kwargs.get("color", discord.Color.blurple())

        self.clear_items()
        self.add_item(ToggleEmbedSections(self))
        self.add_item(EditEmbedSections(self))
        self.add_item(views.DismissButton())
        self.add_item(self.post)

    def sync_select_options(self) -> None:
        edit_embed_sections = self.children[1]
        assert isinstance(edit_embed_sections, EditEmbedSections)

        edit_embed_sections.options = edit_embed_sections.get_options(self)

    def sync_embed_sections(self, embed: discord.Embed) -> discord.Embed:
        if self.author.toggled:
            embed.set_author(
                name=self.author.name or self.interaction.user.name,
                icon_url=self.author.icon or self.interaction.user.display_avatar.url,
            )
        else:
            embed.remove_author()

        if self.title.toggled:
            embed.title = self.title.title
            embed.url = self.title.url
        else:
            embed.title = embed.url = None

        embed.description = self.description.description if self.description.toggled else None

        embed.set_thumbnail(url=self.thumbnail.thumbnail if self.thumbnail.toggled else None)
        embed.set_image(url=self.image.image if self.image.toggled else None)

        if self.footer.toggled:
            embed.set_footer(text=self.footer.text, icon_url=self.footer_icon.icon if self.footer_icon.toggled else None)
        else:
            embed.remove_footer()

        embed.color = self.color

        return embed

    @discord.ui.button(label="Post Embed", style=discord.ButtonStyle.green)
    async def post(self, interaction: discord.Interaction, _) -> None:
        await interaction.response.defer(ephemeral=True)
        await self.on_timeout()

        if self.to_edit:
            message = await self.to_edit.edit(embed=self.message.embeds[0])

            await interaction.followup.send(
                f"Successfully edited the [message]({message.jump_url}) in {self.channel.mention}",
                ephemeral=True,
            )
        else:
            message = await self.channel.send(
                content=getattr(self.mention, "mention", None),
                embed=self.message.embeds[0],
                allowed_mentions=discord.AllowedMentions.all(),
            )

            await interaction.followup.send(
                f"Successfully sent the embed [message]({message.jump_url}) to {self.channel.mention}",
                ephemeral=True,
            )
