#!/bin/bash
python manage.py makemigrations
python manage.py migrate
python manage.py migrate-base-data
python manage.py runserver