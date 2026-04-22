#!/bin/bash
# start.sh

echo "Ejecutando migraciones de la base de datos..."
python manage.py migrate --noinput

echo "Configurando usuarios por defecto..."
python setup_users.py

echo "Iniciando servidor Gunicorn..."
exec gunicorn config.wsgi:application --bind 0.0.0.0:8000
