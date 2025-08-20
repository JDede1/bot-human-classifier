FROM python:3.11-slim

WORKDIR /mlflow

RUN pip install --no-cache-dir mlflow==2.14.1 psycopg2-binary==2.9.9

EXPOSE 5000

# Args passed via docker-compose env:
# MLFLOW_DB_PASSWORD used in the command
CMD ["sh", "-lc", "mlflow server \
  --backend-store-uri postgresql+psycopg2://mlflow:${MLFLOW_DB_PASSWORD}@db:5432/mlflow \
  --artifacts-destination /mlruns \
  --host 0.0.0.0 --port 5000"]
