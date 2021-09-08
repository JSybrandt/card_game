#!/usr/bin/env python3

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
from typing import *
import pathlib
import shutil
import csv
import dataclasses
import textwrap
import random
import math
import hashlib
import colorsys
import enum
import pprint
import colors
import util
import card_art

# Constants

CARDS_CSV_PATH = pathlib.Path("./cards.csv")
assert CARDS_CSV_PATH.is_file()
OUTPUT_DIR= pathlib.Path("./img")
assert OUTPUT_DIR.is_dir() or not OUTPUT_DIR.exists()
FONT_DIR= pathlib.Path("./fonts")
assert FONT_DIR.is_dir()
LEAGUE_GOTHIC_FONT_PATH = FONT_DIR.joinpath("LeagueGothic-Regular.otf")
assert LEAGUE_GOTHIC_FONT_PATH.is_file()
LATO_FONT_PATH = FONT_DIR.joinpath("Lato-Regular.ttf")
assert LATO_FONT_PATH.is_file()
COLWELLA_FONT_PATH = FONT_DIR.joinpath("Colwella.ttf")
assert COLWELLA_FONT_PATH.is_file()

# Card size in inches.
CARD_WIDTH_INCH = 2.5
CARD_HEIGHT_INCH = 3.5
CARD_MARGIN_INCH = 0.1
CARD_PADDING_INCH = 0.025
PIXELS_PER_INCH = 200
# Unless specified, all sizes are in pixels.
CARD_WIDTH = int(CARD_WIDTH_INCH * PIXELS_PER_INCH)
CARD_HEIGHT = int(CARD_HEIGHT_INCH * PIXELS_PER_INCH)
CARD_MARGIN = int(CARD_MARGIN_INCH * PIXELS_PER_INCH)
CARD_PADDING = int(CARD_PADDING_INCH * PIXELS_PER_INCH)

def get_card_type_light_color(card_type:util.CardType):
  if card_type == util.CardType.SPELL:
    return colors.LIGHT_BLUE_500
  if card_type == util.CardType.HOLDING:
    return colors.YELLOW_500
  if card_type == util.CardType.UNIT:
    return colors.RED_300
  if card_type == util.CardType.LEADER:
    return colors.BLUE_GREY_200

def get_card_type_dark_color(card_type:util.CardType):
  if card_type == util.CardType.SPELL:
    return colors.INDIGO_500
  if card_type == util.CardType.HOLDING:
    return colors.AMBER_500
  if card_type == util.CardType.UNIT:
    return colors.RED_700
  if card_type == util.CardType.LEADER:
    return colors.GREY_500

# Border parameters
BORDER_COLOR = colors.BLACK
BORDER_BB = [0, 0, CARD_WIDTH, CARD_HEIGHT]
BORDER_WIDTH = int(CARD_MARGIN/2)
BORDER_CORNER_RADIUS = 20

# Title parameters
TITLE_FONT = ImageFont.truetype(str(LEAGUE_GOTHIC_FONT_PATH), 50)
TITLE_ANCHOR = "ma"  # Top Middle.
TITLE_COORD = (int(CARD_WIDTH/2), CARD_MARGIN)
TITLE_FONT_COLOR=colors.BLACK

# Default icon params
STANDARD_ICON_RADIUS = 0.15 * PIXELS_PER_INCH
LARGE_ICON_RADIUS = 0.2 * PIXELS_PER_INCH
STANDARD_ICON_FONT = ImageFont.truetype(str(LATO_FONT_PATH), 40)
STANDARD_ICON_FONT_COLOR = colors.WHITE

# Cost parameters
COST_COORD = (CARD_MARGIN + STANDARD_ICON_RADIUS,
              CARD_MARGIN + STANDARD_ICON_RADIUS)
COST_BACKGROUND_COLOR = colors.YELLOW_700

# Card Type Icon
TYPE_COORD = (CARD_WIDTH-STANDARD_ICON_RADIUS-CARD_MARGIN,
              CARD_MARGIN+STANDARD_ICON_RADIUS)

# Describes the max width of card contents
CONTENT_WIDTH = CARD_WIDTH - 2*CARD_MARGIN

# Card image parameters
# Width and height of card image
CARD_IMAGE_WIDTH = CONTENT_WIDTH
CARD_IMAGE_HEIGHT = int(CARD_HEIGHT * 0.4)
CARD_IMAGE_TOP = int(CARD_HEIGHT / 7)
CARD_IMAGE_BOTTOM = CARD_IMAGE_TOP + CARD_IMAGE_HEIGHT
CARD_IMAGE_BB = [
  CARD_MARGIN,
  CARD_IMAGE_TOP,
  CARD_MARGIN + CONTENT_WIDTH,
  CARD_IMAGE_BOTTOM,
]


# Card Attributes
ATTRIBUTE_FONT = ImageFont.truetype(str(LATO_FONT_PATH), 25)
ATTRIBUTE_ANCHOR = "md" # middle bottom
ATTRIBUTE_HEIGHT = CARD_HEIGHT / 20
ATTRIBUTE_BOTTOM = CARD_IMAGE_BOTTOM + ATTRIBUTE_HEIGHT
ATTRIBUTE_COORD = (CARD_WIDTH/2, ATTRIBUTE_BOTTOM)
ATTRIBUTE_TEXT_COLOR = colors.BLACK

