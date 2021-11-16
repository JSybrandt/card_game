#!/usr/bin/env python3

import argparse
import datetime
import os
import pathlib
import pprint
import shutil
import tempfile
from typing import Optional

import flask
from PIL import Image, ImageDraw, ImageFont

from . import body_text, card_art, colors, gsheets, icons, upload, util

#pylint: disable=too-many-arguments

# Constants

# Unless specified, all sizes are in pixels.
CARD_WIDTH = int(2.7 * util.PIXELS_PER_INCH)
CARD_HEIGHT = int(3.7 * util.PIXELS_PER_INCH)
CARD_MARGIN = int(0.25 * util.PIXELS_PER_INCH)
CARD_PADDING = int(0.05 * util.PIXELS_PER_INCH)
BORDER_WIDTH = int(0.1 * util.PIXELS_PER_INCH)
CORNDER_RADIUS = int(1 / 8 * util.PIXELS_PER_INCH)

# Default icon params
ICON_HEIGHT = ICON_WIDTH = int(0.3 * util.PIXELS_PER_INCH)
ICON_FONT = ImageFont.truetype(str(util.LATO_FONT_PATH), int(ICON_WIDTH * 0.75))
COST_ICON_FONT = ImageFont.truetype(str(util.LATO_FONT_PATH),
                                    int(ICON_WIDTH * 0.9))
ICON_FONT_COLOR = colors.WHITE

TOP_ICON_X = TOP_ICON_Y = CARD_MARGIN + ICON_HEIGHT // 2

# Cost parameters
COST_COORD = (TOP_ICON_X, TOP_ICON_Y)

# Describes the max width of card contents
CONTENT_WIDTH = CARD_WIDTH - 2 * CARD_MARGIN

# Card image parameters
# Width and height of card image
CARD_IMAGE_BOTTOM = int(2 * util.PIXELS_PER_INCH)
CARD_IMAGE_BB = [
    CARD_MARGIN,
    CARD_MARGIN,
    CARD_WIDTH - CARD_MARGIN,
    CARD_IMAGE_BOTTOM,
]

# Body text
BODY_TEXT_BG_BB = [
    CARD_MARGIN,
    CARD_IMAGE_BOTTOM + CARD_PADDING,
    CARD_MARGIN + CONTENT_WIDTH,
    CARD_HEIGHT - CARD_MARGIN,
]

BOTTOM_ICON_Y = CARD_HEIGHT - ICON_WIDTH // 2 - CARD_MARGIN

ICON_HOR_MARGIN = ICON_WIDTH // 2 + CARD_MARGIN
STRENGTH_COORD = (ICON_HOR_MARGIN, BOTTOM_ICON_Y)

HEALTH_COORD = (CARD_WIDTH - ICON_HOR_MARGIN, BOTTOM_ICON_Y)

