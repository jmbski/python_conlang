#!/bin/bash
#export FLASK_APP=$HOME/coding_base/silverlight/conlang/python/server.py
#source $(pipenv --venv)/bin/activate

# get first command line arg to determine whether to start server with flask or gunicorn
SERVER_RUNNER=$1
if [ -z "$SERVER_RUNNER" ]; then
    SERVER_RUNNER="flask"
fi

if [ "$SERVER_RUNNER" == "flask" ]; then
    echo "Starting server with flask"
    flask --debug run -h 0.0.0.0 
elif [ "$SERVER_RUNNER" == "gunicorn" ]; then
    echo "Starting server with gunicorn"
    gunicorn --bind 0.0.0.0:5000 --max-requests 1 --timeout 0 --reload wsgi:app
else
    echo "Invalid server runner specified: $SERVER_RUNNER, using flask instead"
    flask --debug run -h 0.0.0.0    
fi

