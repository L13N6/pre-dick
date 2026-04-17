#!/bin/sh
# Smart Predict runner v2
# Usage:
#   bash run_predict_v2.sh --mode chartist
#   bash run_predict_v2.sh --mode conservative
#   bash run_predict_v2.sh --mode sentiment
#   bash run_predict_v2.sh --mode macro

set -e

MODE="chartist"
TICKETS="300"

while [ $# -gt 0 ]; do
    case "$1" in
        --mode)
            MODE="$2"
            shift 2
            ;;
        --tickets)
            TICKETS="$2"
            shift 2
            ;;
        *)
            echo "Unknown argument: $1"
            echo "Usage: bash run_predict_v2.sh --mode chartist|conservative|sentiment|macro [--tickets 300]"
            exit 1
            ;;
    esac
done

MODE_LOWER=$(printf '%s' "$MODE" | tr '[:upper:]' '[:lower:]')
case "$MODE_LOWER" in
    chartist|conservative|sentiment|macro|degen|sniper|contrarian)
        MODE="$MODE_LOWER"
        ;;
    *)
        echo "Invalid mode: $MODE"
        echo "Allowed modes: chartist, conservative, sentiment, macro, degen, sniper, contrarian"
        exit 1
        ;;
esac

export PREDICT_MODE="$MODE"
export PREDICT_TICKETS="$TICKETS"

cd "$HOME/.openclaw/workspace" 2>/dev/null || cd /root/.openclaw/workspace 2>/dev/null || true
python3 /root/.openclaw/workspace/run_predict_v2.py
