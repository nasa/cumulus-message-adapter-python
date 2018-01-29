#!/bin/sh

# remove old zip
rm task.zip

# destroy function
aws lambda delete-function --function-name PythonTaskAdapterExample
