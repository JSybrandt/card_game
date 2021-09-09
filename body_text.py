from typing import *
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
import util
import colors
import re
import pathlib
import icons

# Customizations of the body text area.

FONT_DIR= pathlib.Path("./fonts")
assert FONT_DIR.is_dir()
EB_GARAMOND_FONT_PATH = FONT_DIR.joinpath("EBGaramond-VariableFont_wght.ttf")
assert EB_GARAMOND_FONT_PATH.is_file()
LATO_FONT_PATH = FONT_DIR.joinpath("Lato-Regular.ttf")
assert LATO_FONT_PATH.is_file()

FONT = ImageFont.truetype(str(EB_GARAMOND_FONT_PATH), 20)
FONT_COLOR = colors.BLACK
BG_RADIUS = 10
BG_COLOR = colors.BROWN_100
MARGIN = 10
TEXT_HEIGHT = 25
LINE_SPACING = 30

ACTION_ICON_WIDTH = ACTION_ICON_HEIGHT = 15
ACTION_ICON_COLOR = colors.BLACK

MANA_ICON_WIDTH = MANA_ICON_HEIGHT = 25
MANA_ICON_FONT = ImageFont.truetype(str(LATO_FONT_PATH), 20)
MANA_ICON_FONT_COLOR = colors.WHITE
# Currently only matches one character costs.
MANA_ICON_REGEX = "<(.)([FWDLNG])>"

Cursor = List[int]

def draw_action_icon(draw:ImageDraw.Draw, cursor:Cursor):
  left, center_y = cursor
  top = center_y - int(ACTION_ICON_HEIGHT / 2)
  bottom = top + ACTION_ICON_HEIGHT
  right = left + ACTION_ICON_WIDTH
  center_x = left + int(ACTION_ICON_HEIGHT / 2)

  arrow = [(left, top), (center_x, center_y), (left, bottom), (right, center_y)]
  draw.polygon(arrow, fill=ACTION_ICON_COLOR)
  cursor[0] = right

def draw_mana_icon(draw:ImageDraw, cursor:Cursor, text:str, element:util.Element):
  center = (cursor[0] + int(MANA_ICON_WIDTH / 2), cursor[1])
  icons.draw_circle_with_text(draw, center, MANA_ICON_WIDTH, MANA_ICON_HEIGHT,
                              text, MANA_ICON_FONT, MANA_ICON_FONT_COLOR,
                              element.get_dark_color())
  cursor[0] += MANA_ICON_WIDTH


def draw_body_text(
    draw:ImageDraw.Draw,
    text:Optional[str],
    body_text_bb: util.BoundingBox):
  util.assert_valid_bb(body_text_bb)
  draw.rounded_rectangle(
    body_text_bb,
    radius=BG_RADIUS,
    fill=BG_COLOR)
  if text is None:
    return

  bg_x1, bg_y1, bg_x2, bg_y2 = body_text_bb
  text_area_left = bg_x1 + MARGIN
  text_area_right = bg_x2 - MARGIN
  text_area_top = bg_y1 + MARGIN
  text_area_bottom = bg_y2 - MARGIN

  # Cursor should always be the center-left of the new text.
  cursor = [text_area_left, text_area_top + TEXT_HEIGHT/2]
  cursor_state = {
    "newline_indent": 0,
  }

  def _newline():
    cursor[0] = text_area_left + cursor_state["newline_indent"]
    cursor[1] += TEXT_HEIGHT

  def _maybe_newline(token_width:float):
    if cursor[0] + token_width > text_area_right:
      _newline()

  def _print(token:str):
    token_width, _ = FONT.getsize(token)
    _maybe_newline(token_width)
    draw.text(cursor, token, FONT_COLOR, font=FONT, anchor="lm")
    cursor[0] += token_width

  def _draw_action(token_index:int):
    cursor_state["newline_indent"] = 0
    if token_index != 0:
      _newline()
    draw_action_icon(draw, cursor)
    cursor_state["newline_indent"] = ACTION_ICON_WIDTH + FONT.getsize(" ")[0]

  def _draw_token(token:str, token_index:int):
    if token == "<ACTION>":
      _draw_action(token_index)
      return
    mana_match = re.match(MANA_ICON_REGEX, token)
    if mana_match:
      _maybe_newline(MANA_ICON_WIDTH)
      draw_mana_icon(draw, cursor, text=mana_match.group(1),
                     element=util.Element(mana_match.group(2)))
      return
    _print(token)

  token_index = 0
  for line in text.split("\n"):
    for line_idx, token in enumerate(line.split()):
      token_index += 1
      if(line_idx > 0):
        _print(" ")
      _draw_token(token, token_index)
    cursor_state["newline_indent"] = 0
    _newline()

