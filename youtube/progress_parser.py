import csv
import json
import logging
import re
from argparse import ArgumentParser
from typing import Optional
from urllib.parse import parse_qs, urlparse

from bs4 import BeautifulSoup, element

parser = ArgumentParser(description="Outputs data about Youtube watch time")
parser.add_argument("--verbose", action="store_true", help="prints verbose")
args = parser.parse_args()

logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO)


def parse_video_length(text: str) -> int:
    parts = [int(t.strip()) for t in text.split(":")]
    if len(parts) == 3:
        return parts[0] * 3600 + parts[1] * 60 + parts[2]
    elif len(parts) == 2:
        return parts[0] * 60 + parts[1]
    else:
        raise "invalid state for video length"


def parse_progress_percentage(text: str) -> int:
    m = re.match(r"width: ([0-9]+)", text)
    return int(m.group(1))


def progress_for_key(element: element.Tag) -> (str, Optional[int], int):
    url = urlparse(element["href"])
    params = parse_qs(url.query)
    logging.debug(f"Parsed params: {params}")
    key = params["v"][0]

    progress = None
    progress_elem = element.find(id="progress")
    if progress_elem:
        style = progress_elem.attrs["style"]
        logging.debug(f"Got style for progress: {style}")
        progress = parse_progress_percentage(style)

    video_length = 0
    video_length_elem = element.find(
        "span", class_="ytd-thumbnail-overlay-time-status-renderer"
    )
    if video_length_elem:
        video_length = parse_video_length(video_length_elem.get_text())

    return key, progress, video_length


def run():
    data = []

    with open("data/Youtube.htm") as fp:
        soup = BeautifulSoup(fp, features="lxml")

    with open("data/watch-history.json") as wh:
        watch_history = json.load(wh)

    watch_history_by_key = {}
    for item in watch_history:
        if "titleUrl" not in item:
            continue
        key = item["titleUrl"].split("\u003d")[1]
        if key not in watch_history_by_key:
            watch_history_by_key[key] = []
        watch_history_by_key[key].append(item)

    for thumb_elem in soup.find_all("ytd-thumbnail"):
        thumbnail_elem = thumb_elem.find(id="thumbnail")
        if "href" not in thumbnail_elem.attrs:
            logging.debug(f"ran into element without href: {thumbnail_elem}")
            continue
        logging.debug(f"Got href: {thumbnail_elem['href']}")
        key, progress, total_time_in_secs = progress_for_key(thumbnail_elem)
        if progress is None:
            continue
        watched = round(progress / 100.0 * total_time_in_secs)
        data.append(
            {"key": key, "watched": watched, "total_length": total_time_in_secs}
        )

    # Temporary fix. There is currently a mismatch between wh and the html page
    while True:
        if data[0]["key"] in watch_history[0]["titleUrl"]:
            break
        logging.debug(f"had to pop: {data.pop(0)}")

    for item in data:
        key = item["key"]
        if key not in watch_history_by_key:
            logging.debug(f"!!!! somehow {item['key']} is missing")
            continue
        if len(watch_history_by_key[key]) == 0:
            logging.debug(f"ran out of items for {key}")
            continue
        history_item = watch_history_by_key[key].pop(0)
        item["title"] = history_item["title"]
        item["timestamp"] = history_item["time"]
        item["channel"] = history_item["subtitles"][0]["name"]
    # print(
    #     json.dumps([
    #         d for d in data if "timestamp" in d and "2019-" in d["timestamp"]
    #     ]))
    with open("out.csv", "w") as out:
        w = csv.DictWriter(out, data[0].keys())
        w.writeheader()
        w.writerows(data)


if __name__ == "__main__":
    run()
