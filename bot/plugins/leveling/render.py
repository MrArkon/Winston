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
from io import BytesIO

import discord
from jishaku.functools import executor_function
from PIL import Image, ImageChops, ImageDraw, ImageFont

from bot import shorten_number

INTER_BOLD_48 = ImageFont.truetype("./assets/Inter-Bold.ttf", 48)
INTER_BOLD_36 = ImageFont.truetype("./assets/Inter-Bold.ttf", 36)
INTER_BOLD_28 = ImageFont.truetype("./assets/Inter-Bold.ttf", 28)
INTER_BOLD_22 = ImageFont.truetype("./assets/Inter-Bold.ttf", 22)
INTER_MEDIUM_32 = ImageFont.truetype("./assets/Inter-Medium.ttf", 32)
INTER_MEDIUM_28 = ImageFont.truetype("./assets/Inter-Medium.ttf", 28)
INTER_MEDIUM_24 = ImageFont.truetype("./assets/Inter-Medium.ttf", 24)
INTER_MEDIUM_20 = ImageFont.truetype("./assets/Inter-Medium.ttf", 20)

EXPERIENCE = {False: (INTER_BOLD_28, 16), True: (INTER_BOLD_22, 20)}

STAR = Image.open("./assets/star.png")
BUBBLE = Image.open("./assets/bubble.png")
MASK = Image.open("./assets/mask.png").convert("L").resize((184, 184), Image.LANCZOS)


def add_corners(image: Image.Image, rad: int) -> Image.Image:
    with Image.new("L", (rad * 4, rad * 4), 0) as circle:
        draw = ImageDraw.Draw(circle)
        draw.ellipse((0, 0, rad * 4, rad * 4), fill=255)

        alpha = Image.new("L", image.size, "white")

        w, h = image.size
        alpha.paste(circle.crop((0, 0, rad * 2, rad * 2)), (0, 0))
        alpha.paste(circle.crop((0, rad * 2, rad * 2, rad * 4)), (0, h - rad * 2))
        alpha.paste(circle.crop((rad * 2, 0, rad * 4, rad * 2)), (w - rad * 2, 0))
        alpha.paste(circle.crop((rad * 2, rad * 2, rad * 4, rad * 4)), (w - rad * 2, h - rad * 2))
        image.putalpha(alpha)

        return image


def create_rounded_rectangle_mask(size: tuple[int, int], radius: int, alpha: int = 255) -> Image.Image:
    factor = 5
    radius = radius * factor
    image = Image.new("RGBA", (size[0] * factor, size[1] * factor), (0, 0, 0, 0))

    corner = Image.new("RGBA", (radius, radius), (0, 0, 0, 0))
    draw = ImageDraw.Draw(corner)
    draw.pieslice(((0, 0), (radius * 2, radius * 2)), 180, 270, fill=(50, 50, 50, alpha + 55))

    mx, my = (size[0] * factor, size[1] * factor)

    image.paste(corner, (0, 0), corner)
    image.paste(corner.rotate(90), (0, my - radius), corner.rotate(90))
    image.paste(corner.rotate(180), (mx - radius, my - radius), corner.rotate(180))
    image.paste(corner.rotate(270), (mx - radius, 0), corner.rotate(270))

    draw = ImageDraw.Draw(image)
    draw.rectangle((radius, 0, mx - radius, my), fill=(50, 50, 50, alpha))
    draw.rectangle((0, radius, mx, my - radius), fill=(50, 50, 50, alpha))
    image = image.resize(size, Image.ANTIALIAS)

    return image


@executor_function
def render(
    avatar: bytes, user: discord.Member, level: int, current: int, required: int, rank: int, members: int, messages: int
) -> discord.File:
    with Image.open("./assets/template.png") as template:
        # User Avatar
        with Image.open(BytesIO(avatar)).resize((184, 184), Image.BOX) as image:
            mask = ImageChops.darker(MASK, image.split()[-1])

            template.paste(image, (44, 44), mask)

        draw = ImageDraw.Draw(template)

        # User Name
        draw.text((252, 62), user.nick or user.name, font=INTER_BOLD_48, fill=(235, 235, 235))
        draw.text((252, 114), str(user), font=INTER_MEDIUM_28, fill=(216, 216, 216, 204))

        # Rank
        rank_text = f"Rank #{rank}"
        width = INTER_BOLD_48.getlength(rank_text)
        draw.text((1114 - width, 62), text=rank_text, font=INTER_BOLD_48, fill=(235, 235, 235))

        members_text = f"Out Of {shorten_number(members)}"
        width = INTER_MEDIUM_28.getlength(members_text)
        draw.text(
            (1114 - width, 114),
            members_text,
            font=INTER_MEDIUM_28,
            fill=(216, 216, 216, 204),
        )

        # Progress Bar
        if multiplier := abs(current / required):
            with Image.new("RGB", (round(662 * multiplier), 44), color=(0, 173, 181)) as progress_bar:
                template.paste(progress_bar, (252, 168), create_rounded_rectangle_mask(progress_bar.size, 10))

        # Level
        with Image.open("./assets/level.png") as level_background:
            draw = ImageDraw.Draw(level_background)

            text_width = INTER_MEDIUM_32.getlength("Level")
            number_width = INTER_BOLD_36.getlength(str(level))

            offset = int((182 - (text_width + number_width)) / 2)

            draw.text((offset, 14), text="Level", font=INTER_MEDIUM_32, fill=(216, 216, 216))
            draw.text((offset + text_width + 10, 10), text=str(level), font=INTER_BOLD_36, fill=(235, 235, 235))

            template.paste(level_background, (40, 256), level_background)

        # Experience
        with Image.open("./assets/experience.png") as experience_background:
            draw = ImageDraw.Draw(experience_background)
            text = f"{shorten_number(current)} XP / {shorten_number(required)}"

            font, y = EXPERIENCE[False]
            if (text_size := font.getlength(text)) > 190:
                font, y = EXPERIENCE[True]
                text_size = font.getlength(text)

            offset = int((212 - text_size) / 2)

            experience_background.paste(STAR, (offset, 14), STAR)
            draw.text((offset + 48, y), text=text, font=font, fill=(235, 235, 235))

            template.paste(experience_background, (252, 256), experience_background)

        # Messages
        with Image.open("./assets/messages.png") as messages_background:
            draw = ImageDraw.Draw(messages_background)
            msg_count = shorten_number(messages)

            count_font, text_font, count_offset, text_offset = INTER_BOLD_28, INTER_MEDIUM_24, 14, 18
            if (text_size := (count_font.getlength(msg_count) + 8 + text_font.getlength("Messages"))) > 200:
                cfont, tfont, count_offset, text_offset = INTER_BOLD_22, INTER_MEDIUM_20, 18, 20
                text_size = cfont.getlength(msg_count) + 8 + tfont.getlength("Messages")

            offset = int((220 - text_size) / 2)

            messages_background.paste(BUBBLE, (offset, 14), BUBBLE)
            draw.text((offset + 48, count_offset), text=msg_count, font=count_font, fill=(235, 235, 235))
            draw.text(
                (offset + 56 + count_font.getlength(msg_count), text_offset),
                text="Messages",
                font=text_font,
                fill=(216, 216, 216),
            )

            template.paste(messages_background, (846, 256), messages_background)

    buffer = BytesIO()
    template.save(buffer, "png")
    buffer.seek(0)

    return discord.File(buffer, filename="rank.png")
