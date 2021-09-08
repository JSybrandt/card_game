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

class CardType(enum.Enum):
  SPELL = "Spell"
  HOLDING = "Holding"
  UNIT = "Unit"
  LEADER = "Leader"

class Element(enum.Enum):
  FIRE = "F"
  WATER = "W"
  LIGHT = "L"
  DARK = "D"
  NATURE = "N"
  GENERIC = "G"

@dataclasses.dataclass
class CardDesc:
  element: Element
  card_type:  CardType
  title:      str
  cost:       str
  attributes: str
  body_text:  str
  power:      Optional[str]
  health:     Optional[str]

  def hash(self):
    return hashlib.md5(self.title.encode("utf-8")).hexdigest()

def assert_valid_card_desc(fields:Dict[str, Any]):
  missing_fields = [
    a for a in [
      "Element",
      "Card Type",
      "Title",
      "Cost",
      "Attributes",
      "Body Text",
      "Power",
      "Health",
    ] if a not in fields
  ]
  assert len(missing_fields) == 0, f"Missing attributes: {missing_fields}"

def to_card_desc(fields:Dict[str, Any]):
  assert_valid_card_desc(fields)
  fields = {k: str(v).strip() for k, v in fields.items()}
  fields = {k: v if len(v) > 0 else None for k, v in fields.items()}
  return CardDesc(
    element=Element(fields["Element"]),
    card_type=CardType(fields["Card Type"]),
    title=fields["Title"],
    cost=fields["Cost"],
    attributes=fields["Attributes"],
    body_text=fields["Body Text"],
    health=fields["Health"],
    power=fields["Power"],
  )

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
YELLOW = (250, 193, 87)
ORANGE = (250, 158, 87)
LIGHT_GREY = (211,211,211)
DARK_GREY = (192,192,192)

def get_card_type_light_color(card_type:CardType):
  if card_type == CardType.SPELL:
    return LIGHT_BLUE
  if card_type == CardType.HOLDING:
    return BEIGE
  if card_type == CardType.UNIT:
    return LIGHT_RED
  if card_type == CardType.LEADER:
    return LIGHT_GREY

def get_card_type_dark_color(card_type:CardType):
  if card_type == CardType.SPELL:
    return DARK_BLUE
  if card_type == CardType.HOLDING:
    return DARK_BEIGE
  if card_type == CardType.UNIT:
    return DARK_RED
  if card_type == CardType.LEADER:
    return DARK_GREY

# Border parameters
BORDER_COLOR = BLACK
BORDER_BB = [0, 0, CARD_WIDTH, CARD_HEIGHT]
BORDER_WIDTH = int(CARD_MARGIN/2)
BORDER_CORNER_RADIUS = 20

# Title parameters
TITLE_FONT = ImageFont.truetype(str(LEAGUE_GOTHIC_FONT_PATH), 50)
TITLE_ANCHOR = "ma"  # Top Middle.
TITLE_COORD = (int(CARD_WIDTH/2), CARD_MARGIN)
TITLE_FONT_COLOR=BLACK

# Default icon params
STANDARD_ICON_RADIUS = 0.15 * PIXELS_PER_INCH
LARGE_ICON_RADIUS = 0.2 * PIXELS_PER_INCH
STANDARD_ICON_FONT = ImageFont.truetype(str(LATO_FONT_PATH), 40)
STANDARD_ICON_FONT_COLOR = WHITE

# Cost parameters
COST_COORD = (CARD_MARGIN + STANDARD_ICON_RADIUS,
              CARD_MARGIN + STANDARD_ICON_RADIUS)
COST_BACKGROUND_COLOR = GOLD

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
# Background uses card type dark.

# Optional icons
REVENUE_COORD = get_bb_center(BODY_TEXT_BG_BB)
REVENUE_BG_COLOR = GOLD

LOWER_ICON_Y = CARD_HEIGHT - CARD_MARGIN - CARD_PADDING - STANDARD_ICON_RADIUS

POWER_COORD = (CARD_WIDTH * .25, LOWER_ICON_Y)
POWER_BG_COLOR = ORANGE

HEALTH_COORD = (CARD_WIDTH / 2, LOWER_ICON_Y)
HEALTH_BG_COLOR = RED

DEFENSE_COORD = (CARD_WIDTH * .75, LOWER_ICON_Y)
DEFENSE_BG_COLOR = BLUE



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


def draw_icon(
    draw:ImageDraw.Draw,
    center_coord:Coord,
    text:str,
    bg_color:Color,
    radius:float=STANDARD_ICON_RADIUS,
    text_color:Color=STANDARD_ICON_FONT_COLOR,
    font:ImageFont.ImageFont=STANDARD_ICON_FONT):
  assert radius > 0, f"Radius must be positive: {radius}"
  assert len(text) == 1, f"drawn_icon can only draw 1-char icons, not `{text}`"
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
  card_art = generate_card_art(desc)
  img.paste(card_art, CARD_IMAGE_BB[:2])

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
  if desc.card_type != CardType.LEADER:
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
      card_desc = to_card_desc(row)
      pprint.pprint(card_desc)
      generate_card(card_desc, output_path)
