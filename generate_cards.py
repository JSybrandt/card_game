#!/usr/bin/env python3

import fire
from PIL import Image
from PIL import ImageDraw
from typing import *
import pathlib
import shutil
import csv
import dataclasses





CARDS_CSV_PATH = pathlib.Path("./cards.csv")
OUTPUT_DIR= pathlib.Path("./img")
FONT_DIR= pathlib.Path("./fonts")
TITLE_FONT = FONT_DIR.joinpath("LeagueGothic-Regular.otf")

assert CARDS_CSV_PATH.is_file()
assert OUTPUT_DIR.is_dir() or not OUTPUT_DIR.exists()
assert FONT_DIR.is_dir()
assert TITLE_FONT.is_file()

# Card size in inches.
CARD_WIDTH_INCH = 2.5
CARD_HEIGHT_INCH = 3.5
PIXELS_PER_INCH = 200
CARD_WIDTH_PX = int(CARD_WIDTH_INCH * PIXELS_PER_INCH)
CARD_HEIGHT_PX = int(CARD_HEIGHT_INCH * PIXELS_PER_INCH)
TITLE_CENTER_X = int(CARD_WIDTH_PX/2)
TITLE_CENTER_Y = int(CARD_HEIGHT_PX * (1/7))

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
  print(desc)

  img = Image.new(mode="RGBA", size=(CARD_WIDTH_PX, CARD_HEIGHT_PX))


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
