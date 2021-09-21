from typing import List, Any, Optional
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
import pathlib

from . import util

CARD_RANGE="All!1:1000"

SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']

LOCAL_PATH = pathlib.Path.home().joinpath(".local").joinpath("share").joinpath("card_game")
LOCAL_PATH.mkdir(parents=True, exist_ok=True)

TOKEN_CACHE_PATH = LOCAL_PATH.joinpath("token.json")
SECRET_PATH = LOCAL_PATH.joinpath("secret.json")


def _cache_credential(creds:Credentials)->Credentials:
  # Save the credentials for the next run
  with open(TOKEN_CACHE_PATH, "w") as token:
    token.write(creds.to_json())
  return creds

def _get_credential()->Credentials:
  creds = (Credentials.from_authorized_user_file(TOKEN_CACHE_PATH)
           if TOKEN_CACHE_PATH.is_file() else None)
  if creds is not None and creds.valid:
    return creds

  if creds is not None and creds.expired and creds.refresh_token:
    creds.refresh(Request())
    return _cache_credential(creds)

  flow = InstalledAppFlow.from_client_secrets_file(SECRET_PATH, SCOPES)
  creds = flow.run_local_server(port=0)
  return _cache_credential(creds)

EXPECTED_COLUMN_HEADERS = [
  "Element",
  "Card Type",
  "Title",
  "Cost",
  "Attributes",
  "Body Text",
  "Power",
  "Health",
]

def _row_to_card_desc(row:List[str])->util.CardDesc:
  fields = {}
  for idx, header in enumerate(EXPECTED_COLUMN_HEADERS):
    fields[header] = row[idx] if idx < len(row) else None
  return util.field_dict_to_card_desc(fields)


class CardDatabase():
  def __init__(self, sheet_id:str):
    self.sheet_id = sheet_id
    self.creds = _get_credential()
    self.service = build('sheets', 'v4', credentials=self.creds)
    self.cards = None

  def _download(self):
    if self.cards is None:
      print("Downloading cards from gSheets.")
      response = self.service.spreadsheets().values().get(spreadsheetId=self.sheet_id, range=CARD_RANGE).execute()
      self.cards = {}
      for idx, row in enumerate(response.get("values", [])):
        if idx == 0:
          assert row == EXPECTED_COLUMN_HEADERS, "Invalid column headers."
          continue
        desc = _row_to_card_desc(row)
        assert desc.title not in self.cards, f"Duplicate title: {desc.title}"
        self.cards[desc.title] = desc

  def __iter__(self):
    self._download()
    return iter(self.cards.values())

  def __contains__(self, key:Any)->bool:
    self._download()
    return key in self.cards

  def __getitem__(self, key:Any)->Optional[util.CardDesc]:
    self._download()
    return self.cards.get(key, None)



