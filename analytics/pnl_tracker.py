# ====================================
# pnl_tracker.py
# ====================================

from utils.logger import (
    SystemLogger
)

from utils.constants import (

    BUY,

    SELL
)


class PnLTracker:

    def __init__(self):

        # ====================================
        # LOGGER
        # ====================================

        self.logger = (
            SystemLogger()
        )


        # ====================================
        # POSITION STATE
        # ====================================

        self.position = 0

        self.average_price = 0

        self.realized_pnl = 0

        self.unrealized_pnl = 0


        # ====================================
        # TRADE HISTORY
        # ====================================

        self.trade_history = []


    # ====================================
    # RECORD TRADE
    # ====================================

    def record_trade(

        self,

        side,

        qty,

        fill_price

    ):

        # ====================================
        # VALIDATE SIDE
        # ====================================

        if side not in [BUY, SELL]:

            self.logger.error(

                f"Invalid side: {side}"
            )

            return


        # ====================================
        # BUY
        # ====================================

        if side == BUY:

            total_cost = (

                self.average_price
                * self.position
            )

            new_cost = (

                fill_price * qty
            )

            self.position += qty


            if self.position > 0:

                self.average_price = (

                    total_cost + new_cost

                ) / self.position


        # ====================================
        # SELL
        # ====================================

        elif side == SELL:

            pnl = (

                fill_price
                - self.average_price

            ) * qty


            self.realized_pnl += pnl

            self.position -= qty


        # ====================================
        # STORE TRADE
        # ====================================

        trade = {

            "side":
            side,

            "qty":
            qty,

            "fill_price":
            round(fill_price, 4),

            "position":
            self.position,

            "average_price":
            round(
                self.average_price,
                4
            ),

            "realized_pnl":
            round(
                self.realized_pnl,
                2
            )
        }

        self.trade_history.append(
            trade
        )


        self.logger.info(

            f"Trade Recorded | "
            f"{side} {qty} @ {fill_price}"
        )


    # ====================================
    # UPDATE MARKET PRICE
    # ====================================

    def update_market_price(

        self,

        market_price

    ):

        self.unrealized_pnl = (

            market_price
            - self.average_price

        ) * self.position


    # ====================================
    # GET SUMMARY
    # ====================================

    def get_summary(self):

        total_pnl = (

            self.realized_pnl
            + self.unrealized_pnl
        )

        return {

            "position":
            self.position,

            "average_price":
            round(
                self.average_price,
                4
            ),

            "realized_pnl":
            round(
                self.realized_pnl,
                2
            ),

            "unrealized_pnl":
            round(
                self.unrealized_pnl,
                2
            ),

            "total_pnl":
            round(
                total_pnl,
                2
            )
        }


    # ====================================
    # GET TRADE HISTORY
    # ====================================

    def get_trade_history(self):

        return self.trade_history


    # ====================================
    # SHOW SUMMARY
    # ====================================

    def show_summary(self):

        summary = (
            self.get_summary()
        )

        print(

            "\n========== PNL SUMMARY ==========\n"
        )

        print(

            f"Position: "
            f"{summary['position']}"
        )

        print(

            f"Average Price: "
            f"{summary['average_price']}"
        )

        print(

            f"Realized PnL: "
            f"{summary['realized_pnl']}"
        )

        print(

            f"Unrealized PnL: "
            f"{summary['unrealized_pnl']}"
        )

        print(

            f"Total PnL: "
            f"{summary['total_pnl']}"
        )

        print(

            "\n=================================\n"
        )


    # ====================================
    # SHOW TRADE HISTORY
    # ====================================

    def show_trade_history(self):

        print(

            "\n========== TRADE HISTORY ==========\n"
        )

        for trade in self.trade_history:

            print(trade)

            print()

        print(

            "\n===================================\n"
        )