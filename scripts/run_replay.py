# ====================================
# run_replay.py
# ====================================

from utils.logger import (
    SystemLogger
)

from utils.config import (
    REPLAY_DATA_PATH
)

from portfolio.runtime_positions import (
    RuntimePositions
)

from portfolio.portfolio_state import (
    PortfolioState
)

from execution.execution_service import (
    ExecutionService
)

from execution.oms.fake_oms import (
    FakeOMS
)

from data.replay import (
    ReplayMarket
)

from analytics.pnl_tracker import (
    PnLTracker
)

from analytics.trade_blotter import (
    TradeBlotter
)

from data.market_event_bus import (
    MarketEventBus
)

from core.market_state import (
    MarketState
)


# ====================================
# LOGGER
# ====================================

logger = (
    SystemLogger()
)


# ====================================
# RUN REPLAY
# ====================================

def run_replay():

    logger.warning(
        "Starting Replay Runtime..."
    )

    # ====================================
    # MARKET STATE
    # ====================================

    market_state = (
        MarketState()
    )

    # ====================================
    # EVENT BUS
    # ====================================

    event_bus = (
        MarketEventBus()
    )

    # ====================================
    # OMS
    # ====================================

    oms = (
        FakeOMS()
    )

    logger.info(
        "Replay OMS Initialized"
    )

    # ====================================
    # EXECUTION SERVICE
    # ====================================

    execution_service = (

        ExecutionService(

            market_state=
            market_state,

            event_bus=
            event_bus,

            oms=
            oms
        )
    )

    logger.info(
        "Execution Service Initialized"
    )

    # ====================================
    # RUNTIME POSITIONS
    # ====================================

    runtime_positions = (
        RuntimePositions()
    )

    portfolio_state = (
        PortfolioState(
            runtime_positions
        )
    )

    # ====================================
    # ANALYTICS
    # ====================================

    pnl_tracker = (
        PnLTracker()
    )

    trade_blotter = (
        TradeBlotter()
    )

    logger.info(
        "Analytics Initialized"
    )

    # ====================================
    # REPLAY MARKET
    # ====================================

    replay_market = (

        ReplayMarket(
            REPLAY_DATA_PATH
        )
    )

    logger.info(
        "Replay Data Loaded"
    )

    # ====================================
    # REPLAY LOOP
    # ====================================

    logger.warning(
        "Replay Started"
    )

    for market_event in (

        replay_market.stream_market()
    ):

        try:

            # ====================================
            # UPDATE MARKET STATE
            # ====================================

            market_state.last_price = (

                market_event.get(
                    "price"
                )
            )

            market_state.last_symbol = (

                market_event.get(
                    "symbol"
                )
            )

            # ====================================
            # LOG MARKET EVENT
            # ====================================

            logger.info(

                f"Replay Tick | "

                f"{market_event}"
            )

            # ====================================
            # UPDATE PORTFOLIO
            # ====================================

            portfolio_state.get_portfolio_summary()

        except Exception as error:

            logger.error(

                f"Replay Event Failed | "

                f"{error}"
            )

    # ====================================
    # REPLAY COMPLETE
    # ====================================

    logger.warning(
        "Replay Completed"
    )

    # ====================================
    # FINAL REPORTS
    # ====================================

    runtime_positions.show_positions()

    portfolio_state.show_portfolio_summary()

    trade_blotter.generate_report()


# ====================================
# MAIN
# ====================================

if __name__ == "__main__":

    run_replay()