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

  def sample_hue(self)->float:
    hues = [self.primary_hue, self.secondary_hue] + self.alt_hues
    weights = [0.5, 0.25]
    weights += [0.25/len(self.alt_hues) for _ in self.alt_hues]
    return random.choices(hues, weights=weights)[0]


def rand_shape(
  x_offset: float,
  y_offset: float,
  min_radius:float,
  max_radius:float,
)->List[int]:
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

def get_nearby_hue(color:colors.Color)->float:
  hue, _, _ = colorsys.rgb_to_hsv(*color)
  hue += random.uniform(-0.1, 0.1)
  hue %= 1
  return hue


def rand_color_palette(element:util.Element)->ColorPalette:
  primary_hue = (random.uniform(0, 1) if element == util.Element.GENERIC else
                 get_nearby_hue(element.get_primary_color()))
  primary_hue = (primary_hue + random.uniform(-0.1, 0.1)) % 1
  secondary_hue = (primary_hue + 0.5 + random.uniform(-0.4, 0.4)) % 1
  alt_hues = [
    ((primary_hue - secondary_hue)/2) % 1,
    ((secondary_hue - primary_hue)/2) % 1,
    get_nearby_hue(element.get_light_color()),
    get_nearby_hue(element.get_dark_color()),
    random.random(), random.random(),
  ]
  return ColorPalette(primary_hue, secondary_hue, alt_hues)

def rand_color(
  hue: float,
  min_saturation=0.5,
  max_saturation=1,
  min_value=0,
  max_value=1,
)->Tuple[int, int, int]:
  saturation = random.uniform(min_saturation, max_saturation)
  value = random.uniform(min_value, max_value)
  return tuple(int(255*c) for c in colorsys.hsv_to_rgb(hue, saturation, value))


def generate_card_art(desc:util.CardDesc, width:float, height:float)->Image:
  # Seed random number gen with deterministic hash of card description. This
  # gives us the same image if we run the generation script twice.
  random.seed(desc.hash())

  # We generate an internal image and paste it into the card.
  img = Image.new(mode="RGBA", size=(width, height))
  draw = ImageDraw.Draw(img)

  draw.rectangle([0, 0, width, height], fill=colors.BLACK)

  num_shapes = random.randint(RAND_MIN_SHAPES, RAND_MAX_SHAPES)
  color_palette = rand_color_palette(desc.element)
  for shape_idx in range(num_shapes):
    offset_x = random.uniform(0, width)
    offset_y = random.uniform(0, height)
    shape = rand_shape(offset_x, offset_y, min_radius=min(width,height)*0.1,
                       max_radius=min(width,height)*0.3)
    draw.polygon(shape, fill=rand_color(color_palette.sample_hue()))

  # These values make the primary and secondary shapes "pop"
  x_min_offset = width * 0.1
  x_max_offset = width * 0.9
  y_min_offset = height * 0.1
  y_max_offset = height * 0.9
  min_saturation = 0.1 if desc.element == util.Element.GENERIC else 0.6
  max_saturation = 0.5 if desc.element == util.Element.GENERIC else 1
  min_value = 0.6
  max_value = 1
  min_radius = min(width, height) * 0.3
  max_radius = min(width, height) * 0.6

  # Big secondary shape.
  draw.polygon(
      rand_shape(random.uniform(x_min_offset, x_max_offset),
                 random.uniform(y_min_offset, y_max_offset),
                 min_radius, max_radius),
      fill=rand_color(color_palette.secondary_hue, min_saturation,
                      max_saturation, min_value, max_value))

  draw.polygon(
      rand_shape(random.uniform(x_min_offset, x_max_offset),
                 random.uniform(y_min_offset, y_max_offset),
                 min_radius, max_radius),
      fill=rand_color(color_palette.primary_hue, min_saturation,
                      max_saturation, min_value, max_value))

  return img