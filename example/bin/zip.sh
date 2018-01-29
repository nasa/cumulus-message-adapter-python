#!/bin/sh

# remove old zip in case it exists
rm task.zip

# remove task directory in case i've opened it to inspect it
rm -rf task/

# create new zip
zip task.zip -X -r ./* -x '*.git*' '*bin*' 'task/'

# include deps from site-packages
cd /Users/sdv/workspace/virtualenvs/task_python_example/lib/python2.7/site-packages/
zip -r9 /Users/sdv/workspace/cumulus-nasa/python_example/task.zip ./*

# include deps from virtualenv src
cd /Users/sdv/workspace/virtualenvs/task_python_example/src/
#mv /Users/sdv/workspace/virtualenvs/task_python_example/src/cumulus-message-adapter-python /Users/sdv/workspace/virtualenvs/task_python_example/src/cumulus_message_adapter_python
#rm /Users/sdv/workspace/virtualenvs/task_python_example/src/cumulus-message-adapter-python.egg-link
zip -r9 /Users/sdv/workspace/cumulus-nasa/python_example/task.zip ./*

# back to task dir
cd /Users/sdv/workspace/cumulus-nasa/python_example/
