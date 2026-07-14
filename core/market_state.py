# ====================================
# market_state.py
# ====================================

import threading

from utils.logger import (
    SystemLogger
)

from utils.helpers import (

    format_price,

    format_timestamp
)


class MarketState:


    # ====================================
    # INIT
    # ====================================

    def __init__(self):

        self.logger = (
            SystemLogger()
        )

        self.lock = (
            threading.Lock()
        )

        # ====================================
        # PER-SYMBOL STATE
        # ====================================

        self.markets = {}

        # ====================================
        # LEGACY SINGLE-SYMBOL FIELDS
        # Keep these for backward compatibility
        # ====================================

        self.symbol = None

        self.current_price = 0.0

        self.bid_price = 0.0

        self.ask_price = 0.0

        self.mid_price = 0.0

        self.spread = 0.0

        self.current_volume = 0

        self.cumulative_volume = 0

        self.volatility = 0.0

        self.liquidity_score = 100

        self.order_imbalance = 0.0

        self.trade_intensity = 0.0

        self.market_open = True

        self.timestamp = None


    # ====================================
    # DEFAULT SNAPSHOT
    # ====================================

    def _default_snapshot(self, symbol):

        return {

            "symbol":
            symbol,

            "current_price":
            0.0,

            "bid_price":
            0.0,

            "ask_price":
            0.0,

            "mid_price":
            0.0,

            "spread":
            0.0,

            "current_volume":
            0,

            "cumulative_volume":
            0,

            "volatility":
            0.0,

            "liquidity_score":
            100,

            "order_imbalance":
            0.0,

            "trade_intensity":
            0.0,

            "market_open":
            True,

            "timestamp":
            None
        }


    # ====================================
    # UPDATE MARKET STATE
    # ====================================

    def update(

        self,

        symbol=None,

        price=None,

        volume=None,

        bid_price=None,

        ask_price=None,

        volatility=None,

        liquidity_score=None,

        order_imbalance=None,

        trade_intensity=None,

        timestamp=None
    ):

        with self.lock:

            if symbol is None:

                symbol = (
                    self.symbol
                    if self.symbol
                    else "UNKNOWN"
                )

            if symbol not in self.markets:

                self.markets[
                    symbol
                ] = self._default_snapshot(
                    symbol
                )

            snapshot = (
                self.markets[
                    symbol
                ]
            )

            snapshot[
                "symbol"
            ] = symbol

            if price is not None:

                snapshot[
                    "current_price"
                ] = format_price(
                    price
                )

            if bid_price is not None:

                snapshot[
                    "bid_price"
                ] = format_price(
                    bid_price
                )

            if ask_price is not None:

                snapshot[
                    "ask_price"
                ] = format_price(
                    ask_price
                )

            if (

                snapshot[
                    "bid_price"
                ] > 0

                and

                snapshot[
                    "ask_price"
                ] > 0
            ):

                snapshot[
                    "mid_price"
                ] = round(

                    (

                        snapshot[
                            "bid_price"
                        ]

                        +

                        snapshot[
                            "ask_price"
                        ]

                    ) / 2,

                    2
                )

                snapshot[
                    "spread"
                ] = round(

                    snapshot[
                        "ask_price"
                    ]

                    -

                    snapshot[
                        "bid_price"
                    ],

                    4
                )

            if volume is not None:

                volume = int(
                    volume
                )

                snapshot[
                    "current_volume"
                ] = volume

                snapshot[
                    "cumulative_volume"
                ] += volume

            if volatility is not None:

                snapshot[
                    "volatility"
                ] = round(

                    float(volatility),

                    4
                )

            if liquidity_score is not None:

                snapshot[
                    "liquidity_score"
                ] = round(

                    float(liquidity_score),

                    2
                )

            if order_imbalance is not None:

                snapshot[
                    "order_imbalance"
                ] = round(

                    float(order_imbalance),

                    4
                )

            if trade_intensity is not None:

                snapshot[
                    "trade_intensity"
                ] = round(

                    float(trade_intensity),

                    4
                )

            if timestamp is not None:

                snapshot[
                    "timestamp"
                ] = timestamp

            # ====================================
            # UPDATE LEGACY FIELDS WITH LAST SYMBOL
            # ====================================

            self.symbol = symbol

            self.current_price = snapshot[
                "current_price"
            ]

            self.bid_price = snapshot[
                "bid_price"
            ]

            self.ask_price = snapshot[
                "ask_price"
            ]

            self.mid_price = snapshot[
                "mid_price"
            ]

            self.spread = snapshot[
                "spread"
            ]

            self.current_volume = snapshot[
                "current_volume"
            ]

            self.cumulative_volume = snapshot[
                "cumulative_volume"
            ]

            self.volatility = snapshot[
                "volatility"
            ]

            self.liquidity_score = snapshot[
                "liquidity_score"
            ]

            self.order_imbalance = snapshot[
                "order_imbalance"
            ]

            self.trade_intensity = snapshot[
                "trade_intensity"
            ]

            self.market_open = snapshot[
                "market_open"
            ]

            self.timestamp = snapshot[
                "timestamp"
            ]

        self.logger.info(

            f"Market Update | "

            f"Symbol: {symbol} | "

            f"Price: {self.current_price} | "

            f"Spread: {self.spread} | "

            f"Volume: {self.current_volume}"
        )


    # ====================================
    # GET PRICE
    # ====================================

    def get_price(

        self,

        symbol=None
    ):

        snapshot = self.get_snapshot(
            symbol
        )

        return snapshot.get(
            "current_price"
        )


    # ====================================
    # GET QUOTE
    # ====================================

    def get_quote(

        self,

        symbol=None
    ):

        snapshot = self.get_snapshot(
            symbol
        )

        return {

            "bid_price":
            snapshot.get(
                "bid_price"
            ),

            "ask_price":
            snapshot.get(
                "ask_price"
            ),

            "mid_price":
            snapshot.get(
                "mid_price"
            ),

            "spread":
            snapshot.get(
                "spread"
            )
        }


    # ====================================
    # GET SNAPSHOT
    # ====================================

    def get_snapshot(

        self,

        symbol=None
    ):

        with self.lock:

            if symbol is None:

                symbol = self.symbol

            if symbol in self.markets:

                snapshot = dict(
                    self.markets[
                        symbol
                    ]
                )

            else:

                snapshot = self._default_snapshot(
                    symbol
                )

        snapshot[
            "timestamp"
        ] = format_timestamp(
            snapshot.get(
                "timestamp"
            )
        )

        return snapshot


    # ====================================
    # GET ALL SNAPSHOTS
    # ====================================

    def get_all_snapshots(self):

        with self.lock:

            snapshots = {

                symbol:
                dict(snapshot)

                for symbol, snapshot
                in self.markets.items()
            }

        for symbol in snapshots:

            snapshots[
                symbol
            ][
                "timestamp"
            ] = format_timestamp(

                snapshots[
                    symbol
                ].get(
                    "timestamp"
                )
            )

        return snapshots


    # ====================================
    # HAS SYMBOL
    # ====================================

    def has_symbol(

        self,

        symbol
    ):

        with self.lock:

            return symbol in self.markets


    # ====================================
    # DISPLAY STATE
    # ====================================

    def show(self):

        snapshots = (
            self.get_all_snapshots()
        )

        print(
            "\n========== MARKET STATE ==========\n"
        )

        for symbol, snapshot in snapshots.items():

            print(f"[{symbol}]")

            for key, value in snapshot.items():

                print(f"{key}: {value}")

            print("")

        print(
            "\n==================================\n"
        )


    # ====================================
    # RESET MARKET STATE
    # ====================================

    def reset(self):

        self.__init__()

        self.logger.warning(
            "Market State Reset"
        )