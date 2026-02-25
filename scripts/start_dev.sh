#!/bin/sh
set -e

if [ -f .env ]; then
  set -a
  . ./.env
  set +a
fi

uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
