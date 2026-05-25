FROM python:3.12-slim

# Arbeitsverzeichnis innerhalb des Containers
WORKDIR /app/backend

# System-Abhängigkeiten
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Python-Abhängigkeiten
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Projektdateien in das backend-Verzeichnis kopieren
COPY . .

# Monorepo-Root (/app) zum Python-Path hinzufügen,
# damit "import backend.*" funktioniert
ENV PYTHONPATH=/app

EXPOSE 8000

# Start-Skript: führt Alembic-Migrationen aus und startet dann Uvicorn
CMD ["./entrypoint.sh"]
