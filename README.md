# cumulus-message-adapter-python

[![CircleCI]](https://circleci.com/gh/nasa/cumulus-message-adapter-python)
[![PyPI version]](https://badge.fury.io/py/cumulus-message-adapter-python)

## What is Cumulus?

Cumulus is a cloud-based data ingest, archive, distribution and management
prototype for NASA's future Earth science data streams.

Read the [Cumulus Documentation]

## What is the Cumulus Message Adapter?

The Cumulus Message Adapter is a library that adapts incoming messages in the
Cumulus protocol to a format more easily consumable by Cumulus tasks, invokes
the tasks, and then adapts their response back to the Cumulus message protocol
to be sent to the next task.

## Installation

```plain
pip install cumulus-message-adapter-python
```

## Task definition

In order to use the Cumulus Message Adapter, you will need to create two
methods in your task module: a handler function and a business logic function.

The handler function is a standard Lambda handler function which takes two
parameters (as specified by AWS): `event` and `context`.

The business logic function is where the actual work of your task occurs. It
should take two parameters: `event` and `context`.

The `event` object contains two keys:

* `input` - the task's input, typically the `payload` of the message, produced
  at runtime
* `config` - the task's configuration, with any templated variables resolved

The `context` parameter is the standard Lambda context as passed by AWS.

The return value of the business logic function will be placed in the
`payload` of the resulting Cumulus message.

Expectations for input, config, and return values are all defined by the task,
and should be well documented. Tasks should thoughtfully consider their inputs
and return values, as breaking changes may have cascading effects on tasks
throughout a workflow. Configuration changes are slightly less impactful, but
must be communicated to those using the task.

## Cumulus Message Adapter interface

The Cumulus Message adapter for python provides one method:
`run_cumulus_task`. It takes four parameters:

* `task_function` - the function containing your business logic (as described
  above)
* `cumulus_message` - the event passed by Lambda, and should be a Cumulus
  Message, *or* a CMA parameter encapsulated message (see [Cumulus Workflow
  Documentation](https://nasa.github.io/cumulus/docs/workflows/input_output)):

  ```json
  {
     "cma": {
        "event": "<cumulus message object>",
        "SomeCMAConfigKey": "CMA configuration object>"
     }
  }
  ```

* `context` - the Lambda context
* `schemas` - optional: a dict with `input`, `config`, and `output` properties.
  Each should be a string set to the filepath of the corresponding JSON schema
  file. All three properties of this dict are optional. If ommitted, the message
  adapter will look in `/<task_root>/schemas/<schema_type>.json`, and if not
  found there, will be ignored.
* `taskargs` - Optional. Additional keyword arguments for the `task_function`

## Example

Simple example of using this package's `run_cumulus_task` function as a wrapper
around another function:

```python
>>> from run_cumulus_task import run_cumulus_task

# simple task that returns the event
>>> def task(event, context):
...     return event

# handler that is provided to aws lambda
>>> def handler(event, context):
...     return run_cumulus_task(task, event, context)

```

For a full example see the [example folder](./example).

## Creating a deployment package

Tasks that use this library are just standard AWS Lambda tasks. See
[creating release packages].

## Usage in a Cumulus Deployment

For documenation on how to utilize this package in a Cumulus Deployment, view
the [Cumulus Workflow Documenation].

## Development

### Dependency Installation

```plain
$ pip install -r requirements-dev.txt
$ pip install -r requirements.txt
```

### Logging with `CumulusLogger`

Included in this package is the `cumulus_logger` which contains a logging class
`CumulusLogger` that standardizes the log format for Cumulus. Methods are
provided to log error, fatal, warning, debug, info, and trace.

**Import the `CumulusLogger` class:**

```python
>>> from cumulus_logger import CumulusLogger

```

**Instantiate the logger inside the task definition (name and level are
optional):**

```python
>>> import logging
>>> logger = CumulusLogger("event_name", logging.ERROR)

```

**Use the logging methods for different levels:**

```python
>>> logger.trace('<your message>')

>>> logger.debug('<your message>')

>>> logger.info('<your message>')

>>> logger.warn('<your message>')

>>> logger.error('<your message>')

>>> logger.fatal('<your message>')

```

**It can also take additional non-keyword and keyword arguments as in Python
Logger.**

The `msg` is the message format string, the `args` and `kwargs` are the
arguments for string formatting.

If `exc_info` in `kwargs` is not `False`, the exception information in the
`exc_info` or `sys.exc_info()` is added to the message.

```python
>>> logger.debug(msg, *args, **kwargs)

```

**Example usage:**

```python
>>> import os
>>> import sys

>>> from run_cumulus_task import run_cumulus_task
>>> from cumulus_logger import CumulusLogger

# instantiate CumulusLogger
>>> logger = CumulusLogger()

>>> def task(event, context):
...     logger.info('task executed')
... 
...     # log error when an exception is caught
...     logger.error("task formatted message {} exc_info ", "bar", exc_info=True)
... 
...     # return the output of the task
...     return { "example": "output" }

>>> def handler(event, context):
...     # make sure event & context metadata is set in the logger
...     logger.setMetadata(event, context)
...     return run_cumulus_task(task, event, context)

```

### Running Tests

Running tests requires [localstack](https://github.com/localstack/localstack).

Tests only require localstack running S3, which can be initiated with the
following command:

```plain
$ SERVICES=s3 localstack start
```

And then you can check tests pass with the following nosetests command:

```plain
$ CUMULUS_ENV=testing nose2
```

### Linting

```plain
$ pylint run_cumulus_task.py
```

## Why?

This approach has a few major advantages:

1. It explicitly prevents tasks from making assumptions about data structures
   like `meta` and `cumulus_meta` that are owned internally and may therefore
   be broken in future updates. To gain access to fields in these structures,
   tasks must be passed the data explicitly in the workflow configuration.
1. It provides clearer ownership of the various data structures. Operators own
   `meta`. Cumulus owns `cumulus_meta`. Tasks define their own `config`,
   `input`, and `output` formats.
1. The Cumulus Message Adapter greatly simplifies running Lambda functions not
   explicitly created for Cumulus.
1. The approach greatly simplifies testing for tasks, as tasks don't need to
   set up cumbersome structures to emulate the message protocol and can just
   test their business function.

## License

[Apache 2.0](LICENSE)

[circleci]:
  https://circleci.com/gh/nasa/cumulus-message-adapter-python.svg?style=svg
[pypi version]:
  https://badge.fury.io/py/cumulus-message-adapter-python.svg
[Cumulus Documentation]:
  https://nasa.github.io/cumulus/
[creating release packages]:
  https://docs.aws.amazon.com/lambda/latest/dg/gettingstarted-package.html
[cumulus workflow documenation]:
  https://nasa.github.io/cumulus/docs/workflows/input_output
