import json
import datetime

def log(message):
    if type(message) is str:
        message = {
            "message": message
        }

    try:
        message["level"]
    except KeyError:
        message["level"] = "info"

    print json.dumps(message)
