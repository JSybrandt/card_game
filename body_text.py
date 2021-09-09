from typing import *
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
import util
import colors

# Customizations of the body text area.

BG_RADIUS = 10
BG_COLOR = colors.BROWN_100
MARGIN = 10
SPACING = 10

def clean_body_text(text:str)->str:
  text = text.replace("<ACTION>", "\n•")
  # These are pulled from the wikipedia on unicode math symbols
  text = text.replace("<ANY>", "")
  text = text.replace("<HOLDING>", "\U0000201d")
  text = text.replace("<RECRUIT>", "\U0000211d")
  text = text.replace("<COMBAT>", "\U00002102")
  text = text.replace("<RANGED>", "\U000021e2")
  text = text.replace("<EXHAUST>", "\U000021a9")
  text = text.strip()
  return text

def wrap_body_text(font:ImageFont.ImageFont, body_text:str, text_width:float)->str:
  literal_lines = []
  for logical_line in clean_body_text(body_text).split("\n"):
    working_text = []
    for token in logical_line.split():
      if font.getsize(
        " ".join(working_text + [token]))[0] > text_width:
        literal_lines.append(" ".join(working_text))
        working_text = []
      working_text.append(token)
    literal_lines.append(" ".join(working_text))
  return "\n".join(literal_lines)

def draw_body_text(
    draw:ImageDraw.Draw,
    text:Optional[str],
    body_text_bb: util.BoundingBox,
    font:ImageFont.ImageFont):
  util.assert_valid_bb(body_text_bb)
  draw.rounded_rectangle(
    body_text_bb,
    radius=BG_RADIUS,
    fill=BG_COLOR)
  if text is None:
    return
  top_left_coord = (body_text_bb[0] + MARGIN, body_text_bb[1] + MARGIN)
  text_width = body_text_bb[2] - body_text_bb[0] - 2*MARGIN
  draw.multiline_text(
    top_left_coord,
    text=wrap_body_text(font, text, text_width),
    fill=colors.BLACK,
    anchor="la",
    align="left",
    font=font,
    spacing=SPACING,
  )


