#!/bin/sh

# create zip file
./bin/zip.sh

# run function locally
sam local invoke PythonTaskAdapterExample -e tests/fixtures/event.json
