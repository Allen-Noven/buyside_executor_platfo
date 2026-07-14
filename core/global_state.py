# ====================================
# global_state.py
# ====================================

from core.system_state import (
    SystemState
)

from utils.logger import (
    SystemLogger
)


# ====================================
# LOGGER
# ====================================

logger = (
    SystemLogger()
)

# ====================================
# GLOBAL SYSTEM STATE
# ====================================

system_state = (
    SystemState()
)

# ====================================
# STARTUP LOG
# ====================================

logger.info(
    "Global System State Initialized"
)
