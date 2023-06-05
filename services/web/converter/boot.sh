#!/bin/bash
while !</dev/tcp/db/5432; do sleep 1; done;
flask db upgrade
exec gunicorn -b :5000 --access-logfile - --error-logfile - converter:app