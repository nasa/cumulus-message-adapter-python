"""
Interprets incoming messages, passes them to an inner handler, gets the response
and transforms it into an outgoing message, returned by Lambda.
"""
import os
import sys

from cumulus_logger import CumulusLogger
# if the message adapter zip file has been included, put it in the path
# it'll be used instead of the version from the requirements file
if os.path.isfile('cumulus-message-adapter.zip'):
    sys.path.insert(0, 'cumulus-message-adapter.zip')

from message_adapter.message_adapter import message_adapter

def run_cumulus_task(task_function, cumulus_message, context):
    """
    Interprets incoming messages, passes them to an inner handler, gets the response
    and transforms it into an outgoing message, returned by Lambda.

    Arguments:
        task_function -- required. the function containing the business logic of the cumulus task
        cumulus_message -- required. either a full Cumulus Message or a Cumulus Remote Message
        context -- an AWS Lambda context dict
        schema_location -- optional. location of input, config, and output schemas of the task
    """

    logger = CumulusLogger(cumulus_message, context)
    message_adapter_disabled = os.environ.get('CUMULUS_MESSAGE_ADAPTER_DISABLED')

    if message_adapter_disabled is 'true':
        try:
            return task_function(cumulus_message, context)
        except Exception as exception:
            name = exception.args[0]
            if ('WorkflowError' in name):                
                cumulus_message['payload'] = None
                cumulus_message['exception'] = name
                logger.log({ "message": "WorkflowError", "level": "error" })
                return cumulus_message
            else:
                logger.log({ "message": str(exception), "level": "error" })
                raise exception 

    adapter = message_adapter()
    full_event = adapter.loadRemoteEvent(cumulus_message)
    nested_event = adapter.loadNestedEvent(full_event, vars(context))
    message_config = nested_event.get('messageConfig', {})

    try:
        task_response = task_function(cumulus_message, context)
    except Exception as exception:
        name = exception.args[0]
        if ('WorkflowError' in name):                
            cumulus_message['payload'] = None
            cumulus_message['exception'] = name
            logger.log({ "message": "WorkflowError", "level": "error" })
            return cumulus_message
        else:
            logger.log({ "message": str(exception), "level": "error" })
            raise exception

    return adapter.createNextEvent(task_response, full_event, message_config)
