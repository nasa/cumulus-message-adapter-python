import json
from datetime import datetime

class CumulusLogger:
    """
    Log messages with contextual info needed by Cumulus.

    Arguments:
        cumulus_message -- required. either a full Cumulus Message or a Cumulus Remote Message
        context -- an AWS Lambda context dict
    """
    def setMetadata(self, event, context):
        self.event = event
        self.function_name = context.function_name if hasattr(context, 'function_name') else 'unknown'
        self.function_version = context.function_version if hasattr(context, 'function_version') else 'unknown'

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
        message["sender"] = self.function_name
        message["version"] = self.function_version
        return message

    def log(self, message):
        print(json.dumps(self.createMessage(message)))

    def debug(self, message):
        msg = self.createMessage(message)
        msg["level"] = "debug"
        print(json.dumps(msg))

    def info(self, message):
        msg = self.createMessage(message)
        msg["level"] = "info"
        print(json.dumps(msg))

    def warn(self, message):
        msg = self.createMessage(message)
        msg["level"] = "warn"
        print(json.dumps(msg))

    def error(self, message):
        msg = self.createMessage(message)
        msg["level"] = "error"
        print(json.dumps(msg))

    def fatal(self, message):
        msg = self.createMessage(message)
        msg["level"] = "fatal"
        print(json.dumps(msg))

    def trace(self, message):
        msg = self.createMessage(message)
        msg["level"] = "trace"
        print(json.dumps(msg))
