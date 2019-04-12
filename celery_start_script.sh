#!/bin/bash

rm /var/run/celery/*.pid
celery multi start 5 -A app.celery --pidfile="/var/run/celery/%n.pid" --logfile="/var/log/celery/%n%I.log"

celery flower -A app.celery --loglevel=info --persistent=True --basic_auth=$FLOWER_USER:$FLOWER_PASSWORD