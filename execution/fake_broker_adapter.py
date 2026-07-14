# ====================================
# fake_broker_adapter.py
# ====================================

import uuid
import time

from utils.logger import (
    SystemLogger
)

from utils.constants import (
    BUY,
    SELL
)


class FakeOrder:


    # ====================================
    # INIT
    # ====================================

    def __init__(

        self,

        order_id,

        symbol,

        qty,

        side,

        status,

        filled_avg_price
    ):

        self.id = (
            order_id
        )

        self.symbol = (
            symbol
        )

        self.qty = (
            qty
        )

        self.side = (
            side
        )

        self.status = (
            status
        )

        self.filled_avg_price = (
            filled_avg_price
        )

        self.created_at = (
            time.time()
        )


    # ====================================
    # TO DICT
    # ====================================

    def to_dict(self):

        return {

            "id":
            self.id,

            "symbol":
            self.symbol,

            "qty":
            self.qty,

            "side":
            self.side,

            "status":
            self.status,

            "filled_avg_price":
            self.filled_avg_price,

            "created_at":
            self.created_at
        }


class FakeBrokerAdapter:


    # ====================================
    # INIT
    # ====================================

    def __init__(

        self,

        simulation_account=None,

        market_state=None,

        initial_cash=100000
    ):

        self.logger = (
            SystemLogger()
        )

        self.simulation_account = (
            simulation_account
        )

        self.market_state = (
            market_state
        )

        self.initial_cash = float(
            initial_cash
        )

        self.cash = float(
            initial_cash
        )

        self.buying_power = float(
            initial_cash
        )

        self.equity = float(
            initial_cash
        )

        self.orders = {}

        self.open_orders = {}

        self.positions = {}

        self.total_notional_traded = 0.0

        self.total_buys = 0.0

        self.total_sells = 0.0

        self.trade_count = 0

        self.logger.info(
            "Fake Broker Adapter Initialized"
        )


    # ====================================
    # GET MARKET PRICE
    # ====================================

    def get_market_price(

        self,

        symbol
    ):

        symbol = symbol.upper()

        if self.market_state and hasattr(
            self.market_state,
            "get_price"
        ):

            price = self.market_state.get_price(
                symbol
            )

            if price and price > 0:

                return float(
                    price
                )

        if self.market_state and hasattr(
            self.market_state,
            "current_price"
        ):

            price = self.market_state.current_price

            if price and price > 0:

                return float(
                    price
                )

        return 100.0


    # ====================================
    # SUBMIT ORDER
    # ====================================

    def submit_order(

        self,

        symbol,

        qty,

        side
    ):

        symbol = symbol.upper()

        qty = float(
            qty
        )

        if qty <= 0:

            raise ValueError(
                "Quantity Must Be Positive"
            )

        if side not in [
            BUY,
            SELL
        ]:

            raise ValueError(
                f"Invalid Side | {side}"
            )

        fill_price = self.get_market_price(
            symbol
        )

        notional = (
            qty
            *
            fill_price
        )

        if side == BUY:

            available_cash = self.get_cash()

            if notional > available_cash:

                self.logger.error(

                    f"Fake Broker Insufficient Cash | "

                    f"Required={notional} | "

                    f"Cash={available_cash}"
                )

                return None

        order_id = (
            "fake_"
            +
            str(
                uuid.uuid4()
            )
        )

        order = FakeOrder(

            order_id=
            order_id,

            symbol=
            symbol,

            qty=
            qty,

            side=
            side,

            status=
            "filled",

            filled_avg_price=
            fill_price
        )

        self.orders[
            order_id
        ] = order

        self.apply_fill_to_local_account(

            symbol=
            symbol,

            side=
            side,

            qty=
            qty,

            fill_price=
            fill_price
        )

        if self.simulation_account:

            self.simulation_account.apply_fill(

                symbol=
                symbol,

                side=
                side,

                qty=
                qty,

                fill_price=
                fill_price
            )

        self.logger.info(

            f"Fake Order Filled | "

            f"{symbol} | "

            f"{side} | "

            f"Qty={qty} | "

            f"Price={fill_price}"
        )

        return order


    # ====================================
    # APPLY FILL TO LOCAL ACCOUNT
    # ====================================

    def apply_fill_to_local_account(

        self,

        symbol,

        side,

        qty,

        fill_price
    ):

        notional = (
            qty
            *
            fill_price
        )

        current_position = self.positions.get(

            symbol,

            {

                "quantity":
                0.0,

                "avg_price":
                0.0,

                "market_value":
                0.0
            }
        )

        current_qty = (
            current_position[
                "quantity"
            ]
        )

        current_avg = (
            current_position[
                "avg_price"
            ]
        )

        if side == BUY:

            self.cash -= notional

            self.total_buys += notional

            new_qty = (
                current_qty
                +
                qty
            )

            if new_qty != 0:

                new_avg = (

                    (
                        current_qty
                        *
                        current_avg
                    )

                    +

                    (
                        qty
                        *
                        fill_price
                    )

                ) / new_qty

            else:

                new_avg = 0.0

        else:

            self.cash += notional

            self.total_sells += notional

            new_qty = (
                current_qty
                -
                qty
            )

            if new_qty == 0:

                new_avg = 0.0

            else:

                new_avg = current_avg

        market_value = (
            new_qty
            *
            fill_price
        )

        self.positions[
            symbol
        ] = {

            "quantity":
            new_qty,

            "avg_price":
            new_avg,

            "market_value":
            market_value
        }

        self.total_notional_traded += notional

        self.trade_count += 1

        self.buying_power = self.cash

        self.equity = (
            self.cash
            +
            self.get_total_market_value()
        )


    # ====================================
    # GET CASH
    # ====================================

    def get_cash(self):

        if self.simulation_account:

            snapshot = (
                self.simulation_account
                .get_snapshot()
            )

            return float(
                snapshot.get(
                    "cash",
                    0
                )
            )

        return float(
            self.cash
        )


    # ====================================
    # CANCEL ORDER
    # ====================================

    def cancel_order(

        self,

        order_id
    ):

        if order_id in self.open_orders:

            order = self.open_orders.pop(
                order_id
            )

            order.status = "cancelled"

            self.orders[
                order_id
            ] = order

            self.logger.warning(

                f"Fake Order Cancelled | "

                f"{order_id}"
            )

            return True

        self.logger.warning(

            f"Fake Order Not Found Or Already Filled | "

            f"{order_id}"
        )

        return False


    # ====================================
    # GET ORDER
    # ====================================

    def get_order(

        self,

        order_id
    ):

        return self.orders.get(
            order_id
        )


    # ====================================
    # GET ACCOUNT
    # ====================================

    def get_account(self):

        if self.simulation_account:

            return (
                self.simulation_account
                .get_snapshot()
            )

        return {

            "account_type":
            "SIMULATION",

            "initial_cash":
            self.initial_cash,

            "cash":
            self.cash,

            "buying_power":
            self.buying_power,

            "equity":
            self.equity,

            "total_notional_traded":
            self.total_notional_traded,

            "total_buys":
            self.total_buys,

            "total_sells":
            self.total_sells,

            "trade_count":
            self.trade_count
        }


    # ====================================
    # GET POSITIONS
    # ====================================

    def get_positions(self):

        return {

            symbol:
            {

                "quantity":
                position[
                    "quantity"
                ],

                "avg_price":
                position[
                    "avg_price"
                ],

                "market_value":
                position[
                    "market_value"
                ]
            }

            for symbol, position

            in self.positions.items()
        }


    # ====================================
    # GET OPEN ORDERS
    # ====================================

    def get_open_orders(self):

        return list(
            self.open_orders.values()
        )


    # ====================================
    # GET ALL ORDERS
    # ====================================

    def get_all_orders(self):

        return list(
            self.orders.values()
        )


    # ====================================
    # GET TOTAL MARKET VALUE
    # ====================================

    def get_total_market_value(self):

        total = 0

        for symbol, position in self.positions.items():

            price = self.get_market_price(
                symbol
            )

            total += (

                position[
                    "quantity"
                ]

                *

                price
            )

        return total


    # ====================================
    # RESET
    # ====================================

    def reset(self):

        self.cash = float(
            self.initial_cash
        )

        self.buying_power = float(
            self.initial_cash
        )

        self.equity = float(
            self.initial_cash
        )

        self.orders = {}

        self.open_orders = {}

        self.positions = {}

        self.total_notional_traded = 0.0

        self.total_buys = 0.0

        self.total_sells = 0.0

        self.trade_count = 0

        self.logger.warning(
            "Fake Broker Adapter Reset"
        )