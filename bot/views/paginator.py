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

from typing import Type

import discord


class Paginator(discord.ui.View):
    """
    The base paginator interface that handles the buttons and page switching.
    This object is meant to be inherited from to implement an actual paginator.

    Attributes
    ----------
    interaction: :class:`discord.Interaction`
        The app command interaction.
    entries: :class:`list`
        The entries which are supposed to be paginated.
    per_page: :class:`int`
        The number of entries to be formatted per page.
    timeout: :class:`float` | ``None``, default=180
        The timeout in seconds from last interaction with the paginator before
        no longer accepting input. If ``None`` then there is no timeout.
    delete_after: bool, default=False
        Whether or not to delte the message or disable all the buttons.
    """

    def __init__(
        self,
        interaction: discord.Interaction,
        entries: list,
        *,
        per_page: int,
        timeout: float | None = 180,
        delete_after: bool = False,
    ):
        super().__init__(timeout=timeout)

        self.interaction = interaction
        self.entries = entries
        self.per_page = per_page
        self.delete_after = delete_after

        self._current_page = 0
        self.pages = [entries[item : item + per_page] for item in range(0, len(entries), per_page)]

        self.clear_items()
        self._fill_items()

    def _fill_items(self) -> None:
        use_last_and_first = self.max_pages >= 2

        if use_last_and_first:
            self.add_item(self.first_page)

        self.add_item(self.previous_page)
        self.add_item(self.next_page)

        if use_last_and_first:
            self.add_item(self.last_page)

        self.add_item(self.stop_paginator)

    @property
    def is_paginating(self) -> bool:
        """:class:`bool` Whether or not pagination is required."""
        return len(self.entries) > self.per_page

    @property
    def current_page(self) -> int:
        """:class:`int` The current page the user is on."""
        return self._current_page + 1

    @property
    def max_pages(self) -> int:
        """:class:`int` The maximum amount of pages for this paginator."""
        return len(self.pages)

    def _update_labels(self, page_number: int) -> None:
        self.first_page.disabled = self.previous_page.disabled = page_number == 0

        self.last_page.disabled = self.next_page.disabled = (page_number + 1) >= self.max_pages

    async def _show_page(self, interaction: discord.Interaction) -> None:
        entries = self.pages[self._current_page]
        embed = await self.format_page(entries=entries)
        self._update_labels(self._current_page)

        await interaction.response.edit_message(embed=embed, view=self)

    async def format_page(self, entries: list) -> discord.Embed:
        raise NotImplementedError

    @discord.ui.button(label="First", style=discord.ButtonStyle.grey)
    async def first_page(self, interaction: discord.Interaction, _) -> None:
        self._current_page = 0

        await self._show_page(interaction)

    @discord.ui.button(label="Previous", style=discord.ButtonStyle.blurple)
    async def previous_page(self, interaction: discord.Interaction, _) -> None:
        self._current_page += -1

        await self._show_page(interaction)

    @discord.ui.button(label="Next", style=discord.ButtonStyle.blurple)
    async def next_page(self, interaction: discord.Interaction, _) -> None:
        self._current_page += 1

        await self._show_page(interaction)

    @discord.ui.button(label="Last", style=discord.ButtonStyle.grey)
    async def last_page(self, interaction: discord.Interaction, _) -> None:
        self._current_page = self.max_pages - 1

        await self._show_page(interaction)

    @discord.ui.button(label="Stop", style=discord.ButtonStyle.red)
    async def stop_paginator(self, interaction: discord.Interaction, _) -> None:
        await interaction.response.defer()

        await self.on_timeout()
        self.stop()

    @classmethod
    async def start(cls: Type[Paginator], interaction: discord.Interaction, entries: list, per_page: int) -> Paginator:
        paginator = cls(interaction=interaction, entries=entries, per_page=per_page)

        entries = paginator.pages[0]
        embed = await paginator.format_page(entries=entries)
        paginator._update_labels(0)

        await interaction.response.send_message(embed=embed, view=paginator)
        return paginator
