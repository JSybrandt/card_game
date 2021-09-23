import colorsys
import dataclasses
import math
import random
from typing import List, Tuple

from PIL import Image, ImageDraw

from . import colors, util

#pylint: disable=too-many-locals

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

  def sample_hue(self) -> float:
    hues = [self.primary_hue, self.secondary_hue] + self.alt_hues
    weights = [0.5, 0.25]
    weights += [0.25 / len(self.alt_hues) for _ in self.alt_hues]
    return random.choices(hues, weights=weights)[0]


def rand_shape(
    x_offset: float,
    y_offset: float,
    min_radius: float,
    max_radius: float,
) -> List[int]:
  """Returns the points of a shape in clockwise order centered at offset."""
  points = []
  angle_offset = random.random() * 2 * math.pi
  angle = 0
  while angle < 2 * math.pi:
    magnitude = random.uniform(min_radius, max_radius)
    x = math.cos(angle + angle_offset) * magnitude + x_offset
    y = math.sin(angle + angle_offset) * magnitude + y_offset
    points.append((x, y))
    angle += random.uniform(RAND_MIN_POINT_GEN_STEP_RADS,
                            RAND_MAX_POINT_GEN_STEP_RADS)
  return points


def get_nearby_hue(hue: float, closeness: float = 0.05) -> float:
  hue += random.uniform(-closeness, closeness)
  hue %= 1
  return hue


def get_nearby_complimentary_hue(hue: float) -> float:
  return get_nearby_hue((hue + 0.5) % 1, closeness=0.4)


def get_nearby_hue_from_color(color: colors.Color) -> float:
  hue, _, _ = colorsys.rgb_to_hsv(*color)
  return get_nearby_hue(hue)


def get_nearby_hue_from_element(element: util.Element) -> float:
  if element == util.Element.GENERIC:
    return random.uniform(0, 1)
  return get_nearby_hue_from_color(element.get_primary_color())


def rand_color_palette(desc: util.CardDesc) -> ColorPalette:
  primary_hue = get_nearby_hue_from_element(desc.primary_element)
  secondary_hue = (get_nearby_complimentary_hue(primary_hue)
                   if desc.secondary_element is None else
                   get_nearby_hue_from_element(desc.secondary_element))
  alts = [((primary_hue - secondary_hue) / 2) % 1,
          ((secondary_hue - primary_hue) / 2) % 1,
          get_nearby_hue(primary_hue, 0.2),
          get_nearby_hue(secondary_hue, 0.2),
          random.random()]
  return ColorPalette(primary_hue, secondary_hue, alts)


def rand_color(
    hue: float,
    min_saturation=0.5,
    max_saturation=1,
    min_value=0,
    max_value=1,
) -> Tuple[int, int, int]:
  saturation = random.uniform(min_saturation, max_saturation)
  value = random.uniform(min_value, max_value)
  return tuple(
      int(255 * c) for c in colorsys.hsv_to_rgb(hue, saturation, value))


def _get_random_coords(low: int, high: int, avg_step: int,
                       variance: float) -> List[int]:
  step_low = avg_step - int(avg_step * variance)
  step_high = avg_step + int(avg_step * variance)
  cords = []
  x = low
  while x < high:
    cords.append(x)
    x += int(random.uniform(step_low, step_high))
  cords.append(high)
  return cords


def _crop_corners(im: Image, radius: int):
  mask = Image.new("L", (im.width, im.height))
  mask_draw = ImageDraw.Draw(mask)
  mask_draw.rounded_rectangle([0, 0, im.width, im.height],
                              fill=255,
                              radius=radius)
  im.putalpha(mask)


def render_card_art(im: Image, desc: util.CardDesc, image_bb: util.BoundingBox,
                    radius: float) -> Image:
  # Seed random number gen with deterministic hash of card description. This
  # gives us the same image if we run the generation script twice.
  random.seed(desc.hash())
  left, top, right, bottom = image_bb
  width = right - left
  height = bottom - top
  # We generate an internal image and paste it into the card.
  art_image = Image.new(mode="RGBA", size=(width, height))
  art_draw = ImageDraw.Draw(art_image)
  art_draw.rectangle([0, 0, width, height], fill=colors.BLACK)
  num_shapes = random.randint(RAND_MIN_SHAPES, RAND_MAX_SHAPES)
  color_palette = rand_color_palette(desc)
  for _ in range(num_shapes):
    offset_x = random.uniform(0, width)
    offset_y = random.uniform(0, height)
    shape = rand_shape(offset_x,
                       offset_y,
                       min_radius=min(width, height) * 0.1,
                       max_radius=min(width, height) * 0.3)
    art_draw.polygon(shape, fill=rand_color(color_palette.sample_hue()))
  # These values make the primary and secondary shapes "pop"
  x_min_offset = width * 0.1
  x_max_offset = width * 0.9
  y_min_offset = height * 0.1
  y_max_offset = height * 0.9
  min_saturation = 0.1 if desc.primary_element == util.Element.GENERIC else 0.6
  max_saturation = 0.5 if desc.primary_element == util.Element.GENERIC else 1
  min_value = 0.6
  max_value = 1
  min_radius = min(width, height) * 0.3
  max_radius = min(width, height) * 0.6
  # Big secondary shape.
  art_draw.polygon(rand_shape(random.uniform(x_min_offset, x_max_offset),
                              random.uniform(y_min_offset, y_max_offset),
                              min_radius, max_radius),
                   fill=rand_color(color_palette.secondary_hue, min_saturation,
                                   max_saturation, min_value, max_value))
  art_draw.polygon(rand_shape(random.uniform(x_min_offset, x_max_offset),
                              random.uniform(y_min_offset, y_max_offset),
                              min_radius, max_radius),
                   fill=rand_color(color_palette.primary_hue, min_saturation,
                                   max_saturation, min_value, max_value))
  _crop_corners(art_image, radius)
  im.paste(art_image, image_bb, art_image)


