# ====================================
# oms.py
# ====================================

from execution.broker_adapter import (

    AlpacaBrokerAdapter
)

from utils.logger import (
    SystemLogger
)

from utils.helpers import (
    get_current_time
)


class OMS:


    # ====================================
    # INIT
    # ====================================

    def __init__(

        self,

        broker_adapter=None
    ):

        # ====================================
        # LOGGER
        # ====================================

        self.logger = (
            SystemLogger()
        )

        # ====================================
        # BROKER ADAPTER
        # ====================================

        self.broker_adapter = (

            broker_adapter

            if broker_adapter

            else AlpacaBrokerAdapter()
        )

        # ====================================
        # ORDER STORAGE
        # ====================================

        self.orders = []

        self.logger.info(
            "OMS Initialized"
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

            # ====================================
            # SUBMIT TIME
            # ====================================

            submit_time = (
                get_current_time()
            )

            # ====================================
            # SUBMIT TO BROKER
            # ====================================

            order = (

                self.broker_adapter
                .submit_order(

                    symbol=symbol,

                    qty=qty,

                    side=side
                )
            )

            # ====================================
            # FAILURE
            # ====================================

            if order is None:

                self.logger.error(

                    "Broker Submission Failed"
                )

                return None

            # ====================================
            # STORE ORDER
            # ====================================

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

            # ====================================
            # LOG
            # ====================================

            self.logger.info(

                f"Order Submitted | "

                f"{symbol} | "

                f"{side} | "

                f"{qty}"
            )

            return order

        except Exception as error:

            self.logger.error(

                f"OMS Submission Failed | "

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

                self.logger.warning(

                    f"Order Cancelled | "

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

        return [

            order

            for order in self.orders

            if order["status"]

            not in [

                "filled",

                "canceled",

                "cancelled"
            ]
        ]


    # ====================================
    # GET FILLED ORDERS
    # ====================================

    def get_filled_orders(self):

        return [

            order

            for order in self.orders

            if order["status"] == "filled"
        ]


    # ====================================
    # GET ORDER COUNT
    # ====================================

    def get_order_count(self):

        return len(self.orders)


    # ====================================
    # SHOW SUMMARY
    # ====================================

    def show_summary(self):

        total_orders = (
            len(self.orders)
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

        print(

            "\n========== OMS SUMMARY ==========\n"
        )

        print(

            f"Total Orders: "
            f"{total_orders}"
        )

        print(

            f"Filled Orders: "
            f"{filled_orders}"
        )

        print(

            f"Open Orders: "
            f"{open_orders}"
        )

        print(

            "\n=================================\n"
        )
