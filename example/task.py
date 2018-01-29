import os
import sys

# dir = os.path.dirname(os.path.realpath(__file__))
# sys.path.append(dir)

print sys.path

from run_cumulus_task import run_cumulus_task

def task(event, context):
    """simple task that returns the event unchanged"""
    return event

def handler(event, context):
    """handler that is provided to aws lambda"""
    return run_cumulus_task(task, event, context)
