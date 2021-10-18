#!/usr/bin/env python3

import argparse
import datetime
import flask
import os
import pathlib
import pprint
import shutil
import tempfile

from PIL import Image, ImageDraw, ImageFont

from . import body_text, card_art, colors, gsheets, icons, upload, util

#pylint: disable=too-many-arguments

# Constants

# Unless specified, all sizes are in pixels.
CARD_WIDTH = int(2.5 * util.PIXELS_PER_INCH)
CARD_HEIGHT = int(3.5 * util.PIXELS_PER_INCH)
CARD_MARGIN = int(0.125 * util.PIXELS_PER_INCH)

# Default icon params
SMALL_ICON_HEIGHT = SMALL_ICON_WIDTH = int(0.35 * util.PIXELS_PER_INCH)
LARGE_ICON_HEIGHT = LARGE_ICON_WIDTH = int(0.5 * util.PIXELS_PER_INCH)
SMALL_ICON_FONT = ImageFont.truetype(str(util.LATO_FONT_PATH),
                                     int(SMALL_ICON_HEIGHT * 0.9))
LARGE_ICON_FONT = ImageFont.truetype(str(util.LATO_FONT_PATH),
                                     int(LARGE_ICON_HEIGHT * 0.8))
SMALL_ICON_FONT_COLOR = colors.WHITE
LARGE_ICON_FONT_COLOR = colors.WHITE

TOP_ICON_Y = int(0.175 * util.PIXELS_PER_INCH) + CARD_MARGIN

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

HEALTH_COORD = (CARD_WIDTH * 0.8, BOTTOM_ICON_Y)

MANA_COORD = (CARD_WIDTH / 2, BOTTOM_ICON_Y)

# Layout functions


# We may need to shrink
def _get_scaled_font(text: str, font: ImageFont.ImageFont, max_width: int):
  while font.getsize(text)[0] > max_width:
    font = ImageFont.truetype(font.path, font.size - 1)
  return font


TITLE_BG_HEIGHT = int(0.3 * util.PIXELS_PER_INCH)
MAX_TITLE_WIDTH = int(CARD_WIDTH * 0.75)
DEFAULT_TITLE_FONT = ImageFont.truetype(str(util.LEAGUE_GOTHIC_FONT_PATH),
                                        int(util.PIXELS_PER_INCH * 0.25))
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
    bg_width = text_width + 2 * CARD_MARGIN
    bg_bb = util.get_centered_bb(text_coord, bg_width, TITLE_BG_HEIGHT)
    text_anchor = "mm"
  else:
    bg_width = text_width + 2 * CARD_MARGIN + SMALL_ICON_WIDTH
    bg_bb = [
        CARD_MARGIN, CARD_MARGIN, bg_width + CARD_MARGIN,
        TITLE_BG_HEIGHT + CARD_MARGIN
    ]
    text_coord = (2 * CARD_MARGIN if desc.cost is None else 2 * CARD_MARGIN +
                  SMALL_ICON_WIDTH, TOP_ICON_Y)
    text_anchor = "lm"
  if desc.card_type == util.CardType.HOLDING:
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


MAX_ATTRIBUTE_WIDTH = int(CARD_WIDTH * 0.9)
ATTRIBUTE_BG_COLOR = colors.GREY_50
ATTRIBUTE_BG_RADIUS = int(0.1 * util.PIXELS_PER_INCH)
ATTRIBUTE_BG_OUTLINE_COLOR = colors.BLACK
ATTRIBUTE_BG_OUTLINE_WIDTH = int(0.015 * util.PIXELS_PER_INCH)


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
  if desc.card_type == util.CardType.HOLDING:
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


