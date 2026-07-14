# ====================================
# config.py
# ====================================

import os


# ====================================
# ENVIRONMENT CONFIG
# ====================================

ENVIRONMENT = os.getenv(
    "ENVIRONMENT",
    "DEVELOPMENT"
).upper()


# ====================================
# DATA MODE
# ====================================

DATA_MODE = os.getenv(
    "DATA_MODE",
    "SIMULATION"
).upper()

# SIMULATION
# PAPER
# LIVE
# BACKTEST


# ====================================
# PAPER TRADING
# ====================================

PAPER_TRADING = True


# ====================================
# TIMEZONE CONFIG
# ====================================

MARKET_TIMEZONE = "US/Eastern"


# ====================================
# ALPACA API CONFIG
# ====================================

API_KEY = os.getenv(
    "ALPACA_API_KEY"
)

SECRET_KEY = os.getenv(
    "ALPACA_SECRET_KEY"
)

ALPACA_BASE_URL = os.getenv(
    "ALPACA_BASE_URL",
    "https://paper-api.alpaca.markets"
)


# ====================================
# ALPACA MARKET DATA CONFIG
# ====================================

ALPACA_DATA_FEED = os.getenv(
    "ALPACA_DATA_FEED",
    "IEX"
).upper()

# IEX: good for demo / basic data
# SIP: fuller market data, may require subscription


# ====================================
# FINNHUB CONFIG
# ====================================

FINNHUB_API_KEY = os.getenv(
    "FINNHUB_API_KEY"
)

NEWS_PROVIDER = os.getenv(
    "NEWS_PROVIDER",
    "finnhub"
)


# ====================================
# DEEPSEEK CONFIG
# ====================================

DEEPSEEK_API_KEY = os.getenv(
    "DEEPSEEK_API_KEY"
)


# ====================================
# EMAIL CONFIG
# ====================================

EMAIL_SENDER = os.getenv(
    "EMAIL_SENDER"
)

EMAIL_PASSWORD = os.getenv(
    "EMAIL_PASSWORD"
)

PM_EMAIL = os.getenv(
    "PM_EMAIL"
)

TRADER_EMAIL = os.getenv(
    "TRADER_EMAIL"
)


# ====================================
# SYSTEM CONFIG
# ====================================

SYSTEM_NAME = "Allen Execution Platform"

LOG_LEVEL = os.getenv(
    "LOG_LEVEL",
    "INFO"
)

ENABLE_DASHBOARD = True

ENABLE_EMAIL_ALERTS = True


# ====================================
# TRADING CONFIG
# ====================================

DEFAULT_SYMBOL = os.getenv(
    "DEFAULT_SYMBOL",
    "NVDA"
)

DEFAULT_MARKET_DATA_SYMBOLS = [

    "NVDA",

    "AAPL",

    "MSFT"
]

# Backward compatibility
MARKET_DATA_SYMBOLS = DEFAULT_MARKET_DATA_SYMBOLS

WATCHLIST = DEFAULT_MARKET_DATA_SYMBOLS

ALLOW_DYNAMIC_SYMBOL_SUBSCRIPTION = True

DEFAULT_ORDER_QTY = 1


# ====================================
# EXECUTION CONFIG
# ====================================

EXECUTION_INTERVAL = 5

DEFAULT_PARTICIPATION = 0.10

DEFAULT_EXECUTION_STRATEGY = "TWAP"

MAX_CONCURRENT_ORDERS = 5


# ====================================
# STRATEGY CONFIG
# ====================================

TWAP_DEFAULT_SLICES = 5

VWAP_LOOKBACK_MINUTES = 30

POV_MAX_PARTICIPATION = 0.10


# ====================================
# RISK CONFIG
# ====================================

MAX_ORDER_SIZE = 10

MAX_POSITION_SIZE = 100

MAX_NOTIONAL = 100000

MAX_PARTICIPATION = 0.20

MAX_DAILY_LOSS = 5000


# ====================================
# LIQUIDITY CONFIG
# ====================================

SPREAD_THRESHOLD = 0.05

MIN_VOLUME = 1000

MIN_LIQUIDITY_SCORE = 50


# ====================================
# TRANSACTION COST CONFIG
# ====================================

COMMISSION_PER_SHARE = 0.005

MIN_COMMISSION = 1.0

SLIPPAGE_BPS = 2

SPREAD_COST_BPS = 1


# ====================================
# PORTFOLIO CONFIG
# ====================================

ENABLE_POSITION_RECONCILIATION = True

POSITION_SYNC_INTERVAL = 60


# ====================================
# MARKET DATA CONFIG
# ====================================

REALTIME_REFRESH_RATE = 1

MARKET_DATA_RECONNECT_INTERVAL = 5

USE_WEBSOCKET_MARKET_DATA = True


# ====================================
# API CONFIG
# ====================================

API_HOST = "0.0.0.0"

API_PORT = 8000

ENABLE_WEBSOCKET = True


# ====================================
# DASHBOARD CONFIG
# ====================================

DASHBOARD_TITLE = "Allen's Smart Execution System"

DASHBOARD_REFRESH_RATE = 2


# ====================================
# REPORT CONFIG
# ====================================

REPORTS_DIR = "reports/"

SAVE_TRADE_BLOTTER = True


# ====================================
# TEST / REPLAY CONFIG
# ====================================

REPLAY_DATA_PATH = "data/nvda_data.csv"


# ====================================
# FEATURE FLAGS
# ====================================

ENABLE_AI_MODULES = False

ENABLE_REPLAY_MODE = True

ENABLE_FAKE_MARKET = True

FAKE_MARKET_INTERVAL = 1