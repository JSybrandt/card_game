# This  module produces icons.

from typing import *

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
import colors
import util

def draw_circle_with_text(draw:ImageDraw.Draw, center:util.Coord,
                          icon_width:int, icon_height:int, text:str,
                          font:ImageFont.ImageFont, font_color:colors.Color,
                          background_color:colors.Color):
  side = min(icon_width, icon_height)
  icon_bb = util.get_centered_bb(center, side, side)
  draw.ellipse(icon_bb, fill=background_color)
  draw.text(center, text, font_color, anchor="mm", font=font)

