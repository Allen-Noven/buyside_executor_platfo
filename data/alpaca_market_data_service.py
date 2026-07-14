# ====================================
# alpaca_market_data_service.py
# ====================================

import threading

from alpaca.data.live.stock import (
    StockDataStream
)

from alpaca.data.enums import (
    DataFeed
)

from utils.config import (

    API_KEY,

    SECRET_KEY,

    DEFAULT_SYMBOL,

    DEFAULT_MARKET_DATA_SYMBOLS,

    ALPACA_DATA_FEED
)

from utils.constants import (

    MARKET_UPDATE_EVENT,

    MARKET_DATA_CONNECTED,

    MARKET_DATA_DISCONNECTED,

    MARKET_DATA_ERROR,

    MARKET_DATA_SUBSCRIBED
)

from utils.helpers import (

    format_price,

    format_timestamp
)

from utils.logger import (
    SystemLogger
)


class AlpacaMarketDataService:


    # ====================================
    # INIT
    # ====================================

    def __init__(

        self,

        market_state,

        event_bus,

        symbols=None
    ):

        self.logger = (
            SystemLogger()
        )

        self.market_state = (
            market_state
        )

        self.event_bus = (
            event_bus
        )

        self.symbols = set(

            symbols
            if symbols
            else DEFAULT_MARKET_DATA_SYMBOLS
        )

        if not self.symbols:

            self.symbols.add(
                DEFAULT_SYMBOL
            )

        self.feed = (

            DataFeed.SIP
            if ALPACA_DATA_FEED.upper() == "SIP"
            else DataFeed.IEX
        )

        self.stream = StockDataStream(

            API_KEY,

            SECRET_KEY,

            feed=
            self.feed
        )

        self.thread = None

        self.running = False

        self.latest_prices = {}

        self.latest_quotes = {}

        self.latest_bars = {}


    # ====================================
    # SUBSCRIBE
    # ====================================

    def subscribe(

        self,

        symbol
    ):

        symbol = symbol.upper()

        if symbol in self.symbols:

            return

        self.symbols.add(
            symbol
        )

        try:

            self.stream.subscribe_quotes(

                self.on_quote,

                symbol
            )

            self.stream.subscribe_bars(

                self.on_bar,

                symbol
            )

            self.stream.subscribe_trades(

                self.on_trade,

                symbol
            )

            self.logger.info(

                f"Alpaca Market Data Subscribed | "

                f"{symbol}"
            )

            if self.event_bus:

                self.event_bus.publish(

                    MARKET_DATA_SUBSCRIBED,

                    {

                        "symbol":
                        symbol,

                        "source":
                        "AlpacaMarketDataService"
                    }
                )

        except Exception as error:

            self.handle_error(
                error
            )


    # ====================================
    # QUOTE HANDLER
    # ====================================

    async def on_quote(

        self,

        quote
    ):

        try:

            symbol = (
                quote.symbol
            )

            bid_price = float(
                quote.bid_price
            )

            ask_price = float(
                quote.ask_price
            )

            mid_price = (

                bid_price
                +
                ask_price

            ) / 2

            spread = (

                ask_price
                -
                bid_price
            )

            liquidity_score = 0

            if mid_price > 0:

                liquidity_score = max(

                    0,

                    1 - (
                        spread
                        /
                        mid_price
                    )
                )

            timestamp = getattr(
                quote,
                "timestamp",
                None
            )

            volume = (

                self.latest_bars
                .get(
                    symbol,
                    {}
                )
                .get(
                    "volume",
                    0
                )
            )

            market_data = {

                "symbol":
                symbol,

                "price":
                format_price(
                    mid_price
                ),

                "bid_price":
                format_price(
                    bid_price
                ),

                "ask_price":
                format_price(
                    ask_price
                ),

                "spread":
                format_price(
                    spread
                ),

                "volume":
                volume,

                "timestamp":
                format_timestamp(timestamp)
                if timestamp
                else None,

                "volatility":
                0,

                "liquidity_score":
                round(
                    liquidity_score,
                    4
                ),

                "source":
                "ALPACA_QUOTE"
            }

            self.latest_quotes[
                symbol
            ] = market_data

            self.latest_prices[
                symbol
            ] = market_data[
                "price"
            ]

            self.market_state.update(

                symbol=
                symbol,

                price=
                market_data[
                    "price"
                ],

                volume=
                market_data[
                    "volume"
                ],

                bid_price=
                market_data[
                    "bid_price"
                ],

                ask_price=
                market_data[
                    "ask_price"
                ],

                volatility=
                market_data[
                    "volatility"
                ],

                liquidity_score=
                market_data[
                    "liquidity_score"
                ],

                timestamp=
                market_data[
                    "timestamp"
                ]
            )

            self.event_bus.publish(

                MARKET_UPDATE_EVENT,

                market_data
            )

        except Exception as error:

            self.handle_error(
                error
            )


    # ====================================
    # BAR HANDLER
    # ====================================

    async def on_bar(

        self,

        bar
    ):

        try:

            symbol = (
                bar.symbol
            )

            price = float(
                bar.close
            )

            volume = int(
                bar.volume
            )

            timestamp = getattr(
                bar,
                "timestamp",
                None
            )

            market_data = {

                "symbol":
                symbol,

                "price":
                format_price(
                    price
                ),

                "volume":
                volume,

                "timestamp":
                format_timestamp(timestamp)
                if timestamp
                else None,

                "source":
                "ALPACA_BAR"
            }

            self.latest_bars[
                symbol
            ] = market_data

            self.latest_prices[
                symbol
            ] = market_data[
                "price"
            ]

            self.market_state.update(

                symbol=
                symbol,

                price=
                market_data[
                    "price"
                ],

                volume=
                volume,

                timestamp=
                market_data[
                    "timestamp"
                ]
            )

            self.event_bus.publish(

                MARKET_UPDATE_EVENT,

                market_data
            )

        except Exception as error:

            self.handle_error(
                error
            )


    # ====================================
    # TRADE HANDLER
    # ====================================

    async def on_trade(

        self,

        trade
    ):

        try:

            symbol = (
                trade.symbol
            )

            price = float(
                trade.price
            )

            timestamp = getattr(
                trade,
                "timestamp",
                None
            )

            size = getattr(
                trade,
                "size",
                0
            )

            market_data = {

                "symbol":
                symbol,

                "price":
                format_price(
                    price
                ),

                "volume":
                int(
                    size
                )
                if size
                else 0,

                "timestamp":
                format_timestamp(timestamp)
                if timestamp
                else None,

                "source":
                "ALPACA_TRADE"
            }

            self.latest_prices[
                symbol
            ] = market_data[
                "price"
            ]

            self.market_state.update(

                symbol=
                symbol,

                price=
                market_data[
                    "price"
                ],

                volume=
                market_data[
                    "volume"
                ],

                timestamp=
                market_data[
                    "timestamp"
                ]
            )

            self.event_bus.publish(

                MARKET_UPDATE_EVENT,

                market_data
            )

        except Exception as error:

            self.handle_error(
                error
            )


    # ====================================
    # HANDLE ERROR
    # ====================================

    def handle_error(

        self,

        error
    ):

        self.logger.error(

            f"Alpaca Market Data Error | "

            f"{error}"
        )

        if self.event_bus:

            self.event_bus.publish(

                MARKET_DATA_ERROR,

                {

                    "source":
                    "AlpacaMarketDataService",

                    "error":
                    str(error)
                }
            )


    # ====================================
    # START
    # ====================================

    def start(self):

        try:

            self.running = True

            self.logger.warning(

                f"Starting Alpaca Market Data Stream | "

                f"Feed={self.feed.value} | "

                f"Symbols={list(self.symbols)}"
            )

            self.event_bus.publish(

                MARKET_DATA_CONNECTED,

                {

                    "source":
                    "AlpacaMarketDataService",

                    "feed":
                    self.feed.value,

                    "symbols":
                    list(
                        self.symbols
                    )
                }
            )

            for symbol in list(
                self.symbols
            ):

                self.stream.subscribe_quotes(

                    self.on_quote,

                    symbol
                )

                self.stream.subscribe_bars(

                    self.on_bar,

                    symbol
                )

                self.stream.subscribe_trades(

                    self.on_trade,

                    symbol
                )

            self.stream.run()

        except Exception as error:

            self.handle_error(
                error
            )


    # ====================================
    # START ASYNC
    # ====================================

    def start_async(self):

        self.thread = threading.Thread(

            target=
            self.start,

            daemon=True
        )

        self.thread.start()

        self.logger.info(
            "Alpaca Market Data Thread Started"
        )


    # ====================================
    # STOP
    # ====================================

    def stop(self):

        self.logger.warning(
            "Stopping Alpaca Market Data Stream"
        )

        self.running = False

        try:

            self.stream.stop()

            self.event_bus.publish(

                MARKET_DATA_DISCONNECTED,

                {

                    "source":
                    "AlpacaMarketDataService"
                }
            )

        except Exception as error:

            self.handle_error(
                error
            )