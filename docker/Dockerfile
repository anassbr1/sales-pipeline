FROM python:3.11-slim

WORKDIR /app

# Dépendances système (psycopg2 a besoin de libpq)
RUN apt-get update && apt-get install -y \
    gcc libpq-dev cron \
    && rm -rf /var/lib/apt/lists/*

# Dépendances Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Code du projet
COPY scripts/ ./scripts/ 
COPY sql/ ./sql/
COPY data/ ./data/

# Point d'entrée par défaut
CMD ["python", "scripts/etl.py"]