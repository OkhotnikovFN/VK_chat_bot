import textwrap
from io import BytesIO

import requests
from PIL import Image, ImageDraw, ImageFont

TEMPLATE_PATH = 'files/ticket_base.png'
FONT_PATH = 'files/Roboto.ttf'

FONT_SIZE = 35
FONT_COLOR = (0, 0, 0, 255)

TOWN_DEPARTURE_OFFSET = (400, 500)
TOWN_ARRIVAL_OFFSET = (380, 585)
DATE_OFFSET = (430, 670)
QUANTITY_PLACES_OFFSET = (280, 755)
TELEPHONE_OFFSET = (370, 840)

COMMENT_OFFSET_X = 100
COMMENT_OFFSET_Y = 1010
COMMENT_Y_STEP = 85
COMMENT_LINE_WIDTH = 50

AVATAR_SIZE = 300
AVATAR_OFFSET = (400, 150)


def generate_ticket(town_departure, town_arrival, date, quantity_places, comment, telephone):
    base = Image.open(TEMPLATE_PATH)
    font = ImageFont.truetype(FONT_PATH, FONT_SIZE)

    draw = ImageDraw.Draw(base)
    draw.text(TOWN_DEPARTURE_OFFSET, town_departure, font=font, fill=FONT_COLOR)
    draw.text(TOWN_ARRIVAL_OFFSET, town_arrival, font=font, fill=FONT_COLOR)
    draw.text(DATE_OFFSET, date, font=font, fill=FONT_COLOR)
    draw.text(QUANTITY_PLACES_OFFSET, quantity_places, font=font, fill=FONT_COLOR)
    draw.text(TELEPHONE_OFFSET, telephone, font=font, fill=FONT_COLOR)

    comment_offset_y = COMMENT_OFFSET_Y
    for line in textwrap.wrap(comment, width=COMMENT_LINE_WIDTH):
        draw.text((COMMENT_OFFSET_X, comment_offset_y), line, font=font, fill=FONT_COLOR)
        comment_offset_y += COMMENT_Y_STEP

    response = requests.get(url=f'https://api.adorable.io/avatars/{AVATAR_SIZE}/{telephone}')
    avatar_file_like = BytesIO(response.content)
    avatar = Image.open(avatar_file_like)

    base.paste(avatar, AVATAR_OFFSET)

    temp_file = BytesIO()
    base.save(temp_file, 'png')
    temp_file.seek(0)

    return temp_file