# Body text
BODY_TEXT_FONT = ImageFont.truetype(str(COLWELLA_FONT_PATH), 25)
BODY_TEXT_BG_TOP = ATTRIBUTE_BOTTOM + CARD_PADDING
BODY_TEXT_BG_BOTTOM = CARD_HEIGHT - CARD_MARGIN - CARD_PADDING
BODY_TEXT_BG_BB = [
  CARD_MARGIN,
  BODY_TEXT_BG_TOP,
  CARD_MARGIN + CONTENT_WIDTH,
  BODY_TEXT_BG_BOTTOM,
]
BODY_TEXT_COLOR = colors.BLACK
# Estimate text size of body text
BODY_TEXT_WIDTH = CONTENT_WIDTH - CARD_PADDING
BODY_TEXT_HEIGHT = BODY_TEXT_BG_BOTTOM - BODY_TEXT_BG_TOP - CARD_PADDING
BODY_TEXT_COORD = (int(CARD_MARGIN + CARD_PADDING * 3 / 2),
                   int(BODY_TEXT_BG_TOP + CARD_PADDING / 2))
BODY_TEXT_ANCHOR = "la" # top left
# Number of pixels between lines.
BODY_TEXT_SPACING = 10
# Background uses card type dark.

LOWER_ICON_Y = CARD_HEIGHT - CARD_MARGIN - CARD_PADDING - STANDARD_ICON_RADIUS

POWER_COORD = (CARD_WIDTH * .25, LOWER_ICON_Y)
POWER_BG_COLOR = colors.GREY_700

HEALTH_COORD = (CARD_WIDTH / 2, LOWER_ICON_Y)
HEALTH_BG_COLOR = colors.RED_500


# Layout functions

def wrap_body_text(body_text:str)->str:
  tokens = body_text.split()
  lines = []
  working_text = []
  for token in tokens:
    if BODY_TEXT_FONT.getsize(
      " ".join(working_text + [token]))[0] > BODY_TEXT_WIDTH:
      lines.append(" ".join(working_text))
      working_text = []
    working_text.append(token)
  lines.append(" ".join(working_text))
  return "\n".join(lines)


def draw_icon(
    draw:ImageDraw.Draw,
    center_coord:util.Coord,
    text:str,
    bg_color:colors.Color,
    radius:float=STANDARD_ICON_RADIUS,
    text_color:colors.Color=STANDARD_ICON_FONT_COLOR,
    font:ImageFont.ImageFont=STANDARD_ICON_FONT):
  assert radius > 0, f"Radius must be positive: {radius}"
  assert len(text) == 1, f"drawn_icon can only draw 1-char icons, not `{text}`"
  colors.assert_valid_color(bg_color)
  colors.assert_valid_color(text_color)
  util.assert_valid_coord(center_coord)
  center_x, center_y = center_coord
  background_bb = [
    center_x - radius,
    center_y - radius,
    center_x + radius,
    center_y + radius,
  ]
  draw.ellipse(background_bb, fill=bg_color)
  draw.text(center_coord, text, text_color, font=font, anchor="mm")

def generate_card(desc:util.CardDesc, output_path:pathlib.Path):
  assert not output_path.exists(), f"{output_path} already exists"
  img = Image.new(mode="RGBA", size=(CARD_WIDTH, CARD_HEIGHT))
  draw = ImageDraw.Draw(img)

  # Border + background
  draw.rounded_rectangle(
    BORDER_BB,
    outline=BORDER_COLOR,
    width=BORDER_WIDTH,
    radius=BORDER_CORNER_RADIUS,
    fill=get_card_type_light_color(desc.card_type),
  )

  # Title, center text at top of card.
  draw.text(
    TITLE_COORD,
    desc.title,
    TITLE_FONT_COLOR,
    font=TITLE_FONT,
    anchor=TITLE_ANCHOR)

  # Card image placeholder.
  art = card_art.generate_card_art(
    desc, CARD_IMAGE_WIDTH, CARD_IMAGE_HEIGHT)
  img.paste(art, CARD_IMAGE_BB[:2])

  # Card card_type text
  if desc.attributes is not None:
    draw.text(
      ATTRIBUTE_COORD,
      desc.attributes,
      ATTRIBUTE_TEXT_COLOR,
      font=ATTRIBUTE_FONT,
      anchor=ATTRIBUTE_ANCHOR,
    )

  # Body text
  draw.rectangle(
    BODY_TEXT_BG_BB,
    fill=get_card_type_dark_color(desc.card_type))

  if desc.body_text is not None:
    draw.multiline_text(
      BODY_TEXT_COORD,
      text=wrap_body_text(desc.body_text),
      fill=BODY_TEXT_COLOR,
      anchor=BODY_TEXT_ANCHOR,
      align="left",
      font=BODY_TEXT_FONT,
      spacing=BODY_TEXT_SPACING,
    )

  # Draw icons
  if desc.card_type != util.CardType.LEADER:
    draw_icon(draw, TYPE_COORD, str(desc.card_type.value)[0],
              get_card_type_dark_color(desc.card_type))
  if desc.cost is not None:
    draw_icon(draw, COST_COORD, desc.cost, COST_BACKGROUND_COLOR)
  if desc.health is not None:
    draw_icon(draw, HEALTH_COORD, desc.health, HEALTH_BG_COLOR)
  if desc.power is not None:
    draw_icon(draw, POWER_COORD, desc.power, POWER_BG_COLOR)


  print("Saving card:", output_path)
  img.save(output_path)



if __name__ == "__main__":
  if(OUTPUT_DIR.is_dir()):
    print("Deleting directory:", OUTPUT_DIR)
    shutil.rmtree(OUTPUT_DIR)
  print("Creating directory:", OUTPUT_DIR)
  OUTPUT_DIR.mkdir(parents=True)
  with CARDS_CSV_PATH.open() as csv_file:
    for card_idx, row in enumerate(csv.DictReader(csv_file)):
      output_path = OUTPUT_DIR.joinpath(f"card_{card_idx:03d}.png")
      card_desc = util.to_card_desc(row)
      pprint.pprint(card_desc)
      generate_card(card_desc, output_path)
