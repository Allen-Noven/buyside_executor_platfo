# ====================================
# fill_tracker.py
# ====================================

from utils.helpers import (

    get_current_time,

    format_price,

    calculate_notional
)

from utils.logger import (
    SystemLogger
)


class FillTracker:

    def __init__(self):

        # ====================================
        # LOGGER
        # ====================================

        self.logger = (
            SystemLogger()
        )


        # ====================================
        # STORE FILLS
        # ====================================

        self.fills = []


    # ====================================
    # RECORD EXECUTION FILL
    # ====================================

    def record_fill(

        self,

        order_id,

        symbol,

        qty,

        fill_price,

        status,

        side=None,

        strategy=None

    ):

        fill_record = {

            "timestamp":
            get_current_time(),

            "order_id":
            order_id,

            "symbol":
            symbol,

            "side":
            side,

            "strategy":
            strategy,

            "qty":
            qty,

            "fill_price":
            format_price(fill_price),

            "notional":
            format_price(

                calculate_notional(
                    qty,
                    fill_price
                )
            ),

            "status":
            status
        }


        # ====================================
        # STORE FILL
        # ====================================

        self.fills.append(
            fill_record
        )


        self.logger.info(

            f"Fill Recorded | "

            f"{symbol} | "

            f"{qty} @ "

            f"{fill_price}"
        )


    # ====================================
    # GET FILLS
    # ====================================

    def get_fills(self):

        return self.fills


    # ====================================
    # GET RECENT FILLS
    # ====================================

    def get_recent_fills(

        self,

        limit=10

    ):

        return self.fills[-limit:]


    # ====================================
    # FILTER BY SYMBOL
    # ====================================

    def filter_by_symbol(

        self,

        symbol

    ):

        return [

            fill

            for fill in self.fills

            if fill["symbol"] == symbol
        ]


    # ====================================
    # FILTER BY STATUS
    # ====================================

    def filter_by_status(

        self,

        status

    ):

        return [

            fill

            for fill in self.fills

            if fill["status"] == status
        ]


    # ====================================
    # TOTAL FILLED QTY
    # ====================================

    def get_total_filled_qty(self):

        return sum(

            fill["qty"]

            for fill in self.fills
        )


    # ====================================
    # TOTAL NOTIONAL
    # ====================================

    def get_total_notional(self):

        total_notional = sum(

            fill["notional"]

            for fill in self.fills
        )

        return format_price(
            total_notional
        )


    # ====================================
    # AVERAGE FILL PRICE
    # ====================================

    def get_average_fill_price(self):

        total_qty = (
            self.get_total_filled_qty()
        )

        if total_qty == 0:

            return 0


        weighted_sum = sum(

            fill["fill_price"]
            *
            fill["qty"]

            for fill in self.fills
        )


        return format_price(

            weighted_sum
            / total_qty
        )


    # ====================================
    # GET SUMMARY
    # ====================================

    def get_summary(self):

        return {

            "total_fills":
            len(self.fills),

            "total_qty":
            self.get_total_filled_qty(),

            "total_notional":
            self.get_total_notional(),

            "average_fill_price":
            self.get_average_fill_price()
        }


    # ====================================
    # SHOW FILLS
    # ====================================

    def show_fills(self):

        print(

            "\n========== FILL REPORT ==========\n"
        )

        for fill in self.fills:

            print(fill)

        print(

            "\n=================================\n"
        )


    # ====================================
    # SHOW SUMMARY
    # ====================================

    def show_summary(self):

        summary = (
            self.get_summary()
        )

        print(

            "\n========== FILL SUMMARY ==========\n"
        )

        print(

            f"Total Fills: "
            f"{summary['total_fills']}"
        )

        print(

            f"Total Filled Qty: "
            f"{summary['total_qty']}"
        )

        print(

            f"Average Fill Price: "
            f"{summary['average_fill_price']}"
        )

        print(

            f"Total Notional: "
            f"{summary['total_notional']}"
        )

        print(

            "\n==================================\n"
        )