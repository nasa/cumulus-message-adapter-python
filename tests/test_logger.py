import sys
from cumulus_logger import CumulusLogger
import unittest
from helpers import LambdaContextMock, create_event

class TestLogger(unittest.TestCase):

    def test_simple_message(self):
        event, context = create_event(), LambdaContextMock()
        logger = CumulusLogger()
        logger.setMetadata(event, context)
        msg = logger.createMessage("test simple")
        self.assertTrue(msg["sender"] == context.function_name)
        self.assertTrue(msg["version"] == context.function_version)
        self.assertTrue(msg["executions"] == [event["cumulus_meta"]["execution_name"]])
        self.assertTrue(msg["message"] == "test simple")
        logger.info("test simple")

    def test_formatted_message(self):
        event, context = create_event(), LambdaContextMock()
        logger = CumulusLogger()
        logger.setMetadata(event, context)
        msg = logger.createMessage("test formatted {} {}", "foo", "bar")
        self.assertTrue(msg["message"] == "test formatted foo bar")
        logger.debug("test formatted {} {}", "foo", "bar")

    def test_error_message(self):
        event, context = create_event(), LambdaContextMock()
        logger = CumulusLogger()
        logger.setMetadata(event, context)
        try:
            1 / 0
        except ZeroDivisionError as e:
            msg = logger.createMessage("test exc_info", exc_info=False)
            self.assertTrue(msg["message"].find("test exc_info") == 0)
            self.assertTrue(msg["message"].find("ZeroDivisionError") == -1)
            logger.error("test exc_info", exc_info=False)

            msg = logger.createMessage("test formatted {} exc_info ", "bar", exc_info=True)
            self.assertTrue(msg["message"].find("test formatted bar exc_info") == 0)
            self.assertTrue(msg["message"].find("ZeroDivisionError") > 0)
            logger.error("test formatted {} exc_info ", "bar", exc_info=True)

            msg = logger.createMessage("test exc_info", exc_info=sys.exc_info())
            self.assertTrue(msg["message"].find("test exc_info") == 0)
            self.assertTrue(msg["message"].find("ZeroDivisionError") > 0)
            logger.fatal("test exc_info", exc_info=sys.exc_info())

            msg = logger.createMessage("test exc_info", exc_info=e)
            self.assertTrue(msg["message"].find("test exc_info") == 0)
            self.assertTrue(msg["message"].find("ZeroDivisionError") > 0)
            logger.trace("test exc_info", exc_info=e)

