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
BODY_TEXT_MARGIN = 10

TEXT_HEIGHT = 20
TOKEN_PADDING_Y = 3
TOKEN_PADDING_X = 3

COST_BG_COLOR = colors.GREY_200
COST_PADDING_X = 5


UNKNOWN_TEXT = "[?]"
class Token():
  def __init__(self, text:str):
    self.text = text

  def render(self, draw:ImageDraw.Draw, cursor_x:int, cursor_y:int):
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

  def render(self, draw:ImageDraw.Draw, cursor_x:int, cursor_y:int):
    draw.text((cursor_x, cursor_y), self.text, FONT_COLOR, font=FONT,
              anchor="lm")

  def width(self):
    return FONT.getsize(self.text)[0]

  @classmethod
  def is_token(cls, text:str)->bool:
    return text[0] != "<" and text[-1] != ">"

MANA_ICON_WIDTH = MANA_ICON_HEIGHT = int(TEXT_HEIGHT * 0.9)
MANA_ICON_FONT = ImageFont.truetype(str(LATO_FONT_PATH), 16)
MANA_ICON_FONT_COLOR = colors.WHITE
MANA_ICON_REGEX = "<(.+)([FWDLNG])>"
class ManaToken(Token):
  def __init__(self, text:str):
    super().__init__(text)
    mana_match = re.match(MANA_ICON_REGEX, text)
    assert mana_match
    self.icon_text = mana_match.group(1)
    self.element = util.Element(mana_match.group(2))

  def render(self, draw:ImageDraw.Draw, cursor_x:int, cursor_y:int):
    center = cursor_x + int(MANA_ICON_WIDTH / 2), cursor_y
    icons.draw_circle_with_text(
      draw, center, MANA_ICON_WIDTH, MANA_ICON_HEIGHT, self.icon_text,
      MANA_ICON_FONT, MANA_ICON_FONT_COLOR, self.element.get_dark_color())

  def width(self):
    return MANA_ICON_WIDTH

  @classmethod
  def is_token(cls, text:str)->bool:
    return bool(re.match(MANA_ICON_REGEX, text))


ACTION_ICON_WIDTH = 15
ACTION_ICON_COLOR = colors.BLACK

# Also used for "Any"
class ActionToken(Token):
  def __init__(self, text:str):
    super().__init__(text)

  def render(self, draw:ImageDraw.Draw, cursor_x:int, cursor_y:int):
    left = cursor_x
    center_y = cursor_y
    top = center_y - int(TEXT_HEIGHT / 2)
    bottom = top + TEXT_HEIGHT
    right = left + ACTION_ICON_WIDTH
    center_x = left + int(ACTION_ICON_WIDTH / 2)
    arrow = [(left, top), (center_x, center_y), (left, bottom), (right, center_y)]
    draw.polygon(arrow, fill=ACTION_ICON_COLOR)

  def width(self):
    return ACTION_ICON_WIDTH

  @classmethod
  def is_token(cls, text:str)->bool:
    return text in {
      "<HOLDING_ACTION>",
      "<RECRUIT_ACTION>",
      "<COMBAT_ACTION>",
      "<RANGED_ACTION>",
      "<ANY_ACTION>",
      "<BREAK_ACTION>",
    }

class HoldingActionToken(ActionToken):
  def __init__(self, text:str):
    super().__init__(text)

  def render(self, draw:ImageDraw.Draw, cursor_x:int, cursor_y:int):
    left = cursor_x
    center_y = cursor_y
    top = center_y - int(TEXT_HEIGHT / 2)
    bottom = top + TEXT_HEIGHT
    right = left + ACTION_ICON_WIDTH
    center_x = left + int(ACTION_ICON_WIDTH / 2)
    house = [
      (left, bottom),
      (left, center_y),
      (center_x, top),
      (right, center_y),
      (right, bottom)
    ]
    draw.polygon(house, fill=ACTION_ICON_COLOR)

  def width(self):
    return ACTION_ICON_WIDTH

  @classmethod
  def is_token(cls, text:str)->bool:
    return text == "<HOLDING_ACTION>"

class RecruitActionToken(ActionToken):
  def __init__(self, text:str):
    super().__init__(text)

  def render(self, draw:ImageDraw.Draw, cursor_x:int, cursor_y:int):
    left = cursor_x
    center_y = cursor_y
    top = center_y - int(TEXT_HEIGHT / 2)
    bottom = top + TEXT_HEIGHT
    right = left + ACTION_ICON_WIDTH
    center_x = left + int(ACTION_ICON_WIDTH / 2)
    draw.rectangle([left, top, center_x, bottom], fill=ACTION_ICON_COLOR)
    draw.rectangle([left, center_y, right, bottom], fill=ACTION_ICON_COLOR)
    draw.ellipse([center_x, int(top+center_y)/2, right, bottom], fill=ACTION_ICON_COLOR)

  def width(self):
    return ACTION_ICON_WIDTH

  @classmethod
  def is_token(cls, text:str)->bool:
    return text == "<RECRUIT_ACTION>"

