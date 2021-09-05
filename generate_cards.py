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

# Helper functions and types

Color = Tuple[int, int, int]

def assert_valid_color(color:Color):
  assert len(color) == 3, f"Invalid color: {color}"
  assert 0 <= color[0] <= 255, f"Invalid color: {color}"
  assert 0 <= color[1] <= 255, f"Invalid color: {color}"
  assert 0 <= color[2] <= 255, f"Invalid color: {color}"

Coord = Tuple[int, int]

def assert_valid_coord(coord:Coord):
  assert len(coord) == 2, f"Invalid coord: {coord}"

BoundingBox = Tuple[int, int, int, int]

def assert_valid_bb(bb: BoundingBox):
  assert len(bb) == 4, f"Invalid bounding box: {bb}"
  assert bb[0] <= bb[2], f"Invalid bounding box: {bb}"
  assert bb[1] <= bb[3], f"Invalid bounding box: {bb}"

def get_bb_center(bb:Tuple[int, int, int, int])->Tuple[int, int]:
  assert_valid_bb(bb)
  x1, y1, x2, y2 = bb
  return int((x1 + x2) / 2), int((y1 + y2) / 2)

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

# Color pallet (r, g, b)
BLACK = (0,0,0)
WHITE = (255,255,255)
RED = (255, 0, 0)
LIGHT_RED = (250, 132, 144)
DARK_RED = (156, 70, 70)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
LIGHT_BLUE = (114, 122, 212)
DARK_BLUE = (77, 70, 156)
GOLD = (218,165,32)
BEIGE = (224, 201, 166)
DARK_BEIGE = (163, 146, 119)

# Background parameters
SPELL_BACKGROUND_COLOR = LIGHT_BLUE
HOLDING_BACKGROUND_COLOR = BEIGE
UNIT_BACKGROUND_COLOR = LIGHT_RED

# Border parameters
BORDER_COLOR = BLACK
BORDER_BB = [0, 0, CARD_WIDTH, CARD_HEIGHT]
BORDER_WIDTH = int(CARD_MARGIN/2)
BORDER_CORNER_RADIUS = 20

# Title parameters
TITLE_FONT = ImageFont.truetype(str(LEAGUE_GOTHIC_FONT_PATH), 60)
TITLE_ANCHOR = "ma"  # Top Middle.
TITLE_COORD = (int(CARD_WIDTH/2), CARD_MARGIN)
TITLE_FONT_COLOR=BLACK

# Cost parameters
COST_RADIUS = int(CARD_WIDTH / 14)
COST_COORD = (CARD_MARGIN + COST_RADIUS, CARD_MARGIN + COST_RADIUS)
COST_FONT = ImageFont.truetype(str(LATO_FONT_PATH), 50)
COST_BACKGROUND_COLOR = GOLD
COST_FONT_COLOR = WHITE

# Card Type Icon
CARD_TYPE_RADIUS = int(CARD_WIDTH / 14)
CARD_TYPE_COORD = (CARD_WIDTH-CARD_TYPE_RADIUS-CARD_MARGIN,
                   CARD_MARGIN+CARD_TYPE_RADIUS)
CARD_TYPE_ICON_FONT = ImageFont.truetype(str(LATO_FONT_PATH), 50)
CARD_TYPE_ICON_FONT_COLOR = WHITE
CARD_TYPE_ICON_BACKGROUND_COLOR_SPELL = DARK_BLUE
CARD_TYPE_ICON_BACKGROUND_COLOR_HOLDING= DARK_BEIGE
CARD_TYPE_ICON_BACKGROUND_COLOR_UNIT = DARK_RED

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

# Random generation parameters
RAND_SHAPE_MIN_RADIUS =  min(CARD_IMAGE_WIDTH, CARD_IMAGE_HEIGHT) * 0.1
RAND_SHAPE_MAX_RADIUS =  min(CARD_IMAGE_WIDTH, CARD_IMAGE_HEIGHT) * 0.3
# We want to generate between 3 sided and 10-sided shapes.
RAND_MIN_POINT_GEN_STEP_RADS = 2 * math.pi / 20
RAND_MAX_POINT_GEN_STEP_RADS = 2 * math.pi / 3
RAND_MIN_SHAPES = 10
RAND_MAX_SHAPES = 100

