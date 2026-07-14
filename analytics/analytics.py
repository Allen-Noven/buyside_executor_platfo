# ====================================
# analytics.py
# ====================================

from utils.logger import (
    SystemLogger
)


class ExecutionAnalytics:


    # ====================================
    # INIT
    # ====================================

    def __init__(

        self,

        event_bus=None,

        benchmark_engine=None
    ):

        # ====================================
        # LOGGER
        # ====================================

        self.logger = (
            SystemLogger()
        )

        # ====================================
        # EVENT BUS
        # ====================================

        self.event_bus = (
            event_bus
        )

        # ====================================
        # BENCHMARK ENGINE
        # ====================================

        self.benchmark_engine = (
            benchmark_engine
        )

        # ====================================
        # EXECUTION METRICS
        # ====================================

        self.total_executions = 0

        self.total_slippage = 0.0

        self.total_bps = 0.0

        self.total_execution_cost = 0.0

        # ====================================
        # POSITION METRICS
        # ====================================

        self.position = 0

        self.average_price = 0.0

        self.realized_pnl = 0.0

        self.unrealized_pnl = 0.0

        # ====================================
        # EXECUTION HISTORY
        # ====================================

        self.execution_history = []

        # ====================================
        # REGISTER EVENT HANDLERS
        # ====================================

        if self.event_bus:

            self.register_subscriptions()

        self.logger.info(
            "Execution Analytics Initialized"
        )


    # ====================================
    # REGISTER SUBSCRIPTIONS
    # ====================================

    def register_subscriptions(self):

        try:

            self.event_bus.subscribe(

                "EXECUTION_FILLED",

                self.on_execution_fill
            )

            self.logger.info(
                "Analytics Event Subscription Registered"
            )

        except Exception as error:

            self.logger.error(

                f"Analytics Subscription Failed | "

                f"{error}"
            )


    # ====================================
    # EXECUTION FILL EVENT
    # ====================================

    def on_execution_fill(

        self,

        payload
    ):

        try:

            # ====================================
            # EXTRACT DATA
            # ====================================

            symbol = payload.get(
                "symbol"
            )

            quantity = payload.get(
                "quantity",
                0
            )

            fill_price = payload.get(
                "fill_price",
                0
            )

            arrival_price = payload.get(
                "arrival_price",
                fill_price
            )

            side = payload.get(
                "side",
                "BUY"
            )

            execution_cost = payload.get(
                "execution_cost",
                0
            )

            # ====================================
            # CALCULATE SLIPPAGE
            # ====================================

            slippage = abs(

                fill_price -
                arrival_price
            )

            slippage_bps = 0

            if arrival_price > 0:

                slippage_bps = (

                    slippage /
                    arrival_price
                ) * 10000

            # ====================================
            # UPDATE EXECUTION METRICS
            # ====================================

            self.total_executions += 1

            self.total_slippage += slippage

            self.total_bps += slippage_bps

            self.total_execution_cost += (
                execution_cost
            )

            # ====================================
            # UPDATE POSITION
            # ====================================

            if side == "BUY":

                total_cost = (

                    self.average_price *
                    self.position
                )

                total_cost += (

                    fill_price *
                    quantity
                )

                self.position += quantity

                if self.position > 0:

                    self.average_price = (

                        total_cost /
                        self.position
                    )

            elif side == "SELL":

                realized = (

                    fill_price -
                    self.average_price
                ) * quantity

                self.realized_pnl += realized

                self.position -= quantity

            # ====================================
            # STORE EXECUTION
            # ====================================

            execution_record = {

                "symbol":
                symbol,

                "side":
                side,

                "quantity":
                quantity,

                "fill_price":
                fill_price,

                "arrival_price":
                arrival_price,

                "slippage":
                round(
                    slippage,
                    4
                ),

                "slippage_bps":
                round(
                    slippage_bps,
                    2
                ),

                "execution_cost":
                round(
                    execution_cost,
                    2
                )
            }

            self.execution_history.append(
                execution_record
            )

            # ====================================
            # LOG
            # ====================================

            self.logger.info(

                f"Analytics Updated | "

                f"{symbol} | "

                f"{side} | "

                f"Qty={quantity}"
            )

        except Exception as error:

            self.logger.error(

                f"Analytics Update Failed | "

                f"{error}"
            )


    # ====================================
    # UPDATE UNREALIZED PNL
    # ====================================

    def update_market_price(

        self,

        market_price
    ):

        try:

            if self.position == 0:

                self.unrealized_pnl = 0

                return

            self.unrealized_pnl = (

                market_price -
                self.average_price
            ) * self.position

        except Exception as error:

            self.logger.error(

                f"PnL Update Failed | "

                f"{error}"
            )


    # ====================================
    # GET EXECUTION SUMMARY
    # ====================================

    def get_execution_summary(self):

        avg_slippage = 0

        avg_bps = 0

        if self.total_executions > 0:

            avg_slippage = (

                self.total_slippage /
                self.total_executions
            )

            avg_bps = (

                self.total_bps /
                self.total_executions
            )

        return {

            "total_executions":
            self.total_executions,

            "average_slippage":
            round(
                avg_slippage,
                4
            ),

            "average_bps":
            round(
                avg_bps,
                2
            ),

            "total_execution_cost":
            round(
                self.total_execution_cost,
                2
            ),

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
            )
        }


    # ====================================
    # SHOW SUMMARY
    # ====================================

    def show_summary(self):

        summary = (
            self.get_execution_summary()
        )

        self.logger.warning(

            "========== EXECUTION ANALYTICS =========="
        )

        for key, value in summary.items():

            self.logger.info(

                f"{key} = {value}"
            )

        self.logger.warning(

            "========================================="
        )


    # ====================================
    # GET EXECUTION HISTORY
    # ====================================

    def get_execution_history(self):

        return (
            self.execution_history
        )