import unittest
from helpers import LambdaContextMock, create_event

from run_cumulus_task import run_cumulus_task


class TestSledHandler(unittest.TestCase):
    def test_simple_handler(self):
        def handler_fn(event, context):
            return event
        test_event = create_event()
        context = LambdaContextMock()
        response = run_cumulus_task(handler_fn, test_event, context)
        self.assertIsNotNone(response)
        self.assertEqual(response['cumulus_meta']['task'], 'Example')
        # payload includes the entire event
        self.assertEqual(response['payload']['input']['anykey'], 'anyvalue')

    def test_workflow_error(self):
        def workflow_error_fn(event, context):
            raise Exception('SomeWorkflowError')
        test_event = create_event()
        context = LambdaContextMock()
        response = run_cumulus_task(workflow_error_fn, test_event, context)
        self.assertIsNone(response['payload'])
        self.assertEqual(response['exception'], 'SomeWorkflowError')

    def test_other_error(self):
        def other_error_fn(event, context):
            raise Exception('SomeError')
        test_event = create_event()
        context = LambdaContextMock()
        try:
            run_cumulus_task(other_error_fn, test_event, context)
        except Exception as exception:
            name = exception.args[0]
            self.assertEqual(name, 'SomeError')

    def test_empty_error(self):
        empty_exception = Exception()
        def empty_error_fn(event, context):
            raise empty_exception
        test_event = create_event()
        context = LambdaContextMock()
        try:
            run_cumulus_task(empty_error_fn, test_event, context)
        except Exception as exception:
            self.assertEqual(exception, empty_exception)

    def test_simple_handler_without_context(self):
        def handler_fn(event, context):
            return event
        test_event = create_event()
        response = run_cumulus_task(handler_fn, test_event)
        self.assertIsNotNone(response)
        self.assertEqual(response['cumulus_meta']['task'], 'Example')
        self.assertEqual(response['payload']['input']['anykey'], 'anyvalue')

    def test_task_function_with_additional_arguments(self):
        taskargs = {"taskArgOne": "one", "taskArgTwo": "two"}

        def handler_fn(event, context, taskArgOne, taskArgTwo):
            self.assertEqual(taskArgOne, taskargs['taskArgOne'])
            self.assertEqual(taskArgTwo, taskargs['taskArgTwo'])
            return event
        test_event = create_event()
        response = run_cumulus_task(handler_fn, test_event, **taskargs)
        self.assertIsNotNone(response)
        self.assertEqual(response['cumulus_meta']['task'], 'Example')
        self.assertEqual(response['payload']['input']['anykey'], 'anyvalue')
