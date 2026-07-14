# ====================================
# helpers.py
# ====================================

from datetime import datetime

import pytz

from utils.config import (
    MARKET_TIMEZONE
)


# ====================================
# TIMEZONE
# ====================================

MARKET_TZ = pytz.timezone(
    MARKET_TIMEZONE
)


# ====================================
# FORMAT PRICE
# ====================================

def format_price(price):

    if price is None:

        return None

    return round(

        float(price),

        2
    )


# ====================================
# FORMAT QUANTITY
# ====================================

def format_quantity(qty):

    if qty is None:

        return None

    return round(

        float(qty),

        4
    )


# ====================================
# CURRENT MARKET TIME
# ====================================

def get_current_time():

    return datetime.now(
        MARKET_TZ
    )


# ====================================
# CURRENT TIMESTAMP STRING
# ====================================

def get_current_timestamp():

    return format_timestamp(
        get_current_time()
    )


# ====================================
# FORMAT TIMESTAMP
# ====================================

def format_timestamp(timestamp):

    if timestamp is None:

        return None

    return timestamp.strftime(

        "%Y-%m-%d %H:%M:%S"
    )


# ====================================
# CALCULATE NOTIONAL
# ====================================

def calculate_notional(

    qty,

    price
):

    if qty is None or price is None:

        return 0

    return qty * price


# ====================================
# CALCULATE SLIPPAGE
# ====================================

def calculate_slippage(

    arrival_price,

    fill_price
):

    if (

        arrival_price is None
        or
        fill_price is None

    ):

        return 0

    return (

        fill_price
        - arrival_price
    )


# ====================================
# CALCULATE BPS
# ====================================

def calculate_bps(

    arrival_price,

    fill_price
):

    if (

        arrival_price is None
        or
        fill_price is None
        or
        arrival_price == 0

    ):

        return 0

    return (

        (

            fill_price
            - arrival_price

        )

        / arrival_price

    ) * 10000


# ====================================
# CALCULATE PARTICIPATION RATE
# ====================================

def calculate_participation_rate(

    qty,

    market_volume
):

    if (

        market_volume is None
        or
        market_volume == 0

    ):

        return 0

    return qty / market_volume


# ====================================
# SAFE DIVISION
# ====================================

def safe_divide(

    numerator,

    denominator
):

    if denominator == 0:

        return 0

    return numerator / denominator


# ====================================
# FORMAT ORDER LOG
# ====================================

def format_order_log(

    symbol,

    qty,

    status
):

    return (

        f"Symbol: {symbol} | "

        f"Qty: {qty} | "

        f"Status: {status}"
    )


# ====================================
# FORMAT EXECUTION LOG
# ====================================

def format_execution_log(

    symbol,

    side,

    qty,

    strategy
):

    return (

        f"{side} "

        f"{qty} "

        f"{symbol} "

        f"using "

        f"{strategy}"
    )