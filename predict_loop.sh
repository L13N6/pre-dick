#!/bin/sh
# ================================================
# Predict Loop Script
# Run predict.sh repeatedly with cooldown between runs
# Usage:
#   bash predict_loop.sh --mode chartist
#   bash predict_loop.sh --mode conservative --sleep 900
# ================================================

set -e

MODE="chartist"
SLEEP_SECS="60"
TICKETS="300"

while [ $# -gt 0 ]; do
    case "$1" in
        --mode)
            MODE="$2"
            shift 2
            ;;
        --sleep)
            SLEEP_SECS="$2"
            shift 2
            ;;
        --tickets)
            TICKETS="$2"
            shift 2
            ;;
        *)
            echo "Unknown argument: $1"
            echo "Usage: bash predict_loop.sh --mode chartist|conservative|sentiment|macro [--sleep 900] [--tickets 300]"
            exit 1
            ;;
    esac
done

SCRIPT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
LOG_DIR="$HOME/.openclaw/workspace"
LOG_FILE="$LOG_DIR/predict.log"
mkdir -p "$LOG_DIR"

echo "================================================" | tee -a "$LOG_FILE"
echo " Predict Loop Started" | tee -a "$LOG_FILE"
echo " Mode   : $MODE" | tee -a "$LOG_FILE"
echo " Sleep  : $SLEEP_SECS seconds" | tee -a "$LOG_FILE"
echo " Tickets: $TICKETS" | tee -a "$LOG_FILE"
echo "================================================" | tee -a "$LOG_FILE"

while true; do
    echo "[$(date -u '+%Y-%m-%d %H:%M:%S UTC')] Running predict..." | tee -a "$LOG_FILE"
    bash "$SCRIPT_DIR/predict.sh" --mode "$MODE" --tickets "$TICKETS" 2>&1 | tee -a "$LOG_FILE" || true

    echo "[$(date -u '+%Y-%m-%d %H:%M:%S UTC')] Sleeping for $SLEEP_SECS seconds..." | tee -a "$LOG_FILE"
    sleep "$SLEEP_SECS"
done
