# cumulus-message-adapter-python

[![CircleCI](https://circleci.com/gh/cumulus-nasa/cumulus-message-adapter-python.svg?style=svg)](https://circleci.com/gh/cumulus-nasa/cumulus-message-adapter-python)

## Install

```
$ pip install git+https://github.com/cumulus-nasa/cumulus-message-adapter-python.git
```

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

### Full example

For a full example see the [example folder](./example).

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

## License

[Apache 2.0](LICENSE)
