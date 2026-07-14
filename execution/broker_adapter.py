# ====================================
# broker_adapter.py
# ====================================

from abc import (
    ABC,
    abstractmethod
)

from alpaca.trading.client import (
    TradingClient
)

from alpaca.trading.requests import (
    MarketOrderRequest
)

from alpaca.trading.enums import (

    OrderSide,

    TimeInForce
)

from utils.config import (

    API_KEY,

    SECRET_KEY,

    PAPER_TRADING
)

from utils.constants import (

    BUY,

    SELL
)

from utils.logger import (
    SystemLogger
)


# ====================================
# BASE BROKER ADAPTER
# ====================================

class BrokerAdapter(ABC):


    def __init__(self):

        self.logger = (
            SystemLogger()
        )


    @abstractmethod
    def submit_order(

        self,

        symbol,

        qty,

        side
    ):

        pass


    @abstractmethod
    def cancel_order(

        self,

        order_id
    ):

        pass


    @abstractmethod
    def get_order(

        self,

        order_id
    ):

        pass


    @abstractmethod
    def get_account(self):

        pass


    @abstractmethod
    def get_positions(self):

        pass


    @abstractmethod
    def get_open_orders(self):

        pass


# ====================================
# ALPACA BROKER ADAPTER
# ====================================

class AlpacaBrokerAdapter(BrokerAdapter):


    def __init__(self):

        super().__init__()

        self.client = TradingClient(

            API_KEY,

            SECRET_KEY,

            paper=
            PAPER_TRADING
        )

        self.logger.info(
            "Alpaca Broker Adapter Initialized"
        )


    def convert_side(

        self,

        side
    ):

        if side == BUY:

            return OrderSide.BUY

        if side == SELL:

            return OrderSide.SELL

        raise ValueError(
            f"Invalid Side | {side}"
        )


    def submit_order(

        self,

        symbol,

        qty,

        side
    ):

        try:

            alpaca_side = (
                self.convert_side(
                    side
                )
            )

            order_request = MarketOrderRequest(

                symbol=
                symbol,

                qty=
                qty,

                side=
                alpaca_side,

                time_in_force=
                TimeInForce.DAY
            )

            order = self.client.submit_order(

                order_data=
                order_request
            )

            self.logger.info(

                f"Broker Order Submitted | "

                f"{symbol} | "

                f"{qty}"
            )

            return order

        except Exception as error:

            self.logger.error(

                f"Broker Submit Failed | "

                f"{error}"
            )

            return None


    def cancel_order(

        self,

        order_id
    ):

        try:

            self.client.cancel_order_by_id(
                order_id
            )

            self.logger.warning(

                f"Broker Order Cancelled | "

                f"{order_id}"
            )

            return True

        except Exception as error:

            self.logger.error(

                f"Broker Cancel Failed | "

                f"{error}"
            )

            return False


    def get_order(

        self,

        order_id
    ):

        try:

            return self.client.get_order_by_id(
                order_id
            )

        except Exception as error:

            self.logger.error(

                f"Broker Get Order Failed | "

                f"{error}"
            )

            return None


    def get_account(self):

        try:

            return self.client.get_account()

        except Exception as error:

            self.logger.error(

                f"Broker Account Failed | "

                f"{error}"
            )

            return None


    def get_positions(self):

        try:

            positions = (
                self.client.get_all_positions()
            )

            result = {}

            for position in positions:

                result[
                    position.symbol
                ] = {

                    "quantity":
                    float(
                        position.qty
                    )
                }

            return result

        except Exception as error:

            self.logger.error(

                f"Broker Positions Failed | "

                f"{error}"
            )

            return {}


    def get_open_orders(self):

        try:

            return self.client.get_orders()

        except Exception as error:

            self.logger.error(

                f"Broker Open Orders Failed | "

                f"{error}"
            )

            return []


# ====================================
# FAKE BROKER ADAPTER
# ====================================

class FakeBrokerAdapter(BrokerAdapter):


    def __init__(

        self,

        simulation_account=None
    ):

        super().__init__()

        self.orders = {}

        self.positions = {}

        self.simulation_account = (
            simulation_account
        )

        self.logger.info(
            "Fake Broker Adapter Initialized"
        )


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

        fake_price = 100.0

        fake_order = {

            "id":
            f"fake_{len(self.orders) + 1}",

            "symbol":
            symbol,

            "qty":
            qty,

            "side":
            side,

            "status":
            "filled",

            "filled_avg_price":
            fake_price
        }

        if self.simulation_account:

            self.simulation_account.apply_fill(

                symbol=
                symbol,

                side=
                side,

                qty=
                qty,

                fill_price=
                fake_price
            )

        current_qty = (
            self.positions
            .get(
                symbol,
                {}
            )
            .get(
                "quantity",
                0
            )
        )

        if side == BUY:

            new_qty = (
                current_qty
                +
                qty
            )

        elif side == SELL:

            new_qty = (
                current_qty
                -
                qty
            )

        else:

            raise ValueError(
                f"Invalid Side | {side}"
            )

        self.positions[
            symbol
        ] = {

            "quantity":
            new_qty
        }

        self.orders[
            fake_order[
                "id"
            ]
        ] = fake_order

        self.logger.info(

            f"Fake Order Filled | "

            f"{symbol} | "

            f"{qty}"
        )

        return type(

            "FakeOrder",

            (object,),

            fake_order
        )


    def cancel_order(

        self,

        order_id
    ):

        if order_id in self.orders:

            self.orders[
                order_id
            ][
                "status"
            ] = "cancelled"

            self.logger.warning(

                f"Fake Order Cancelled | "

                f"{order_id}"
            )

            return True

        return False


    def get_order(

        self,

        order_id
    ):

        return self.orders.get(
            order_id
        )


    def get_account(self):

        if self.simulation_account:

            return (
                self.simulation_account
                .get_snapshot()
            )

        return {

            "account_type":
            "SIMULATION",

            "equity":
            100000,

            "cash":
            100000,

            "buying_power":
            100000
        }


    def get_positions(self):

        return self.positions


    def get_open_orders(self):

        return []