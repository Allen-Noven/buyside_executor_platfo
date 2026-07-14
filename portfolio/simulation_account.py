# ====================================
# simulation_account.py
# ====================================

import threading

from utils.logger import (
    SystemLogger
)

from utils.helpers import (
    format_price
)

from utils.constants import (
    BUY,
    SELL
)


class SimulationAccount:


    # ====================================
    # INIT
    # ====================================

    def __init__(

        self,

        initial_cash=100000
    ):

        self.logger = (
            SystemLogger()
        )

        self.account_lock = (
            threading.Lock()
        )

        self.initial_cash = float(
            initial_cash
        )

        self.cash = float(
            initial_cash
        )

        self.buying_power = float(
            initial_cash
        )

        self.equity = float(
            initial_cash
        )

        self.realized_pnl = 0.0

        self.unrealized_pnl = 0.0

        self.total_buys = 0.0

        self.total_sells = 0.0

        self.total_commission = 0.0

        self.total_notional_traded = 0.0

        self.trade_count = 0

        self.logger.info(
            "Simulation Account Initialized"
        )


    # ====================================
    # APPLY FILL
    # ====================================

    def apply_fill(

        self,

        symbol,

        side,

        qty,

        fill_price,

        commission=0
    ):

        qty = float(
            qty
        )

        fill_price = float(
            fill_price
        )

        commission = float(
            commission
        )

        notional = (
            qty
            *
            fill_price
        )

        with self.account_lock:

            if side == BUY:

                total_cost = (
                    notional
                    +
                    commission
                )

                if total_cost > self.cash:

                    raise RuntimeError(

                        f"Insufficient Simulation Cash | "

                        f"Required={total_cost} | "

                        f"Cash={self.cash}"
                    )

                self.cash -= total_cost

                self.total_buys += notional

            elif side == SELL:

                proceeds = (
                    notional
                    -
                    commission
                )

                self.cash += proceeds

                self.total_sells += notional

            else:

                raise ValueError(
                    f"Invalid Side | {side}"
                )

            self.total_commission += commission

            self.total_notional_traded += notional

            self.trade_count += 1

            self.buying_power = self.cash

            self.logger.info(

                f"Simulation Account Fill Applied | "

                f"{symbol} | "

                f"{side} | "

                f"{qty} @ {fill_price}"
            )


    # ====================================
    # MARK TO MARKET
    # ====================================

    def mark_to_market(

        self,

        total_market_value,

        total_unrealized_pnl
    ):

        with self.account_lock:

            self.unrealized_pnl = float(
                total_unrealized_pnl
            )

            self.equity = (

                self.cash

                +

                float(
                    total_market_value
                )
            )

            self.buying_power = self.cash


    # ====================================
    # SET REALIZED PNL
    # ====================================

    def set_realized_pnl(

        self,

        realized_pnl
    ):

        with self.account_lock:

            self.realized_pnl = float(
                realized_pnl
            )


    # ====================================
    # GET SNAPSHOT
    # ====================================

    def get_snapshot(self):

        with self.account_lock:

            return {

                "account_type":
                "SIMULATION",

                "initial_cash":
                format_price(
                    self.initial_cash
                ),

                "cash":
                format_price(
                    self.cash
                ),

                "buying_power":
                format_price(
                    self.buying_power
                ),

                "equity":
                format_price(
                    self.equity
                ),

                "realized_pnl":
                format_price(
                    self.realized_pnl
                ),

                "unrealized_pnl":
                format_price(
                    self.unrealized_pnl
                ),

                "total_buys":
                format_price(
                    self.total_buys
                ),

                "total_sells":
                format_price(
                    self.total_sells
                ),

                "total_commission":
                format_price(
                    self.total_commission
                ),

                "total_notional_traded":
                format_price(
                    self.total_notional_traded
                ),

                "trade_count":
                self.trade_count
            }


    # ====================================
    # RESET
    # ====================================

    def reset(self):

        with self.account_lock:

            self.cash = float(
                self.initial_cash
            )

            self.buying_power = float(
                self.initial_cash
            )

            self.equity = float(
                self.initial_cash
            )

            self.realized_pnl = 0.0

            self.unrealized_pnl = 0.0

            self.total_buys = 0.0

            self.total_sells = 0.0

            self.total_commission = 0.0

            self.total_notional_traded = 0.0

            self.trade_count = 0

        self.logger.warning(
            "Simulation Account Reset"
        )