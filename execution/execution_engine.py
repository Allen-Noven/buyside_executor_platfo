# ====================================
# execution_engine.py
# ====================================

from core.parent_order import (
    ParentOrder
)

from data.replay import (
    MarketReplay
)

from data.real_time_data_loader import (
    RealTimeDataLoader
)

from runtime.runtime_context import (

    market_state,

    redis_state,

    event_bus,

    order_queue,

    execution_worker,

    start_worker
)

from utils.constants import (
    BUY
)

from utils.config import (

    DEFAULT_SYMBOL,

    DATA_MODE
)

from utils.logger import (
    SystemLogger
)


# ====================================
# START EXECUTION ENGINE
# ====================================

def start_execution_engine():

    # ====================================
    # LOGGER
    # ====================================

    logger = (
        SystemLogger()
    )

    logger.info(
        "Starting Execution Engine"
    )

    # ====================================
    # RESET ALERTS
    # ====================================

    redis_state.set_alerts([])

    # ====================================
    # MARKET DATA SOURCE
    # ====================================

    if DATA_MODE == "replay":

        market_data_source = (

            MarketReplay(

                data_path=
                "data/nvda_data.csv",

                market_state=
                market_state,

                event_bus=
                event_bus
            )
        )

    elif DATA_MODE == "live":

        market_data_source = (

            RealTimeDataLoader(

                market_state=
                market_state
            )
        )

    else:

        raise ValueError(

            f"Unsupported DATA_MODE: "

            f"{DATA_MODE}"
        )

    # ====================================
    # START MARKET DATA
    # ====================================

    print(

        "\nStarting Market Data Source...\n"
    )

    if DATA_MODE == "replay":

        print(
            "Replay Mode Enabled.\n"
        )

        market_data_source.run()

    elif DATA_MODE == "live":

        print(
            "Live Market Feed Enabled.\n"
        )

        market_data_source.run(
            DEFAULT_SYMBOL
        )

    # ====================================
    # INITIAL MARKET STATE
    # ====================================

    market_state.update(

        symbol=
        DEFAULT_SYMBOL,

        price=170,

        volume=50000,

        timestamp="09:30"
    )

    # ====================================
    # REDIS MARKET SNAPSHOT
    # ====================================

    redis_state.set_market_state(

        DEFAULT_SYMBOL,

        market_state.get_snapshot()
    )

    # ====================================
    # START WORKER
    # ====================================

    if not execution_worker.is_running():

        start_worker()

    # ====================================
    # CREATE PARENT ORDER
    # ====================================

    parent_order = (

        ParentOrder(

            symbol=
            DEFAULT_SYMBOL,

            side=
            BUY,

            quantity=
            5,

            strategy=
            "TWAP",

            arrival_price=
            market_state.current_price
        )
    )

    # ====================================
    # DISPLAY ORDER
    # ====================================

    parent_order.show()

    # ====================================
    # QUEUE ORDER
    # ====================================

    order_queue.submit_order(
        parent_order
    )

    # ====================================
    # EXECUTION STATUS
    # ====================================

    redis_state.set_execution_status(

        {

            "status":
            "RUNNING",

            "halted":
            False,

            "reason":
            None
        }
    )

    print(

        f"\nOrder Queued | "

        f"{parent_order.order_id}\n"
    )

    return {

        "status":
        "QUEUED",

        "order_id":
        parent_order.order_id
    }


# ====================================
# MAIN
# ====================================

if __name__ == "__main__":

    start_execution_engine()
