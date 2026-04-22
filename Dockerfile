# Usar una imagen oficial de Python ligera
FROM python:3.12-slim

# Evitar que Python escriba archivos .pyc y forzar salida por consola
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Directorio de trabajo en el contenedor
WORKDIR /app

# Instalar dependencias del sistema necesarias para PostgreSQL
RUN apt-get update \
    && apt-get install -y gcc libpq-dev \
    && apt-get clean

# Copiar dependencias e instalarlas
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el resto del código
COPY . /app/

# Recopilar archivos estáticos (con variables dummy para el build)
RUN DATABASE_URL=sqlite:///db.sqlite3 SECRET_KEY=dummy python manage.py collectstatic --noinput

# Dar permisos de ejecución al script de inicio
RUN chmod +x start.sh

# Exponer el puerto
EXPOSE 8000

# Usar el script de inicio
CMD ["./start.sh"]