#!/usr/bin/env python3

import argparse
import csv
import pathlib
import pprint
import shutil

from PIL import Image, ImageDraw, ImageFont

from . import body_text, card_art, colors, icons, util, gsheets

# Constants

# Unless specified, all sizes are in pixels.
CARD_WIDTH = int(2.5 * util.PIXELS_PER_INCH)
CARD_HEIGHT = int(3.5 * util.PIXELS_PER_INCH)
CARD_MARGIN = int(0.1 * util.PIXELS_PER_INCH)

# Default icon params
SMALL_ICON_HEIGHT = SMALL_ICON_WIDTH = int(0.35 * util.PIXELS_PER_INCH)
LARGE_ICON_HEIGHT = LARGE_ICON_WIDTH = int(0.5 * util.PIXELS_PER_INCH)
SMALL_ICON_FONT = ImageFont.truetype(str(util.LATO_FONT_PATH),
                                     int(SMALL_ICON_HEIGHT * 0.8))
LARGE_ICON_FONT = ImageFont.truetype(str(util.LATO_FONT_PATH),
                                     int(LARGE_ICON_HEIGHT * 0.8))
SMALL_ICON_FONT_COLOR = colors.WHITE
LARGE_ICON_FONT_COLOR = colors.WHITE

TOP_ICON_Y = int(SMALL_ICON_HEIGHT / 2) + CARD_MARGIN

