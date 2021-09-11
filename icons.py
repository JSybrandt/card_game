# This  module produces icons.

from typing import *

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
import colors
import util
import math

def draw_circle_with_text(draw:ImageDraw.Draw, center:util.Coord,
                          icon_width:int, icon_height:int, text:str,
                          font:ImageFont.ImageFont, font_color:colors.Color,
                          background_color:colors.Color):
  side = min(icon_width, icon_height)
  icon_bb = util.get_centered_bb(center, side, side)
  draw.ellipse(icon_bb, fill=background_color)
  draw.text(center, text, font_color, anchor="mm", font=font)

def draw_diamond_with_text(draw:ImageDraw.Draw, center:util.Coord,
                          icon_width:int, icon_height:int, text:str,
                          font:ImageFont.ImageFont, font_color:colors.Color,
                          background_color:colors.Color):
  diamon = [
    (center[0], center[1] - int(icon_height/2)),
    (center[0] - int(icon_width/2), center[1]),
    (center[0], center[1] + int(icon_height/2)),
    (center[0] + int(icon_width/2), center[1]),
  ]
  draw.polygon(diamon, fill=background_color)
  draw.text(center, text, font_color, anchor="mm", font=font)

def draw_heart_with_text(draw:ImageDraw.Draw, center:util.Coord,
                          icon_width:int, icon_height:int, text:str,
                          font:ImageFont.ImageFont, font_color:colors.Color,
                          background_color:colors.Color):
  center_x, center_y = center
  left, top, right, bottom = util.get_centered_bb(center, icon_width, icon_height)
  lobe_radius = int((center_x - left) / 2)
  triangle_top = int(top + lobe_radius + math.cos(math.pi/4)*lobe_radius)
  triangle_left = int(center_x - lobe_radius - math.sin(math.pi/4)*lobe_radius)
  triangle_right= int(center_x + lobe_radius + math.sin(math.pi/4)*lobe_radius)
  left_lobe = [left, top, center_x, center_y]
  right_lobe = [center_x, top, right, center_y]
  bottom_triangle = [
    (triangle_left, triangle_top),
    (center_x, bottom),
    (triangle_right, triangle_top),
  ]
  middle_left, middly_top = util.get_bb_center(left_lobe)
  middle_fill = [
    (middle_left, middly_top),
    (middle_left + 2*lobe_radius, middly_top + lobe_radius)
  ]
  draw.ellipse(left_lobe, fill=background_color)
  draw.ellipse(right_lobe,  fill=background_color)
  draw.polygon(bottom_triangle, fill=background_color)
  draw.rectangle(middle_fill, fill=background_color)
  draw.text(center, text, font_color, anchor="mm", font=font)
