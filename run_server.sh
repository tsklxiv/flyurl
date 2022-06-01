#!/bin/sh

gunicorn -w 4 -b localhost:5000 app:app --reload
