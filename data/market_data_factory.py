# ====================================
# market_data_factory.py
# ====================================

from utils.runtime_mode import (

    RUNTIME_MODE,

    SIMULATION,

    PAPER,

    LIVE
)

from utils.logger import (
    SystemLogger
)

from data.fake_market_generator import (
    SimulationMarketGenerator
)

from data.alpaca_market_data_service import (
    AlpacaMarketDataService
)


logger = (
    SystemLogger()
)


# ====================================
# CREATE MARKET DATA SERVICE
# ====================================

def create_market_data_service(

    market_state,

    event_bus
):

    logger.warning(

        f"Creating Market Data Service | "

        f"Mode={RUNTIME_MODE}"
    )

    if RUNTIME_MODE == SIMULATION:

        logger.warning(
            "Using Simulation Market Data"
        )

        return SimulationMarketGenerator(

            market_state=
            market_state,

            event_bus=
            event_bus
        )

    if RUNTIME_MODE in [

        PAPER,

        LIVE
    ]:

        logger.warning(
            "Using Alpaca WebSocket Market Data"
        )

        return AlpacaMarketDataService(

            market_state=
            market_state,

            event_bus=
            event_bus
        )

    raise RuntimeError(

        f"Unsupported Runtime Mode For Market Data | "

        f"{RUNTIME_MODE}"
    )