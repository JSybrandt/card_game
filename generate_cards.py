#!/usr/bin/env python3

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
from typing import *
import pathlib
import shutil
import csv
import pprint
import colors
import util
import card_art
import icons
import body_text

# Constants

CARDS_CSV_PATH = pathlib.Path("./cards.csv")
assert CARDS_CSV_PATH.is_file()
OUTPUT_DIR= pathlib.Path("./img")
assert OUTPUT_DIR.is_dir() or not OUTPUT_DIR.exists()


# Card size in inches.
CARD_WIDTH_INCH = 2.5
CARD_HEIGHT_INCH = 3.5
CARD_MARGIN_INCH = 0.1
CARD_PADDING_INCH = 0.025
# Unless specified, all sizes are in pixels.
CARD_WIDTH = int(2.5 * util.PIXELS_PER_INCH)
CARD_HEIGHT = int(3.5 * util.PIXELS_PER_INCH)
CARD_MARGIN = int(0.1 * util.PIXELS_PER_INCH)
CARD_PADDING = int(0.025 * util.PIXELS_PER_INCH)

# Default icon params
SMALL_ICON_HEIGHT = SMALL_ICON_WIDTH = int(0.3*util.PIXELS_PER_INCH)
LARGE_ICON_HEIGHT = LARGE_ICON_WIDTH = int(0.4*util.PIXELS_PER_INCH)
SMALL_ICON_FONT = ImageFont.truetype(str(util.LATO_FONT_PATH), int(util.PIXELS_PER_INCH * 0.2))
LARGE_ICON_FONT = ImageFont.truetype(str(util.LATO_FONT_PATH), int(util.PIXELS_PER_INCH * 0.3))
SMALL_ICON_FONT_COLOR = colors.WHITE
LARGE_ICON_FONT_COLOR = colors.WHITE

TOP_ICON_Y = int(SMALL_ICON_HEIGHT / 2) + CARD_MARGIN

# Title parameters
TITLE_FONT = ImageFont.truetype(str(util.LEAGUE_GOTHIC_FONT_PATH), int(util.PIXELS_PER_INCH * 0.25))
TITLE_ANCHOR = "mm"  # Middle Middle.
TITLE_COORD = (int(CARD_WIDTH/2), TOP_ICON_Y)
TITLE_FONT_COLOR=colors.BLACK

# Cost parameters
COST_COORD = (CARD_MARGIN + int(SMALL_ICON_WIDTH / 2), TOP_ICON_Y)

# Describes the max width of card contents
CONTENT_WIDTH = CARD_WIDTH - 2*CARD_MARGIN

# Card image parameters
# Width and height of card image
CARD_IMAGE_WIDTH = CONTENT_WIDTH
CARD_IMAGE_HEIGHT = int(CARD_HEIGHT * 0.4)
CARD_IMAGE_TOP = TOP_ICON_Y + int(SMALL_ICON_HEIGHT / 2) + CARD_PADDING
CARD_IMAGE_BOTTOM = CARD_IMAGE_TOP + CARD_IMAGE_HEIGHT
CARD_IMAGE_BB = [
  CARD_MARGIN,
  CARD_IMAGE_TOP,
  CARD_MARGIN + CONTENT_WIDTH,
  CARD_IMAGE_BOTTOM,
]


# Card Attributes
ATTRIBUTE_FONT = ImageFont.truetype(str(util.LATO_FONT_PATH), int(util.PIXELS_PER_INCH * 0.125))
ATTRIBUTE_ANCHOR = "md" # middle bottom
ATTRIBUTE_HEIGHT = int(CARD_HEIGHT / 20)
ATTRIBUTE_BOTTOM = CARD_IMAGE_BOTTOM + ATTRIBUTE_HEIGHT
ATTRIBUTE_COORD = (CARD_WIDTH/2, ATTRIBUTE_BOTTOM)
ATTRIBUTE_TEXT_COLOR = colors.BLACK

# Body text
BODY_TEXT_BG_BB = [
  CARD_MARGIN,
  ATTRIBUTE_BOTTOM + CARD_PADDING,
  CARD_MARGIN + CONTENT_WIDTH,
  CARD_HEIGHT - int(LARGE_ICON_HEIGHT / 2) - CARD_MARGIN,
]

BOTTOM_ICON_Y = CARD_HEIGHT - int(LARGE_ICON_HEIGHT / 2) - CARD_MARGIN

POWER_COORD = (CARD_WIDTH * 0.25, BOTTOM_ICON_Y)
POWER_BG_COLOR = colors.BLUE_GREY_800

HEALTH_COORD = (CARD_WIDTH * 0.75, BOTTOM_ICON_Y)
HEALTH_BG_COLOR = colors.RED_A400

MANA_COORD = (CARD_WIDTH/2, BOTTOM_ICON_Y)


# Layout functions


def generate_card(desc:util.CardDesc, output_path:pathlib.Path):
  assert not output_path.exists(), f"{output_path} already exists"
  im = Image.new(mode="RGBA", size=(CARD_WIDTH, CARD_HEIGHT))
  draw = ImageDraw.Draw(im)

  card_art.render_background(im, draw, desc, [0, 0, CARD_WIDTH, CARD_HEIGHT])

  # Title, center text at top of card.
  draw.text(
    TITLE_COORD,
    desc.title,
    TITLE_FONT_COLOR,
    font=TITLE_FONT,
    anchor=TITLE_ANCHOR)

  # Card image placeholder.
  card_art.render_card_art(im, draw, desc, CARD_IMAGE_BB)

  # Card card_type text
  if desc.attributes is not None:
    draw.text(
      ATTRIBUTE_COORD,
      f"{desc.card_type.value}— {desc.attributes}",
      ATTRIBUTE_TEXT_COLOR,
      font=ATTRIBUTE_FONT,
      anchor=ATTRIBUTE_ANCHOR,
    )

  body_text.render_body_text(im, draw, desc.body_text, BODY_TEXT_BG_BB)

  # Draw icons
  if desc.cost is not None:
    icons.draw_circle_with_text(
      draw, COST_COORD, SMALL_ICON_WIDTH, SMALL_ICON_HEIGHT,  desc.cost,
      SMALL_ICON_FONT, SMALL_ICON_FONT_COLOR, desc.element.get_dark_color())
  if desc.health is not None:
    icons.draw_circle_with_text(
      draw, HEALTH_COORD, LARGE_ICON_WIDTH, LARGE_ICON_HEIGHT, desc.health,
      LARGE_ICON_FONT, LARGE_ICON_FONT_COLOR, HEALTH_BG_COLOR)
  if desc.power is not None:
    icons.draw_circle_with_text(
      draw, POWER_COORD, LARGE_ICON_WIDTH, LARGE_ICON_HEIGHT, desc.power,
      LARGE_ICON_FONT, LARGE_ICON_FONT_COLOR, POWER_BG_COLOR)
  if desc.card_type == util.CardType.HOLDING:
    icons.draw_circle_with_text(
      draw, MANA_COORD, LARGE_ICON_WIDTH, LARGE_ICON_HEIGHT, "1",
      LARGE_ICON_FONT, LARGE_ICON_FONT_COLOR, desc.element.get_dark_color())

  print("Saving card:", output_path)
  im.save(output_path)



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
