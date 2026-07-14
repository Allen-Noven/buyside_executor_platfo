# ====================================
# fake_oms.py
# ====================================

from execution.oms.base_oms import (
    BaseOMS
)

from execution.fake_broker_adapter import (
    FakeBrokerAdapter
)

from utils.logger import (
    SystemLogger
)

from utils.helpers import (
    get_current_time
)

from utils.constants import (

    COMPLETED,

    CANCELLED,

    SIMULATION
)


class SimulationOMS(BaseOMS):


    # ====================================
    # INIT
    # ====================================

    def __init__(

        self,

        broker_adapter=None,

        simulation_account=None,

        market_state=None
    ):

        self.logger = (
            SystemLogger()
        )

        self.runtime_mode = (
            SIMULATION
        )

        self.broker_adapter = (

            broker_adapter
            if broker_adapter
            else FakeBrokerAdapter(

                simulation_account=
                simulation_account,

                market_state=
                market_state
            )
        )

        self.orders = []

        self.logger.info(
            "SimulationOMS Initialized"
        )


    # ====================================
    # GET ACCOUNT
    # ====================================

    def get_account(self):

        return (
            self.broker_adapter
            .get_account()
        )


    # ====================================
    # SUBMIT MARKET ORDER
    # ====================================

    def submit_market_order(

        self,

        symbol,

        qty,

        side
    ):

        try:

            submit_time = (
                get_current_time()
            )

            order = (

                self.broker_adapter
                .submit_order(

                    symbol=
                    symbol,

                    qty=
                    qty,

                    side=
                    side
                )
            )

            if order is None:

                self.logger.error(
                    "Simulation Broker Submission Failed"
                )

                return None

            order_record = {

                "timestamp":
                submit_time,

                "order_id":
                str(
                    order.id
                ),

                "symbol":
                symbol,

                "qty":
                qty,

                "side":
                side,

                "status":
                COMPLETED,

                "fill_price":
                float(
                    order.filled_avg_price
                )
            }

            self.orders.append(
                order_record
            )

            self.logger.info(

                f"Simulation Order Filled | "

                f"{symbol} | "

                f"{side} | "

                f"{qty} | "

                f"{order.filled_avg_price}"
            )

            return order

        except Exception as error:

            self.logger.error(

                f"SimulationOMS Failed | "

                f"{error}"
            )

            return None


    # ====================================
    # GET ORDER
    # ====================================

    def get_order(

        self,

        order_id
    ):

        try:

            broker_order = (
                self.broker_adapter
                .get_order(
                    order_id
                )
            )

            if broker_order:

                return broker_order

            for order in self.orders:

                if order[
                    "order_id"
                ] == order_id:

                    return order

            return None

        except Exception as error:

            self.logger.error(

                f"Get Order Failed | "

                f"{error}"
            )

            return None


    # ====================================
    # CANCEL ORDER
    # ====================================

    def cancel_order(

        self,

        order_id
    ):

        try:

            success = (

                self.broker_adapter
                .cancel_order(
                    order_id
                )
            )

            if success:

                for order in self.orders:

                    if order[
                        "order_id"
                    ] == order_id:

                        order[
                            "status"
                        ] = CANCELLED

                self.logger.warning(

                    f"Simulation Order Cancelled | "

                    f"{order_id}"
                )

            return success

        except Exception as error:

            self.logger.error(

                f"Cancel Order Failed | "

                f"{error}"
            )

            return False


    # ====================================
    # GET ALL ORDERS
    # ====================================

    def get_orders(self):

        return self.orders


    # ====================================
    # GET OPEN ORDERS
    # ====================================

    def get_open_orders(self):

        return (

            self.broker_adapter
            .get_open_orders()
        )


    # ====================================
    # GET FILLED ORDERS
    # ====================================

    def get_filled_orders(self):

        return [

            order

            for order in self.orders

            if order[
                "status"
            ] == COMPLETED
        ]


    # ====================================
    # GET ORDER COUNT
    # ====================================

    def get_order_count(self):

        return len(
            self.orders
        )


    # ====================================
    # GET POSITIONS
    # ====================================

    def get_positions(self):

        return (

            self.broker_adapter
            .get_positions()
        )


    # ====================================
    # SHOW SUMMARY
    # ====================================

    def show_summary(self):

        total_orders = (
            len(
                self.orders
            )
        )

        filled_orders = (
            len(
                self.get_filled_orders()
            )
        )

        open_orders = (
            len(
                self.get_open_orders()
            )
        )

        self.logger.warning(

            "========== "
            "SIMULATION OMS SUMMARY "
            "=========="
        )

        self.logger.info(

            f"Total Orders = "

            f"{total_orders}"
        )

        self.logger.info(

            f"Filled Orders = "

            f"{filled_orders}"
        )

        self.logger.info(

            f"Open Orders = "

            f"{open_orders}"
        )

        self.logger.info(

            f"Account = "

            f"{self.get_account()}"
        )

        self.logger.warning(
            "================================="
        )