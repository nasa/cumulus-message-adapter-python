from os import path, environ

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
    function_name = "example"
    def __getitem__(self, item):
        return getattr(self, item)
