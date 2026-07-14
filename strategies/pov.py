# ====================================
# pov.py
# ====================================

from utils.logger import (
    SystemLogger
)


class POVStrategy:

    def __init__(

        self,

        total_qty,

        participation_rate,

        market_state=None,

        max_child_qty=None

    ):

        # ====================================
        # LOGGER
        # ====================================

        self.logger = (
            SystemLogger()
        )


        # ====================================
        # ORDER TARGET
        # ====================================

        self.total_qty = total_qty

        self.remaining_qty = (
            total_qty
        )


        # ====================================
        # EXECUTION PARAMETERS
        # ====================================

        self.base_participation_rate = (
            participation_rate
        )

        self.participation_rate = (
            participation_rate
        )

        self.max_child_qty = (
            max_child_qty
        )


        # ====================================
        # MARKET STATE
        # ====================================

        self.market_state = (
            market_state
        )


        # ====================================
        # EXECUTION TRACKING
        # ====================================

        self.executed_qty = 0

        self.slice_id = 0


    # ====================================
    # DYNAMIC PARTICIPATION
    # ====================================

    def adjust_participation_rate(self):

        if self.market_state is None:

            return


        volatility = (
            self.market_state.volatility
        )

        liquidity_score = (
            self.market_state.liquidity_score
        )


        adjusted_rate = (
            self.base_participation_rate
        )


        # ====================================
        # HIGH VOLATILITY
        # ====================================

        if (

            volatility is not None
            and
            volatility > 0.05

        ):

            adjusted_rate *= 0.5


        # ====================================
        # LOW LIQUIDITY
        # ====================================

        if (

            liquidity_score is not None
            and
            liquidity_score < 50

        ):

            adjusted_rate *= 0.5


        self.participation_rate = (
            adjusted_rate
        )


    # ====================================
    # NEXT CHILD ORDER
    # ====================================

    def get_next_order(

        self,

        market_volume=None

    ):

        # ====================================
        # USE MARKET STATE
        # ====================================

        if (

            market_volume is None
            and
            self.market_state is not None

        ):

            market_volume = (

                self.market_state
                .current_volume
            )


        if (

            market_volume is None
            or
            market_volume <= 0

        ):

            self.logger.warning(

                "No valid market volume"
            )

            return None


        # ====================================
        # ADAPT PARTICIPATION
        # ====================================

        self.adjust_participation_rate()


        # ====================================
        # CALCULATE CHILD SIZE
        # ====================================

        child_qty = int(

            market_volume
            *
            self.participation_rate
        )


        # ====================================
        # MAX CHILD LIMIT
        # ====================================

        if self.max_child_qty:

            child_qty = min(

                child_qty,

                self.max_child_qty
            )


        # ====================================
        # REMAINING QTY
        # ====================================

        child_qty = min(

            child_qty,

            self.remaining_qty
        )


        # ====================================
        # EMPTY CHILD ORDER
        # ====================================

        if child_qty <= 0:

            return None


        # ====================================
        # UPDATE STATE
        # ====================================

        self.remaining_qty -= (
            child_qty
        )

        self.executed_qty += (
            child_qty
        )

        self.slice_id += 1


        # ====================================
        # BUILD CHILD ORDER
        # ====================================

        child_order = {

            "slice_id":
            self.slice_id,

            "qty":
            child_qty,

            "remaining_qty":
            self.remaining_qty,

            "participation_rate":
            round(

                self.participation_rate,

                4
            )
        }


        self.logger.info(

            f"POV Child Order | "

            f"Slice: {self.slice_id} | "

            f"Qty: {child_qty} | "

            f"Participation: "

            f"{self.participation_rate}"
        )


        return child_order


    # ====================================
    # EXECUTION COMPLETE
    # ====================================

    def is_complete(self):

        return self.remaining_qty <= 0


    # ====================================
    # EXECUTION SUMMARY
    # ====================================

    def get_summary(self):

        return {

            "total_qty":
            self.total_qty,

            "executed_qty":
            self.executed_qty,

            "remaining_qty":
            self.remaining_qty,

            "participation_rate":
            self.participation_rate
        }