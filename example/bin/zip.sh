#!/bin/sh

PROJECT_DIR=`pwd`
echo $PROJECT_DIR
echo "$PROJECT_DIR/task.zip"

# remove old zip in case it exists
rm "$PROJECT_DIR/task.zip"

# remove task directory in case i've opened it to inspect it
rm -rf "$PROJECT_DIR/task/"

# create new zip
zip "$PROJECT_DIR/task.zip" -X -r ./* -x '*.git*' '*bin*' 'task/'

# include deps from site-packages
cd "$VIRTUAL_ENV/lib/python2.7/site-packages/"
zip -r9 "$PROJECT_DIR/task.zip" ./*

# include deps from virtualenv src
cd $VIRTUAL_ENV/src/
zip -r9 "$PROJECT_DIR/task.zip" ./*

# back to task dir
cd $PROJECT_DIR
