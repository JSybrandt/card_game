import dataclasses
import ftplib
import pathlib
import time
from typing import List

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

#pylint: disable=too-many-arguments

UNTAP_URL = "https://untap.in/"
MAX_WAIT = 10

FTP_URL = "ftp.sybrandt.com"
FTP_USER = "ftpuser"
FTP_PASSWD_FILE = (pathlib.Path.home().joinpath(".local").joinpath(
    "share").joinpath("card_game").joinpath("ftp_password"))

# Following the upload, you can search for our cards with the "set" search.


@dataclasses.dataclass
class UploadCardMetadata:
  image_path: pathlib.Path
  title: str


def _login(driver, username, password):
  # We are currently on the front page
  form_element = WebDriverWait(driver, MAX_WAIT).until(
      EC.presence_of_element_located((By.ID, "main")))
  username_input, password_input = form_element.find_elements_by_tag_name(
      "input")
  login_button = form_element.find_element_by_tag_name("button")

  assert username_input.get_attribute("type") == "text"
  assert password_input.get_attribute("type") == "password"
  assert login_button.text.lower() == "login"

  (webdriver.ActionChains(driver).double_click(username_input).send_keys(
      username).click(password_input).send_keys(password).click(
          login_button).perform())


def _dismiss_notifications(driver):
  # we are currently on the "new browser" screen for first-timers.
  modal_element = WebDriverWait(driver, MAX_WAIT).until(
      EC.presence_of_element_located((By.CLASS_NAME, "input-style")))
  dissmiss_link = modal_element.find_element_by_tag_name("a")
  time.sleep(1)
  # Need to click dismiss and somewhere in the background.
  (webdriver.ActionChains(driver).click(dissmiss_link).perform())


def _click_new_deck(driver):
  decklists_element = WebDriverWait(driver, MAX_WAIT).until(
      EC.presence_of_element_located((By.CLASS_NAME, "body-deck-list")))
  new_deck_button = decklists_element.find_element_by_tag_name("button")
  webdriver.ActionChains(driver).double_click(new_deck_button).perform()


def _click_custom_deck(driver):
  modal = WebDriverWait(driver, MAX_WAIT).until(
      EC.presence_of_element_located((By.CLASS_NAME, "container")))
  deck_type_grid = modal.find_element_by_class_name("grid")

  deck_name_input = modal.find_element_by_tag_name("input")
  assert deck_name_input.get_attribute("type") == "text"

  found_deck_label = None
  for deck_type_label in deck_type_grid.find_elements_by_tag_name("label"):
    if deck_type_label.text == "Custom CCG":
      found_deck_label = deck_type_label
  assert found_deck_label is not None

  found_create_deck_button = None
  for button in modal.find_elements_by_tag_name("button"):
    if button.text == "Create Deck":
      found_create_deck_button = button
  assert found_create_deck_button is not None

  (webdriver.ActionChains(driver).double_click(deck_name_input).send_keys(
      time.asctime()).double_click(found_deck_label).double_click(
          found_create_deck_button).perform())


def _open_submenu(driver):
  menu_icon = WebDriverWait(driver, MAX_WAIT).until(
      EC.presence_of_element_located((By.CLASS_NAME, "icon-menu")))
  (webdriver.ActionChains(driver).move_to_element(menu_icon).click().perform())
  menu_overlay = WebDriverWait(driver, MAX_WAIT).until(
      EC.presence_of_element_located((By.ID, "sub-menu-overlay")))

  add_card_option = None
  for option in menu_overlay.find_elements_by_tag_name("span"):
    if option.text == "Add Missing Card":
      add_card_option = option
      break
  assert add_card_option is not None

  # Click and open "I understand"
  webdriver.ActionChains(driver).click(add_card_option).perform()


def _click_i_understand(driver):
  i_understand_button = None
  for button in driver.find_elements_by_tag_name("button"):
    if button.text == "I Understand":
      i_understand_button = button
  assert i_understand_button is not None
  webdriver.ActionChains(driver).click(i_understand_button).perform()


def _fill_card_contents(driver, title, set_name, image_url):
  form = WebDriverWait(driver, MAX_WAIT).until(
      EC.presence_of_element_located((By.ID, "add-card")))
  card_title_input, card_set_input, card_img_url_input, _ = \
    form.find_elements_by_tag_name("input")
  _, card_type_select, _, _, _ = form.find_elements_by_tag_name("select")

  add_card_button = None
  for button in driver.find_elements_by_tag_name("button"):
    if button.text == "Add Card":
      add_card_button = button
      break
  assert add_card_button is not None

  (webdriver.ActionChains(driver).double_click(card_title_input).send_keys(
      title).double_click(card_set_input).send_keys(set_name).double_click(
          card_img_url_input).send_keys(image_url).double_click(
              card_type_select).send_keys("c").send_keys(
                  Keys.ENTER).double_click(add_card_button).perform())


def _upload_image(ftp_session: ftplib.FTP,
                  local_image_path: pathlib.Path) -> str:
  """Returns the remote URL where to find this file."""
  with open(local_image_path, 'rb') as data_file:
    ftp_session.storbinary(f"STOR {local_image_path.name}", data_file)
  return f"http://{FTP_URL}/{local_image_path.name}"
  return http_url


def _attempt(fn, tries=3):
  for i in range(tries):
    try:
      return fn()
    except Exception as e:
      print(e)
      if i == tries - 1:
        raise e
      else:
        print("Trying again...")


def upload_cards(card_metadata: List[UploadCardMetadata],
                 selenium_driver_path: pathlib.Path, card_set_name: str,
                 untap_username: str, untap_password: str):
  assert selenium_driver_path.is_file()
  with open(FTP_PASSWD_FILE) as f:
    ftp_pass = f.read().strip()
  ftp_session = ftplib.FTP_TLS()
  ftp_session.set_debuglevel(2)
  ftp_session.connect(FTP_URL, 21)
  ftp_session.sendcmd(f"USER {FTP_USER}")
  ftp_session.sendcmd(f"PASS {ftp_pass}")

  # If we go to sleep, the automated browser iterations may fail.
  driver = webdriver.Chrome(executable_path=selenium_driver_path)
  driver.get(UNTAP_URL)
  driver.set_window_position(0, 0)
  # The damn icons on the left hand side can cover up the buttons we need.
  driver.set_window_size(1920, 1080)
  _login(driver, untap_username, untap_password)
  time.sleep(1)
  _dismiss_notifications(driver)
  time.sleep(1)
  _click_new_deck(driver)
  time.sleep(1)
  _click_custom_deck(driver)
  for card in card_metadata:
    time.sleep(1)
    card_link = _attempt(lambda: _upload_image(ftp_session, card.image_path))
    print(f"Uploaded '{card.title}' to {card_link}")
    _attempt(lambda: _open_submenu(driver))
    time.sleep(1)
    _attempt(lambda: _click_i_understand(driver))
    time.sleep(1)
    _attempt(lambda: _fill_card_contents(driver, card.title, card_set_name,
                                         card_link))

  ftp_session.close()
