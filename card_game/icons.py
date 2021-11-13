# This  module produces icons.

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
  draw.ellipse(icon_bb, fill=primary_element.get_color())
  if secondary_element is not None:
    secondary_im = Image.new("RGBA", (side, side),
                             color=secondary_element.get_color())
    secondary_mask = Image.new("L", (side, side))
    secondary_mask_draw = ImageDraw.Draw(secondary_mask)
    # Fill in the center
    secondary_mask_draw.ellipse([0, 0, side, side], fill=255)
    # Delete the top/left
    secondary_mask_draw.polygon([(0, 0), (side, 0), (0, side)], fill=0)
    secondary_im.putalpha(secondary_mask)
    im.paste(secondary_im, icon_bb, secondary_im)
  draw.text(center, text, font_color, anchor="mm", font=font)


STRENGTH_ICON_IMG = Image.open(
    util.ICON_DIR.joinpath("strength.png")).convert("RGBA")


def draw_strength_with_text(im: Image, draw: ImageDraw.Draw, center: util.Coord,
                            icon_width: int, icon_height: int, text: str,
                            font: ImageFont.ImageFont,
                            font_color: colors.Color):
  bb = util.get_centered_bb(center, icon_width, icon_height)
  icon_img = STRENGTH_ICON_IMG.resize([icon_width, icon_height])
  im.paste(icon_img, bb, icon_img)
  draw.text(center, text, font_color, anchor="mm", font=font)


TARGET_ICON_IMG = Image.open(
    util.ICON_DIR.joinpath("target.png")).convert("RGBA")


def draw_target_with_text(im: Image, draw: ImageDraw.Draw, center: util.Coord,
                          icon_width: int, icon_height: int, text: str,
                          font: ImageFont.ImageFont, font_color: colors.Color):
  bb = util.get_centered_bb(center, icon_width, icon_height)
  icon_img = TARGET_ICON_IMG.resize([icon_width, icon_height])
  im.paste(icon_img, bb, icon_img)
  draw.text(center, text, font_color, anchor="mm", font=font)


HEART_ICON_IMG = Image.open(util.ICON_DIR.joinpath("heart.png")).convert("RGBA")


def draw_heart_with_text(im: Image, draw: ImageDraw.Draw, center: util.Coord,
                         icon_width: int, icon_height: int, text: str,
                         font: ImageFont.ImageFont, font_color: colors.Color):
  bb = util.get_centered_bb(center, icon_width, icon_height)
  icon_img = HEART_ICON_IMG.resize([icon_width, icon_height])
  im.paste(icon_img, bb, icon_img)
  draw.text(center, text, font_color, anchor="mm", font=font)
