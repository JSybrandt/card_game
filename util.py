from typing import *
import enum
import dataclasses
import hashlib
import colors

Coord = Tuple[int, int]

def assert_valid_coord(coord:Coord):
  assert len(coord) == 2, f"Invalid coord: {coord}"

BoundingBox = Tuple[int, int, int, int]

def assert_valid_bb(bb: BoundingBox):
  assert len(bb) == 4, f"Invalid bounding box: {bb}"
  assert bb[0] <= bb[2], f"Invalid bounding box: {bb}"
  assert bb[1] <= bb[3], f"Invalid bounding box: {bb}"

def get_bb_center(bb:BoundingBox)->Coord:
  assert_valid_bb(bb)
  x1, y1, x2, y2 = bb
  return int((x1 + x2) / 2), int((y1 + y2) / 2)

def get_centered_bb(center:Coord, width:int, height:int)->BoundingBox:
  x, y = center
  return [int(x - width / 2), int(y - height / 2),
          int(x + width / 2), int(y + height / 2)]

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

  def get_primary_color(self)->colors.Color:
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

  def get_light_color(self)->colors.Color:
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

  def get_dark_color(self)->colors.Color:
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