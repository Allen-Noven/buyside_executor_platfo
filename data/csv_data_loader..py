# ====================================
# data_loader.py
# ====================================

from datetime import datetime

import pandas as pd

from alpaca.data.historical import (
    StockHistoricalDataClient
)

from alpaca.data.requests import (
    StockBarsRequest
)

from alpaca.data.timeframe import (
    TimeFrame
)

from utils.config import (

    API_KEY,

    SECRET_KEY,

    DEFAULT_SYMBOL
)

from utils.logger import (
    SystemLogger
)


class MarketDataLoader:

    def __init__(self):

        # ====================================
        # LOGGER
        # ====================================

        self.logger = (
            SystemLogger()
        )


        # ====================================
        # ALPACA CLIENT
        # ====================================

        self.client = (

            StockHistoricalDataClient(

                API_KEY,

                SECRET_KEY
            )
        )


    # ====================================
    # FETCH HISTORICAL BARS
    # ====================================

    def get_historical_bars(

        self,

        symbol=DEFAULT_SYMBOL,

        start_date=None,

        end_date=None,

        timeframe=TimeFrame.Minute

    ):

        # ====================================
        # DEFAULT DATES
        # ====================================

        if start_date is None:

            start_date = datetime(
                2025,
                1,
                3
            )

        if end_date is None:

            end_date = datetime(
                2025,
                1,
                4
            )


        self.logger.info(

            f"Loading Historical Data | "
            f"{symbol}"
        )


        # ====================================
        # REQUEST
        # ====================================

        request = StockBarsRequest(

            symbol_or_symbols=[symbol],

            timeframe=timeframe,

            start=start_date,

            end=end_date
        )


        # ====================================
        # FETCH DATA
        # ====================================

        bars = (

            self.client.get_stock_bars(
                request
            )
        )


        # ====================================
        # DATAFRAME
        # ====================================

        df = bars.df.reset_index()


        # ====================================
        # FORMAT TIMESTAMP
        # ====================================

        if "timestamp" in df.columns:

            df["timestamp"] = (

                df["timestamp"]
                .astype(str)
            )


        # ====================================
        # ESTIMATED BID/ASK
        # ====================================

        df["bid_price"] = (

            df["close"] - 0.01
        )

        df["ask_price"] = (

            df["close"] + 0.01
        )


        # ====================================
        # SPREAD
        # ====================================

        df["spread"] = (

            df["ask_price"]
            -
            df["bid_price"]
        )


        # ====================================
        # VOLATILITY
        # ====================================

        df["returns"] = (

            df["close"]
            .pct_change()
        )

        df["volatility"] = (

            df["returns"]
            .rolling(10)
            .std()
        )


        # ====================================
        # LIQUIDITY SCORE
        # ====================================

        max_volume = (
            df["volume"].max()
        )

        df["liquidity_score"] = (

            df["volume"]
            / max_volume
        )


        self.logger.info(

            f"Loaded "
            f"{len(df)} bars"
        )

        return df


    # ====================================
    # SAVE CSV
    # ====================================

    def save_to_csv(

        self,

        df,

        path

    ):

        df.to_csv(

            path,

            index=False
        )

        self.logger.info(

            f"Saved Market Data | "
            f"{path}"
        )