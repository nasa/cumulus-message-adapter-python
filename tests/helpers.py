from os import path


def create_parameter_event():
    event = create_event()
    event.update({
        "payload": {
            "granules": [
                {"granuleId": "parameter_id1"},
                {"granuleId": "parameter_id2"}
            ]
        }
    })

    return {
        "cma": {
            "event": event
        }
    }


def create_event():
    return {
        "task_config": {
            "Example": {
                "foo": "wut",
                "cumulus_message": {}
            }
        },
        "cumulus_meta": {
            "task": "Example",
            "message_source": "local",
            "id": "id-1234",
            "execution_name": "123123",
            "asyncOperationId": "3141592654",
            "parentExecutionArn": "arn:foo"
        },
        "meta": {
            "foo": "bar",
            "stack": "Sleestak",
            "input_granules": [
                {"granuleId": "id1"},
                {"granuleId": "id2"}
            ]
        },
        "payload": {
            "anykey": "anyvalue"
        }
    }


def create_handler_config():
    return {
        "task": {
            "root": path.join(
                path.dirname(path.realpath(__file__)),
                "fixtures"),
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
