# ====================================
# broker_position_service.py
# ====================================

import threading
import copy

from alpaca.trading.client import (
    TradingClient
)

from utils.logger import (
    SystemLogger
)

from utils.helpers import (

    format_price,

    get_current_timestamp
)

from utils.config import (

    API_KEY,

    SECRET_KEY,

    PAPER_TRADING
)

from utils.constants import (

    ALPACA,

    SYSTEM_RUNNING,

    SYSTEM_ERROR,

    BROKER_POSITION_UPDATE_EVENT
)


class BrokerPositionService:


    # ====================================
    # INIT
    # ====================================

    def __init__(

        self,

        event_bus=None
    ):

        self.logger = (
            SystemLogger()
        )

        self.event_bus = (
            event_bus
        )

        self.position_lock = (
            threading.Lock()
        )

        self.broker_name = (
            ALPACA
        )

        self.status = (
            SYSTEM_RUNNING
        )

        self.last_sync_time = None

        self.positions = {}

        self.trading_client = (

            TradingClient(

                API_KEY,

                SECRET_KEY,

                paper=PAPER_TRADING
            )
        )

        self.logger.info(
            "Broker Position Service Initialized"
        )


    # ====================================
    # FETCH BROKER POSITIONS
    # ====================================

    def fetch_positions(self):

        try:

            broker_positions = (

                self.trading_client
                .get_all_positions()
            )

            formatted_positions = {}

            # ====================================
            # FORMAT POSITIONS
            # ====================================

            for position in broker_positions:

                symbol = (
                    position.symbol
                )

                qty = float(
                    position.qty
                )

                avg_price = float(

                    position.avg_entry_price
                )

                market_value = float(
                    position.market_value
                )

                unrealized_pl = float(

                    position.unrealized_pl
                )

                formatted_positions[
                    symbol
                ] = {

                    "symbol":
                    symbol,

                    "qty":
                    qty,

                    "avg_price":
                    format_price(
                        avg_price
                    ),

                    "market_value":
                    format_price(
                        market_value
                    ),

                    "unrealized_pl":
                    format_price(
                        unrealized_pl
                    )
                }

            # ====================================
            # UPDATE CACHE
            # ====================================

            with self.position_lock:

                self.positions = (
                    formatted_positions
                )

                self.last_sync_time = (
                    get_current_timestamp()
                )

                self.status = (
                    SYSTEM_RUNNING
                )

            positions_snapshot = (
                self.snapshot_positions()
            )

            # ====================================
            # PUBLISH EVENT
            # ====================================

            if self.event_bus:

                self.event_bus.publish(

                    BROKER_POSITION_UPDATE_EVENT,

                    positions_snapshot
                )

            self.logger.info(

                f"Broker Positions Synced | "

                f"{len(positions_snapshot)} "

                f"positions loaded"
            )

            return positions_snapshot

        except Exception as error:

            with self.position_lock:

                self.status = (
                    SYSTEM_ERROR
                )

            self.logger.error(

                f"Broker Position Sync Failed | "

                f"{error}"
            )

            return {}


    # ====================================
    # SNAPSHOT POSITIONS
    # ====================================

    def snapshot_positions(self):

        with self.position_lock:

            return copy.deepcopy(
                self.positions
            )


    # ====================================
    # GET POSITION
    # ====================================

    def get_position(

        self,

        symbol
    ):

        with self.position_lock:

            return copy.deepcopy(

                self.positions.get(
                    symbol
                )
            )


    # ====================================
    # GET ALL POSITIONS
    # ====================================

    def get_all_positions(self):

        return self.snapshot_positions()


    # ====================================
    # GET TOTAL MARKET VALUE
    # ====================================

    def get_total_market_value(self):

        positions = (
            self.snapshot_positions()
        )

        total_market_value = 0

        for position in positions.values():

            total_market_value += abs(

                position[
                    "market_value"
                ]
            )

        return format_price(
            total_market_value
        )


    # ====================================
    # GET TOTAL UNREALIZED PNL
    # ====================================

    def get_total_unrealized_pnl(self):

        positions = (
            self.snapshot_positions()
        )

        total_unrealized_pnl = 0

        for position in positions.values():

            total_unrealized_pnl += (

                position[
                    "unrealized_pl"
                ]
            )

        return format_price(
            total_unrealized_pnl
        )


    # ====================================
    # GET LAST SYNC TIME
    # ====================================

    def get_last_sync_time(self):

        with self.position_lock:

            return self.last_sync_time


    # ====================================
    # GET SERVICE STATUS
    # ====================================

    def get_status(self):

        with self.position_lock:

            return self.status


    # ====================================
    # REFRESH POSITIONS
    # ====================================

    def refresh(self):

        self.logger.info(
            "Refreshing broker positions..."
        )

        return self.fetch_positions()


    # ====================================
    # SHOW POSITIONS
    # ====================================

    def show_positions(self):

        positions = (
            self.snapshot_positions()
        )

        self.logger.warning(

            "========== "
            "BROKER POSITIONS "
            "=========="
        )

        for symbol, position in positions.items():

            self.logger.info(

                f"{symbol} | "

                f"Qty={position['qty']} | "

                f"Avg Price={position['avg_price']} | "

                f"Market Value={position['market_value']} | "

                f"Unrealized PnL={position['unrealized_pl']}"
            )

        self.logger.info(

            f"Total Market Value = "
            f"{self.get_total_market_value()}"
        )

        self.logger.info(

            f"Total Unrealized PnL = "
            f"{self.get_total_unrealized_pnl()}"
        )

        self.logger.info(

            f"Last Sync = "
            f"{self.get_last_sync_time()}"
        )