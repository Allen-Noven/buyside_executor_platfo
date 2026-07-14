# ====================================
# slippage_analyzer.py
# ====================================

from utils.helpers import (

    calculate_slippage,

    calculate_bps
)

from utils.logger import (
    SystemLogger
)

from utils.constants import (

    BUY,

    SELL
)


class SlippageAnalyzer:

    def __init__(self):

        # ====================================
        # LOGGER
        # ====================================

        self.logger = (
            SystemLogger()
        )


        # ====================================
        # EXECUTION RECORDS
        # ====================================

        self.records = []


    # ====================================
    # RECORD EXECUTION
    # ====================================

    def record_execution(

        self,

        symbol,

        side,

        qty,

        arrival_price,

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
        # CALCULATE SLIPPAGE
        # ====================================

        raw_slippage = (

            calculate_slippage(

                arrival_price,

                fill_price
            )
        )


        # ====================================
        # SELL SIDE ADJUSTMENT
        # ====================================

        if side == SELL:

            raw_slippage *= -1


        # ====================================
        # BPS
        # ====================================

        slippage_bps = (

            calculate_bps(

                arrival_price,

                fill_price
            )
        )

        if side == SELL:

            slippage_bps *= -1


        # ====================================
        # EXECUTION COST
        # ====================================

        execution_cost = (

            raw_slippage * qty
        )


        # ====================================
        # BUILD RECORD
        # ====================================

        record = {

            "symbol":
            symbol,

            "side":
            side,

            "qty":
            qty,

            "arrival_price":
            round(arrival_price, 4),

            "fill_price":
            round(fill_price, 4),

            "slippage":
            round(raw_slippage, 4),

            "slippage_bps":
            round(slippage_bps, 2),

            "execution_cost":
            round(execution_cost, 2)
        }


        # ====================================
        # STORE RECORD
        # ====================================

        self.records.append(
            record
        )


        self.logger.info(

            f"Slippage Recorded | "

            f"{symbol} | "

            f"{side} | "

            f"Slippage: "

            f"{round(raw_slippage, 4)}"
        )


    # ====================================
    # GET RECORDS
    # ====================================

    def get_records(self):

        return self.records


    # ====================================
    # GET SUMMARY
    # ====================================

    def get_summary(self):

        if len(self.records) == 0:

            return {

                "total_executions": 0,

                "average_slippage": 0,

                "average_bps": 0,

                "total_execution_cost": 0
            }


        total_slippage = sum(

            record["slippage"]

            for record in self.records
        )


        total_bps = sum(

            record["slippage_bps"]

            for record in self.records
        )


        total_execution_cost = sum(

            record["execution_cost"]

            for record in self.records
        )


        total_records = (
            len(self.records)
        )


        return {

            "total_executions":
            total_records,

            "average_slippage":
            round(
                total_slippage
                / total_records,
                4
            ),

            "average_bps":
            round(
                total_bps
                / total_records,
                2
            ),

            "total_execution_cost":
            round(
                total_execution_cost,
                2
            )
        }


    # ====================================
    # SHOW SUMMARY
    # ====================================

    def show_summary(self):

        summary = (
            self.get_summary()
        )

        print(

            "\n========== SLIPPAGE SUMMARY ==========\n"
        )

        print(

            f"Total Executions: "
            f"{summary['total_executions']}"
        )

        print(

            f"Average Slippage: "
            f"{summary['average_slippage']}"
        )

        print(

            f"Average BPS: "
            f"{summary['average_bps']}"
        )

        print(

            f"Execution Cost: "
            f"{summary['total_execution_cost']}"
        )

        print(

            "\n=======================================\n"
        )


    # ====================================
    # SHOW RECORDS
    # ====================================

    def show_records(self):

        print(

            "\n========== SLIPPAGE RECORDS ==========\n"
        )

        for record in self.records:

            print(record)

            print()

        print(

            "\n======================================\n"
        )