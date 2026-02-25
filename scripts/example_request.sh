#!/bin/sh
set -e

BASE="${BASE_URL:-http://localhost:8000}"

echo "Creating job..."
RESP=$(curl -s -X POST "$BASE/jobs" \
  -H "Content-Type: application/json" \
  -d '{"topic": "best seo tools", "run_immediately": true}')

if command -v jq >/dev/null 2>&1; then
  JOB_ID=$(echo "$RESP" | jq -r '.job.id')
  STATUS=$(echo "$RESP" | jq -r '.job.status')
else
  JOB_ID=$(echo "$RESP" | grep -o '"id":"[^"]*"' | head -1 | cut -d'"' -f4)
  STATUS=$(echo "$RESP" | grep -o '"status":"[^"]*"' | head -1 | cut -d'"' -f4)
fi

echo "Job ID: $JOB_ID"
echo "Status: $STATUS"

while [ "$STATUS" = "pending" ] || [ "$STATUS" = "running" ]; do
  sleep 2
  RESP=$(curl -s "$BASE/jobs/$JOB_ID")
  if command -v jq >/dev/null 2>&1; then
    STATUS=$(echo "$RESP" | jq -r '.status // .job.status')
  else
    STATUS=$(echo "$RESP" | grep -oE '"status":"[^"]*"' | head -1 | cut -d'"' -f4)
  fi
  echo "  Status: $STATUS"
done

if [ "$STATUS" = "completed" ]; then
  echo ""
  echo "Result:"
  curl -s "$BASE/jobs/$JOB_ID/result" | head -c 500
  echo "..."
else
  echo "Job ended with status: $STATUS"
  if command -v jq >/dev/null 2>&1; then
    echo "$RESP" | jq -r 'if .error then .error else .job.error // empty end'
  fi
fi
