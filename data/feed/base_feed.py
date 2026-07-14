# ====================================
# base_oms.py
# ====================================

from abc import (
    ABC,
    abstractmethod
)


class BaseOMS(ABC):


    # ====================================
    # SUBMIT MARKET ORDER
    # ====================================

    @abstractmethod
    def submit_market_order(

        self,

        symbol,

        qty,

        side
    ):

        pass


    # ====================================
    # CANCEL ORDER
    # ====================================

    @abstractmethod
    def cancel_order(

        self,

        order_id
    ):

        pass


    # ====================================
    # GET ORDER
    # ====================================

    @abstractmethod
    def get_order(

        self,

        order_id
    ):

        pass


    # ====================================
    # GET OPEN ORDERS
    # ====================================

    @abstractmethod
    def get_open_orders(self):

        pass


    # ====================================
    # GET POSITIONS
    # ====================================

    @abstractmethod
    def get_positions(self):

        pass