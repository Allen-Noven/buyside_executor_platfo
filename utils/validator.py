# ====================================
# validators.py
# ====================================

from utils.constants import (

    BUY,

    SELL,

    TWAP,

    VWAP,

    POV
)

from utils.config import (

    MAX_ORDER_SIZE,

    WATCHLIST
)


# ====================================
# VALID STRATEGIES
# ====================================

VALID_STRATEGIES = [

    TWAP,

    VWAP,

    POV
]


# ====================================
# VALID SIDES
# ====================================

VALID_SIDES = [

    BUY,

    SELL
]


# ====================================
# VALIDATE SYMBOL
# ====================================

def validate_symbol(symbol):

    if symbol is None:

        raise ValueError(

            "Symbol cannot be None"
        )

    if not isinstance(symbol, str):

        raise TypeError(

            "Symbol must be string"
        )

    if len(symbol.strip()) == 0:

        raise ValueError(

            "Symbol cannot be empty"
        )

    if symbol not in WATCHLIST:

        raise ValueError(

            f"Unsupported symbol: "
            f"{symbol}"
        )

    return True


# ====================================
# VALIDATE QUANTITY
# ====================================

def validate_quantity(qty):

    if qty is None:

        raise ValueError(

            "Quantity cannot be None"
        )

    if not isinstance(qty, (int, float)):

        raise TypeError(

            "Quantity must be numeric"
        )

    if qty <= 0:

        raise ValueError(

            "Quantity must be positive"
        )

    if qty > MAX_ORDER_SIZE:

        raise ValueError(

            f"Quantity exceeds "
            f"MAX_ORDER_SIZE: "
            f"{MAX_ORDER_SIZE}"
        )

    return True


# ====================================
# VALIDATE SIDE
# ====================================

def validate_side(side):

    if side not in VALID_SIDES:

        raise ValueError(

            f"Invalid side: {side}"
        )

    return True


# ====================================
# VALIDATE STRATEGY
# ====================================

def validate_strategy(strategy):

    if strategy not in VALID_STRATEGIES:

        raise ValueError(

            f"Invalid strategy: "
            f"{strategy}"
        )

    return True


# ====================================
# VALIDATE NOTIONAL
# ====================================

def validate_notional(

    qty,

    price
):

    if price is None:

        raise ValueError(

            "Price cannot be None"
        )

    notional = qty * price

    if notional <= 0:

        raise ValueError(

            "Invalid notional value"
        )

    return True


# ====================================
# VALIDATE PARENT ORDER
# ====================================

def validate_parent_order(

    parent_order
):

    if parent_order is None:

        raise ValueError(

            "Parent order cannot be None"
        )

    validate_symbol(
        parent_order.symbol
    )

    validate_quantity(
        parent_order.total_qty
    )

    validate_side(
        parent_order.side
    )

    validate_strategy(
        parent_order.strategy
    )

    return True