# Cost parameters
COST_COORD = (CARD_MARGIN + SMALL_ICON_WIDTH // 2, TOP_ICON_Y)

# Describes the max width of card contents
CONTENT_WIDTH = CARD_WIDTH - 2 * CARD_MARGIN

# Card image parameters
# Width and height of card image
CARD_IMAGE_BOTTOM = int(1.5 * util.PIXELS_PER_INCH)
CARD_IMAGE_BB = [
    CARD_MARGIN,
    CARD_MARGIN,
    CARD_WIDTH - CARD_MARGIN,
    CARD_IMAGE_BOTTOM,
]

# Card Attributes
ATTRIBUTE_FONT = ImageFont.truetype(str(util.LATO_FONT_PATH),
                                    int(util.PIXELS_PER_INCH * 0.125))
ATTRIBUTE_ANCHOR = "mm"  # middle bottom
ATTRIBUTE_HEIGHT = int(0.2 * util.PIXELS_PER_INCH)
ATTRIBUTE_BOTTOM = CARD_IMAGE_BOTTOM + ATTRIBUTE_HEIGHT
ATTRIBUTE_COORD = (CARD_WIDTH / 2,
                   CARD_IMAGE_BOTTOM + int(ATTRIBUTE_HEIGHT / 2))
ATTRIBUTE_TEXT_COLOR = colors.BLACK

# Body text
BODY_TEXT_BG_BB = [
    CARD_MARGIN,
    ATTRIBUTE_BOTTOM + CARD_MARGIN,
    CARD_MARGIN + CONTENT_WIDTH,
    CARD_HEIGHT - int(LARGE_ICON_HEIGHT / 2) - CARD_MARGIN,
]

BOTTOM_ICON_Y = CARD_HEIGHT - int(LARGE_ICON_HEIGHT / 2) - CARD_MARGIN

POWER_COORD = (CARD_WIDTH * 0.2, BOTTOM_ICON_Y)
POWER_BG_COLOR = colors.BLUE_GREY_800

HEALTH_COORD = (CARD_WIDTH * 0.8, BOTTOM_ICON_Y)
HEALTH_BG_COLOR = colors.RED_A400

MANA_COORD = (CARD_WIDTH / 2, BOTTOM_ICON_Y)

# Layout functions


# We may need to shrink
def _get_scaled_font(text: str, font: ImageFont.ImageFont, max_width: int):
  while font.getsize(text)[0] > max_width:
    font = ImageFont.truetype(font.path, font.size - 1)
  return font


MAX_TITLE_WIDTH = int(CARD_WIDTH * 0.8)
DEFAULT_TITLE_FONT = ImageFont.truetype(str(util.LEAGUE_GOTHIC_FONT_PATH),
                                        int(util.PIXELS_PER_INCH * 0.25))
TITLE_BG_COLOR = colors.GREY_50
TITLE_BG_RADIUS = int(0.05 * util.PIXELS_PER_INCH)
TITLE_BG_OUTLINE_COLOR = colors.BLACK
TITLE_BG_OUTLINE_WIDTH = 8
TITLE_FONT_COLOR = colors.BLACK


def render_title(draw: ImageDraw.Draw, desc: util.CardDesc):
  scaled_font = _get_scaled_font(desc.title, DEFAULT_TITLE_FONT,
                                 MAX_TITLE_WIDTH)
  text_width, _ = scaled_font.getsize(desc.title)
  bg_width = text_width + 2 * CARD_MARGIN
  if desc.cost is not None:
    bg_width += SMALL_ICON_WIDTH
  bg_height = SMALL_ICON_HEIGHT
  bg_bb = [
      CARD_MARGIN, CARD_MARGIN, bg_width + CARD_MARGIN, bg_height + CARD_MARGIN
  ]
  draw.rounded_rectangle(bg_bb,
                         fill=TITLE_BG_COLOR,
                         radius=bg_height // 2,
                         width=TITLE_BG_OUTLINE_WIDTH,
                         outline=TITLE_BG_OUTLINE_COLOR)
  left_middle_coord = (2 *
                       CARD_MARGIN if desc.cost is None else 2 * CARD_MARGIN +
                       SMALL_ICON_WIDTH, TOP_ICON_Y)
  draw.text(left_middle_coord,
            desc.title,
            TITLE_FONT_COLOR,
            font=scaled_font,
            anchor="lm")


MAX_ATTRIBUTE_WIDTH = int(CARD_WIDTH * 0.9)
ATTRIBUTE_BG_COLOR = colors.GREY_50
ATTRIBUTE_BG_RADIUS = int(0.1 * util.PIXELS_PER_INCH)
ATTRIBUTE_BG_OUTLINE_COLOR = colors.BLACK
ATTRIBUTE_BG_OUTLINE_WIDTH = 5


def render_attributes(draw: ImageDraw.Draw, desc: util.CardDesc):
  text = desc.card_type.value
  if desc.attributes is not None:
    text += f"— {desc.attributes}"
  font = _get_scaled_font(text, ATTRIBUTE_FONT, MAX_ATTRIBUTE_WIDTH)
  width, height = font.getsize(text)
  width += 2 * CARD_MARGIN
  height += CARD_MARGIN
  bb = util.get_centered_bb(ATTRIBUTE_COORD, width, height)
  # Move top under image
  bb[1] -= 2 * ATTRIBUTE_BG_RADIUS
  draw.rounded_rectangle(bb,
                         fill=ATTRIBUTE_BG_COLOR,
                         radius=ATTRIBUTE_BG_RADIUS,
                         width=ATTRIBUTE_BG_OUTLINE_WIDTH,
                         outline=ATTRIBUTE_BG_OUTLINE_COLOR)
  draw.text(ATTRIBUTE_COORD,
            text,
            ATTRIBUTE_TEXT_COLOR,
            font=font,
            anchor=ATTRIBUTE_ANCHOR)


def generate_card(desc: util.CardDesc, output_path: pathlib.Path):
  assert not output_path.exists(), f"{output_path} already exists"
  im = Image.new(mode="RGBA", size=(CARD_WIDTH, CARD_HEIGHT))
  draw = ImageDraw.Draw(im)

  card_art.render_background(im, draw, desc, [0, 0, CARD_WIDTH, CARD_HEIGHT])

  render_attributes(draw, desc)

  card_art.render_card_art(im, desc, CARD_IMAGE_BB, SMALL_ICON_HEIGHT // 2)

  render_title(draw, desc)

  body_text.render_body_text(im, draw, desc.body_text, BODY_TEXT_BG_BB)

  # Draw icons
  if desc.cost is not None:
    icons.draw_circle_with_text(draw, COST_COORD, SMALL_ICON_WIDTH,
                                SMALL_ICON_HEIGHT, desc.cost, SMALL_ICON_FONT,
                                SMALL_ICON_FONT_COLOR,
                                desc.element.get_dark_color())
  if desc.health is not None:
    icons.draw_heart_with_text(draw, HEALTH_COORD, LARGE_ICON_WIDTH,
                               LARGE_ICON_HEIGHT, desc.health, LARGE_ICON_FONT,
                               LARGE_ICON_FONT_COLOR, HEALTH_BG_COLOR)
  if desc.power is not None:
    icons.draw_diamond_with_text(draw, POWER_COORD, LARGE_ICON_WIDTH,
                                 LARGE_ICON_HEIGHT, desc.power, LARGE_ICON_FONT,
                                 LARGE_ICON_FONT_COLOR, POWER_BG_COLOR)
  if desc.card_type == util.CardType.HOLDING:
    icons.draw_circle_with_text(draw, MANA_COORD, LARGE_ICON_WIDTH,
                                LARGE_ICON_HEIGHT, "1", LARGE_ICON_FONT,
                                LARGE_ICON_FONT_COLOR,
                                desc.element.get_dark_color())

  card_art.render_boarder(draw, desc, [0, 0, CARD_WIDTH, CARD_HEIGHT])

  print("Saving card:", output_path)
  im.save(output_path)


def main():
  parser = argparse.ArgumentParser()
  parser.add_argument("--output_dir",
                      type=pathlib.Path,
                      default=pathlib.Path("./img"))
  parser.add_argument("--card_database_gsheets_id",
                      type=str, default="1x9sT5zJ-JZzshgyqEQ30OoTz0F2ZO0ZKSDe6aRMBD_4")
  args = parser.parse_args()

  if args.output_dir.is_dir():
    print("Deleting directory:", args.output_dir)
    shutil.rmtree(args.output_dir)
  print("Creating directory:", args.output_dir)
  args.output_dir.mkdir(parents=True)

  db = gsheets.CardDatabase(args.card_database_gsheets_id)
  for card_idx, card_desc in enumerate(db):
    output_path = args.output_dir.joinpath(f"card_{card_idx:03d}.png")
    pprint.pprint(card_desc)
    generate_card(card_desc, output_path)


if __name__ == "__main__":
  main()
