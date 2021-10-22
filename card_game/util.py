import dataclasses
import enum
import hashlib
import math
import pathlib
import json
from typing import Any, Dict, Optional, Tuple

from . import colors

#pylint: disable=too-many-return-statements
#pylint: disable=too-many-instance-attributes

CONFIG_PATH = pathlib.Path("./config.json")
if CONFIG_PATH.is_file():
  with open(CONFIG_PATH, "r") as config_file:
    GLOBAL_CONFIG = json.loads(config_file.read())
  print("Loaded global config:", GLOBAL_CONFIG)
else:
  GLOBAL_CONFIG = {}

PIXELS_PER_INCH = GLOBAL_CONFIG.get("pixels_per_inch", 100)

FONT_DIR = pathlib.Path("./fonts")
assert FONT_DIR.is_dir()
LEAGUE_GOTHIC_FONT_PATH = FONT_DIR.joinpath("LeagueGothic-Regular.otf")
assert LEAGUE_GOTHIC_FONT_PATH.is_file()
LATO_FONT_PATH = FONT_DIR.joinpath("Lato-Regular.ttf")
assert LATO_FONT_PATH.is_file()
COLWELLA_FONT_PATH = FONT_DIR.joinpath("Colwella.ttf")
assert COLWELLA_FONT_PATH.is_file()
EB_GARAMOND_FONT_PATH = FONT_DIR.joinpath("EBGaramond-VariableFont_wght.ttf")
assert EB_GARAMOND_FONT_PATH.is_file()
GARAMOND_MATH_FONT_PATH = FONT_DIR.joinpath("Garamond-Math.otf")
assert GARAMOND_MATH_FONT_PATH.is_file()

ICON_DIR = pathlib.Path("./icons")
assert ICON_DIR.is_dir()

Coord = Tuple[int, int]


def assert_valid_coord(coord: Coord):
  assert len(coord) == 2, f"Invalid coord: {coord}"


BoundingBox = Tuple[int, int, int, int]


def assert_valid_bb(bb: BoundingBox):
  assert len(bb) == 4, f"Invalid bounding box: {bb}"
  assert bb[0] <= bb[2], f"Invalid bounding box: {bb}"
  assert bb[1] <= bb[3], f"Invalid bounding box: {bb}"


def get_bb_center(bb: BoundingBox) -> Coord:
  assert_valid_bb(bb)
  x1, y1, x2, y2 = bb
  return int((x1 + x2) / 2), int((y1 + y2) / 2)


def get_centered_bb(center: Coord, width: int, height: int) -> BoundingBox:
  x, y = center
  return [
      int(x - width / 2),
      int(y - height / 2),
      int(x + width / 2),
      int(y + height / 2)
  ]


class CardType(enum.Enum):
  ATTACHMENT = "Attachment"
  SPELL = "Spell"
  MEMORY = "Memory"
  UNIT = "Unit"
  LEADER = "Leader"
  TOKEN = "Token"


class Element(enum.Enum):
  FIRE = "F"
  WATER = "W"
  LIGHT = "L"
  DARK = "D"
  NATURE = "N"
  GENERIC = "G"

  def get_primary_color(self) -> colors.Color:
    if self == Element.FIRE:
      return colors.RED_500
    if self == Element.WATER:
      return colors.BLUE_500
    if self == Element.LIGHT:
      return colors.YELLOW_500
    if self == Element.DARK:
      return colors.PURPLE_500
    if self == Element.NATURE:
      return colors.GREEN_500
    if self == Element.GENERIC:
      return colors.GREY_400
    return colors.BLACK

  def get_light_color(self) -> colors.Color:
    if self == Element.FIRE:
      return colors.RED_200
    if self == Element.WATER:
      return colors.BLUE_200
    if self == Element.LIGHT:
      return colors.YELLOW_200
    if self == Element.DARK:
      return colors.PURPLE_200
    if self == Element.NATURE:
      return colors.GREEN_200
    if self == Element.GENERIC:
      return colors.GREY_200
    return colors.BLACK

  def get_dark_color(self) -> colors.Color:
    if self == Element.FIRE:
      return colors.RED_900
    if self == Element.WATER:
      return colors.BLUE_900
    if self == Element.LIGHT:
      return colors.YELLOW_900
    if self == Element.DARK:
      return colors.PURPLE_900
    if self == Element.NATURE:
      return colors.GREEN_900
    if self == Element.GENERIC:
      return colors.GREY_600
    return colors.BLACK


@dataclasses.dataclass
class CardDesc:
  primary_element: Element
  secondary_element: Optional[Element]
  card_type: CardType
  title: str
  cost: str
  attributes: str
  body_text: str
  strength: Optional[str]
  health: Optional[str]

  def hash_title(self):
    return hashlib.md5(self.title.encode("utf-8")).hexdigest()

  def hash_all(self):
    return hashlib.md5(str(self).encode("utf-8")).hexdigest()


# The CSV headers in order.
EXPECTED_COLUMN_HEADERS = [
    "Primary Element",
    "Secondary Element",
    "Card Type",
    "Title",
    "Cost",
    "Attributes",
    "Body Text",
    "Strength",
    "Health",
]


def assert_valid_card_desc(fields: Dict[str, Any]):
  missing_fields = [a for a in EXPECTED_COLUMN_HEADERS if a not in fields]
  assert len(missing_fields) == 0, f"Missing attributes: {missing_fields}"


def field_dict_to_card_desc(fields: Dict[str, Any]):
  assert_valid_card_desc(fields)

  def _clean_value(v: Any) -> Optional[str]:
    if v is None:
      return v
    v = str(v).strip()
    if len(v) == 0:
      return None
    return v

  fields = {k: _clean_value(v) for k, v in fields.items()}
  fields["Primary Element"] = Element(fields["Primary Element"])
  if fields["Secondary Element"] is not None:
    fields["Secondary Element"] = Element(fields["Secondary Element"])
  fields["Card Type"] = CardType(fields["Card Type"])

  return CardDesc(
      primary_element=fields["Primary Element"],
      secondary_element=fields["Secondary Element"],
      card_type=fields["Card Type"],
      title=fields["Title"],
      cost=fields["Cost"],
      attributes=fields["Attributes"],
      body_text=fields["Body Text"],
      health=fields["Health"],
      strength=fields["Strength"],
  )


def sigmoid(x):
  sig = 1 / (1 + math.exp(-x))
  return sig

def get_output_path(output_dir:pathlib.Path, card_desc:CardDesc)->pathlib.Path:
  assert output_dir.is_dir()
  return output_dir.joinpath(f"{card_desc.hash_all()}.png")
