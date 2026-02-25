FROM python:3.11-slim

RUN apt-get update && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY pyproject.toml .
COPY src/ src/
RUN pip install --no-cache-dir -e .
COPY docker/entrypoint.sh docker/healthcheck.sh /app/
RUN chmod +x /app/entrypoint.sh /app/healthcheck.sh

EXPOSE 8000

ENTRYPOINT ["/app/entrypoint.sh"]
