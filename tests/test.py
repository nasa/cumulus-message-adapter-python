import unittest
from helpers import LambdaContextMock, create_event, create_handler_config

from run_cumulus_task import run_cumulus_task

class TestSledHandler(unittest.TestCase):
    def test_simple_handler(self):
        def handler_fn(event, context):
            return event

        handler_config = create_handler_config()
        test_event = create_event()
        context = LambdaContextMock()
        response = run_cumulus_task(handler_fn, test_event, context)
        self.assertTrue(response['cumulus_meta']['task'] == 'Example')
        # payload includes the entire event
        self.assertTrue(response['payload']['input']['anykey'] == 'anyvalue')
        self.assertTrue(response)

    def test_workflow_error(self):
        def workflow_error_fn(event, context):
            raise Exception('SomeWorkflowError')
    
        handler_config = create_handler_config()
        test_event = create_event()
        context = LambdaContextMock()
        response = run_cumulus_task(workflow_error_fn, test_event, context)
        self.assertTrue(response['payload'] is None)
        self.assertTrue(response['exception'] is 'SomeWorkflowError')
    
    def test_other_error(self):
        def other_error_fn(event, context):
            raise Exception('SomeError')
    
        handler_config = create_handler_config()
        test_event = create_event()
        context = LambdaContextMock()
        try:
            response = run_cumulus_task(other_error_fn, test_event, context)
        except Exception as exception:
            name = exception.args[0]
            self.assertTrue(name is 'SomeError')
