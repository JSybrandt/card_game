# This  module produces icons.

import math
from typing import Optional

from PIL import Image, ImageDraw, ImageFont

from . import colors, util

#pylint: disable=too-many-arguments
#pylint: disable=too-many-locals


def draw_cost_icon(im: Image,
                   draw: ImageDraw.Draw,
                   center: util.Coord,
                   icon_width: int,
                   icon_height: int,
                   text: str,
                   font: ImageFont.ImageFont,
                   font_color: colors.Color,
                   primary_element: util.Element,
                   secondary_element: Optional[util.Element] = None):
  side = min(icon_width, icon_height)
  icon_bb = util.get_centered_bb(center, side, side)
  draw.ellipse(icon_bb, fill=primary_element.get_dark_color())
  if secondary_element is not None:
    secondary_im = Image.new("RGBA", (side, side),
                             color=secondary_element.get_dark_color())
    secondary_mask = Image.new("L", (side, side))
    secondary_mask_draw = ImageDraw.Draw(secondary_mask)
    # Fill in the center
    secondary_mask_draw.ellipse([0, 0, side, side], fill=255)
    # Delete the top/left
    secondary_mask_draw.polygon([(0, 0), (side, 0), (0, side)], fill=0)
    secondary_im.putalpha(secondary_mask)
    im.paste(secondary_im, icon_bb, secondary_im)
  draw.text(center, text, font_color, anchor="mm", font=font)


def draw_diamond_with_text(draw: ImageDraw.Draw, center: util.Coord,
                           icon_width: int, icon_height: int, text: str,
                           font: ImageFont.ImageFont, font_color: colors.Color,
                           background_color: colors.Color=colors.BLUE_GREY_800):
  diamon = [
      (center[0], center[1] - int(icon_height / 2)),
      (center[0] - int(icon_width / 2), center[1]),
      (center[0], center[1] + int(icon_height / 2)),
      (center[0] + int(icon_width / 2), center[1]),
  ]
  draw.polygon(diamon, fill=background_color)
  draw.text(center, text, font_color, anchor="mm", font=font)


HEART_ICON_IMG = Image.open(util.ICON_DIR.joinpath("heart.png")).convert("RGBA")

def draw_heart_with_text(im: Image, draw: ImageDraw.Draw, center: util.Coord,
                         icon_width: int, icon_height: int, text: str,
                         font: ImageFont.ImageFont, font_color: colors.Color,
                         background_color: colors.Color=colors.RED_A400):
  center_x, center_y = center
  bb = util.get_centered_bb(center, icon_width, icon_height)
  heart_im = HEART_ICON_IMG.resize([icon_width, icon_height])
  im.paste(heart_im, bb, heart_im)
  draw.text(center, text, font_color, anchor="mm", font=font)
