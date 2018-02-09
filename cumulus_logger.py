import json
from datetime import datetime

class CumulusLogger:
    """
    Log messages with contextual info needed by Cumulus.

    Arguments:
        cumulus_message -- required. either a full Cumulus Message or a Cumulus Remote Message
        context -- an AWS Lambda context dict
    """
    def __init__(self, cumulus_message, context):
        self.event = cumulus_message
        self.context = context

    def createMessage(self, message):
        if type(message) is str:
            message = {
                "message": message
            }

        try:
            message["level"]
        except KeyError:
            message["level"] = "info"

        message["executions"] = [self.event["cumulus_meta"]["execution_name"]]
        message["timestamp"] = datetime.now().isoformat()
        message["sender"] = self.context["function_name"]

        return message

    def log(self, message):
        print json.dumps(self.createMessage(message))