BORDER_WIDTH = int(0.05 * util.PIXELS_PER_INCH)
BORDER_CORNER_RADIUS = int(0.2 * util.PIXELS_PER_INCH)
BG_PATTERN_SIZE = int(0.2 * util.PIXELS_PER_INCH)


def render_background(im: Image, draw: ImageDraw.Draw, desc: util.CardDesc,
                      image_bb: util.BoundingBox):
  random.seed(desc.hash())
  color_palette = rand_color_palette(desc)
  left, top, right, bottom = image_bb
  image_width = right - left

  # Generate a triangle mesh
  bg_left = left - BG_PATTERN_SIZE
  bg_right = right + BG_PATTERN_SIZE
  bg_top = top - BG_PATTERN_SIZE
  bg_bottom = bottom + BG_PATTERN_SIZE
  bg_ceter = (bg_left + bg_right) / 2

  def _get_hue(x: float) -> float:
    """Gets the hue based on the horizontal location."""
    if desc.secondary_element is None:
      return color_palette.primary_hue
    # fuzzy the card in half, left side is primary.
    color_frac = util.sigmoid((x - bg_ceter) / image_width * 100 +
                              random.uniform(-20, 20))
    return (color_frac * color_palette.secondary_hue +
            (1 - color_frac) * color_palette.primary_hue)

  x_cords = _get_random_coords(bg_left, bg_right, BG_PATTERN_SIZE, 0.2)
  y_cords = _get_random_coords(bg_top, bg_bottom, BG_PATTERN_SIZE, 0.2)
  min_saturation = 0 if desc.primary_element == util.Element.GENERIC else 0.1
  max_saturation = 0 if desc.primary_element == util.Element.GENERIC else 0.3

  for x, _ in enumerate(x_cords):
    this_offset = 0 if x % 2 == 0 else int(BG_PATTERN_SIZE / 2)
    next_offset = 0 if x % 2 == 0 else int(BG_PATTERN_SIZE / 2)
    for y, _ in enumerate(y_cords):
      if x + 1 < len(x_cords) and y + 1 < len(y_cords):
        square = [
            (x_cords[x], y_cords[y] + this_offset),
            (x_cords[x + 1], y_cords[y] + next_offset),
            (x_cords[x + 1], y_cords[y + 1] + next_offset),
            (x_cords[x], y_cords[y + 1] + this_offset),
        ]
        square_center_x = (x_cords[x] + x_cords[x + 1]) / 2
        draw.polygon(square,
                     fill=rand_color(_get_hue(square_center_x),
                                     max_saturation=max_saturation,
                                     min_saturation=min_saturation,
                                     min_value=0.9))
  _crop_corners(im, BORDER_CORNER_RADIUS)


def render_boarder(im: Image, draw: ImageDraw.Draw, desc: util.CardDesc,
                   image_bb: util.BoundingBox):
  draw.rounded_rectangle(
      image_bb,
      outline=desc.primary_element.get_dark_color(),
      width=BORDER_WIDTH,
      radius=BORDER_CORNER_RADIUS,
  )
  if desc.secondary_element is not None:
    right_border = Image.new("RGBA", (im.width, im.height),
                             color=desc.secondary_element.get_dark_color())
    right_mask = Image.new("L", (im.width, im.height), color=0)
    right_mask_draw = ImageDraw.Draw(right_mask)
    # Cut out the border
    right_mask_draw.rounded_rectangle(
        image_bb,
        fill=0,
        outline=255,
        width=BORDER_WIDTH,
        radius=BORDER_CORNER_RADIUS,
    )
    # Mask out left side
    right_mask_draw.rectangle([0, 0, im.width // 2, im.height], fill=0)
    right_border.putalpha(right_mask)
    im.paste(right_border, image_bb, right_border)
