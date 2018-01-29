#!/bin/sh

# create zip file
./bin/zip.sh

# update function code on aws
aws lambda update-function-code --function-name PythonTaskAdapterExample --zip-file fileb://task.zip
