import os, sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

import json
import pickle
import os.path
import dateutil.parser
import time

from settings import Settings

from googleapiclient.discovery import build

from auth.google import CredentialManager


def main(settings: Settings):
    manager = CredentialManager(settings)
    creds = manager.load_or_prompt()
    service = build("photoslibrary", "v1", credentials=creds)
    page_token = ""
    things = []
    i = 0
    previous_year = None
    while True:
        i += 1
        # pylint: disable=no-member
        items = service.mediaItems().list(pageToken=page_token, pageSize=100).execute()

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
    with open(settings.output_path_for("all_photos.json"), "w") as file:
        json.dump(things, file, indent=2)


if __name__ == "__main__":
    main(Settings())
