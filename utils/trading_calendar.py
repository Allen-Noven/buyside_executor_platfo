# ====================================
# trading_calendar.py
# ====================================

from datetime import (

    datetime,

    time,

    timedelta
)

import pytz

from utils.config import (
    MARKET_TIMEZONE
)

from utils.constants import (

    PREMARKET,

    REGULAR,

    AFTERHOURS,

    CLOSED
)


# ====================================
# MARKET TIMEZONE
# ====================================

MARKET_TZ = pytz.timezone(
    MARKET_TIMEZONE
)


# ====================================
# MARKET HOURS
# ====================================

MARKET_OPEN = time(
    9,
    30
)

MARKET_CLOSE = time(
    16,
    0
)

PREMARKET_OPEN = time(
    4,
    0
)

AFTERHOURS_CLOSE = time(
    20,
    0
)


# ====================================
# GET CURRENT MARKET TIME
# ====================================

def get_market_time():

    return datetime.now(
        MARKET_TZ
    )


# ====================================
# CHECK WEEKDAY
# ====================================

def is_weekday(

    current_dt=None
):

    if current_dt is None:

        current_dt = (
            get_market_time()
        )

    return current_dt.weekday() < 5


# ====================================
# CHECK MARKET OPEN
# ====================================

def is_market_open():

    current_dt = (
        get_market_time()
    )

    if not is_weekday(current_dt):

        return False

    current_time = (
        current_dt.time()
    )

    return (

        MARKET_OPEN
        <= current_time
        <= MARKET_CLOSE
    )


# ====================================
# CHECK PREMARKET
# ====================================

def is_premarket():

    current_dt = (
        get_market_time()
    )

    current_time = (
        current_dt.time()
    )

    return (

        PREMARKET_OPEN
        <= current_time
        <
        MARKET_OPEN
    )


# ====================================
# CHECK AFTERHOURS
# ====================================

def is_afterhours():

    current_dt = (
        get_market_time()
    )

    current_time = (
        current_dt.time()
    )

    return (

        MARKET_CLOSE
        <
        current_time
        <=
        AFTERHOURS_CLOSE
    )


# ====================================
# GET MARKET SESSION
# ====================================

def get_market_session():

    if not is_weekday():

        return CLOSED

    if is_premarket():

        return PREMARKET

    if is_market_open():

        return REGULAR

    if is_afterhours():

        return AFTERHOURS

    return CLOSED


# ====================================
# SECONDS TO MARKET OPEN
# ====================================

def seconds_to_market_open():

    current_dt = (
        get_market_time()
    )

    market_open_dt = (

        current_dt.replace(

            hour=9,

            minute=30,

            second=0,

            microsecond=0
        )
    )

    if current_dt.time() > MARKET_OPEN:

        market_open_dt += (
            timedelta(days=1)
        )

    delta = (
        market_open_dt
        - current_dt
    )

    return max(

        int(delta.total_seconds()),

        0
    )


# ====================================
# SECONDS TO MARKET CLOSE
# ====================================

def seconds_to_market_close():

    current_dt = (
        get_market_time()
    )

    market_close_dt = (

        current_dt.replace(

            hour=16,

            minute=0,

            second=0,

            microsecond=0
        )
    )

    delta = (
        market_close_dt
        - current_dt
    )

    return max(

        int(delta.total_seconds()),

        0
    )


# ====================================
# CAN EXECUTE ORDERS
# ====================================

def can_execute_orders():

    return is_market_open()


# ====================================
# GET TRADING DAY
# ====================================

def get_trading_day():

    current_dt = (
        get_market_time()
    )

    return current_dt.strftime(
        "%Y-%m-%d"
    )


# ====================================
# FORMAT MARKET TIME
# ====================================

def format_market_time():

    return get_market_time().strftime(

        "%Y-%m-%d %H:%M:%S %Z"
    )
