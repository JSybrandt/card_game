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

FONT = ImageFont.truetype(str(util.EB_GARAMOND_FONT_PATH), int(util.PIXELS_PER_INCH*0.1))
FONT_COLOR = colors.BLACK
BG_RADIUS = int(util.PIXELS_PER_INCH * 0.05)
BG_COLOR = colors.BROWN_100
BODY_TEXT_MARGIN = int(util.PIXELS_PER_INCH * 0.05)

TEXT_HEIGHT = int(util.PIXELS_PER_INCH * 0.1)
TOKEN_PADDING_Y = int(util.PIXELS_PER_INCH * 0.01)
TOKEN_PADDING_X = int(util.PIXELS_PER_INCH * 0.02)

COST_BG_COLOR = colors.GREY_200
COST_PADDING_X = int(util.PIXELS_PER_INCH * 0.025)


UNKNOWN_TEXT = "[?]"
class Token():
  def __init__(self, text:str):
    self.text = text

  def render(self,im:Image,  draw:ImageDraw.Draw, cursor_x:int, cursor_y:int):
    draw.text((cursor_x, cursor_y), UNKNOWN_TEXT, FONT_COLOR, font=FONT,
              anchor="lm")

  def width(self):
    return FONT.getsize(UNKNOWN_TEXT)[0]

  @classmethod
  def is_token(cls, text:str)->bool:
    return True

class Newline(Token):
  def __init__(self, text:str):
    super().__init__(text)

  @classmethod
  def is_token(cls, text:str)->bool:
    return text == "<NEWLINE>"

class EndCost(Token):
  def __init__(self, text:str):
    super().__init__(text)

  @classmethod
  def is_token(cls, text:str)->bool:
    return text == "<END_COST>"

class TextToken(Token):
  def __init__(self, text:str):
    super().__init__(text)

  def render(self,im:Image,  draw:ImageDraw.Draw, cursor_x:int, cursor_y:int):
    draw.text((cursor_x, cursor_y), self.text, FONT_COLOR, font=FONT,
              anchor="lm")

  def width(self):
    return FONT.getsize(self.text)[0]

  @classmethod
  def is_token(cls, text:str)->bool:
    return text[0] != "<" and text[-1] != ">"

MANA_ICON_WIDTH = MANA_ICON_HEIGHT = int(TEXT_HEIGHT * 0.9)
MANA_ICON_FONT = ImageFont.truetype(str(util.LATO_FONT_PATH), int(util.PIXELS_PER_INCH * 0.08))
MANA_ICON_FONT_COLOR = colors.WHITE
MANA_ICON_REGEX = "<(.+)([FWDLNG])>"
class ManaToken(Token):
  def __init__(self, text:str):
    super().__init__(text)
    mana_match = re.match(MANA_ICON_REGEX, text)
    assert mana_match
    self.icon_text = mana_match.group(1)
    self.element = util.Element(mana_match.group(2))

  def render(self,im:Image,  draw:ImageDraw.Draw, cursor_x:int, cursor_y:int):
    center = cursor_x + int(MANA_ICON_WIDTH / 2), cursor_y
    icons.draw_circle_with_text(
      draw, center, MANA_ICON_WIDTH, MANA_ICON_HEIGHT, self.icon_text,
      MANA_ICON_FONT, MANA_ICON_FONT_COLOR, self.element.get_dark_color())

  def width(self):
    return MANA_ICON_WIDTH

  @classmethod
  def is_token(cls, text:str)->bool:
    return bool(re.match(MANA_ICON_REGEX, text))


ACTION_ICON_WIDTH = int(util.PIXELS_PER_INCH * 0.075)
ACTION_ICON_COLOR = colors.BLACK

ACTION_TYPES = {
  "<HOLDING_ACTION>": util.ICON_DIR.joinpath("any_action.png"),
  "<RECRUIT_ACTION>": util.ICON_DIR.joinpath("any_action.png"),
  "<COMBAT_ACTION>": util.ICON_DIR.joinpath("any_action.png"),
  "<RANGED_ACTION>": util.ICON_DIR.joinpath("any_action.png"),
  "<ANY_ACTION>": util.ICON_DIR.joinpath("any_action.png"),
  "<BREAK_ACTION>": util.ICON_DIR.joinpath("any_action.png"),
}

for _, v in ACTION_TYPES.items():
  assert v.is_file()


