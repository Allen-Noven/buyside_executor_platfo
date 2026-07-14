# ====================================
# constants.py
# ====================================


# ====================================
# ORDER SIDES
# ====================================

BUY = "BUY"

SELL = "SELL"


# ====================================
# EXECUTION STRATEGIES
# ====================================

TWAP = "TWAP"

VWAP = "VWAP"

POV = "POV"


# ====================================
# RUNTIME MODES
# ====================================

SIMULATION = "SIMULATION"

PAPER = "PAPER"

LIVE = "LIVE"

BACKTEST = "BACKTEST"


# ====================================
# ENVIRONMENTS
# ====================================

DEVELOPMENT = "DEVELOPMENT"

STAGING = "STAGING"

PRODUCTION = "PRODUCTION"


# ====================================
# ORDER STATUS
# ====================================

PENDING = "PENDING"

RUNNING = "RUNNING"

PARTIALLY_FILLED = "PARTIALLY_FILLED"

COMPLETED = "COMPLETED"

CANCELLED = "CANCELLED"

REJECTED = "REJECTED"

FAILED = "FAILED"

HALTED = "HALTED"


# ====================================
# SYSTEM STATUS
# ====================================

SYSTEM_RUNNING = "SYSTEM_RUNNING"

SYSTEM_HALTED = "SYSTEM_HALTED"

SYSTEM_ERROR = "SYSTEM_ERROR"

SYSTEM_WARNING = "SYSTEM_WARNING"


# ====================================
# MARKET SESSIONS
# ====================================

PREMARKET = "PREMARKET"

REGULAR = "REGULAR"

AFTERHOURS = "AFTERHOURS"

CLOSED = "CLOSED"


# ====================================
# RISK LEVELS
# ====================================

LOW = "LOW"

MEDIUM = "MEDIUM"

HIGH = "HIGH"


# ====================================
# GENERAL EVENT TYPES
# ====================================

MARKET_UPDATE_EVENT = "MARKET_UPDATE_EVENT"

ORDER_SUBMITTED_EVENT = "ORDER_SUBMITTED_EVENT"

ORDER_FILLED_EVENT = "ORDER_FILLED_EVENT"

ORDER_CANCELLED_EVENT = "ORDER_CANCELLED_EVENT"

POSITION_UPDATE_EVENT = "POSITION_UPDATE_EVENT"

RISK_ALERT_EVENT = "RISK_ALERT_EVENT"

LIQUIDITY_ALERT_EVENT = "LIQUIDITY_ALERT_EVENT"

KILL_SWITCH_EVENT = "KILL_SWITCH_EVENT"

SYSTEM_ERROR_EVENT = "SYSTEM_ERROR_EVENT"

SYSTEM_WARNING_EVENT = "SYSTEM_WARNING_EVENT"


# ====================================
# MARKET DATA EVENTS
# ====================================

MARKET_DATA_CONNECTED = "MARKET_DATA_CONNECTED"

MARKET_DATA_DISCONNECTED = "MARKET_DATA_DISCONNECTED"

MARKET_DATA_ERROR = "MARKET_DATA_ERROR"

MARKET_DATA_SUBSCRIBED = "MARKET_DATA_SUBSCRIBED"

MARKET_DATA_UNSUBSCRIBED = "MARKET_DATA_UNSUBSCRIBED"


# ====================================
# EXECUTION EVENTS
# ====================================

CHILD_ORDER_CREATED = "CHILD_ORDER_CREATED"

CHILD_ORDER_FILLED = "CHILD_ORDER_FILLED"

EXECUTION_STARTED = "EXECUTION_STARTED"

EXECUTION_COMPLETED = "EXECUTION_COMPLETED"


# ====================================
# POSITION MODES
# ====================================

LIVE_POSITIONS = "LIVE_POSITIONS"

RUNTIME_POSITIONS = "RUNTIME_POSITIONS"


# ====================================
# BROKER TYPES
# ====================================

ALPACA = "ALPACA"

SIMULATION_BROKER = "SIMULATION_BROKER"

REPLAY_BROKER = "REPLAY_BROKER"


# ====================================
# RECONCILIATION EVENTS
# ====================================

BROKER_POSITION_UPDATE_EVENT = "BROKER_POSITION_UPDATE_EVENT"

POSITION_MISMATCH_EVENT = "POSITION_MISMATCH_EVENT"

RECONCILIATION_COMPLETED_EVENT = "RECONCILIATION_COMPLETED_EVENT"
# ====================================
# PARENT ORDER EVENTS
# ====================================

PARENT_ORDER_SPLIT = "PARENT_ORDER_SPLIT"

PARENT_ORDER_PROGRESS = "PARENT_ORDER_PROGRESS"

PARENT_ORDER_COMPLETED = "PARENT_ORDER_COMPLETED"

PARENT_ORDER_HALTED = "PARENT_ORDER_HALTED"