class CombatActionToken(ActionToken):
  def __init__(self, text:str):
    super().__init__(text)

  def render(self, draw:ImageDraw.Draw, cursor_x:int, cursor_y:int):
    left = cursor_x
    top = cursor_y - int(TEXT_HEIGHT / 2)
    bottom = top + TEXT_HEIGHT
    right = left + ACTION_ICON_WIDTH
    blade_left = left + int(ACTION_ICON_WIDTH*0.35)
    blade_top = top + int(TEXT_HEIGHT * 0.3)
    blade_right = left + int(ACTION_ICON_WIDTH*0.65)
    hilt_top = top + int(TEXT_HEIGHT*0.6)
    hilt_bottom = top + int(TEXT_HEIGHT*0.7)
    center_x = int((left + right) / 2)
    sword = [
      (center_x, top),
      (blade_left, blade_top),
      (blade_left, hilt_top),
      (left, hilt_top),
      (left, hilt_bottom),
      (blade_left, hilt_bottom),
      (blade_left, bottom),
      (blade_right, bottom),
      (blade_right, hilt_bottom),
      (right, hilt_bottom),
      (right, hilt_top),
      (blade_right, hilt_top),
      (blade_right, blade_top),
    ]
    draw.polygon(sword, fill=ACTION_ICON_COLOR)

  def width(self):
    return ACTION_ICON_WIDTH

  @classmethod
  def is_token(cls, text:str)->bool:
    return text == "<COMBAT_ACTION>"

class RangedActionToken(ActionToken):
  def __init__(self, text:str):
    super().__init__(text)

  def render(self, draw:ImageDraw.Draw, cursor_x:int, cursor_y:int):
    left = cursor_x
    top = cursor_y - int(TEXT_HEIGHT / 2)
    bottom = top + TEXT_HEIGHT
    right = left + ACTION_ICON_WIDTH
    arrow_top = top + int(TEXT_HEIGHT * 0.45)
    arrow_bottom = top + int(TEXT_HEIGHT * 0.55)
    bow_left = left + int(ACTION_ICON_WIDTH * 0.3)
    bow_right = left + int(ACTION_ICON_WIDTH * 0.75)
    draw.rectangle([left, arrow_top, right, arrow_bottom], fill=ACTION_ICON_COLOR)
    draw.pieslice([bow_left, top, bow_right, bottom], start=-90, end=90, fill=ACTION_ICON_COLOR)

  def width(self):
    return ACTION_ICON_WIDTH

  @classmethod
  def is_token(cls, text:str)->bool:
    return text == "<RANGED_ACTION>"

class BreakActionToken(ActionToken):
  def __init__(self, text:str):
    super().__init__(text)

  def render(self, draw:ImageDraw.Draw, cursor_x:int, cursor_y:int):
    left = cursor_x
    top = cursor_y - int(TEXT_HEIGHT / 2)
    bottom = top + TEXT_HEIGHT
    right = left + ACTION_ICON_WIDTH
    lightning = [
      (left, top),
      (right- int(ACTION_ICON_WIDTH*0.1), top + int(TEXT_HEIGHT*0.2)),
      (left + int(ACTION_ICON_WIDTH*0.2), top + int(TEXT_HEIGHT*0.4)),
      (right - int(ACTION_ICON_WIDTH*0.3), top + int(TEXT_HEIGHT*0.6)),
      (left + int(ACTION_ICON_WIDTH*0.4), top + int(TEXT_HEIGHT*0.8)),
      (right - int(ACTION_ICON_WIDTH*0.5), bottom)
    ]
    draw.line(lightning, fill=ACTION_ICON_COLOR, width=3)

  def width(self):
    return ACTION_ICON_WIDTH

  @classmethod
  def is_token(cls, text:str)->bool:
    return text == "<BREAK_ACTION>"

class BodyTextWriter():
  def __init__(self, draw:ImageDraw.Draw,  body_text_bb:util.BoundingBox):
    util.assert_valid_bb(body_text_bb)
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
    action.render(self.draw, self.cursor_x, self.cursor_y)
    self.cursor_x += action.width() + TOKEN_PADDING_X
    self._render_cost_background(cost)
    self.cursor_x += COST_PADDING_X
    for c in cost:
      c.render(self.draw, self.cursor_x, self.cursor_y)
      self.cursor_x += c.width() + TOKEN_PADDING_X
    self.cursor_x += COST_PADDING_X
    for c in content:
      if self.cursor_x + c.width() > self.right:
        self._newline(action.width())
      c.render(self.draw, self.cursor_x, self.cursor_y)
      self.cursor_x += c.width() + TOKEN_PADDING_X

  def _render_text_line(self, content:List[Token]):
    for token in content:
      if self.cursor_x + token.width() > self.right:
        self._newline()
      token.render(self.draw, self.cursor_x, self.cursor_y)
      self.cursor_x += token.width() + TOKEN_PADDING_X


  def _get_token(self, text:str)->Token:
    if Newline.is_token(text):
      return Newline(text)
    if EndCost.is_token(text):
      return EndCost(text)
    if HoldingActionToken.is_token(text):
      return HoldingActionToken(text)
    if RecruitActionToken.is_token(text):
      return RecruitActionToken(text)
    if CombatActionToken.is_token(text):
      return CombatActionToken(text)
    if RangedActionToken.is_token(text):
      return RangedActionToken(text)
    if BreakActionToken.is_token(text):
      return BreakActionToken(text)
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
      print(token, token.text)
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

  BodyTextWriter(draw, [text_area_left, text_area_top, text_area_right, text_area_bottom]).render_text(text)