# Also used for "Any"
class ActionToken(Token):
  def __init__(self, text:str):
    super().__init__(text)
    assert text in ACTION_TYPES
    self.icon_path = ACTION_TYPES[text]

  def render(self, im:Image, draw:ImageDraw.Draw, cursor_x:int, cursor_y:int):
    bb = [cursor_x, cursor_y - int(TEXT_HEIGHT / 2),
          cursor_x + ACTION_ICON_WIDTH,
          cursor_y + int(TEXT_HEIGHT/2)
          ]
    with Image.open(self.icon_path) as icon:
      icon = icon.convert("RGBA").resize((ACTION_ICON_WIDTH, TEXT_HEIGHT))
      im.paste(icon, bb, icon)

  def width(self):
    return ACTION_ICON_WIDTH

  @classmethod
  def is_token(cls, text:str)->bool:
    return text in ACTION_TYPES


class BodyTextWriter():
  def __init__(self, im: Image, draw:ImageDraw.Draw,  body_text_bb:util.BoundingBox):
    util.assert_valid_bb(body_text_bb)
    self.im = im
    self.draw = draw
    self.left, self.top, self.right, self.bottom = body_text_bb
    self.cursor_x = self.left
    self.cursor_y = self.top + int(TEXT_HEIGHT / 2)

  def render_text(self, text:str):
    for line in self._get_logical_lines(text):
      self._render_line(line)

  def _render_line(self, tokens:List[Token]):
    if isinstance(tokens[0], ActionToken):
      action = tokens[0]
      end_cost_idx = None
      for idx, t in enumerate(tokens):
        if isinstance(t, EndCost):
          end_cost_idx = idx
      # This should remove cost_end from the tokens.
      cost = [] if end_cost_idx is None else tokens[1:end_cost_idx]
      content = tokens[1:] if end_cost_idx is None else tokens[end_cost_idx+1:]
      self._render_action_line(action, cost, content)
    else:
      self._render_text_line(tokens)
    self._newline()

  def _newline(self, indent:int=0):
    self.cursor_x = self.left + indent
    self.cursor_y += TEXT_HEIGHT + TOKEN_PADDING_Y

  def _render_cost_background(self, cost:List[Token]):
    cost_width = sum(c.width() for c in cost) + TOKEN_PADDING_X * (len(cost)-1) + 2 * COST_PADDING_X
    bb = self.cursor_x, self.cursor_y - int(TEXT_HEIGHT/2), self.cursor_x + cost_width, self.cursor_y + int(TEXT_HEIGHT/2)
    self.draw.rounded_rectangle(bb, radius=int(TEXT_HEIGHT/2), fill=COST_BG_COLOR)

  def _render_action_line(self, action:ActionToken, cost:List[Token], content:List[Token]):
    action.render(self.im, self.draw, self.cursor_x, self.cursor_y)
    self.cursor_x += action.width() + TOKEN_PADDING_X
    self._render_cost_background(cost)
    self.cursor_x += COST_PADDING_X
    for c in cost:
      c.render(self.im, self.draw, self.cursor_x, self.cursor_y)
      self.cursor_x += c.width() + TOKEN_PADDING_X
    self.cursor_x += COST_PADDING_X
    for c in content:
      if self.cursor_x + c.width() > self.right:
        self._newline(action.width())
      c.render(self.im, self.draw, self.cursor_x, self.cursor_y)
      self.cursor_x += c.width() + TOKEN_PADDING_X

  def _render_text_line(self, content:List[Token]):
    for token in content:
      if self.cursor_x + token.width() > self.right:
        self._newline()
      token.render(self.im, self.draw, self.cursor_x, self.cursor_y)
      self.cursor_x += token.width() + TOKEN_PADDING_X


  def _get_token(self, text:str)->Token:
    if Newline.is_token(text):
      return Newline(text)
    if EndCost.is_token(text):
      return EndCost(text)
    if ActionToken.is_token(text):
      return ActionToken(text)
    if ManaToken.is_token(text):
      return ManaToken(text)
    if TextToken.is_token(text):
      return TextToken(text)
    return Token(text)

  def _get_logical_lines(self, text:str)->List[Token]:
    lines = []
    current_line = []
    for token in [self._get_token(t) for t in text.split()]:
      # This should remove all the newlines from the tokens.
      if isinstance(token, Newline) or isinstance(token, ActionToken):
        lines.append(current_line)
        current_line = [token] if isinstance(token, ActionToken) else []
      else:
        current_line.append(token)
    lines.append(current_line)

    # check all our lines
    return [l for l in lines if len(l) > 0]


def render_body_text(
    im: Image,
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
  text_area_left = bg_x1 + BODY_TEXT_MARGIN
  text_area_right = bg_x2 - BODY_TEXT_MARGIN
  text_area_top = bg_y1 + BODY_TEXT_MARGIN
  text_area_bottom = bg_y2 - BODY_TEXT_MARGIN

  BodyTextWriter(im, draw, [text_area_left, text_area_top, text_area_right, text_area_bottom]).render_text(text)
