"""
Interprets incoming messages, passes them to an inner handler, gets the
response and transforms it into an outgoing message, returned by Lambda.
"""
import os
import sys

from cumulus_logger import CumulusLogger


def set_sys_path():
    # If the lambda has CUMULUS_MESSAGE_ADAPTER_DIR set, use the CMA lib
    # present at that location
    if os.environ.get('CUMULUS_MESSAGE_ADAPTER_DIR'):
        sys.path.insert(0, os.environ.get('CUMULUS_MESSAGE_ADAPTER_DIR'))

    # if the message adapter zip file has been included, put it in the path
    # it'll be used instead of the version from the requirements file
    if os.path.isfile('cumulus-message-adapter.zip'):
        sys.path.insert(0, 'cumulus-message-adapter.zip')

def handle_task_exception(
    exception,
    cumulus_message,
    logger
):
    name = exception.args[0] if exception.args else None
    if isinstance(name, str) and 'WorkflowError' in name:
        cumulus_message['payload'] = None
        cumulus_message['exception'] = name
        logger.error('WorkflowError')
        return cumulus_message
    logger.error(exception)
    raise

def run_cumulus_task(
        task_function,
        cumulus_message,
        context=None,
        schemas=None,
        **taskargs):
    """
    Interprets incoming messages, passes them to an inner handler, gets the
    response and transforms it into an outgoing message, returned by Lambda.

    Arguments:
        task_function -- Required. The function containing the business logic
            of the cumulus task
        cumulus_message -- Required. Either a full Cumulus Message or a Cumulus
            Remote Message
        context -- AWS Lambda context object
        schemas -- Optional. A dict with filepaths of `input`, `config`, and
            `output` schemas that are relative to the task root directory. All
            three properties of this dict are optional. If omitted, the message
            adapter will look in `/<task_root>/schemas/<schema_type>.json`, and
            if not found there, will be ignored.
        taskargs -- Optional. Additional keyword arguments for the
            task_function
    """

    set_sys_path()
    from message_adapter.message_adapter import MessageAdapter

    context_dict = vars(context) if context else {}
    logger = CumulusLogger()
    logger.setMetadata(cumulus_message, context)
    message_adapter_disabled = str(
        os.environ.get('CUMULUS_MESSAGE_ADAPTER_DISABLED')
    ).lower()

    if message_adapter_disabled == 'true':
        try:
            return task_function(cumulus_message, context, **taskargs)
        except Exception as exception:
            return handle_task_exception(exception, cumulus_message, logger)

    adapter = MessageAdapter(schemas)
    full_event = adapter.load_and_update_remote_event(cumulus_message, context_dict)
    nested_event = adapter.load_nested_event(full_event)
    message_config = nested_event.get('messageConfig', {})

    try:
        task_response = task_function(nested_event, context, **taskargs)
    except Exception as exception:
        return handle_task_exception(exception, cumulus_message, logger)

    return adapter.create_next_event(task_response, full_event, message_config)
