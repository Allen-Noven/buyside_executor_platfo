# ====================================
# replay.py
# ====================================

import time
import pandas as pd

from utils.logger import (
    SystemLogger
)

from utils.config import (
    EXECUTION_INTERVAL
)

from utils.constants import (
    MARKET_UPDATE_EVENT
)


class MarketReplay:

    def __init__(

        self,

        data_path,

        market_state,

        event_bus,

        replay_speed=1.0

    ):

        self.logger = (
            SystemLogger()
        )

        self.df = pd.read_csv(
            data_path,encoding="utf-8-sig"
        )
        self.df.columns = (self.df.columns.str.strip())
        print(self.df.columns)

        self.market_state = (
            market_state
        )

        self.event_bus = (
            event_bus
        )

        self.replay_speed = (
            replay_speed
        )

        self.running = False


    # ====================================
    # START REPLAY
    # ====================================

    def run(self):

        self.logger.info(
            "Starting Replay"
        )

        self.running = True

        for _, row in self.df.iterrows():

            if not self.running:

                break

            # ====================================
            # UPDATE MARKET STATE
            # ====================================

            self.market_state.update(

                price=row["close"],

                volume=row["volume"],

                timestamp=row["timestamp"],

                bid_price=row.get(
                    "bid_price"
                ),

                ask_price=row.get(
                    "ask_price"
                ),

                volatility=row.get(
                    "volatility"
                ),

                liquidity_score=row.get(
                    "liquidity_score"
                )
            )

            # ====================================
            # PUBLISH EVENT
            # ====================================

            self.event_bus.publish(

                MARKET_UPDATE_EVENT,

                self.market_state
            )

            self.logger.info(

                f"Replay Tick | "

                f"{self.market_state.current_price}"
            )

            time.sleep(

                EXECUTION_INTERVAL
                / self.replay_speed
            )


    # ====================================
    # STOP REPLAY
    # ====================================

    def stop(self):

        self.running = False
