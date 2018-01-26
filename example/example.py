from run_cumulus_task import run_cumulus_task

def task(event, context):
    return event

def handler(event, context):
    return run_cumulus_task(task, event, context)
