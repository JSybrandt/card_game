import enum
import pathlib
import re
from typing import List

from PIL import Image, ImageDraw, ImageFont

from . import colors, icons, util

#pylint: disable=too-few-public-methods
#pylint: disable=too-many-instance-attributes
#pylint: disable=too-many-locals

# Customizations of the body text area.

FONT_COLOR = colors.BLACK
BG_RADIUS = int(util.PIXELS_PER_INCH * 0.05)
BG_COLOR = colors.GREY_50
BODY_TEXT_MARGIN = int(util.PIXELS_PER_INCH * 0.05)
FLAVOR_TEXT_MARGIN = int(util.PIXELS_PER_INCH * 0.42)

TEXT_HEIGHT = int(util.PIXELS_PER_INCH * 0.14)
FONT = ImageFont.truetype(str(util.EB_GARAMOND_FONT_PATH), TEXT_HEIGHT)
FLAVOR_TEXT_HEIGHT = int(util.PIXELS_PER_INCH * 0.12)
FLAVOR_TEXT_FONT = ImageFont.truetype(str(util.GARAMOND_ITALIC_FONT_PATH),
                                      FLAVOR_TEXT_HEIGHT)
TOKEN_PADDING_Y = int(util.PIXELS_PER_INCH * 0.02)
TOKEN_PADDING_X = int(util.PIXELS_PER_INCH * 0.02)

COST_BG_COLOR = colors.AMBER_400
COST_PADDING_X = int(util.PIXELS_PER_INCH * 0.05)

