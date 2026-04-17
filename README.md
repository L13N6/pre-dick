Predict Bot Setup & Execution

This repository provides a set of scripts for setting up and running a prediction bot on your server. The bot interacts with a prediction server, unlocks a wallet, and submits market predictions based on different modes (Chartist, Conservative, Sentiment, etc.).

Table of Contents
- Setup
- Usage
- Files
  - setup.sh
  - run.sh
  - run_predict_v2.py
  - status.sh
- Configuration
- License

Setup

1. Clone the repository

First, clone this repository to your local machine:

git clone https://github.com/L13N6/pre-dick.git
cd predict-bot

2. Install Dependencies

Run the install_predict.sh script to install necessary dependencies and set up the bot:

bash install_predict.sh

This will:
- Install required software (Node.js, Python, Git, etc.).
- Install awp-wallet and predict-agent.
- Set up a wallet and check your wallet address.

3. Wallet Setup

The script will prompt to initialize your wallet. If needed, it will provide the wallet address, which is required for bot operations.

Usage

1. Run the Prediction Bot

After setting up the bot, run the run_predict.sh script to start the prediction loop:

bash run_predict.sh --mode chartist --tickets 300

You can specify the mode as one of the following:
- chartist
- conservative
- sentiment
- macro
- degen
- sniper
- contrarian

If no mode is provided, it defaults to chartist.

The --tickets parameter defines how many tickets the bot will use for predictions (default is 300).

2. Check Bot Status

You can check the bot's status, orders, and history with the status_predict.sh script:

bash status_predict.sh

This will give you:
- The agent's current status.
- A list of orders.
- A history of predictions.
- Logs from the bot's activity.

Files

setup_predict.sh
This script installs all the necessary dependencies for the prediction bot:
- Installs Node.js, Python, and other required tools.
- Installs awp-wallet and predict-agent.
- Initializes the wallet.

run_predict_v2.sh
This shell script runs the Python script run_predict_v2.py with the provided arguments. It allows you to specify the prediction mode and number of tickets. It sets up environment variables and executes the Python script accordingly.

run_predict_v2.py
This is the core Python script that:
- Unlocks the wallet using awp-wallet.
- Performs preflight checks and retrieves the current market context.
- Makes predictions based on the selected mode (e.g., chartist, conservative).
- Submits the prediction to the server.

status_predict.sh
This script checks the status of the bot. It retrieves:
- The current status of the bot.
- Pending and completed orders.
- A history of past predictions.
- Logs for debugging purposes.

Configuration

You can configure the bot by setting environment variables:
- PREDICT_SERVER_URL: The URL of the prediction server (default: https://api.agentpredict.work).
- PREDICT_MODE: The mode for making predictions (chartist, conservative, etc.).
- PREDICT_TICKETS: The number of tickets for predictions (default: 300).
- PREDICT_MARKET: The preferred market for predictions (default: recommended).
- PREDICT_MAX_RETRIES: The maximum number of retries for submitting predictions (default: 2).

License

This project is licensed under the MIT License - see the LICENSE file for details.
