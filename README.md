# cumulus-message-adapter-python

[![CircleCI](https://circleci.com/gh/cumulus-nasa/cumulus-message-adapter-python.svg?style=svg)](https://circleci.com/gh/cumulus-nasa/cumulus-message-adapter-python)

## What is Cumulus?

Cumulus is a cloud-based data ingest, archive, distribution and management
prototype for NASA's future Earth science data streams.

Read the [Cumulus Documentation](https://cumulus-nasa.github.io/)

## What is the Cumulus Message Adapter?

The Cumulus Message Adapter is a library that adapts incoming messages in the
Cumulus protocol to a format more easily consumable by Cumulus tasks, invokes
the tasks, and then adapts their response back to the Cumulus message protocol
to be sent to the next task.

## Installation

```
$ pip install git+https://github.com/cumulus-nasa/cumulus-message-adapter-python.git
```

## Task definition

In order to use the Cumulus Message Adapter, you will need to create two
methods in your task module: a handler function and a business logic function.

The handler function is a standard Lambda handler function which takes three
parameters (as specified by AWS): `event` and `context`.

The business logic function is where the actual work of your task occurs. It
should take two parameters: `event` and `context`.

The `event` object contains two keys:

  * `input` - the task's input, typically the `payload` of the message,
    produced at runtime
  * `config` - the task's configuration, with any templated variables
    resolved

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
    Message
  * `context` - the Lambda context
  * `schemas` - optional: a dict with `input`, `config`, and `output` properties. Each should be set to the filepath of the corresponding JSON schema file

## Example

Simple example of using this package's `run_cumulus_task` function as a wrapper around another function:

```py
from run_cumulus_task import run_cumulus_task

# simple task that returns the event
def task(event, context):
    return event

# handler that is provided to aws lambda
def handler(event, context):
    return run_cumulus_task(task, event, context)
```

For a full example see the [example folder](./example).

## Creating a deployment package

Tasks that use this library are just standard AWS Lambda tasks. Information on
creating release packages is available [here](https://docs.aws.amazon.com/lambda/latest/dg/deployment-package-v2.html).

## Usage in a Cumulus Deployment

During deployment, Cumulus will automatically obtain and inject the [Cumulus Message Adapter](https://github.com/cumulus-nasa/cumulus-message-adapter) into the compiled code and create a zip file to be deployed to Lambda.

The example task in the [example folder](./example) of this repository would be configured in lambdas.yml as follows:

```yaml
PythonExample:
  handler: task.handler
  timeout: 300
  source: './example'
  useSled: true
  runtime: python2.7
  memory: 256
```

## Development

### Dependency Installation

```
$ pip install -r requirements-dev.txt
$ pip install -r requirements.txt
```

### Running Tests

Running tests requires [localstack](https://github.com/localstack/localstack).

Tests only require localstack running S3, which can be initiated with the following command:

```
$ SERVICES=s3 localstack start
```

And then you can check tests pass with the following nosetests command:

```
$ CUMULUS_ENV=testing nosetests -v -s
```

### Linting

```
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