# Card Attributes
ATTRIBUTE_FONT = ImageFont.truetype(str(LATO_FONT_PATH), 25)
ATTRIBUTE_ANCHOR = "md" # middle bottom
ATTRIBUTE_HEIGHT = CARD_HEIGHT / 20
ATTRIBUTE_BOTTOM = CARD_IMAGE_BOTTOM + ATTRIBUTE_HEIGHT
ATTRIBUTE_COORD = (CARD_WIDTH/2, ATTRIBUTE_BOTTOM)
ATTRIBUTE_TEXT_COLOR = BLACK

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
BODY_TEXT_COLOR = BLACK
# Estimate text size of body text
BODY_TEXT_WIDTH = CONTENT_WIDTH - CARD_PADDING
BODY_TEXT_HEIGHT = BODY_TEXT_BG_BOTTOM - BODY_TEXT_BG_TOP - CARD_PADDING
BODY_TEXT_COORD = (int(CARD_MARGIN + CARD_PADDING * 3 / 2),
                   int(BODY_TEXT_BG_TOP + CARD_PADDING / 2))
BODY_TEXT_ANCHOR = "la" # top left
# Number of pixels between lines.
BODY_TEXT_SPACING = 10
BODY_TEXT_BG_COLOR_SPELL = DARK_BLUE
BODY_TEXT_BG_COLOR_HOLDING = DARK_BEIGE
BODY_TEXT_BG_COLOR_UNIT= DARK_RED


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

class CardType(enum.Enum):
  SPELL = "Spell"
  HOLDING = "Holding"
  UNIT = "Unit"

@dataclasses.dataclass
class CardDesc:
  card_type:CardType
  title: str
  cost: int
  attributes: List[str]
  body_text: str

  def hash(self):
    text = f"{self.title}{self.cost}{self.attributes}{self.body_text}"
    return hashlib.md5(text.encode("utf-8")).hexdigest()


EXPECTED_CSV_HEADER = set([
  "Card Type",
  "Title",
  "Cost",
  "Attributes",
  "Body Text",
])

def get_background_color(desc:CardDesc):
  if desc.card_type == CardType.SPELL:
    return SPELL_BACKGROUND_COLOR
  if desc.card_type == CardType.HOLDING:
    return HOLDING_BACKGROUND_COLOR
  if desc.card_type == CardType.UNIT:
    return UNIT_BACKGROUND_COLOR

def get_body_text_background_color(desc:CardDesc):
  if desc.card_type == CardType.SPELL:
    return BODY_TEXT_BG_COLOR_SPELL
  if desc.card_type == CardType.HOLDING:
    return BODY_TEXT_BG_COLOR_HOLDING
  if desc.card_type == CardType.UNIT:
    return BODY_TEXT_BG_COLOR_UNIT

def get_card_type_icon_background_color(desc:CardDesc):
  if desc.card_type == CardType.SPELL:
    return CARD_TYPE_ICON_BACKGROUND_COLOR_SPELL
  if desc.card_type == CardType.HOLDING:
    return CARD_TYPE_ICON_BACKGROUND_COLOR_HOLDING
  if desc.card_type == CardType.UNIT:
    return CARD_TYPE_ICON_BACKGROUND_COLOR_UNIT

def rand_shape(x_offset: float, y_offset: float, scale:float)->List[int]:
  """Returns the points of a shape in clockwise order centered at offset."""
  points = []
  angle_offset = random.random() * 2 * math.pi
  angle = 0
  while angle < 2*math.pi:
    magnitude = random.uniform(
      RAND_SHAPE_MIN_RADIUS, RAND_SHAPE_MAX_RADIUS) * scale
    x = math.cos(angle + angle_offset) * magnitude + x_offset
    y = math.sin(angle + angle_offset) * magnitude + y_offset
    points.append((x, y))
    angle += random.uniform(RAND_MIN_POINT_GEN_STEP_RADS,
                            RAND_MAX_POINT_GEN_STEP_RADS)
  return points

@dataclasses.dataclass
class ColorPalette:
  # These are in 0-1
  primary_hue: float
  secondary_hue: float
  alt_hues: List[float]

  def primary(self)->Tuple[int, int, int]:
    return tuple(
      int(255*c) for c in colorsys.hsv_to_rgb(self.primary_hue, 1, 1))

  def secondary(self)->Tuple[int, int, int]:
    return tuple(
      int(255*c) for c in colorsys.hsv_to_rgb(self.secondary_hue, 1, 1))


def rand_color_palette()->ColorPalette:
  primary_hue = random.random()
  secondary_hue = (primary_hue + 0.5 + random.uniform(-0.2, 0.2)) % 1
  alt_hues = [
    ((primary_hue - secondary_hue)/2) % 1,
    ((secondary_hue - primary_hue)/2) % 1,
    random.random(), random.random(), random.random(),
  ]
  return ColorPalette(primary_hue, secondary_hue, alt_hues)

def rand_color(palette:ColorPalette)->Tuple[int, int, int]:
  hue = random.choices(
    [palette.primary_hue, palette.secondary_hue] + palette.alt_hues,
    weights=[0.5, 0.25] + [0.25/len(palette.alt_hues) for _ in palette.alt_hues]
  )[0]
  saturation = random.uniform(0.5, 1)
  value = random.uniform(0, 1)
  return tuple(int(255*c) for c in colorsys.hsv_to_rgb(hue, saturation, value))


