#!/bin/sh

# create zip file
./bin/zip.sh

# create function
aws lambda create-function \
--region us-east-1 \
--function-name PythonTaskAdapterExample \
--zip-file fileb://task.zip \
--role "arn:aws:iam::$AWS_IAM_ID:role/lambda_basic_execution"  \
--handler task.handler \
--runtime python3.10 \
--timeout 15 \
--memory-size 512
