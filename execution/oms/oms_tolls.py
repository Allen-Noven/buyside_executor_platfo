# ====================================
# oms_tools.py
# ====================================

from utils.logger import (
    SystemLogger
)


logger = SystemLogger()


# ====================================
# NORMALIZE ORDER STATUS
# ====================================

def normalize_order_status(

    status
):

    if status is None:

        return "UNKNOWN"

    status = str(status).lower()

    mapping = {

        "new":
        "OPEN",

        "accepted":
        "OPEN",

        "pending":
        "OPEN",

        "partially_filled":
        "PARTIALLY_FILLED",

        "filled":
        "FILLED",

        "canceled":
        "CANCELLED",

        "cancelled":
        "CANCELLED",

        "rejected":
        "REJECTED"
    }

    return mapping.get(

        status,

        status.upper()
    )


# ====================================
# BUILD ORDER RECORD
# ====================================

def build_order_record(

    order_id,

    symbol,

    qty,

    side,

    status,

    fill_price=None,

    timestamp=None
):

    return {

        "order_id":
        str(order_id),

        "symbol":
        symbol,

        "qty":
        qty,

        "side":
        side,

        "status":
        normalize_order_status(
            status
        ),

        "fill_price":
        fill_price,

        "timestamp":
        timestamp
    }


# ====================================
# CALCULATE POSITION QTY
# ====================================

def calculate_position_quantity(

    orders
):

    positions = {}

    for order in orders:

        status = normalize_order_status(

            order.get(
                "status"
            )
        )

        if status != "FILLED":

            continue

        symbol = order.get(
            "symbol"
        )

        qty = order.get(
            "qty",
            0
        )

        side = order.get(
            "side"
        )

        signed_qty = qty

        if side == "SELL":

            signed_qty = -qty

        if symbol not in positions:

            positions[symbol] = {

                "quantity": 0
            }

        positions[symbol]["quantity"] += (
            signed_qty
        )

    return positions


# ====================================
# FILTER OPEN ORDERS
# ====================================

def filter_open_orders(

    orders
):

    open_status = [

        "OPEN",

        "PARTIALLY_FILLED"
    ]

    return [

        order

        for order in orders

        if normalize_order_status(

            order.get(
                "status"
            )

        ) in open_status
    ]


# ====================================
# FILTER FILLED ORDERS
# ====================================

def filter_filled_orders(

    orders
):

    return [

        order

        for order in orders

        if normalize_order_status(

            order.get(
                "status"
            )

        ) == "FILLED"
    ]


# ====================================
# GET ORDER COUNT
# ====================================

def get_order_count(

    orders
):

    return len(orders)


# ====================================
# SHOW OMS SUMMARY
# ====================================

def show_oms_summary(

    orders
):

    total_orders = len(orders)

    open_orders = len(

        filter_open_orders(
            orders
        )
    )

    filled_orders = len(

        filter_filled_orders(
            orders
        )
    )

    print(

        "\n========== OMS SUMMARY ==========\n"
    )

    print(

        f"Total Orders: "
        f"{total_orders}"
    )

    print(

        f"Open Orders: "
        f"{open_orders}"
    )

    print(

        f"Filled Orders: "
        f"{filled_orders}"
    )

    print(

        "\n=================================\n"
    )

    logger.info(
        "OMS Summary Displayed"
    )