def generate_card_art(desc:CardDesc)->Image:
  # Seed random number gen with deterministic hash of card description. This
  # gives us the same image if we run the generation script twice.
  random.seed(desc.hash())

  # We generate an internal image and paste it into the card.
  img = Image.new(mode="RGBA", size=(CARD_IMAGE_WIDTH, CARD_IMAGE_HEIGHT))
  draw = ImageDraw.Draw(img)

  draw.rectangle([0, 0, CARD_IMAGE_WIDTH, CARD_IMAGE_HEIGHT],
                 fill=BLACK)

  num_shapes = random.randint(RAND_MIN_SHAPES, RAND_MAX_SHAPES)
  color_palette = rand_color_palette()
  for shape_idx in range(num_shapes):
    offset_x = random.uniform(0, CARD_IMAGE_WIDTH)
    offset_y = random.uniform(0, CARD_IMAGE_HEIGHT)
    shape = rand_shape(offset_x, offset_y, scale=1)
    draw.polygon(shape, fill=rand_color(color_palette))
  # Draw a big secondary
  offset_x = random.uniform(CARD_IMAGE_WIDTH*0.1, CARD_IMAGE_WIDTH*0.9)
  offset_y = random.uniform(CARD_IMAGE_HEIGHT*0.1, CARD_IMAGE_HEIGHT*0.9)
  shape = rand_shape(offset_x, offset_y, scale=3)
  draw.polygon(shape, fill=color_palette.secondary())

  offset_x = random.uniform(CARD_IMAGE_WIDTH*0.1, CARD_IMAGE_WIDTH*0.9)
  offset_y = random.uniform(CARD_IMAGE_HEIGHT*0.1, CARD_IMAGE_HEIGHT*0.9)
  shape = rand_shape(offset_x, offset_y, scale=3)
  draw.polygon(shape, fill=color_palette.primary())

  return img


def draw_icon(draw:ImageDraw.Draw, center_coord:Coord, radius:float, text:str,
              bg_color:Color, text_color:Color, font:ImageFont.ImageFont):
  assert radius > 0, f"Radius must be positive: {radius}"
  assert len(text) == 1, f"drawn_icon can only draw 1-letter icons, not {text}"
  assert_valid_color(bg_color)
  assert_valid_color(text_color)
  assert_valid_coord(center_coord)
  center_x, center_y = center_coord
  background_bb = [
    center_x - radius,
    center_y - radius,
    center_x + radius,
    center_y + radius,
  ]
  draw.ellipse(background_bb, fill=bg_color)
  draw.text(center_coord, text, text_color, font=font, anchor="mm")

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
    fill=get_background_color(desc),
  )

  # Title, center text at top of card.
  draw.text(
    TITLE_COORD,
    desc.title,
    TITLE_FONT_COLOR,
    font=TITLE_FONT,
    anchor=TITLE_ANCHOR)

  # Cost in the top left.
  draw_icon(draw, COST_COORD, COST_RADIUS, str(desc.cost),
            COST_BACKGROUND_COLOR, COST_FONT_COLOR, COST_FONT)

  # Card type icon in the top right.
  draw_icon(draw, CARD_TYPE_COORD, CARD_TYPE_RADIUS,
            str(desc.card_type.value)[0],
            get_card_type_icon_background_color(desc),
            CARD_TYPE_ICON_FONT_COLOR, CARD_TYPE_ICON_FONT)

  # Card image placeholder.
  card_art = generate_card_art(desc)
  img.paste(card_art, CARD_IMAGE_BB[:2])

  # Card card_type text
  draw.text(
    ATTRIBUTE_COORD,
    ", ".join(desc.attributes),
    ATTRIBUTE_TEXT_COLOR,
    font=ATTRIBUTE_FONT,
    anchor=ATTRIBUTE_ANCHOR,
  )

  # Body text
  draw.rectangle(
    BODY_TEXT_BG_BB,
    fill=get_body_text_background_color(desc))

  draw.multiline_text(
    BODY_TEXT_COORD,
    text=wrap_body_text(desc.body_text),
    fill=BODY_TEXT_COLOR,
    anchor=BODY_TEXT_ANCHOR,
    align="left",
    font=BODY_TEXT_FONT,
    spacing=BODY_TEXT_SPACING,
  )


  print("Saving card:", output_path)
  img.save(output_path)


def to_card_desc(attr:Dict[str, Any]):
  assert set(attr.keys()) == EXPECTED_CSV_HEADER, f"{set(attr.keys())}"
  return CardDesc(
    card_type=CardType(attr["Card Type"]),
    title=attr["Title"],
    cost=int(attr["Cost"]),
    attributes=list(attr["Attributes"].split(",")),
    body_text=attr["Body Text"],
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