TEXT_SEGMENT_PADDING_Y = int(0.03 * util.PIXELS_PER_INCH)
TEXT_SEGMENT_BORDER_COLOR = colors.BLACK
TEXT_SEGMENT_BORDER_WIDTH = int(0.01 * util.PIXELS_PER_INCH)
TEXT_SEGMENT_FONT = ImageFont.truetype(str(util.EB_GARAMOND_FONT_PATH),
                                       TEXT_HEIGHT // 2)
TEXT_SEGMENT_FONT_COLOR = colors.BLACK
TEXT_SEGMENT_FONT_PADDING_Y = int(1.2 * TEXT_SEGMENT_FONT.size)

UNKNOWN_TEXT = "[?]"


class Token():

  def __init__(self, desc: util.CardDesc, text: str, font: ImageFont.ImageFont):
    self.text = text
    self.desc = desc
    self.font = font

  def render(self, _: Image, draw: ImageDraw.Draw, cursor_x: int,
             cursor_y: int):
    """Renders the token.

    Assume that cursor_x is the left-hand side, while cursor_y is the
    middle-line. Assume that you are allowed to render at most TEXT_HEIGHT tall
    (centered at cursor_y), and self.width() wide. You can also assume that the
    cursor location has been placed such that this rendering will stay within
    the border of the card.
    """
    print(f"Warning, unidentified token: {self.text}")
    draw.text((cursor_x, cursor_y),
              UNKNOWN_TEXT,
              FONT_COLOR,
              font=self.font,
              anchor="lm")

  def width(self):
    #pylint: disable=no-self-use
    return self.font.getsize(UNKNOWN_TEXT)[0]

  @classmethod
  def is_token(cls, text: str) -> bool:
    #pylint: disable=unused-argument
    return True


class Newline(Token):

  @classmethod
  def is_token(cls, text: str) -> bool:
    return text == "<NEWLINE>"


class StartTetherSegmentToken(Token):

  @classmethod
  def is_token(cls, text: str) -> bool:
    return text == "<TETHER>"


class EndTetherSegmentToken(Token):

  @classmethod
  def is_token(cls, text: str) -> bool:
    return text == "</TETHER>"


class TextToken(Token):

  def render(self, _: Image, draw: ImageDraw.Draw, cursor_x: int,
             cursor_y: int):
    #pylint: disable=unused-argument
    draw.text((cursor_x, cursor_y),
              self.text,
              FONT_COLOR,
              font=self.font,
              anchor="lm")

  def width(self):
    return self.font.getsize(self.text)[0]

  @classmethod
  def is_token(cls, text: str) -> bool:
    return text[0] != "<" or text[-1] != ">"


class SpaceToken(TextToken):

  def __init__(self, desc: util.CardDesc, *args, **kwargs):
    super().__init__(desc, *args, **kwargs)

  @classmethod
  def is_token(cls, text: str) -> bool:
    return text in [" ", ""]


ICON_WIDTH = TEXT_HEIGHT
ICON_HEIGHT = ICON_WIDTH
ICON_FONT = ImageFont.truetype(str(util.LATO_FONT_PATH), int(TEXT_HEIGHT * 0.8))
ICON_FONT_COLOR = colors.WHITE

MANA_ICON_REGEX = "<([0-9X]+)([FWDLNG])>"


class ManaToken(Token):

  def __init__(
      self,
      desc: util.CardDesc,
      text: str,
      *args,
      **kwargs,
  ):
    super().__init__(desc, text, *args, **kwargs)
    mana_match = re.match(MANA_ICON_REGEX, text)
    assert mana_match
    self.icon_text = mana_match.group(1)
    self.element = util.Element(mana_match.group(2))

  def render(self, im: Image, draw: ImageDraw.Draw, cursor_x: int,
             cursor_y: int):
    center = cursor_x + int(ICON_WIDTH / 2), cursor_y
    icons.draw_cost_icon(im, draw, center, ICON_WIDTH, ICON_HEIGHT,
                         self.icon_text, ICON_FONT, ICON_FONT_COLOR,
                         self.element)

  def width(self):
    return ICON_WIDTH

  @classmethod
  def is_token(cls, text: str) -> bool:
    return bool(re.match(MANA_ICON_REGEX, text))


HEALTH_ICON_REGEX = "<([0-9X]+)_HEALTH>"


class HealthToken(Token):

  def __init__(self, desc: util.CardDesc, text: str, *args, **kwargs):
    super().__init__(desc, text, *args, **kwargs)
    mana_match = re.match(HEALTH_ICON_REGEX, text)
    assert mana_match
    self.icon_text = mana_match.group(1)

  def render(self, im: Image, draw: ImageDraw.Draw, cursor_x: int,
             cursor_y: int):
    center = cursor_x + int(ICON_WIDTH / 2), cursor_y
    icons.draw_heart_with_text(im, draw, center, ICON_WIDTH, ICON_HEIGHT,
                               self.icon_text, ICON_FONT, ICON_FONT_COLOR)

  def width(self):
    return ICON_WIDTH

  @classmethod
  def is_token(cls, text: str) -> bool:
    return bool(re.match(HEALTH_ICON_REGEX, text))


STRENGTH_REGEX = "<([0-9X]+)_STRENGTH>"


class StrengthToken(Token):

  def __init__(self, desc: util.CardDesc, text: str, *args, **kwargs):
    super().__init__(desc, text, *args, **kwargs)
    mana_match = re.match(STRENGTH_REGEX, text)
    assert mana_match
    self.icon_text = mana_match.group(1)

  def render(self, im: Image, draw: ImageDraw.Draw, cursor_x: int,
             cursor_y: int):
    center = cursor_x + int(ICON_WIDTH / 2), cursor_y
    icons.draw_strength_with_text(im, draw, center, ICON_WIDTH, ICON_HEIGHT,
                                  self.icon_text, ICON_FONT, ICON_FONT_COLOR)

  def width(self):
    return ICON_WIDTH

  @classmethod
  def is_token(cls, text: str) -> bool:
    return bool(re.match(STRENGTH_REGEX, text))


DAMAGE_ICON_REGEX = "<([0-9X]+)_DAMAGE>"
DAMAGE_ICON_COLOR = colors.RED_A400
DAMAGE_ICON_FONT_COLOR = colors.WHITE
DAMAGE_ICON_FONT = ImageFont.truetype(str(util.LATO_FONT_PATH),
                                      int(TEXT_HEIGHT * 0.8))


class DamageToken(Token):

  def __init__(self, desc: util.CardDesc, text: str, *args, **kwargs):
    super().__init__(desc, text, *args, **kwargs)
    damage_match = re.match(DAMAGE_ICON_REGEX, text)
    assert damage_match
    self.icon_text = damage_match.group(1)

  def render(self, im: Image, draw: ImageDraw.Draw, cursor_x: int,
             cursor_y: int):
    center = cursor_x + int(ICON_WIDTH / 2), cursor_y
    icons.draw_target_with_text(im, draw, center, ICON_WIDTH, ICON_HEIGHT,
                                self.icon_text, ICON_FONT, ICON_FONT_COLOR)

  def width(self):
    return ICON_WIDTH

  @classmethod
  def is_token(cls, text: str) -> bool:
    return bool(re.match(DAMAGE_ICON_REGEX, text))


def _load_image(img_path: pathlib.Path) -> Image:
  assert img_path.is_file(), str(img_path)
  return Image.open(img_path).convert("RGBA").resize((ICON_WIDTH, TEXT_HEIGHT))


ICONS = {
    "<END_COST>": _load_image(util.ICON_DIR.joinpath("end_cost.png")),
    "<EXHAUST>": _load_image(util.ICON_DIR.joinpath("exhaust.png")),
    "<READY>": _load_image(util.ICON_DIR.joinpath("ready.png")),
    "<DRAW_CARD>": _load_image(util.ICON_DIR.joinpath("draw_card.png")),
    "<SACRIFICE>": _load_image(util.ICON_DIR.joinpath("sacrifice.png")),
    "<MEMORY_ACTION>": _load_image(util.ICON_DIR.joinpath("memory_action.png")),
    "<SUMMON_ACTION>": _load_image(util.ICON_DIR.joinpath("summon_action.png")),
    "<COMBAT_ACTION>": _load_image(util.ICON_DIR.joinpath("combat_action.png")),
    "<RANGED_ACTION>": _load_image(util.ICON_DIR.joinpath("ranged_action.png")),
    "<ANY_ACTION>": _load_image(util.ICON_DIR.joinpath("any_action.png")),
    "<BREAK_ACTION>": _load_image(util.ICON_DIR.joinpath("break_action.png")),
    "<REVEAL_ACTION>": _load_image(util.ICON_DIR.joinpath("reveal.png")),
}


class IconToken(Token):

  def __init__(self, desc: util.CardDesc, text: str, *args, **kwargs):
    super().__init__(desc, text, *args, **kwargs)
    assert text in ICONS

  def render(self, im: Image, draw: ImageDraw.Draw, cursor_x: int,
             cursor_y: int):
    bb = [
        cursor_x, cursor_y - TEXT_HEIGHT // 2, cursor_x + ICON_WIDTH,
        cursor_y + TEXT_HEIGHT // 2
    ]
    im.paste(ICONS[self.text], bb, ICONS[self.text])

  def width(self):
    return ICON_WIDTH

  @classmethod
  def is_token(cls, text: str) -> bool:
    return text in ICONS


class EndCostToken(IconToken):

  def width(self):
    return ICON_WIDTH // 2

  @classmethod
  def is_token(cls, text: str) -> bool:
    return text == "<END_COST>"


class ActionToken(IconToken):

  @classmethod
  def is_token(cls, text: str) -> bool:
    return text in ICONS and re.match("<[A-Z]+_ACTION>", text)


def _get_token(desc: util.CardDesc, text: str,
               font: ImageFont.ImageFont) -> Token:
  for token_class in [
      SpaceToken, Newline, EndCostToken, ActionToken, IconToken, ManaToken,
      DamageToken, HealthToken, StrengthToken, TextToken,
      StartTetherSegmentToken, EndTetherSegmentToken, Token
  ]:
    if token_class.is_token(text):
      return token_class(desc, text, font)
  return Token(desc, text, font)


class TextSegmentType(enum.Enum):
  MAIN = "Main"
  TETHER = "Tether"


class TextSegment():

  def __init__(self, segment_type: TextSegmentType = TextSegmentType.MAIN):
    self.segment_type = segment_type
    self.tokens = []


def _get_logical_segments(tokens: List[Token]) -> List[TextSegment]:
  segments = []
  current_segment = TextSegment()
  for token in tokens:
    if isinstance(token, StartTetherSegmentToken):
      assert current_segment.segment_type == TextSegmentType.MAIN, \
        "Nested segments are not supported."
      segments.append(current_segment)
      current_segment = TextSegment(TextSegmentType.TETHER)
    elif isinstance(token, EndTetherSegmentToken):
      assert current_segment.segment_type == TextSegmentType.TETHER, \
        "EndTetherSegmentToken must occur after StartTetherSegmentToken"
      segments.append(current_segment)
      current_segment = TextSegment(TextSegmentType.MAIN)
    else:
      # This isn't a segment token.
      current_segment.tokens.append(token)
  segments.append(current_segment)
  return segments


def _strip_tokens(tokens: List[Token]) -> List[Token]:
  t = tokens[:]
  while len(t) > 0 and isinstance(t[0], SpaceToken):
    t.pop(0)
  while len(t) > 0 and isinstance(t[-1], SpaceToken):
    t.pop(-1)
  return t


def _get_logical_lines(text_segment: TextSegment) -> List[Token]:
  lines = []
  current_line = []
  for token in text_segment.tokens:
    # This should remove all the newlines from the tokens.
    if isinstance(token, (Newline, ActionToken)):
      lines.append(current_line)
      current_line = [token] if isinstance(token, ActionToken) else []
    else:
      current_line.append(token)
  lines.append(current_line)
  # check all our lines
  lines = [_strip_tokens(l) for l in lines]
  lines = [l for l in lines if len(l) > 0]
  return lines


def _parse_text(desc: util.CardDesc, text: str,
                font: ImageFont.ImageFont) -> List[Token]:
  text = text.replace("<THIS>", desc.title)
  text = text.strip()
  text = re.sub(r"\s+", " ", text)
  token_texts = [""]
  for c in text:
    if c in " <":
      token_texts.append("")
    token_texts[-1] += c
    if c in " >":
      token_texts.append("")
  return [_get_token(desc, t, font) for t in token_texts]


class BodyTextWriter():

  def __init__(self, im: Image, draw: ImageDraw.Draw,
               body_text_bb: util.BoundingBox, font: ImageFont.ImageFont):
    util.assert_valid_bb(body_text_bb)
    self.im = im
    self.draw = draw
    self.left, self.top, self.right, self.bottom = body_text_bb
    self.cursor_x = self.left
    self.cursor_y = self.top + int(TEXT_HEIGHT / 2)
    self.font = font

  def render_text(self, desc: util.CardDesc, text: str):
    for segment in _get_logical_segments(_parse_text(desc, text, self.font)):
      self._render_segment(segment)

  def _render_segment(self, text_segment: TextSegment):
    lines = _get_logical_lines(text_segment)
    if text_segment.segment_type == TextSegmentType.MAIN:
      # Just print the contents and move on.
      for line in lines:
        self._render_line(line)
    else:
      # Add some vertical space for the segment header text.
      self.cursor_y += TEXT_SEGMENT_FONT_PADDING_Y
      # Measure how much vertical space this segment is going to take.
      init_y_pos = self.cursor_y
      segment_bb_top = self.cursor_y - TEXT_HEIGHT // 2
      self.cursor_y += TEXT_SEGMENT_PADDING_Y
      for line in lines:
        self._render_line(line, dry_run=True)
      segment_bb_bottom = (self.cursor_y - TEXT_HEIGHT // 2 +
                           TEXT_SEGMENT_PADDING_Y)

      # Draw the segment header text
      self.draw.text((self.right, segment_bb_top),
                     text_segment.segment_type.value,
                     TEXT_SEGMENT_FONT_COLOR,
                     font=TEXT_SEGMENT_FONT,
                     anchor="rb")
      text_width, _ = TEXT_SEGMENT_FONT.getsize(text_segment.segment_type.value)
      # Draw the "tabbed box" around the segment
      poly = [
          (self.left - BODY_TEXT_MARGIN, segment_bb_top),
          (self.right - text_width - BODY_TEXT_MARGIN, segment_bb_top),
          (self.right - text_width - BODY_TEXT_MARGIN,
           segment_bb_top - TEXT_SEGMENT_FONT_PADDING_Y),
          (self.right + BODY_TEXT_MARGIN,
           segment_bb_top - TEXT_SEGMENT_FONT_PADDING_Y),
          (self.right + BODY_TEXT_MARGIN, segment_bb_bottom),
          (self.left - BODY_TEXT_MARGIN, segment_bb_bottom),
          (self.left - BODY_TEXT_MARGIN, segment_bb_top),
      ]
      self.draw.line(poly,
                     fill=TEXT_SEGMENT_BORDER_COLOR,
                     width=TEXT_SEGMENT_BORDER_WIDTH)

      # Now, reset the cursor position at the top of the box.
      self.cursor_y = init_y_pos + TEXT_SEGMENT_PADDING_Y
      for line in lines:
        self._render_line(line)
      # Now, place the cursor position at the end of the box.
      self.cursor_y = (segment_bb_bottom + TEXT_SEGMENT_PADDING_Y +
                       TEXT_HEIGHT // 2)

  def _render_line(self, tokens: List[Token], dry_run: bool = False):
    if isinstance(tokens[0], ActionToken):
      action = tokens[0]
      end_cost_idx = None
      for idx, t in enumerate(tokens):
        if isinstance(t, EndCostToken):
          end_cost_idx = idx
      # This should remove cost_end from the tokens.
      cost = [] if end_cost_idx is None else tokens[1:end_cost_idx + 1]
      cost = [c for c in cost if not isinstance(c, SpaceToken)]
      content = (tokens[1:] if end_cost_idx is None else tokens[end_cost_idx +
                                                                1:])
      content = _strip_tokens(content)
      self._render_action_line(action, cost, content, dry_run)
    else:
      self._render_text_line(tokens, dry_run)
    self._newline()

  def _newline(self, indent: int = 0):
    self.cursor_x = self.left + indent
    self.cursor_y += self.font.size + TOKEN_PADDING_Y

  def _render_cost_background(self, cost: List[Token]):
    assert isinstance(cost[-1], EndCostToken)
    cost_width = sum(
        c.width() for c in cost[:-1]) + COST_PADDING_X + ICON_WIDTH / 2
    bb = [
        self.cursor_x, self.cursor_y - TEXT_HEIGHT // 2 - 1,
        self.cursor_x + cost_width, self.cursor_y + TEXT_HEIGHT // 2
    ]
    self.draw.rounded_rectangle(bb, radius=TEXT_HEIGHT // 2, fill=COST_BG_COLOR)

  def _render_action_line(self,
                          action: ActionToken,
                          cost: List[Token],
                          content: List[Token],
                          dry_run: bool = False):
    if not dry_run:
      action.render(self.im, self.draw, self.cursor_x, self.cursor_y)
    self.cursor_x += action.width() + TOKEN_PADDING_X
    if len(cost) > 0:
      if not dry_run:
        self._render_cost_background(cost)
      self.cursor_x += COST_PADDING_X
      for c in cost:
        if not dry_run:
          c.render(self.im, self.draw, self.cursor_x, self.cursor_y)
        self.cursor_x += c.width()
      self.cursor_x += COST_PADDING_X
    self.cursor_x += TOKEN_PADDING_X
    for token in content:
      if self.cursor_x + token.width() > self.right:
        self._newline(action.width())
        if isinstance(token, SpaceToken):
          # Don't render a space if we've just started a new line.
          continue
      if not dry_run:
        token.render(self.im, self.draw, self.cursor_x, self.cursor_y)
      self.cursor_x += token.width()

  def _render_text_line(self, content: List[Token], dry_run: bool = False):
    for token in content:
      if self.cursor_x + token.width() > self.right:
        self._newline()

        if isinstance(token, SpaceToken):
          # Don't render a space if we've just started a new line.
          continue
      if not dry_run:
        token.render(self.im, self.draw, self.cursor_x, self.cursor_y)
      self.cursor_x += token.width()


def render_body_text(im: Image, draw: ImageDraw.Draw, desc: util.CardDesc,
                     body_text_bb: util.BoundingBox):
  util.assert_valid_bb(body_text_bb)
  if desc.card_type == util.CardType.MEMORY:
    draw.rectangle(body_text_bb, fill=BG_COLOR)
  else:
    draw.rounded_rectangle(body_text_bb, radius=BG_RADIUS, fill=BG_COLOR)
  bg_x1, bg_y1, bg_x2, bg_y2 = body_text_bb
  text_area_left = bg_x1 + BODY_TEXT_MARGIN
  text_area_right = bg_x2 - BODY_TEXT_MARGIN
  text_area_top = bg_y1 + BODY_TEXT_MARGIN
  text_area_bottom = bg_y2 - BODY_TEXT_MARGIN
  flavor_text_top = 0.4 * text_area_top + 0.6 * text_area_bottom
  flavor_text_left = text_area_left + FLAVOR_TEXT_MARGIN
  flavor_text_right = text_area_right - FLAVOR_TEXT_MARGIN

  if desc.body_text is not None:
    writer = BodyTextWriter(
        im, draw,
        [text_area_left, text_area_top, text_area_right, text_area_bottom],
        FONT)
    writer.render_text(desc, desc.body_text)
    flavor_text_top = max(writer.cursor_y, flavor_text_top)

  if desc.flavor_text is not None:
    writer = BodyTextWriter(im, draw, [
        flavor_text_left, flavor_text_top, flavor_text_right, text_area_bottom
    ], FLAVOR_TEXT_FONT)
    writer.render_text(desc, desc.flavor_text)
