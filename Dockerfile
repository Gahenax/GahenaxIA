FROM python:3.11-slim

WORKDIR /app

# Instalar dependencias primero (cache layer)
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código del backend
COPY backend/ .

# Volumen para persistir el SQLite (ua_ledger.sqlite)
VOLUME ["/app/data"]

# Apuntar la DB al volumen
ENV DB_PATH=/app/data/ua_ledger.sqlite

EXPOSE 8080

CMD ["python", "main.py"]
