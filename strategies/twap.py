# ====================================
# twap.py
# ====================================

import math

from utils.logger import (
    SystemLogger
)


class TWAPStrategy:

    def __init__(

        self,

        total_qty,

        total_minutes,

        slices,

        market_state=None

    ):

        # ====================================
        # LOGGER
        # ====================================

        self.logger = (
            SystemLogger()
        )


        # ====================================
        # EXECUTION TARGET
        # ====================================

        self.total_qty = (
            total_qty
        )

        self.remaining_qty = (
            total_qty
        )

        self.executed_qty = 0


        # ====================================
        # SCHEDULING
        # ====================================

        self.total_minutes = (
            total_minutes
        )

        self.slices = slices


        # ====================================
        # MARKET STATE
        # ====================================

        self.market_state = (
            market_state
        )


    # ====================================
    # DYNAMIC INTERVAL
    # ====================================

    def get_dynamic_interval(self):

        base_interval = (

            self.total_minutes
            / self.slices
        )


        if self.market_state is None:

            return base_interval


        volatility = (
            self.market_state.volatility
        )


        if volatility is None:

            return base_interval


        # ====================================
        # HIGH VOLATILITY
        # ====================================

        if volatility > 0.05:

            return base_interval * 1.5


        # ====================================
        # LOW VOLATILITY
        # ====================================

        elif volatility < 0.01:

            return base_interval * 0.8


        return base_interval


    # ====================================
    # GENERATE SCHEDULE
    # ====================================

    def generate_schedule(self):

        schedule = []


        # ====================================
        # BASE CHILD QTY
        # ====================================

        child_qty = (

            self.total_qty
            // self.slices
        )


        remainder = (

            self.total_qty
            % self.slices
        )


        # ====================================
        # DYNAMIC INTERVAL
        # ====================================

        interval = (
            self.get_dynamic_interval()
        )


        # ====================================
        # BUILD SCHEDULE
        # ====================================

        for i in range(self.slices):

            qty = child_qty


            # ====================================
            # DISTRIBUTE REMAINDER
            # ====================================

            if i < remainder:

                qty += 1


            schedule.append({

                "slice_id":
                i + 1,

                "qty":
                qty,

                "time_offset":
                round(

                    interval * i,

                    2
                )
            })


        self.logger.info(

            f"TWAP Schedule Generated | "

            f"{self.slices} slices | "

            f"{self.total_qty} shares"
        )


        return schedule


    # ====================================
    # UPDATE EXECUTION
    # ====================================

    def update_execution(

        self,

        filled_qty

    ):

        self.executed_qty += (
            filled_qty
        )

        self.remaining_qty -= (
            filled_qty
        )


    # ====================================
    # EXECUTION COMPLETE
    # ====================================

    def is_complete(self):

        return self.remaining_qty <= 0


    # ====================================
    # EXECUTION SUMMARY
    # ====================================

    def get_summary(self):

        completion = 0

        if self.total_qty > 0:

            completion = round(

                (

                    self.executed_qty
                    / self.total_qty

                ) * 100,

                2
            )


        return {

            "strategy":
            "TWAP",

            "total_qty":
            self.total_qty,

            "executed_qty":
            self.executed_qty,

            "remaining_qty":
            self.remaining_qty,

            "completion_percentage":
            completion,

            "slices":
            self.slices,

            "total_minutes":
            self.total_minutes
        }
