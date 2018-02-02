import os
import sys

from run_cumulus_task import run_cumulus_task

def task(event, context):
    """simple task that returns the event unchanged"""
    return event

def handler(event, context):
    """handler that is provided to aws lambda"""
    return run_cumulus_task(task, event, context)
