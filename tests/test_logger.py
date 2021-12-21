import json
import logging
import sys
import unittest
from cumulus_logger import CumulusLogger
from helpers import LambdaContextMock, create_event, create_parameter_event


class TestLogger(unittest.TestCase):
    def set_up_logger(self, event=None, context=None, logger=None, **kwargs):
        if event is None:
            event = create_event()

        if context is None:
            context = LambdaContextMock()

        if logger is None:
            logger = CumulusLogger(**kwargs)
        logger.setMetadata(event, context)

        return logger

    def test_simple_message(self):
        event, context = create_event(), LambdaContextMock()
        logger = self.set_up_logger(event=event, context=context)
        msg = logger.createMessage("test simple")
        self.assertEqual(msg["sender"], context.function_name)
        self.assertEqual(msg["version"], context.function_version)
        self.assertEqual(
            msg["executions"],
            event["cumulus_meta"]["execution_name"])
        self.assertEqual(
            msg["asyncOperationId"],
            event["cumulus_meta"]["asyncOperationId"])
        self.assertEqual(
            msg["granules"],
            json.dumps([granule["granuleId"]
                        for granule in event["meta"]["input_granules"]]))
        self.assertEqual(
            msg["parentArn"],
            event["cumulus_meta"]["parentExecutionArn"])
        self.assertEqual(msg["stackName"], event["meta"]["stack"])
        self.assertEqual(msg["message"], "test simple")
        logger.info("test simple")

    def test_parameter_configured_message(self):
        event, context = create_parameter_event(), LambdaContextMock()
        logger = self.set_up_logger(event=event, context=context)
        msg = logger.createMessage("test parameter event")
        self.assertEqual(msg["sender"], context.function_name)
        self.assertEqual(msg["version"], context.function_version)
        self.assertEqual(
            msg["executions"],
            event["cma"]["event"]["cumulus_meta"]["execution_name"])
        self.assertEqual(
            msg["asyncOperationId"],
            event["cma"]["event"]["cumulus_meta"]["asyncOperationId"])
        self.assertEqual(
            msg["granules"],
            json.dumps([granule["granuleId"]
                        for granule in event["cma"]["event"]["payload"]["granules"]]))
        self.assertEqual(
            msg["parentArn"],
            event["cma"]["event"]["cumulus_meta"]["parentExecutionArn"])
        self.assertEqual(
            msg["stackName"],
            event["cma"]["event"]["meta"]["stack"])
        self.assertEqual(msg["message"], "test parameter event")
        logger.info("test parameter configured message")

    def test_empty_event_and_context(self):
        logger = self.set_up_logger(event={}, context={})
        msg = logger.createMessage("empty event and context")
        self.assertEqual(set(msg.keys()),
                         {"version", "sender", "message", "timestamp"})

    def test_formatted_message(self):
        logger = self.set_up_logger()
        msg = logger.createMessage("test formatted {} {}", "foo", "bar")
        self.assertEqual(msg["message"], "test formatted foo bar")
        logger.debug("test formatted {} {}", "foo", "bar")

    def test_formatted_message_with_positional_args(self):
        logger = self.set_up_logger()
        msg = logger.createMessage("test formatted {0}", "bar")
        self.assertEqual(msg["message"], "test formatted bar")

    def test_formatted_message_with_kwargs(self):
        logger = self.set_up_logger()
        msg = logger.createMessage("test formatted {foo}", foo="bar")
        self.assertEqual(msg["message"], "test formatted bar")

    def test_formatted_message_with_args_and_kwargs(self):
        logger = self.set_up_logger()
        msg = logger.createMessage("test formatted {0} {foo}", 'foo', foo="bar")
        self.assertEqual(msg["message"], "test formatted foo bar")

    def test_error_message(self):
        logger = self.set_up_logger()
        try:
            1 / 0
        except ZeroDivisionError as ex:
            msg = logger.createMessage("test exc_info", exc_info=False)
            self.assertIn("test exc_info", msg["message"])
            self.assertNotIn("ZeroDivisionError", msg["message"])
            logger.error("test exc_info", exc_info=False)

            msg = logger.createMessage(
                "test formatted {} exc_info ", "bar", exc_info=True)
            self.assertIn("test formatted bar exc_info", msg["message"])
            self.assertIn("ZeroDivisionError", msg["message"])
            logger.warn("test formatted {} exc_info ", "bar", exc_info=True)

            msg = logger.createMessage(
                "test exc_info", exc_info=sys.exc_info())
            self.assertIn("test exc_info", msg["message"])
            self.assertIn("ZeroDivisionError", msg["message"])
            logger.fatal("test exc_info", exc_info=sys.exc_info())

            msg = logger.createMessage("test exc_info", exc_info=ex)
            self.assertIn("test exc_info", msg["message"])
            self.assertIn("ZeroDivisionError", msg["message"])
            logger.trace("test exc_info", exc_info=ex)

    def test_logger_name_loglevel(self):
        logger = self.set_up_logger(logger=CumulusLogger('logger_test', logging.INFO))
        self.assertTrue(logger.logger.getEffectiveLevel() == logging.INFO)
        logger.debug("test logging level debug")
        logger.info("test logging level info")
        logger.warning("test logging level warning")

    def test_simple_message_with_braces_no_args(self):
        logger = self.set_up_logger()
        msg = logger.createMessage("test simple {}")
        self.assertEqual(msg["message"], "test simple {}")

    def test_simple_message_with_braces_no_kwargs(self):
        logger = self.set_up_logger()
        msg = logger.createMessage("test {simple}")
        self.assertEqual(msg["message"], "test {simple}")

    def test_message_with_json_no_kwargs(self):
        logger = self.set_up_logger()
        msg = logger.createMessage('some message about JSON and the json: {"test": "simple"}')
        self.assertEqual(msg["message"], 'some message about JSON and the json: {"test": "simple"}')

    def test_multiple_instances_with_same_name_dont_have_multiple_handlers(self):
        logger1 = self.set_up_logger(name='test')
        self.assertEqual(1, len(logger1.logger.handlers))

        logger2 = self.set_up_logger(name='test')
        self.assertEqual(1, len(logger1.logger.handlers))
        self.assertEqual(1, len(logger2.logger.handlers))
