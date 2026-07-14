# ====================================
# order_router.py
# ====================================

from utils.logger import (
    SystemLogger
)

from utils.helpers import (
    get_current_time
)

from utils.constants import (

    BUY,

    SELL
)


class OrderRouter:


    # ====================================
    # INIT
    # ====================================

    def __init__(

        self,

        market_state=None,

        oms=None,

        risk_manager=None,

        system_state=None
    ):

        self.logger = (
            SystemLogger()
        )

        self.market_state = (
            market_state
        )

        self.oms = oms

        self.risk_manager = (
            risk_manager
        )

        self.system_state = (
            system_state
        )

        self.total_orders_routed = 0

        self.total_rejected_orders = 0

        self.total_filled_orders = 0


    # ====================================
    # ROUTE ORDER
    # ====================================

    def route_order(

        self,

        parent_order,

        child_qty
    ):

        if child_qty <= 0:

            self.logger.error(
                "Invalid Child Quantity"
            )

            return None

        if self.risk_manager:

            approved = (

                self.risk_manager
                .validate_order(

                    symbol=
                    parent_order.symbol,

                    qty=
                    child_qty,

                    side=
                    parent_order.side
                )
            )

            if not approved:

                self.total_rejected_orders += 1

                self.logger.warning(
                    "Order Rejected By Risk"
                )

                return None

        if not self.market_state:

            self.logger.error(
                "Market State Missing"
            )

            return None

        symbol = (
            parent_order.symbol
        )

        market_snapshot = (
            self.market_state
            .get_snapshot(
                symbol
            )
        )

        market_price = (
            market_snapshot
            .get(
                "current_price",
                0
            )
        )

        if not market_price:

            self.logger.error(

                f"Market Price Missing | "

                f"{symbol}"
            )

            return None

        spread = (
            market_snapshot
            .get(
                "spread",
                0
            )
        )

        liquidity = (
            market_snapshot
            .get(
                "liquidity_score",
                0
            )
        )

        execution_price = (
            self.determine_execution_price(

                symbol=
                symbol,

                side=
                parent_order.side
            )
        )

        child_order = {

            "timestamp":
            get_current_time(),

            "parent_order_id":
            parent_order.order_id,

            "symbol":
            symbol,

            "side":
            parent_order.side,

            "quantity":
            child_qty,

            "execution_price":
            execution_price,

            "market_price":
            market_price,

            "spread":
            spread,

            "liquidity":
            liquidity,

            "strategy":
            parent_order.strategy,

            "status":
            "ROUTED"
        }

        if self.oms:

            self.oms.submit_market_order(

                symbol=
                child_order[
                    "symbol"
                ],

                qty=
                child_order[
                    "quantity"
                ],

                side=
                child_order[
                    "side"
                ]
            )

        parent_order.add_child_order(
            child_order
        )

        self.total_orders_routed += 1

        self.logger.info(

            f"Order Routed | "

            f"{symbol} | "

            f"Qty={child_qty} | "

            f"Price={execution_price}"
        )

        return child_order


    # ====================================
    # DETERMINE EXECUTION PRICE
    # ====================================

    def determine_execution_price(

        self,

        symbol,

        side
    ):

        snapshot = (

            self.market_state
            .get_snapshot(
                symbol
            )
        )

        bid = (
            snapshot.get(
                "bid_price",
                0
            )
        )

        ask = (
            snapshot.get(
                "ask_price",
                0
            )
        )

        mid = (
            snapshot.get(
                "mid_price",
                0
            )
        )

        spread = (
            snapshot.get(
                "spread",
                0
            )
        )

        current_price = (
            snapshot.get(
                "current_price",
                0
            )
        )

        if mid == 0:

            return current_price

        if side == BUY:

            if spread <= 0.02:

                return ask

            return round(

                mid + (
                    spread * 0.25
                ),

                2
            )

        if side == SELL:

            if spread <= 0.02:

                return bid

            return round(

                mid - (
                    spread * 0.25
                ),

                2
            )

        return mid


    # ====================================
    # FILL ORDER
    # ====================================

    def fill_order(

        self,

        parent_order,

        child_order
    ):

        fill_qty = (
            child_order[
                "quantity"
            ]
        )

        fill_price = (
            child_order[
                "execution_price"
            ]
        )

        parent_order.add_fill(

            fill_qty=
            fill_qty,

            fill_price=
            fill_price
        )

        if (

            self.oms
            and
            hasattr(
                self.oms,
                "record_fill"
            )
        ):

            self.oms.record_fill(

                symbol=
                parent_order.symbol,

                qty=
                fill_qty,

                price=
                fill_price
            )

        self.total_filled_orders += 1

        self.logger.info(

            f"Order Filled | "

            f"{parent_order.symbol} | "

            f"{fill_qty} @ "

            f"{fill_price}"
        )


    # ====================================
    # GET STATS
    # ====================================

    def get_stats(self):

        return {

            "total_orders_routed":
            self.total_orders_routed,

            "total_rejected_orders":
            self.total_rejected_orders,

            "total_filled_orders":
            self.total_filled_orders
        }


    # ====================================
    # SHOW STATS
    # ====================================

    def show_stats(self):

        stats = (
            self.get_stats()
        )

        print(
            "\n========== ORDER ROUTER ==========\n"
        )

        for key, value in stats.items():

            print(f"{key}: {value}")

        print(
            "\n==================================\n"
        )