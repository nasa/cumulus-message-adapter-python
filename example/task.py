import os
import sys

from run_cumulus_task import run_cumulus_task
from cumulus_logger import CumulusLogger

logger = CumulusLogger()

schemas = {
    "input": "schemas/input.json",
    "config": "schemas/config.json",
    "output": "schemas/output.json"
}

def task(event, context):
    """simple task that returns the updated event"""
    # example logging inside of a task using CumulusLogger
    logger.info('task executed')

    # log error when an exception is caught
    logger.error("task formatted message {} exc_info ", "bar", exc_info=True)

    # return the output of the task
    return { "goodbye": event["input"]["hello"] }

def handler(event, context):
    """handler that is provided to aws lambda"""
    # make sure event & context metadata is set in the logger
    logger.setMetadata(event, context)
    return run_cumulus_task(task, event, context, schemas)
