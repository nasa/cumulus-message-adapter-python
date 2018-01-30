"""
Interprets incoming messages, passes them to an inner handler, gets the response
and transforms it into an outgoing message, returned by Lambda.
"""
import os

from message_adapter.message_adapter import message_adapter

def run_cumulus_task(task_function, cumulus_message, context):
    """
    Interprets incoming messages, passes them to an inner handler, gets the response
    and transforms it into an outgoing message, returned by Lambda.

    Arguments:
        task_function -- the function containing the business logic of the cumulus task
        cumulus_message -- either a full Cumulus Message or a Cumulus Remote Message
        context -- an AWS Lambda context dict
    """

    message_adapter_disabled = os.environ.get('CUMULUS_MESSAGE_ADAPTER_DISABLED')

    if message_adapter_disabled:
        return task_function(cumulus_message, context)

    adapter = message_adapter()
    full_event = adapter.loadRemoteEvent(cumulus_message)
    nested_event = adapter.loadNestedEvent(full_event, vars(context))
    message_config = nested_event.get('messageConfig', {})
    task_response = task_function(nested_event, context)
    return adapter.createNextEvent(task_response, full_event, message_config)
