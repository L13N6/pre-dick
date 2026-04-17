# Predict Bot Setup & Execution

This repository contains a simple VPS-friendly toolkit for installing and running an AWP Predict WorkNet bot.

## Files

- `setup.sh` → install dependencies, `awp-wallet`, `predict-agent`, and initialize wallet
- `predict.sh` → run the smart v2 predictor with `--mode`
- `run_predict_v2.py` → core adaptive logic (challenge parsing, reasoning composition, submit retries)
- `status.sh` → check status, orders, history, and recent logs

## Setup

Clone the repo:

```bash
git clone https://github.com/L13N6/pre-dick.git
cd pre-dick
```

Run setup:

```bash
bash setup.sh
```

This will:
- install Node.js / Python / Git / curl
- install `awp-wallet`
- install `predict-agent`
- initialize wallet if needed
- show wallet address

## Run

Basic usage:

```bash
bash predict.sh --mode chartist
```

Other supported modes:

```bash
bash predict.sh --mode conservative
bash predict.sh --mode sentiment
bash predict.sh --mode macro
```

Also supported if needed:

```bash
bash predict.sh --mode degen
bash predict.sh --mode sniper
bash predict.sh --mode contrarian
```

Optional tickets override:

```bash
bash predict.sh --mode chartist --tickets 300
```

## Status

Check bot status:

```bash
bash status.sh
```

This shows:
- agent status
- orders
- history
- PID if present
- recent log tail

## How it works

`predict.sh` is the launcher.

It passes arguments into `run_predict_v2.py`, which will:
1. unlock wallet
2. run preflight
3. fetch market context
4. choose a market
5. fetch the current challenge/nonce
6. build reasoning adapted to the prompt constraints
7. submit prediction
8. retry on certain validation failures

## Configuration

Environment variables supported by `run_predict_v2.py`:

- `PREDICT_SERVER_URL` → default `https://api.agentpredict.work`
- `PREDICT_MODE` → set automatically by `predict.sh --mode ...`
- `PREDICT_TICKETS` → set automatically by `predict.sh --tickets ...`
- `PREDICT_MARKET` → optional market preference, default `recommended`
- `PREDICT_MAX_RETRIES` → retry count, default `2`

## Quick Start

```bash
git clone https://github.com/L13N6/pre-dick.git
cd pre-dick
bash setup.sh
bash predict.sh --mode chartist
bash status.sh
```
