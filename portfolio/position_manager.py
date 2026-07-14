# ====================================
# position_manager.py
# ====================================

import threading
import copy

from utils.logger import (
    SystemLogger
)

from utils.helpers import (

    calculate_notional,

    format_price
)

from utils.constants import (

    BUY,

    SELL,

    MARKET_UPDATE_EVENT
)


class PositionManager:


    # ====================================
    # INIT
    # ====================================

    def __init__(

        self,

        event_bus=None,

        simulation_account=None
    ):

        self.logger = (
            SystemLogger()
        )

        self.position_lock = (
            threading.Lock()
        )

        self.positions = {}

        self.total_realized_pnl = 0

        self.total_unrealized_pnl = 0

        self.total_exposure = 0

        self.total_market_value = 0

        self.event_bus = (
            event_bus
        )

        self.simulation_account = (
            simulation_account
        )

        if self.event_bus:

            self.event_bus.subscribe(

                MARKET_UPDATE_EVENT,

                self.on_market_update
            )

        self.logger.info(
            "Position Manager Initialized"
        )


    # ====================================
    # MARKET UPDATE EVENT
    # ====================================

    def on_market_update(

        self,

        market_event
    ):

        try:

            symbol = (
                market_event[
                    "symbol"
                ]
            )

            market_price = (
                market_event[
                    "price"
                ]
            )

            self.mark_to_market(

                symbol=
                symbol,

                market_price=
                market_price
            )

        except Exception as error:

            self.logger.error(

                f"MTM Update Failed | "

                f"{error}"
            )


    # ====================================
    # CREATE POSITION
    # ====================================

    def create_position(

        self,

        symbol
    ):

        self.positions[
            symbol
        ] = {

            "symbol":
            symbol,

            "qty":
            0,

            "avg_price":
            0,

            "market_price":
            0,

            "market_value":
            0,

            "realized_pnl":
            0,

            "unrealized_pnl":
            0,

            "total_bought":
            0,

            "total_sold":
            0
        }


    # ====================================
    # UPDATE POSITION
    # ====================================

    def update_position(

        self,

        symbol,

        side,

        qty,

        fill_price,

        market_price=None
    ):

        symbol = symbol.upper()

        qty = float(
            qty
        )

        fill_price = float(
            fill_price
        )

        with self.position_lock:

            if symbol not in self.positions:

                self.create_position(
                    symbol
                )

            position = (
                self.positions[
                    symbol
                ]
            )

            current_qty = (
                position[
                    "qty"
                ]
            )

            current_avg_price = (
                position[
                    "avg_price"
                ]
            )

            realized_pnl = (
                position[
                    "realized_pnl"
                ]
            )

            if market_price is None:

                market_price = fill_price

            market_price = float(
                market_price
            )

            if side == BUY:

                if current_qty < 0:

                    closing_qty = min(

                        abs(
                            current_qty
                        ),

                        qty
                    )

                    pnl = (

                        current_avg_price

                        -

                        fill_price

                    ) * closing_qty

                    realized_pnl += pnl

                    new_qty = (
                        current_qty
                        +
                        qty
                    )

                    if new_qty > 0:

                        new_avg_price = (
                            fill_price
                        )

                    elif new_qty == 0:

                        new_avg_price = 0

                    else:

                        new_avg_price = (
                            current_avg_price
                        )

                else:

                    new_qty = (
                        current_qty
                        +
                        qty
                    )

                    total_cost = (

                        current_qty
                        *
                        current_avg_price

                    ) + (

                        qty
                        *
                        fill_price
                    )

                    if new_qty == 0:

                        new_avg_price = 0

                    else:

                        new_avg_price = (

                            total_cost

                            /

                            new_qty
                        )

                position[
                    "total_bought"
                ] += qty

            elif side == SELL:

                if current_qty > 0:

                    closing_qty = min(

                        current_qty,

                        qty
                    )

                    pnl = (

                        fill_price

                        -

                        current_avg_price

                    ) * closing_qty

                    realized_pnl += pnl

                    new_qty = (
                        current_qty
                        -
                        qty
                    )

                    if new_qty < 0:

                        new_avg_price = (
                            fill_price
                        )

                    elif new_qty == 0:

                        new_avg_price = 0

                    else:

                        new_avg_price = (
                            current_avg_price
                        )

                else:

                    new_qty = (
                        current_qty
                        -
                        qty
                    )

                    total_cost = (

                        abs(
                            current_qty
                        )

                        *

                        current_avg_price

                    ) + (

                        qty
                        *
                        fill_price
                    )

                    if abs(
                        new_qty
                    ) == 0:

                        new_avg_price = 0

                    else:

                        new_avg_price = (

                            total_cost

                            /

                            abs(
                                new_qty
                            )
                        )

                position[
                    "total_sold"
                ] += qty

            else:

                raise ValueError(
                    f"Invalid Side | {side}"
                )

            market_value = calculate_notional(

                new_qty,

                market_price
            )

            if new_qty > 0:

                unrealized_pnl = (

                    market_price

                    -

                    new_avg_price

                ) * new_qty

            elif new_qty < 0:

                unrealized_pnl = (

                    new_avg_price

                    -

                    market_price

                ) * abs(
                    new_qty
                )

            else:

                unrealized_pnl = 0

            self.positions[
                symbol
            ] = {

                "symbol":
                symbol,

                "qty":
                new_qty,

                "avg_price":
                format_price(
                    new_avg_price
                ),

                "market_price":
                format_price(
                    market_price
                ),

                "market_value":
                format_price(
                    market_value
                ),

                "realized_pnl":
                format_price(
                    realized_pnl
                ),

                "unrealized_pnl":
                format_price(
                    unrealized_pnl
                ),

                "total_bought":
                position[
                    "total_bought"
                ],

                "total_sold":
                position[
                    "total_sold"
                ]
            }

            self.recalculate_portfolio_locked()

        self.sync_simulation_account()

        self.logger.info(

            f"Position Updated | "

            f"{symbol} | "

            f"Qty={new_qty}"
        )


    # ====================================
    # MARK TO MARKET
    # ====================================

    def mark_to_market(

        self,

        symbol,

        market_price
    ):

        symbol = symbol.upper()

        market_price = float(
            market_price
        )

        with self.position_lock:

            if symbol not in self.positions:

                return

            position = (
                self.positions[
                    symbol
                ]
            )

            qty = (
                position[
                    "qty"
                ]
            )

            avg_price = (
                position[
                    "avg_price"
                ]
            )

            market_value = calculate_notional(

                qty,

                market_price
            )

            if qty > 0:

                unrealized_pnl = (

                    market_price
                    -
                    avg_price

                ) * qty

            elif qty < 0:

                unrealized_pnl = (

                    avg_price
                    -
                    market_price

                ) * abs(
                    qty
                )

            else:

                unrealized_pnl = 0

            position[
                "market_price"
            ] = format_price(
                market_price
            )

            position[
                "market_value"
            ] = format_price(
                market_value
            )

            position[
                "unrealized_pnl"
            ] = format_price(
                unrealized_pnl
            )

            self.recalculate_portfolio_locked()

        self.sync_simulation_account()


    # ====================================
    # RECALCULATE PORTFOLIO LOCKED
    # ====================================

    def recalculate_portfolio_locked(self):

        total_realized = 0

        total_unrealized = 0

        total_exposure = 0

        total_market_value = 0

        for position in self.positions.values():

            total_realized += (
                position[
                    "realized_pnl"
                ]
            )

            total_unrealized += (
                position[
                    "unrealized_pnl"
                ]
            )

            total_exposure += abs(
                position[
                    "market_value"
                ]
            )

            total_market_value += (
                position[
                    "market_value"
                ]
            )

        self.total_realized_pnl = format_price(
            total_realized
        )

        self.total_unrealized_pnl = format_price(
            total_unrealized
        )

        self.total_exposure = format_price(
            total_exposure
        )

        self.total_market_value = format_price(
            total_market_value
        )


    # ====================================
    # RECALCULATE PORTFOLIO
    # ====================================

    def recalculate_portfolio(self):

        with self.position_lock:

            self.recalculate_portfolio_locked()

        self.sync_simulation_account()


    # ====================================
    # SYNC SIMULATION ACCOUNT
    # ====================================

    def sync_simulation_account(self):

        if not self.simulation_account:

            return

        self.simulation_account.set_realized_pnl(
            self.total_realized_pnl
        )

        self.simulation_account.mark_to_market(

            total_market_value=
            self.total_market_value,

            total_unrealized_pnl=
            self.total_unrealized_pnl
        )


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

        symbol = symbol.upper()

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
    # GET PORTFOLIO SUMMARY
    # ====================================

    def get_portfolio_summary(self):

        with self.position_lock:

            summary = {

                "total_realized_pnl":
                self.total_realized_pnl,

                "total_unrealized_pnl":
                self.total_unrealized_pnl,

                "total_exposure":
                self.total_exposure,

                "total_market_value":
                self.total_market_value,

                "position_count":
                len(
                    self.positions
                )
            }

        if self.simulation_account:

            summary[
                "simulation_account"
            ] = self.simulation_account.get_snapshot()

        return summary


    # ====================================
    # RESET POSITIONS
    # ====================================

    def reset_positions(self):

        with self.position_lock:

            self.positions = {}

            self.total_realized_pnl = 0

            self.total_unrealized_pnl = 0

            self.total_exposure = 0

            self.total_market_value = 0

        if self.simulation_account:

            self.simulation_account.reset()

        self.logger.warning(
            "All Positions Reset"
        )