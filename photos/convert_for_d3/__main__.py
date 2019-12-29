import sys
import json

with open(sys.argv[1], "r") as r:
    obj = json.loads(r.read())

# for o in obj:
#     if "width" not in o["mediaMetadata"]:
#         print(o)


def metadataFor(o, field):
    md = o["mediaMetadata"]
    mdm = md["photo"] if "photo" in md else md["video"]
    return mdm[field] if field in mdm else "UNKNOWN"


sanitized = [
    {
        "mimeType": o["mimeType"],
        "creationTime": o["mediaMetadata"]["creationTime"],
        "width": o["mediaMetadata"]["width"],
        "height": o["mediaMetadata"]["height"],
        "cameraMake": metadataFor(o, "cameraMake"),
        "cameraModel": metadataFor(o, "cameraModel"),
    }
    for o in obj
    if "width" in o["mediaMetadata"]
]

print(json.dumps(sanitized))
