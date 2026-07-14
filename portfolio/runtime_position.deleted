# ====================================
# runtime_positions.py
# ====================================

from utils.logger import (
    SystemLogger
)

from utils.helpers import (

    calculate_notional,

    format_price
)


class RuntimePositions:


    # ====================================
    # INIT
    # ====================================

    def __init__(self):

        self.logger = (
            SystemLogger()
        )

        self.runtime_positions = {}


    # ====================================
    # UPDATE POSITION
    # ====================================

    def update_position(

        self,

        symbol,

        side,

        qty,

        fill_price
    ):

        if symbol not in (

            self.runtime_positions
        ):

            self.runtime_positions[
                symbol
            ] = {

                "qty": 0,

                "avg_price": 0,

                "market_value": 0
            }

        current_position = (

            self.runtime_positions[
                symbol
            ]
        )

        current_qty = (
            current_position["qty"]
        )

        current_avg_price = (

            current_position[
                "avg_price"
            ]
        )


        # ====================================
        # BUY
        # ====================================

        if side == "BUY":

            new_qty = (
                current_qty + qty
            )

            if new_qty == 0:

                new_avg_price = 0

            else:

                new_avg_price = (

                    (

                        current_qty
                        * current_avg_price

                    )

                    +

                    (

                        qty
                        * fill_price
                    )

                ) / new_qty


        # ====================================
        # SELL
        # ====================================

        else:

            new_qty = (
                current_qty - qty
            )

            new_avg_price = (
                current_avg_price
            )


        # ====================================
        # MARKET VALUE
        # ====================================

        market_value = (
            calculate_notional(

                new_qty,

                fill_price
            )
        )


        # ====================================
        # UPDATE RUNTIME BOOK
        # ====================================

        self.runtime_positions[
            symbol
        ] = {

            "qty": new_qty,

            "avg_price": format_price(
                new_avg_price
            ),

            "market_value": format_price(
                market_value
            )
        }


        # ====================================
        # LOG
        # ====================================

        self.logger.info(

            f"[RUNTIME] "

            f"Position Updated | "

            f"{symbol} | "

            f"Qty: {new_qty}"
        )


    # ====================================
    # GET POSITION
    # ====================================

    def get_position(

        self,

        symbol
    ):

        return self.runtime_positions.get(

            symbol,

            None
        )


    # ====================================
    # GET ALL POSITIONS
    # ====================================

    def get_all_positions(self):

        return self.runtime_positions


    # ====================================
    # GET TOTAL EXPOSURE
    # ====================================

    def get_total_exposure(self):

        total_exposure = 0

        for symbol in (

            self.runtime_positions
        ):

            total_exposure += abs(

                self.runtime_positions[
                    symbol
                ][
                    "market_value"
                ]
            )

        return format_price(
            total_exposure
        )


    # ====================================
    # RESET RUNTIME POSITIONS
    # ====================================

    def reset_positions(self):

        self.runtime_positions = {}

        self.logger.warning(

            "[RUNTIME] "

            "All runtime positions reset"
        )


    # ====================================
    # SHOW POSITIONS
    # ====================================

    def show_positions(self):

        print(

            "\n========== "
            "RUNTIME POSITIONS "
            "==========\n"
        )

        for symbol, position in (

            self.runtime_positions.items()
        ):

            print(

                f"{symbol} | "

                f"Qty: {position['qty']} | "

                f"Avg Price: "
                f"{position['avg_price']} | "

                f"Market Value: "
                f"{position['market_value']}"
            )

        print(

            "\nTotal Runtime Exposure: "

            f"{self.get_total_exposure()}"
        )

        print(

            "\n==============================="
            "===================\n"
        )