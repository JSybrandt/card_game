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

# Color pallet (r, g, b)
BLACK = (0,0,0)
WHITE = (255,255,255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
GOLD = (218,165,32)
BEIGE = (224, 201, 166)
DARK_BEIGE = (163, 146, 119)

# Background parameters
BACKGROUND_COLOR = BEIGE

# Border parameters
BORDER_COLOR = BLACK
BORDER_BB = [0, 0, CARD_WIDTH, CARD_HEIGHT]
BORDER_WIDTH = int(CARD_MARGIN/2)
BORDER_CORNER_RADIUS = 20

# Title parameters
TITLE_FONT = ImageFont.truetype(str(LEAGUE_GOTHIC_FONT_PATH), 60)
TITLE_ANCHOR = "ma"  # Top Middle.
TITLE_COORD = (CARD_WIDTH/2, CARD_MARGIN)
TITLE_FONT_COLOR=BLACK

# Cost parameters
COST_WIDTH = CARD_WIDTH / 7
COST_BACKGROUND_BB = [
  CARD_MARGIN, CARD_MARGIN, COST_WIDTH + CARD_MARGIN, COST_WIDTH + CARD_MARGIN]
COST_BACKGROUND_COLOR = GOLD
COST_FONT = ImageFont.truetype(str(LATO_FONT_PATH), 50)
COST_ANCHOR = "mm"  # Middle
COST_COORD = (CARD_MARGIN + COST_WIDTH / 2, CARD_MARGIN + COST_WIDTH / 2)
COST_FONT_COLOR = WHITE

# Describes the max width of card contents
CONTENT_WIDTH = CARD_WIDTH - 2*CARD_MARGIN

# Card image parameters
# Width and height of card image
CARD_IMAGE_WIDTH = CONTENT_WIDTH
CARD_IMAGE_HEIGHT = CARD_HEIGHT * 0.4
CARD_IMAGE_TOP = CARD_HEIGHT / 7
CARD_IMAGE_BOTTOM = CARD_IMAGE_TOP + CARD_IMAGE_HEIGHT
CARD_IMAGE_BB = [
  CARD_MARGIN,
  CARD_IMAGE_TOP,
  CARD_MARGIN + CONTENT_WIDTH,
  CARD_IMAGE_BOTTOM,
]

# Body text
BODY_TEXT_FONT = ImageFont.truetype(str(COLWELLA_FONT_PATH), 20)
BODY_TEXT_BG_TOP = CARD_IMAGE_BOTTOM + CARD_PADDING
BODY_TEXT_BG_BOTTOM = CARD_HEIGHT - CARD_MARGIN - CARD_PADDING
BODY_TEXT_BG_BB = [
  CARD_MARGIN,
  BODY_TEXT_BG_TOP,
  CARD_MARGIN + CONTENT_WIDTH,
  BODY_TEXT_BG_BOTTOM,
]
BODY_TEXT_COLOR = BLACK
BODY_TEXT_BG_COLOR = DARK_BEIGE
# Estimate text size of body text
BODY_TEXT_WIDTH = CONTENT_WIDTH - CARD_PADDING
BODY_TEXT_HEIGHT = BODY_TEXT_BG_BOTTOM - BODY_TEXT_BG_TOP - CARD_PADDING
BODY_TEXT_COORD = (CARD_MARGIN + CARD_PADDING * 3 / 2,
              BODY_TEXT_BG_TOP + CARD_PADDING / 2)
BODY_TEXT_ANCHOR = "la" # top left


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


@dataclasses.dataclass
class CardDesc:
  name: str
  cost: int
  types: Set[str]
  body_text: str
  flavor_text: str

EXPECTED_CSV_HEADER = set([
  "Name",
  "Cost",
  "Types",
  "Body Text",
  "Flavor Text",
])

def generate_card(desc:CardDesc, output_path:pathlib.Path):
  assert not output_path.exists(), f"{output_path} already exists"
  img = Image.new(mode="RGBA", size=(CARD_WIDTH, CARD_HEIGHT))
  draw = ImageDraw.Draw(img)

  # Border + background
  draw.rounded_rectangle(
    BORDER_BB,
    outline=BORDER_COLOR,
    width=BORDER_WIDTH,
    radius=BORDER_CORNER_RADIUS,
    fill=BACKGROUND_COLOR
  )

  # Title, center text at top of card.
  draw.text(
    TITLE_COORD,
    desc.name,
    TITLE_FONT_COLOR,
    font=TITLE_FONT,
    anchor=TITLE_ANCHOR)

  # Cost in the top left.
  draw.ellipse(
    COST_BACKGROUND_BB,
    fill=COST_BACKGROUND_COLOR
  )
  draw.text(
    COST_COORD,
    str(desc.cost),
    COST_FONT_COLOR,
    font=COST_FONT,
    anchor=COST_ANCHOR)

  # Card image placeholder.
  # TODO replace this with some filler image.
  draw.rectangle(
    CARD_IMAGE_BB,
    fill=BLACK)

  # Body text
  draw.rectangle(
    BODY_TEXT_BG_BB,
    fill=BODY_TEXT_BG_COLOR)

  draw.multiline_text(
    BODY_TEXT_COORD,
    text=wrap_body_text(desc.body_text),
    fill=BODY_TEXT_COLOR,
    anchor=BODY_TEXT_ANCHOR,
    align="left",
    font=BODY_TEXT_FONT)


  print("Saving card:", output_path)
  img.save(output_path)


def to_card_desc(attr:Dict[str, Any]):
  assert set(attr.keys()) == EXPECTED_CSV_HEADER
  return CardDesc(
    name=attr["Name"],
    cost=int(attr["Cost"]),
    types=set(attr["Types"].split(",")),
    body_text=attr["Body Text"],
    flavor_text=attr["Flavor Text"],
  )

if __name__ == "__main__":
  if(OUTPUT_DIR.is_dir()):
    print("Deleting directory:", OUTPUT_DIR)
    shutil.rmtree(OUTPUT_DIR)
  print("Creating directory:", OUTPUT_DIR)
  OUTPUT_DIR.mkdir(parents=True)
  with CARDS_CSV_PATH.open() as csv_file:
    for card_idx, row in enumerate(csv.DictReader(csv_file)):
      output_path = OUTPUT_DIR.joinpath(f"card_{card_idx}.png")
      card_desc = to_card_desc(row)
      generate_card(card_desc, output_path)
