import copy
from mock import patch
import os
import sys
import unittest

from helpers import LambdaContextMock, create_event, create_handler_config

from run_cumulus_task import run_cumulus_task, set_sys_path

class TestSledHandler(unittest.TestCase):
    @patch('os.path.isfile')
    def test_set_sys_path_sets_adapter_dir_paths(self, isfile_mock):
        isfile_mock.value = True
        stored_sys_path = copy.copy(sys.path)
        try:
            os.environ['CUMULUS_MESSAGE_ADAPTER_DIR'] = '/opt/'
            set_sys_path()
            self.assertTrue(sys.path[1] == '/opt/')
            self.assertTrue(sys.path[0] == 'cumulus-message-adapter.zip')
        finally:
            sys.path = stored_sys_path

    def test_message_adapter_disabled(self):
        def disabled_adapter_handler_fn(event, context):
            return { "message": "hello" }

        os.environ['CUMULUS_MESSAGE_ADAPTER_DISABLED'] = 'true'
        handler_config = create_handler_config()
        test_event = create_event()
        context = LambdaContextMock()
        response = run_cumulus_task(disabled_adapter_handler_fn, test_event, context)
        self.assertTrue(response["message"] is "hello")
