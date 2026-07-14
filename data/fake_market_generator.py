# ====================================
# fake_market_generator.py
# ====================================

import time
import random
import threading

from utils.logger import (
    SystemLogger
)

from utils.constants import (

    MARKET_UPDATE_EVENT,

    MARKET_DATA_SUBSCRIBED
)

from utils.config import (

    FAKE_MARKET_INTERVAL,

    DEFAULT_SYMBOL,

    DEFAULT_MARKET_DATA_SYMBOLS
)

from utils.helpers import (
    get_current_time
)


class SimulationMarketGenerator:


    # ====================================
    # INIT
    # ====================================

    def __init__(

        self,

        market_state,

        event_bus,

        symbols=None,

        start_price=172.0,

        price_volatility=0.5
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

        self.start_price = (
            start_price
        )

        self.price_volatility = (
            price_volatility
        )

        self.prices = {}

        for symbol in self.symbols:

            self.prices[
                symbol
            ] = (

                start_price

                +

                random.uniform(
                    -3,
                    3
                )
            )

        self.running = False

        self.market_thread = None

        self.logger.info(

            f"Simulation Market Generator Initialized | "

            f"Symbols={list(self.symbols)}"
        )


    # ====================================
    # SUBSCRIBE SYMBOL
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

        self.prices[
            symbol
        ] = (

            self.start_price

            +

            random.uniform(
                -5,
                5
            )
        )

        self.logger.info(

            f"Simulation Market Subscribed | "

            f"{symbol}"
        )

        if self.event_bus:

            self.event_bus.publish(

                MARKET_DATA_SUBSCRIBED,

                {

                    "symbol":
                    symbol,

                    "source":
                    "SimulationMarketGenerator"
                }
            )


    # ====================================
    # START ASYNC
    # ====================================

    def start_async(self):

        self.market_thread = threading.Thread(

            target=
            self.start,

            daemon=True
        )

        self.market_thread.start()

        self.logger.info(
            "Simulation Market Thread Started"
        )


    # ====================================
    # START GENERATOR
    # ====================================

    def start(self):

        self.logger.warning(

            f"Starting Simulation Market | "

            f"Symbols={list(self.symbols)}"
        )

        self.running = True

        while self.running:

            try:

                symbols = list(
                    self.symbols
                )

                for symbol in symbols:

                    self.generate_tick(
                        symbol
                    )

                time.sleep(
                    FAKE_MARKET_INTERVAL
                )

            except Exception as error:

                self.logger.error(

                    f"Simulation Market Error | "

                    f"{error}"
                )

                time.sleep(1)


    # ====================================
    # GENERATE TICK
    # ====================================

    def generate_tick(

        self,

        symbol
    ):

        if symbol not in self.prices:

            self.prices[
                symbol
            ] = self.start_price

        price = (

            self.prices[
                symbol
            ]

            +

            random.uniform(

                -self.price_volatility,

                self.price_volatility
            )
        )

        price = round(
            max(
                price,
                1
            ),
            2
        )

        self.prices[
            symbol
        ] = price

        spread = round(

            random.uniform(
                0.01,
                0.08
            ),

            2
        )

        bid_price = round(

            price
            -
            spread / 2,

            2
        )

        ask_price = round(

            price
            +
            spread / 2,

            2
        )

        volume = random.randint(
            1000,
            10000
        )

        liquidity_score = random.randint(
            20,
            100
        )

        simulated_volatility = round(

            random.uniform(
                0.1,
                3.0
            ),

            2
        )

        self.market_state.update(

            symbol=
            symbol,

            price=
            price,

            volume=
            volume,

            bid_price=
            bid_price,

            ask_price=
            ask_price,

            volatility=
            simulated_volatility,

            liquidity_score=
            liquidity_score,

            timestamp=
            get_current_time()
        )

        market_event = {

            "timestamp":
            get_current_time(),

            "symbol":
            symbol,

            "price":
            price,

            "bid_price":
            bid_price,

            "ask_price":
            ask_price,

            "spread":
            spread,

            "volume":
            volume,

            "volatility":
            simulated_volatility,

            "liquidity_score":
            liquidity_score,

            "source":
            "SIMULATION"
        }

        self.event_bus.publish(

            MARKET_UPDATE_EVENT,

            market_event
        )

        self.logger.info(

            f"Simulation Tick | "

            f"{symbol} | "

            f"Price={price}"
        )


    # ====================================
    # STOP
    # ====================================

    def stop(self):

        self.running = False

        self.logger.warning(
            "Simulation Market Generator Stopped"
        )


    # ====================================
    # GET LATEST SNAPSHOT
    # ====================================

    def get_latest_snapshot(

        self,

        symbol
    ):

        return self.market_state.get_snapshot(
            symbol.upper()
        )