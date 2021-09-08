from typing import *
import random
import dataclasses
import colorsys
import math
import util 
import colors
from PIL import Image
from PIL import ImageDraw

# We want to generate between 3 sided and 10-sided shapes.
RAND_MIN_POINT_GEN_STEP_RADS = 2 * math.pi / 20
RAND_MAX_POINT_GEN_STEP_RADS = 2 * math.pi / 3
RAND_MIN_SHAPES = 10
RAND_MAX_SHAPES = 100

@dataclasses.dataclass
class ColorPalette:
  # These are in 0-1
  primary_hue: float
  secondary_hue: float
  alt_hues: List[float]

  def primary(self)->Tuple[int, int, int]:
    return tuple(
      int(255*c) for c in colorsys.hsv_to_rgb(self.primary_hue, 1, 1))

  def secondary(self)->Tuple[int, int, int]:
    return tuple(
      int(255*c) for c in colorsys.hsv_to_rgb(self.secondary_hue, 1, 1))


def rand_shape(x_offset: float, y_offset: float, min_radius:float, max_radius:float)->List[int]:
  """Returns the points of a shape in clockwise order centered at offset."""
  points = []
  angle_offset = random.random() * 2 * math.pi
  angle = 0
  while angle < 2*math.pi:
    magnitude = random.uniform(min_radius, max_radius)
    x = math.cos(angle + angle_offset) * magnitude + x_offset
    y = math.sin(angle + angle_offset) * magnitude + y_offset
    points.append((x, y))
    angle += random.uniform(RAND_MIN_POINT_GEN_STEP_RADS,
                            RAND_MAX_POINT_GEN_STEP_RADS)
  return points



def rand_color_palette()->ColorPalette:
  primary_hue = random.random()
  secondary_hue = (primary_hue + 0.5 + random.uniform(-0.2, 0.2)) % 1
  alt_hues = [
    ((primary_hue - secondary_hue)/2) % 1,
    ((secondary_hue - primary_hue)/2) % 1,
    random.random(), random.random(), random.random(),
  ]
  return ColorPalette(primary_hue, secondary_hue, alt_hues)

def rand_color(palette:ColorPalette)->Tuple[int, int, int]:
  hue = random.choices(
    [palette.primary_hue, palette.secondary_hue] + palette.alt_hues,
    weights=[0.5, 0.25] + [0.25/len(palette.alt_hues) for _ in palette.alt_hues]
  )[0]
  saturation = random.uniform(0.5, 1)
  value = random.uniform(0, 1)
  return tuple(int(255*c) for c in colorsys.hsv_to_rgb(hue, saturation, value))


def generate_card_art(desc:util.CardDesc, width:float, height:float)->Image:
  # Seed random number gen with deterministic hash of card description. This
  # gives us the same image if we run the generation script twice.
  random.seed(desc.hash())

  # We generate an internal image and paste it into the card.
  img = Image.new(mode="RGBA", size=(width, height))
  draw = ImageDraw.Draw(img)

  draw.rectangle([0, 0, width, height],
                 fill=colors.BLACK)

  num_shapes = random.randint(RAND_MIN_SHAPES, RAND_MAX_SHAPES)
  color_palette = rand_color_palette()
  for shape_idx in range(num_shapes):
    offset_x = random.uniform(0, width)
    offset_y = random.uniform(0, height)
    shape = rand_shape(offset_x, offset_y, min_radius=min(width,height)*0.1,
                       max_radius=min(width,height)*0.3)
    draw.polygon(shape, fill=rand_color(color_palette))
  # Big secondary shape.
  offset_x = random.uniform(width*0.1, width*0.9)
  offset_y = random.uniform(height*0.1, height*0.9)
  shape = rand_shape(offset_x, offset_y, min_radius=min(width,height)*0.3,
                     max_radius=min(width,height)*0.9)
  draw.polygon(shape, fill=color_palette.secondary())
  # Big primary shape.
  offset_x = random.uniform(width*0.1, width*0.9)
  offset_y = random.uniform(height*0.1, height*0.9)
  shape = rand_shape(offset_x, offset_y, min_radius=min(width,height)*0.3,
                     max_radius=min(width,height)*0.9)
  draw.polygon(shape, fill=color_palette.primary())

  return img
