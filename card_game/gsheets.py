from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
import pathlib

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


class CardDatabase():
  def __init__(self, sheet_id:str):
    self.sheet_id = sheet_id
    self.creds = _get_credential()
    self.service = build('sheets', 'v4', credentials=self.creds)

  def _download(self):
    sheet = self.service.spreadsheets().get(spreadsheetId=self.sheet_id).execute()
    print(sheet)





