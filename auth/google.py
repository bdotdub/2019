import os
import pickle
from settings import Settings
from typing import Optional

from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

SCOPES = ["https://www.googleapis.com/auth/photoslibrary.readonly"]


class CredentialManager:

    settings: Settings

    def __init__(self, settings: Settings):
        self.settings = settings

    def load_or_prompt(self) -> Credentials:
        creds = self.load()
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.settings.config_path_for("google", "client_secret.json"),
                    SCOPES,
                )
                creds = flow.run_local_server(port=0)
            self.save(creds)
        return creds

    def load(self) -> Optional[Credentials]:
        creds = None
        if os.path.exists(self.credentials_file_path()):
            with open(self.credentials_file_path(), "rb") as token:
                creds = pickle.load(token)
        return creds

    def save(self, creds: Credentials):
        with open(self.credentials_file_path(), "wb") as token:
            pickle.dump(creds, token)

    def credentials_file_path(self):
        return self.settings.config_path_for("google", "token.pickle")
