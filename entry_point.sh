#!/bin/bash

export LD_LIBRARY_PATH=/lib64
cd /app
gunicorn -w 1 -b 0.0.0.0:80 "app:create_app()"
