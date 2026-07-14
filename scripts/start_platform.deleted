# ====================================
# start_platform.py
# ====================================

from utils.logger import (
    SystemLogger
)

from utils.config import (

    SYSTEM_NAME,

    DATA_MODE,

    ENABLE_DASHBOARD
)

from portfolio.position_manager import (
    PositionManager
)

from portfolio.runtime_positions import (
    RuntimePositions
)

from portfolio.portfolio_state import (
    PortfolioState
)

from portfolio.broker_position_service import (
    BrokerPositionService
)

from execution.execution_service import (
    ExecutionService
)

from data.real_time_data_loader import (
    RealTimeDataLoader
)

from dashboard.app import (
    start_dashboard
)


# ====================================
# LOGGER
# ====================================

logger = SystemLogger()


# ====================================
# START PLATFORM
# ====================================

def start_platform():

    logger.info(

        f"Starting {SYSTEM_NAME}"
    )


    # ====================================
    # INITIALIZE PORTFOLIO
    # ====================================

    logger.info(

        "Initializing Portfolio Layer..."
    )

    position_manager = (
        PositionManager()
    )

    runtime_positions = (
        RuntimePositions()
    )

    portfolio_state = (
        PortfolioState(
            position_manager
        )
    )


    # ====================================
    # INITIALIZE BROKER
    # ====================================

    logger.info(

        "Initializing Broker Services..."
    )

    broker_position_service = (
        BrokerPositionService()
    )

    broker_position_service.fetch_positions()


    # ====================================
    # INITIALIZE MARKET DATA
    # ====================================

    logger.info(

        "Initializing Market Data..."
    )

    market_data_loader = (
        RealTimeDataLoader()
    )


    # ====================================
    # INITIALIZE EXECUTION SERVICE
    # ====================================

    logger.info(

        "Initializing Execution Service..."
    )

    execution_service = (
        ExecutionService()
    )


    # ====================================
    # DASHBOARD
    # ====================================

    if ENABLE_DASHBOARD:

        logger.info(

            "Starting Dashboard..."
        )

        start_dashboard()


    # ====================================
    # START RUNTIME
    # ====================================

    logger.info(

        f"{SYSTEM_NAME} Running | "

        f"Mode: {DATA_MODE}"
    )

    execution_service.start()


# ====================================
# MAIN
# ====================================

if __name__ == "__main__":

    start_platform()