def render_card(desc: util.CardDesc, output_dir:pathlib.Path):
  output_path = util.get_output_path(output_dir, desc)
  if output_path.exists():
    print(f"Image already exists: {output_path}")
    return
  im = Image.new(mode="RGBA", size=(CARD_WIDTH, CARD_HEIGHT))
  draw = ImageDraw.Draw(im)

  card_art.render_background(im, draw, desc, [0, 0, CARD_WIDTH, CARD_HEIGHT])

  render_attributes(draw, desc)

  card_art.render_card_art(im, desc, CARD_IMAGE_BB, SMALL_ICON_HEIGHT // 2)

  render_title(draw, desc)

  body_text.render_body_text(im, draw, desc, BODY_TEXT_BG_BB)

  # Draw icons
  if desc.cost is not None:
    icons.draw_cost_icon(im, draw, COST_COORD, int(SMALL_ICON_WIDTH * 1.2),
                         int(SMALL_ICON_HEIGHT * 1.2), desc.cost,
                         SMALL_ICON_FONT, SMALL_ICON_FONT_COLOR,
                         desc.primary_element, desc.secondary_element)
  if desc.health is not None:
    icons.draw_heart_with_text(draw, HEALTH_COORD, LARGE_ICON_WIDTH,
                               LARGE_ICON_HEIGHT, desc.health, LARGE_ICON_FONT,
                               LARGE_ICON_FONT_COLOR)
  if desc.power is not None:
    icons.draw_diamond_with_text(draw, POWER_COORD, LARGE_ICON_WIDTH,
                                 LARGE_ICON_HEIGHT, desc.power, LARGE_ICON_FONT,
                                 LARGE_ICON_FONT_COLOR)
  if desc.card_type == util.CardType.HOLDING:
    icons.draw_cost_icon(im, draw, MANA_COORD, LARGE_ICON_WIDTH,
                         LARGE_ICON_HEIGHT, "1", LARGE_ICON_FONT,
                         LARGE_ICON_FONT_COLOR, desc.primary_element,
                         desc.secondary_element)

  card_art.render_boarder(im, draw, desc, [0, 0, CARD_WIDTH, CARD_HEIGHT])

  print("Saving card:", output_path)
  im.save(output_path)


def _render_all_cards(db: gsheets.CardDatabase, output_dir: pathlib.Path):
  for card_idx, card_desc in enumerate(db):
    output_path = util.get_output_path(output_dir, card_desc)
    pprint.pprint(card_desc)
    render_card(card_desc, output_path)


def _start_render_server(image_dir:pathlib.Path, port:int, enable_debug:bool):
  app = flask.Flask(__name__)

  # we want to disable caching for the render server. Its not worth it.
  temp_dir = pathlib.Path(tempfile.mkdtemp())

  @app.route("/<name>")
  def _retrieve_card(name:str):
    try:
      img_path = image_dir.joinpath(name)
      assert img_path.is_file()
      return flask.send_file(img_path.resolve())
    except Exception as e:
      print(e)
      return str(e), 405

  @app.route("/", methods=["POST"])
  def _render_card():
    try:
      fields = flask.request.get_json(silent=True)
      util.assert_valid_card_desc(fields)
      card_desc = util.field_dict_to_card_desc(fields)
      output_path = util.get_output_path(temp_dir, card_desc)
      render_card(card_desc, output_path)
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
  for card_idx, card_desc in enumerate(db):
    output_path = util.get_output_path(output_dir, card_desc)
    pprint.pprint(card_desc)
    render_card(card_desc, output_path)
    card_metadata.append(
        upload.UploadCardMetadata(image_path=output_path,
                                  title=card_desc.title))

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
        render_card(card_desc, output_path)
        card_idx += 1


def main():
  parser = argparse.ArgumentParser()
  parser.add_argument("--render_card", type=str, default=None)
  parser.add_argument("--render_decklist", type=pathlib.Path, default=None)
  parser.add_argument("--remove_outdir", action="store_true")
  parser.add_argument("--ignore_decklist_counts", action="store_true")
  parser.add_argument("--render_all", action="store_true")
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
                      default=f"JJ{today_yyyymmdd}")
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
      args.render_card is not None,
      args.render_decklist is not None,
      args.render_all,
      args.untap_username is not None,
      args.render_server
  ])
  assert (num_behavior_options == 1), "Must specify exactly one behavior."

  if args.render_server:
    _start_render_server(args.output_dir, args.render_server_port, args.render_server_debug)
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



if __name__ == "__main__":
  main()
