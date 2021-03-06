#!/bin/bash

rm /var/run/celery/*.pid

export LD_LIBRARY_PATH="${LD_LIBRARY_PATH}:/usr/local/lib/R/lib"

celery multi start $CELERY_WORKERS -A app.celery --pidfile="/var/run/celery/%n.pid" --logfile="/var/log/celery/%n%I.log"

celery flower -A app.celery --loglevel=info --persistent=True --basic_auth=$FLOWER_USER:$FLOWER_PASSWORD