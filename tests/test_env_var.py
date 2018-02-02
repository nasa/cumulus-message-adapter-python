import unittest
import os
from helpers import LambdaContextMock, create_event, create_handler_config

from run_cumulus_task import run_cumulus_task

class TestSledHandler(unittest.TestCase):
    def test_message_adapter_disabled(self):
        def disabled_adapter_handler_fn(event, context):
            return { "message": "hello" }
    
        os.environ['CUMULUS_MESSAGE_ADAPTER_DISABLED'] = 'true'
        handler_config = create_handler_config()
        test_event = create_event()
        context = LambdaContextMock()
        response = run_cumulus_task(disabled_adapter_handler_fn, test_event, context)
        self.assertTrue(response["message"] is "hello")
