from os import path

def create_parameter_event ():
    return {
        "cma": {
            "event": {
                "workflow_config": {
                    "Example": {
                        "foo": "wut",
                        "cumulus_message": {}
                    }
                },
                "cumulus_meta": {
                    "task": "Example",
                    "message_source": "local",
                    "id": "id-1234",
                    "execution_name": "123123"
                },
                "meta": { "foo": "bar" },
                "payload": { "anykey": "anyvalue" }
            }
        }
    }


def create_event ():
    return {
      "workflow_config": {
        "Example": {
            "foo": "wut",
            "cumulus_message": {}
        }
      },
      "cumulus_meta": {
        "task": "Example",
        "message_source": "local",
        "id": "id-1234",
        "execution_name": "123123"
      },
      "meta": { "foo": "bar" },
      "payload": { "anykey": "anyvalue" }
    }


def create_handler_config():
    return {
        "task": {
            "root": path.join(path.dirname(path.realpath(__file__)), "fixtures"),
            "schemas": {
                "input": "schemas/input.json",
                "config": "schemas/config.json",
                "output": "schemas/output.json"
            }
        }
    }


class LambdaContextMock:
    def __init__(self):
        self.function_name = "function_name_example"
        self.function_version = 1
        self.invoked_function_arn = "arn:aws:lambda:us-east-1:123:function:function_name_example:1"
