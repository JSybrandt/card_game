from typing import *
import enum
import dataclasses
import hashlib

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