MANA_COORD = (CARD_WIDTH // 2, BOTTOM_ICON_Y)

# Layout functions


# We may need to shrink
def _get_scaled_font(text: str, font: ImageFont.ImageFont, max_width: int):
  while font.getsize(text)[0] > max_width:
    font = ImageFont.truetype(font.path, font.size - 1)
  return font


TITLE_BG_HEIGHT = int(0.28 * util.PIXELS_PER_INCH)
MAX_TITLE_WIDTH = int(CARD_WIDTH * 0.75)
DEFAULT_TITLE_FONT = ImageFont.truetype(str(util.LEAGUE_GOTHIC_FONT_PATH),
                                        int(util.PIXELS_PER_INCH * 0.2))
TITLE_BG_COLOR = colors.GREY_50
TITLE_BG_RADIUS = int(0.05 * util.PIXELS_PER_INCH)
TITLE_BG_OUTLINE_COLOR = colors.BLACK
TITLE_BG_OUTLINE_WIDTH = int(0.025 * util.PIXELS_PER_INCH)
TITLE_FONT_COLOR = colors.BLACK


def render_title(draw: ImageDraw.Draw, desc: util.CardDesc):
  scaled_font = _get_scaled_font(desc.title, DEFAULT_TITLE_FONT,
                                 MAX_TITLE_WIDTH)
  text_width, _ = scaled_font.getsize(desc.title)
  if desc.cost is None:
    text_coord = (CARD_WIDTH // 2, CARD_MARGIN + TITLE_BG_HEIGHT // 2)
    bg_width = text_width + 4 * CARD_PADDING
    bg_bb = util.get_centered_bb(text_coord, bg_width, TITLE_BG_HEIGHT)
    text_anchor = "mm"
  else:
    bg_width = text_width + 4 * CARD_PADDING + ICON_WIDTH
    bg_bb = [
        CARD_MARGIN, CARD_MARGIN, bg_width + CARD_MARGIN,
        TITLE_BG_HEIGHT + CARD_MARGIN
    ]
    text_coord = (CARD_MARGIN +
                  CARD_PADDING if desc.cost is None else CARD_MARGIN +
                  CARD_PADDING + ICON_WIDTH, TOP_ICON_Y)
    text_anchor = "lm"
  if desc.card_type == util.CardType.MEMORY:
    draw.rectangle(bg_bb,
                   fill=TITLE_BG_COLOR,
                   width=TITLE_BG_OUTLINE_WIDTH,
                   outline=TITLE_BG_OUTLINE_COLOR)
  else:
    draw.rounded_rectangle(bg_bb,
                           fill=TITLE_BG_COLOR,
                           radius=TITLE_BG_HEIGHT // 2,
                           width=TITLE_BG_OUTLINE_WIDTH,
                           outline=TITLE_BG_OUTLINE_COLOR)
  draw.text(text_coord,
            desc.title,
            TITLE_FONT_COLOR,
            font=scaled_font,
            anchor=text_anchor)


# Card Attributes
ATTRIBUTE_FONT = ImageFont.truetype(str(util.LATO_FONT_PATH),
                                    int(util.PIXELS_PER_INCH * 0.1))
ATTRIBUTE_ANCHOR = "mm"
ATTRIBUTE_HEIGHT = int(0.12 * util.PIXELS_PER_INCH)
ATTRIBUTE_BG_OUTLINE_WIDTH = int(0.015 * util.PIXELS_PER_INCH)
ATTRIBUTE_BOTTOM = CARD_HEIGHT
ATTRIBUTE_COORD = (CARD_WIDTH / 2, CARD_IMAGE_BOTTOM + CARD_PADDING // 2)
ATTRIBUTE_TEXT_COLOR = colors.BLACK
MAX_ATTRIBUTE_WIDTH = int(CARD_WIDTH * 0.6)
ATTRIBUTE_BG_COLOR = colors.GREY_50
ATTRIBUTE_BG_RADIUS = int(0.1 * util.PIXELS_PER_INCH)
ATTRIBUTE_BG_OUTLINE_COLOR = colors.BLACK


def render_attributes(draw: ImageDraw.Draw, desc: util.CardDesc):
  text = desc.card_type.value
  if desc.attributes is not None:
    text += f"— {desc.attributes}"
  font = _get_scaled_font(text, ATTRIBUTE_FONT, MAX_ATTRIBUTE_WIDTH)
  width, height = font.getsize(text)
  width += 2 * CARD_PADDING
  height += CARD_PADDING
  bb = util.get_centered_bb(ATTRIBUTE_COORD, width, height)
  if desc.card_type == util.CardType.MEMORY:
    draw.rectangle(bb,
                   fill=ATTRIBUTE_BG_COLOR,
                   width=ATTRIBUTE_BG_OUTLINE_WIDTH,
                   outline=ATTRIBUTE_BG_OUTLINE_COLOR)
  else:
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


def render_card_back(output_dir: pathlib.Path):
  output_path = output_dir.joinpath("card_back.png")
  im = Image.new(mode="RGBA", size=(CARD_WIDTH, CARD_HEIGHT))
  draw = ImageDraw.Draw(im)
  card_art.render_card_back(im, draw)
  print("Saving card:", output_path)
  im.save(output_path)


def render_card(desc: util.CardDesc,
                output_dir: Optional[pathlib.Path] = None,
                output_path: Optional[pathlib.Path] = None,
                crop_border: bool = True):
  assert (output_path is None) != (
      output_dir is
      None), "Must call render_card with only output_dir or output_path."
  if output_path is None:
    output_path = util.get_output_path(output_dir, desc)
  if output_path.exists():
    print(f"Image already exists: {output_path}")
    return
  im = Image.new(mode="RGBA", size=(CARD_WIDTH, CARD_HEIGHT))
  draw = ImageDraw.Draw(im)

  card_art.render_background(im, draw, desc, [0, 0, CARD_WIDTH, CARD_HEIGHT])

  card_art.render_card_art(im, desc, CARD_IMAGE_BB)

  render_title(draw, desc)

  body_text.render_body_text(im, draw, desc, BODY_TEXT_BG_BB)

  render_attributes(draw, desc)

  # Draw icons
  if desc.cost is not None:
    icons.draw_cost_icon(im, draw, COST_COORD, int(ICON_WIDTH * 1.2),
                         int(ICON_HEIGHT * 1.2), desc.cost, COST_ICON_FONT,
                         ICON_FONT_COLOR, desc.primary_element,
                         desc.secondary_element)
  if desc.health is not None:
    icons.draw_heart_with_text(im, draw, HEALTH_COORD, ICON_HEIGHT, ICON_WIDTH,
                               desc.health, ICON_FONT, ICON_FONT_COLOR)
  if desc.strength is not None:
    icons.draw_strength_with_text(im, draw, STRENGTH_COORD, ICON_HEIGHT,
                                  ICON_WIDTH, desc.strength, ICON_FONT,
                                  ICON_FONT_COLOR)
  if desc.card_type == util.CardType.MEMORY:
    icons.draw_cost_icon(im, draw, MANA_COORD, ICON_HEIGHT, ICON_WIDTH, "1",
                         ICON_FONT, ICON_FONT_COLOR, desc.primary_element,
                         desc.secondary_element)

  card_art.render_boarder(im, draw, desc, [0, 0, CARD_WIDTH, CARD_HEIGHT])

  print("Saving card:", output_path)
  if crop_border:
    im = card_art.crop_image_border(im, BORDER_WIDTH, CORNDER_RADIUS)
  im.save(output_path)


def _render_all_cards(db: gsheets.CardDatabase, output_dir: pathlib.Path):
  for card_desc in db:
    pprint.pprint(card_desc)
    render_card(card_desc, output_dir)


def _start_render_server(image_dir: pathlib.Path, port: int,
                         enable_debug: bool):
  app = flask.Flask(__name__)

  # we want to disable caching for the render server. Its not worth it.
  temp_dir = pathlib.Path(tempfile.mkdtemp())

  @app.route("/<name>")
  def _retrieve_card(name: str):
    try:
      img_path = image_dir.joinpath(name)
      assert img_path.is_file()
      return flask.send_file(img_path.resolve())
    except Exception as exception:
      print(exception)
      return str(exception), 405

  @app.route("/", methods=["POST"])
  def _render_card():
    try:
      fields = flask.request.get_json(silent=True)
      util.assert_valid_card_desc(fields)
      card_desc = util.field_dict_to_card_desc(fields)
      output_path = util.get_output_path(temp_dir, card_desc)
      render_card(card_desc, output_path=output_path)
      response = flask.send_file(output_path.resolve(), as_attachment=True)
      os.remove(output_path)
      return response
    except Exception as e:
      print(e)
      return str(e), 405

  app.run(host='0.0.0.0', port=port, debug=enable_debug)


def _render_and_upload_all_cards(db: gsheets.CardDatabase,
                                 output_dir: pathlib.Path,
                                 selenium_driver_path: pathlib.Path,
                                 card_set_name: str, untap_username: str,
                                 untap_password: str):

  card_metadata = []
  for desc in db:
    output_path = util.get_output_path(output_dir, desc)
    pprint.pprint(desc)
    render_card(desc, output_path=output_path)
    card_metadata.append(
        upload.UploadCardMetadata(image_path=output_path, desc=desc))

  upload.upload_cards(card_metadata, selenium_driver_path, card_set_name,
                      untap_username, untap_password)


def _render_deck(decklist: pathlib.Path, db: gsheets.CardDatabase,
                 output_dir: pathlib.Path, ignore_decklist_counts: bool):
  card_idx = 0
  assert decklist.is_file(), f"File not found: {decklist}"
  with decklist.open() as f:
    for row in f:
      row = row.strip()
      if len(row) == 0 or row[0] == "#":
        continue
      count, title = row.split(" ", 1)
      count = 1 if ignore_decklist_counts else int(count)
      assert count > 0
      assert title in db, f"Card not found: {title}"
      card_desc = db[title]
      pprint.pprint(card_desc)
      for _ in range(count):
        output_path = output_dir.joinpath(f"card_{card_idx}.png")
        render_card(card_desc, output_path=output_path)
        card_idx += 1


def main():
  parser = argparse.ArgumentParser()
  parser.add_argument("--render_card", type=str, default=None)
  parser.add_argument("--render_decklist", type=pathlib.Path, default=None)
  parser.add_argument("--remove_outdir", action="store_true")
  parser.add_argument("--ignore_decklist_counts", action="store_true")
  parser.add_argument("--render_all", action="store_true")
  parser.add_argument("--render_card_back", action="store_true")
  parser.add_argument("--render_server", action="store_true")
  parser.add_argument("--render_server_port", type=int, default=5000)
  parser.add_argument("--render_server_debug", action="store_true")
  parser.add_argument("--output_dir",
                      type=pathlib.Path,
                      default=pathlib.Path("./img"))
  parser.add_argument("--card_database_gsheets_id",
                      type=str,
                      default="1x9sT5zJ-JZzshgyqEQ30OoTz0F2ZO0ZKSDe6aRMBD_4")
  parser.add_argument("--selenium_driver_path",
                      type=pathlib.Path,
                      default="./drivers/chromedriver")
  today_yyyymmdd = datetime.datetime.today().strftime("%Y%m%d")
  parser.add_argument("--upload_card_set_name",
                      type=str,
                      default=f"HRK-{today_yyyymmdd}")
  # Specify these for imgur upload
  parser.add_argument("--untap_username", type=str, default=None)
  parser.add_argument("--untap_password", type=str, default=None)

  args = parser.parse_args()

  if args.output_dir.is_dir() and args.remove_outdir:
    print("Deleting directory:", args.output_dir)
    shutil.rmtree(args.output_dir)
  print("Creating directory:", args.output_dir)
  args.output_dir.mkdir(parents=True, exist_ok=True)

  assert (args.untap_username is None) == (args.untap_password is None), \
    "Must specify untap username and password together."

  num_behavior_options = sum([
      args.render_card is not None, args.render_decklist is not None,
      args.render_all, args.untap_username is not None, args.render_server,
      args.render_card_back
  ])
  assert (num_behavior_options == 1), "Must specify exactly one behavior."

  if args.render_server:
    _start_render_server(args.output_dir, args.render_server_port,
                         args.render_server_debug)
    return

  db = gsheets.CardDatabase(args.card_database_gsheets_id)

  if args.render_card is not None:
    assert args.render_card in db
    render_card(db[args.render_card], args.output_dir)
    return

  if args.render_decklist is not None:
    _render_deck(args.render_decklist, db, args.output_dir,
                 args.ignore_decklist_counts)
    return

  if args.render_all:
    _render_all_cards(db, args.output_dir)
    return

  if args.untap_username is not None and args.untap_password is not None:
    _render_and_upload_all_cards(db, args.output_dir, args.selenium_driver_path,
                                 args.upload_card_set_name, args.untap_username,
                                 args.untap_password)
    return

  if args.render_card_back:
    render_card_back(args.output_dir)
    return


if __name__ == "__main__":
  main()
