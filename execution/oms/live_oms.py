# ====================================
# live_oms.py
# ====================================

from execution.broker_adapter import (

    AlpacaBrokerAdapter
)

from execution.oms.base_oms import (
    BaseOMS
)

from utils.logger import (
    SystemLogger
)

from utils.helpers import (
    get_current_time
)

from utils.constants import (
    LIVE
)


class LiveOMS(BaseOMS):


    # ====================================
    # INIT
    # ====================================

    def __init__(

        self,

        broker_adapter=None
    ):

        self.logger = (
            SystemLogger()
        )

        self.execution_logger = (
            SystemLogger(
                log_type="execution"
            )
        )

        self.runtime_mode = (
            LIVE
        )

        self.broker_adapter = (

            broker_adapter

            if broker_adapter

            else AlpacaBrokerAdapter()
        )

        self.orders = []

        self.logger.info(
            "LiveOMS Initialized"
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
                    "Broker Submission Failed"
                )

                return None

            order_record = {

                "timestamp":
                submit_time,

                "order_id":
                str(order.id),

                "symbol":
                symbol,

                "qty":
                qty,

                "side":
                side,

                "status":
                str(order.status)
            }

            self.orders.append(
                order_record
            )

            self.execution_logger.warning(

                f"LIVE ORDER SUBMITTED | "

                f"OrderID={str(order.id)} | "

                f"{symbol} | "

                f"{side} | "

                f"Qty={qty} | "

                f"Status={str(order.status)}"
            )

            return order

        except Exception as error:

            self.logger.error(

                f"LiveOMS Failed | "

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

            return (

                self.broker_adapter
                .get_order(order_id)
            )

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
                .cancel_order(order_id)
            )

            if success:

                self.execution_logger.warning(

                    f"LIVE ORDER CANCELLED | "

                    f"OrderID={order_id}"
                )

            return success

        except Exception as error:

            self.logger.error(

                f"Cancel Order Failed | "

                f"{error}"
            )

            return False


    # ====================================
    # GET OPEN ORDERS
    # ====================================

    def get_open_orders(self):

        try:

            return (

                self.broker_adapter
                .get_open_orders()
            )

        except Exception as error:

            self.logger.error(

                f"Get Open Orders Failed | "

                f"{error}"
            )

            return []


    # ====================================
    # GET POSITIONS
    # ====================================

    def get_positions(self):

        try:

            return (

                self.broker_adapter
                .get_positions()
            )

        except Exception as error:

            self.logger.error(

                f"Get Positions Failed | "

                f"{error}"
            )

            return {}