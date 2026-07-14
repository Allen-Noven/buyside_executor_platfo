# ====================================
# execution_optimizer.py
# ====================================

from utils.logger import (
    SystemLogger
)

from utils.helpers import (
    format_price
)

from utils.config import (

    DEFAULT_PARTICIPATION,

    SPREAD_THRESHOLD
)


class ExecutionOptimizer:


    # ====================================
    # INIT
    # ====================================

    def __init__(self):

        self.logger = (
            SystemLogger()
        )

        self.current_participation = (
            DEFAULT_PARTICIPATION
        )


    # ====================================
    # OPTIMIZE PARTICIPATION
    # ====================================

    def optimize_participation(

        self,

        spread,

        volatility,

        liquidity_score
    ):

        participation = (
            DEFAULT_PARTICIPATION
        )


        # ====================================
        # WIDE SPREAD
        # ====================================

        if spread > SPREAD_THRESHOLD:

            participation *= 0.5

            self.logger.warning(

                "Wide spread detected | "

                "Reducing participation"
            )


        # ====================================
        # HIGH VOLATILITY
        # ====================================

        if volatility > 0.03:

            participation *= 0.7

            self.logger.warning(

                "High volatility detected | "

                "Reducing aggressiveness"
            )


        # ====================================
        # LOW LIQUIDITY
        # ====================================

        if liquidity_score < 50:

            participation *= 0.6

            self.logger.warning(

                "Low liquidity detected | "

                "Reducing participation"
            )


        # ====================================
        # FINAL CAP
        # ====================================

        participation = min(

            participation,

            0.20
        )

        participation = max(

            participation,

            0.01
        )

        self.current_participation = (
            participation
        )

        self.logger.info(

            f"Optimized Participation: "

            f"{participation}"
        )

        return participation


    # ====================================
    # OPTIMIZE CHILD ORDER SIZE
    # ====================================

    def optimize_child_order_size(

        self,

        parent_qty,

        volatility
    ):

        child_order_size = (
            parent_qty * 0.10
        )


        # ====================================
        # HIGH VOLATILITY
        # ====================================

        if volatility > 0.03:

            child_order_size *= 0.5

            self.logger.warning(

                "Reducing child order size "
                "due to volatility"
            )


        return max(

            round(child_order_size),

            1
        )


    # ====================================
    # OPTIMIZE EXECUTION_INTERVAL
    # ====================================

    def optimize_execution_interval(

        self,

        volatility
    ):

        execution_interval = 5


        # ====================================
        # HIGH VOLATILITY
        # ====================================

        if volatility > 0.03:

            execution_interval = 10

            self.logger.warning(

                "Increasing execution interval "
                "due to volatility"
            )


        return execution_interval


    # ====================================
    # GENERATE EXECUTION PROFILE
    # ====================================

    def generate_execution_profile(

        self,

        spread,

        volatility,

        liquidity_score,

        parent_qty
    ):

        profile = {

            "participation":

            self.optimize_participation(

                spread,

                volatility,

                liquidity_score
            ),

            "child_order_size":

            self.optimize_child_order_size(

                parent_qty,

                volatility
            ),

            "execution_interval":

            self.optimize_execution_interval(

                volatility
            )
        }

        self.logger.info(

            f"Execution Profile Generated | "

            f"{profile}"
        )

        return profile