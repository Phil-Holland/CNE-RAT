#!/bin/bash

# if we're in debug mode, use the simple flask start command, 
# otherwise use the production-ready gunicorn

if [ "$DEBUG" -eq "1" ]; then
    echo "Starting web service in DEBUG mode";
    python app.py;
else 
    echo "Starting web service in PRODUCTION mode";
    gunicorn -b 0.0.0.0:5000 app:app;
fi