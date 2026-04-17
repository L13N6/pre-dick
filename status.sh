#!/bin/sh
# ================================================
# Predict Bot Status Script
# Check agent status, orders, history, and log tail
# ================================================

set -e

AGENT_ID="${AGENT_ID:-predict-worker}"
PREDICT_SERVER_URL="${PREDICT_SERVER_URL:-https://api.agentpredict.work}"

echo "================================================"
echo " Predict Bot Status"
echo "================================================"
echo "Agent ID: $AGENT_ID"

echo ""
echo "== STATUS =="
PREDICT_SERVER_URL="$PREDICT_SERVER_URL" predict-agent status || true

echo ""
echo "== ORDERS =="
PREDICT_SERVER_URL="$PREDICT_SERVER_URL" predict-agent orders || true

echo ""
echo "== HISTORY =="
PREDICT_SERVER_URL="$PREDICT_SERVER_URL" predict-agent history || true

echo ""
echo "== PID =="
if [ -f "$HOME/${AGENT_ID}.pid" ]; then
  cat "$HOME/${AGENT_ID}.pid"
else
  echo "No PID file found"
fi

echo ""
echo "== LOG TAIL =="
if [ -f "$HOME/${AGENT_ID}.log" ]; then
  tail -n 80 "$HOME/${AGENT_ID}.log"
else
  echo "No log file found"
fi
