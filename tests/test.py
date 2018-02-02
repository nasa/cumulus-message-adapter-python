import unittest
from os import path
from run_cumulus_task import run_cumulus_task

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
        "id": "id-1234"
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
    example = "context"

class TestSledHandler(unittest.TestCase):

    def test_simple_handler(self):
        def handler_fn(event, context):
            return event

        handler_config = create_handler_config()
        test_event = create_event()
        context = LambdaContextMock()
        response = run_cumulus_task(handler_fn, test_event, context) 
        self.assertTrue(response['cumulus_meta']['task'] == 'Example')
        self.assertTrue(response['payload']['anykey'] == 'anyvalue')
        self.assertTrue(response)

    def test_workflow_error(self):
        def workflow_error_fn(event, context):
            raise Exception('WorkflowError')

        handler_config = create_handler_config()
        test_event = create_event()
        context = LambdaContextMock()

        response = run_cumulus_task(workflow_error_fn, test_event, context)
        self.assertTrue(response['exception'] is 'WorkflowError')

    def test_other_error(self):
        def other_error_fn(event, context):
            raise Exception('SomeError')

        handler_config = create_handler_config()
        test_event = create_event()
        context = LambdaContextMock()

        try:
            response = run_cumulus_task(other_error_fn, test_event, context) 
        except Exception as exception:
            name = exception.args
            self.assertTrue(name is 'SomeError')

    def test_message_adapter_disabled(self):
        def disabled_adapter_handler_fn(event, context):
            return { "message": "hello" }

        handler_config = create_handler_config()
        test_event = create_event()
        context = LambdaContextMock()
        response = run_cumulus_task(disabled_adapter_handler_fn, test_event, context) 
        self.assertTrue(response["message"] is "hello")
