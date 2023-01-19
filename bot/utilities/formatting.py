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


class Plural:
    """
    A format spec which handles making words plural or singular based off of its value.

    Credit: https://github.com/Rapptz/RoboDanny/blob/rewrite/cogs/utils/formats.py#L8-L18
    """

    def __init__(self, value: int) -> None:
        self.value = value

    def __format__(self, format_spec: str) -> str:
        singular, _, plural = format_spec.partition("|")
        plural = plural or f"{singular}s"

        return f"{self.value:,} {plural}" if abs(self.value) != 1 else f"{self.value} {singular}"


def shorten_number(number: int | float) -> str:
    number = float(f"{number:.3g}")
    magnitude = 0

    while abs(number) >= 1000:
        magnitude += 1
        number /= 1000

    return f"{f'{number:f}'.rstrip('0').rstrip('.')}{['', 'K', 'M', 'B', 'T'][magnitude]}"
