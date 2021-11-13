import dataclasses
import enum
import hashlib
import json
import math
import pathlib
from typing import Any, Dict, Optional, Tuple

from . import colors

#pylint: disable=too-many-return-statements
#pylint: disable=too-many-instance-attributes

CONFIG_PATH = pathlib.Path("./config.json")
if CONFIG_PATH.is_file():
  with open(CONFIG_PATH, "r", encoding="utf=8") as config_file:
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
GARAMOND_ITALIC_FONT_PATH = FONT_DIR.joinpath("Garamond Italic.ttf")
assert GARAMOND_ITALIC_FONT_PATH.is_file()
GARAMOND_MATH_FONT_PATH = FONT_DIR.joinpath("Garamond-Math.otf")
assert GARAMOND_MATH_FONT_PATH.is_file()

ICON_DIR = pathlib.Path("./icons")
assert ICON_DIR.is_dir()

RESOURCE_DIR = pathlib.Path("./resources")
assert RESOURCE_DIR.is_dir()

MAIN_CARD_BACK_IMG_PATH = RESOURCE_DIR.joinpath("card_back.png")
assert MAIN_CARD_BACK_IMG_PATH.is_file()
MEMORY_CARD_BACK_IMG_PATH = RESOURCE_DIR.joinpath("card_back_pentagon.png")
assert MEMORY_CARD_BACK_IMG_PATH.is_file()

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
  left = x - width // 2
  top = y - height // 2
  right = left + width
  bottom = top + height
  return [left, top, right, bottom]


class CardType(enum.Enum):
  ATTACHMENT = "Attachment"
  SPELL = "Spell"
  MEMORY = "Memory"
  UNIT = "Unit"
  LEADER = "Leader"
  TOKEN = "Token"


class Element(enum.Enum):

  BLUE="B"
  RED="R"
  GREEN="G"
  ORANGE="O"
  PURPLE="P"
  BROWN="W"
  SILVER="S"
  COLORLESS="X"

  def get_color(self) -> colors.Color:
    if self == Element.BLUE:
      return (48, 63, 159)
    if self ==  Element.RED:
      return ( 197, 17, 98)
    if self ==  Element.GREEN:
      return ( 104, 159, 56)
    if self ==  Element.ORANGE:
      return ( 245, 124, 0)
    if self ==  Element.PURPLE:
      return ( 170, 0, 255)
    if self ==  Element.BROWN:
      return ( 121, 85, 72)
    if self ==  Element.SILVER:
      return ( 120, 144, 156)
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
  flavor_text: Optional[str]

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
    "Flavor Text",
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
      flavor_text=fields["Flavor Text"],
  )


def sigmoid(x):
  sig = 1 / (1 + math.exp(-x))
  return sig


def get_output_path(output_dir: pathlib.Path,
                    card_desc: CardDesc) -> pathlib.Path:
  assert output_dir.is_dir()
  return output_dir.joinpath(f"{card_desc.hash_all()}.png")
