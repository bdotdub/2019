import os, sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

import json
import pickle
import os.path
import dateutil.parser
import time

from settings import Settings

from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# If modifying these scopes, delete the file token.pickle.
SCOPES = ["https://www.googleapis.com/auth/photoslibrary.readonly"]


def main(settings: Settings):
    """Shows basic usage of the Docs API.
    Prints the title of a sample document.
    """
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    token_path = settings.config_path_for("google", "token.pickle")
    if os.path.exists(token_path):
        with open(token_path, "rb") as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                settings.config_path_for("google", "client_secret.json"), SCOPES
            )
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open(token_path, "wb") as token:
            pickle.dump(creds, token)

    service = build("photoslibrary", "v1", credentials=creds)
    page_token = ""
    things = []
    i = 0
    previous_year = None
    while True:
        i += 1
        # pylint: disable=no-member
        items = service.mediaItems().list(pageToken=page_token, pageSize=100).execute()
        with open("last_request.txt", "w") as file:
            file.write(f"{items}")

        media_items = items.get("mediaItems", None)
        page_token = items.get("nextPageToken")
        if page_token and not media_items:
            continue
        d = dateutil.parser.parse(media_items[-1]["mediaMetadata"]["creationTime"])
        if previous_year and d.year > previous_year:
            break
        previous_year = d.year

        things.extend(media_items)
        d = dateutil.parser.parse(things[-1]["mediaMetadata"]["creationTime"])
        print(f"{i}: got a bunch of photos: {len(things)} {d.year}")
        time.sleep(1)
    with open("all_photos.json", "w") as file:
        json.dump(things, file, indent=2)


if __name__ == "__main__":
    main(Settings())
