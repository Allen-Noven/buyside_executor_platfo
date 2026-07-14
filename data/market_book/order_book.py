# ====================================
# order_book.py
# ====================================

from utils.logger import (
    SystemLogger
)


class OrderBook:


    # ====================================
    # INIT
    # ====================================

    def __init__(

        self,

        symbol,

        max_depth=20
    ):

        self.symbol = symbol

        self.max_depth = max_depth

        self.logger = (
            SystemLogger()
        )

        # ====================================
        # BOOK SIDES
        # ====================================

        self.bids = []

        self.asks = []

        # ====================================
        # METRICS
        # ====================================

        self.best_bid = None

        self.best_ask = None

        self.spread = None

        self.mid_price = None

        self.imbalance = 0.0

        self.bid_volume = 0

        self.ask_volume = 0

        self.last_update = None

        self.logger.info(

            f"OrderBook Initialized | "

            f"{symbol}"
        )


    # ====================================
    # UPDATE BOOK
    # ====================================

    def update_book(

        self,

        bids,

        asks,

        timestamp=None
    ):

        # ====================================
        # NORMALIZE BIDS
        # ====================================

        normalized_bids = []

        for level in bids:

            if len(level) != 2:

                continue

            price = float(level[0])

            size = float(level[1])

            if size <= 0:

                continue

            normalized_bids.append(
                [price, size]
            )

        # ====================================
        # NORMALIZE ASKS
        # ====================================

        normalized_asks = []

        for level in asks:

            if len(level) != 2:

                continue

            price = float(level[0])

            size = float(level[1])

            if size <= 0:

                continue

            normalized_asks.append(
                [price, size]
            )

        # ====================================
        # SORT BIDS
        # ====================================

        self.bids = sorted(

            normalized_bids,

            key=lambda x: x[0],

            reverse=True
        )[:self.max_depth]

        # ====================================
        # SORT ASKS
        # ====================================

        self.asks = sorted(

            normalized_asks,

            key=lambda x: x[0]
        )[:self.max_depth]

        self.last_update = (
            timestamp
        )

        # ====================================
        # RECALCULATE
        # ====================================

        self.recalculate()


    # ====================================
    # RECALCULATE
    # ====================================

    def recalculate(self):

        # ====================================
        # BEST BID
        # ====================================

        self.best_bid = (

            self.bids[0]

            if len(self.bids) > 0

            else None
        )

        # ====================================
        # BEST ASK
        # ====================================

        self.best_ask = (

            self.asks[0]

            if len(self.asks) > 0

            else None
        )

        # ====================================
        # SPREAD
        # ====================================

        if (

            self.best_bid is not None
            and
            self.best_ask is not None

        ):

            self.spread = (

                self.best_ask[0]
                -
                self.best_bid[0]
            )

            self.mid_price = (

                self.best_bid[0]
                +
                self.best_ask[0]

            ) / 2

        else:

            self.spread = None

            self.mid_price = None

        # ====================================
        # VOLUMES
        # ====================================

        self.bid_volume = sum(

            level[1]

            for level in self.bids
        )

        self.ask_volume = sum(

            level[1]

            for level in self.asks
        )

        # ====================================
        # IMBALANCE
        # ====================================

        total_volume = (

            self.bid_volume
            +
            self.ask_volume
        )

        if total_volume == 0:

            self.imbalance = 0

        else:

            self.imbalance = (

                self.bid_volume
                -
                self.ask_volume

            ) / total_volume


    # ====================================
    # GET BEST BID
    # ====================================

    def get_best_bid(self):

        return self.best_bid


    # ====================================
    # GET BEST ASK
    # ====================================

    def get_best_ask(self):

        return self.best_ask


    # ====================================
    # GET SPREAD
    # ====================================

    def get_spread(self):

        return self.spread


    # ====================================
    # GET MID PRICE
    # ====================================

    def get_mid_price(self):

        return self.mid_price


    # ====================================
    # GET IMBALANCE
    # ====================================

    def get_imbalance(self):

        return self.imbalance


    # ====================================
    # GET TOP LEVELS
    # ====================================

    def get_top_levels(

        self,

        levels=5
    ):

        return {

            "bids":
            self.bids[:levels],

            "asks":
            self.asks[:levels]
        }


    # ====================================
    # CLEAR
    # ====================================

    def clear(self):

        self.bids = []

        self.asks = []

        self.best_bid = None

        self.best_ask = None

        self.spread = None

        self.mid_price = None

        self.imbalance = 0

        self.bid_volume = 0

        self.ask_volume = 0

        self.last_update = None

        self.logger.warning(

            f"OrderBook Cleared | "

            f"{self.symbol}"
        )


    # ====================================
    # SNAPSHOT
    # ====================================

    def get_snapshot(self):

        return {

            "symbol":
            self.symbol,

            "best_bid":
            self.best_bid,

            "best_ask":
            self.best_ask,

            "spread":
            self.spread,

            "mid_price":
            self.mid_price,

            "imbalance":
            self.imbalance,

            "bid_volume":
            self.bid_volume,

            "ask_volume":
            self.ask_volume,

            "bids":
            self.bids,

            "asks":
            self.asks,

            "last_update":
            self.last_update
        }


    # ====================================
    # SHOW BOOK
    # ====================================

    def show_book(

        self,

        levels=5
    ):

        print(

            "\n========== "
            f"{self.symbol} ORDER BOOK "
            "==========\n"
        )

        print("ASKS")

        for price, size in self.asks[:levels]:

            print(

                f"{price:<12} "
                f"{size}"
            )

        print("\n--------------------------\n")

        print("BIDS")

        for price, size in self.bids[:levels]:

            print(

                f"{price:<12} "
                f"{size}"
            )

        print(

            "\n====================================\n"
        )