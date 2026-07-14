# ====================================
# app.py
# ====================================

import os
import sys
import json
import queue
import threading

import requests
import streamlit as st
import websocket
import pandas as pd

from dashboard.order_entry import (
    OrderEntryPanel
)

from dashboard.pnl_dashboard import (
    PnLDashboard
)

from utils.runtime_mode import (
    RUNTIME_MODE
)

from utils.config import (
    DATA_MODE
)


# ====================================
# ADD PROJECT ROOT
# ====================================

PROJECT_ROOT = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

if PROJECT_ROOT not in sys.path:

    sys.path.append(
        PROJECT_ROOT
    )


# ====================================
# CONFIG
# ====================================

API_URL = (
    "http://127.0.0.1:8000"
)

WEBSOCKET_URL = (
    "ws://127.0.0.1:8000/ws"
)


# ====================================
# DISABLE LOCAL PROXY
# ====================================

os.environ["NO_PROXY"] = (
    "127.0.0.1,localhost"
)

os.environ["no_proxy"] = (
    "127.0.0.1,localhost"
)


# ====================================
# API SESSION
# ====================================

api_session = (
    requests.Session()
)

api_session.trust_env = False


# ====================================
# PAGE CONFIG
# ====================================

st.set_page_config(
    page_title="Smart Execution Dashboard",
    layout="wide"
)


# ====================================
# SAFE API GET
# ====================================

def safe_get(

    path,

    default=None,

    timeout=8
):

    try:

        response = api_session.get(

            f"{API_URL}{path}",

            timeout=timeout
        )

        if response.status_code == 200:

            return response.json()

        print(

            f"API GET Non-200 | "

            f"{path} | "

            f"{response.status_code}"
        )

    except Exception as error:

        print(

            f"API GET Failed | "

            f"{path} | "

            f"{error}"
        )

    return default


# ====================================
# SESSION STATE INIT
# ====================================

if "initialized" not in st.session_state:

    st.session_state.initialized = True

    st.session_state.websocket_connected = False

    st.session_state.ws_started = False

    st.session_state.ws_message_queue = queue.Queue()

    st.session_state.ws_status_queue = queue.Queue()

    st.session_state.market_data = {}

    st.session_state.market_snapshots = {}

    st.session_state.runtime_status = {}

    st.session_state.portfolio = {}

    st.session_state.positions = {}

    st.session_state.fills = []

    st.session_state.active_orders = {}

    st.session_state.alerts = []

    st.session_state.parent_orders = {}

    st.session_state.parent_order_notifications = []

    st.session_state.execution_status = {

        "status":
        "IDLE",

        "halted":
        False,

        "reason":
        None
    }


# ====================================
# UPDATE PARENT ORDER STATE
# ====================================

def update_parent_order_state(

    event,

    payload
):

    parent_order_id = (

        payload.get(
            "parent_order_id"
        )

        or

        payload.get(
            "order_id"
        )

        or

        f"{payload.get('symbol', 'UNKNOWN')}_{payload.get('strategy', 'UNKNOWN')}"
    )

    existing = (

        st.session_state
        .parent_orders
        .get(
            parent_order_id,
            {}
        )
    )

    updated = {

        **existing,

        "parent_order_id":
        parent_order_id,

        "symbol":
        payload.get(
            "symbol",
            existing.get(
                "symbol",
                ""
            )
        ),

        "side":
        payload.get(
            "side",
            existing.get(
                "side",
                ""
            )
        ),

        "strategy":
        payload.get(
            "strategy",
            existing.get(
                "strategy",
                ""
            )
        ),

        "total_qty":
        payload.get(
            "total_qty",
            existing.get(
                "total_qty",
                0
            )
        ),

        "total_children":
        payload.get(
            "total_children",
            existing.get(
                "total_children",
                0
            )
        ),

        "completed_children":
        payload.get(
            "completed_children",
            existing.get(
                "completed_children",
                0
            )
        ),

        "current_slice":
        payload.get(
            "current_slice",
            existing.get(
                "current_slice",
                0
            )
        ),

        "completion_pct":
        payload.get(
            "completion_pct",
            existing.get(
                "completion_pct",
                0
            )
        ),

        "status":
        payload.get(
            "status",
            event
        ),

        "reason":
        payload.get(
            "reason",
            existing.get(
                "reason",
                ""
            )
        )
    }

    st.session_state.parent_orders[
        parent_order_id
    ] = updated

    if event == "PARENT_ORDER_SPLIT":

        st.session_state.parent_order_notifications.append(

            {

                "level":
                "success",

                "message":
                f"Parent Order Split Successfully | "
                f"{updated.get('symbol', '')} | "
                f"{updated.get('total_children', 0)} child orders"
            }
        )

    elif event == "PARENT_ORDER_COMPLETED":

        st.session_state.parent_order_notifications.append(

            {

                "level":
                "success",

                "message":
                f"Parent Order Completed | "
                f"{updated.get('symbol', '')} | "
                f"{updated.get('completion_pct', 100)}%"
            }
        )

    elif event == "PARENT_ORDER_HALTED":

        st.session_state.parent_order_notifications.append(

            {

                "level":
                "warning",

                "message":
                f"Parent Order Halted | "
                f"{updated.get('symbol', '')} | "
                f"{updated.get('reason', '')}"
            }
        )


# ====================================
# PROCESS WEBSOCKET EVENT
# ====================================

def process_websocket_event(

    event,

    payload
):

    if event in [

        "MARKET_UPDATE",

        "MARKET_UPDATE_EVENT"
    ]:

        symbol = payload.get(
            "symbol"
        )

        if symbol:

            st.session_state.market_snapshots[
                symbol
            ] = payload

            st.session_state.market_data = payload

    elif event in [

        "EXECUTION_STARTED",

        "EXECUTION_COMPLETED"
    ]:

        st.session_state.execution_status = {

            "status":
            event,

            "halted":
            False,

            "reason":
            None
        }

    elif event in [

        "ORDER_UPDATE"
    ]:

        st.session_state.execution_status = {

            "status":
            payload.get(
                "status",
                "UNKNOWN"
            ),

            "halted":
            payload.get(
                "status"
            ) == "HALTED",

            "reason":
            payload.get(
                "reason"
            )
        }

    elif event in [

        "PARENT_ORDER_SPLIT",

        "PARENT_ORDER_PROGRESS",

        "PARENT_ORDER_COMPLETED",

        "PARENT_ORDER_HALTED"
    ]:

        update_parent_order_state(

            event,

            payload
        )

    elif event in [

        "ORDER_FILLED_EVENT",

        "FILL_UPDATE"
    ]:

        st.session_state.fills.append(
            payload
        )

    elif event in [

        "POSITION_UPDATE",

        "POSITION_UPDATE_EVENT"
    ]:

        portfolio = payload.get(
            "portfolio",
            {}
        )

        st.session_state.portfolio = portfolio

    else:

        st.session_state.alerts.append(

            {

                "event":
                event,

                "payload":
                payload
            }
        )


# ====================================
# DRAIN WEBSOCKET QUEUES
# ====================================

def drain_websocket_queues():

    while not st.session_state.ws_status_queue.empty():

        status_event = (

            st.session_state
            .ws_status_queue
            .get()
        )

        event_type = status_event.get(
            "type"
        )

        if event_type == "connected":

            st.session_state.websocket_connected = True

        elif event_type == "disconnected":

            st.session_state.websocket_connected = False

            st.session_state.ws_started = False

        elif event_type == "error":

            st.session_state.websocket_connected = False

            st.session_state.ws_started = False

            st.session_state.alerts.append(

                {

                    "event":
                    "WEBSOCKET_ERROR",

                    "payload":
                    status_event
                }
            )

    while not st.session_state.ws_message_queue.empty():

        message = (

            st.session_state
            .ws_message_queue
            .get()
        )

        process_websocket_event(

            event=
            message.get(
                "event"
            ),

            payload=
            message.get(
                "payload",
                {}
            )
        )


# ====================================
# WEBSOCKET THREAD
# ====================================

def websocket_listener(

    message_queue,

    status_queue
):

    def on_open(ws):

        status_queue.put(

            {
                "type":
                "connected"
            }
        )

        print(
            "WebSocket Connected"
        )


    def on_close(

        ws,

        close_status_code,

        close_msg
    ):

        status_queue.put(

            {
                "type":
                "disconnected",

                "code":
                close_status_code,

                "message":
                close_msg
            }
        )

        print(
            "WebSocket Disconnected"
        )


    def on_error(

        ws,

        error
    ):

        status_queue.put(

            {
                "type":
                "error",

                "message":
                str(error)
            }
        )

        print(

            f"WebSocket Error | "

            f"{error}"
        )


    def on_message(

        ws,

        message
    ):

        try:

            data = json.loads(
                message
            )

            message_queue.put(
                data
            )

        except Exception as error:

            status_queue.put(

                {
                    "type":
                    "error",

                    "message":
                    f"Message Parse Failed | {error}"
                }
            )


    ws = websocket.WebSocketApp(

        WEBSOCKET_URL,

        on_open=on_open,

        on_close=on_close,

        on_error=on_error,

        on_message=on_message
    )

    ws.run_forever(

        http_proxy_host=None,

        http_proxy_port=None,

        proxy_type=None
    )


# ====================================
# START WEBSOCKET ONCE
# ====================================

if not st.session_state.ws_started:

    websocket_thread = threading.Thread(

        target=
        websocket_listener,

        args=(

            st.session_state.ws_message_queue,

            st.session_state.ws_status_queue
        ),

        daemon=True
    )

    websocket_thread.start()

    st.session_state.ws_started = True


# ====================================
# DRAIN QUEUES BEFORE RENDER
# ====================================

drain_websocket_queues()


# ====================================
# SIDEBAR CONTROLS
# ====================================

st.sidebar.title(
    "Controls"
)

if st.sidebar.button(

    "Refresh Dashboard",

    use_container_width=True
):

    st.rerun()


# ====================================
# LOAD API SNAPSHOTS
# ====================================

runtime_status = safe_get(
    "/health",
    {},
    timeout=5
)

portfolio = safe_get(
    "/portfolio",
    {},
    timeout=8
)

positions = safe_get(
    "/positions",
    {},
    timeout=10
)

fills = safe_get(
    "/fills",
    [],
    timeout=8
)

active_orders = safe_get(
    "/orders/active",
    {},
    timeout=8
)

market_snapshots = safe_get(
    "/market",
    {},
    timeout=8
)


# ====================================
# UPDATE SESSION STATE FROM SNAPSHOTS
# ====================================

if runtime_status:

    st.session_state.runtime_status = runtime_status

if portfolio:

    st.session_state.portfolio = portfolio

if positions:

    st.session_state.positions = positions

if fills:

    st.session_state.fills = fills

if active_orders:

    st.session_state.active_orders = active_orders

if market_snapshots:

    st.session_state.market_snapshots = market_snapshots


# ====================================
# TITLE
# ====================================

st.title(
    "Smart Execution Dashboard"
)


# ====================================
# PARENT ORDER NOTIFICATIONS
# ====================================

for notification in st.session_state.parent_order_notifications[-5:]:

    level = notification.get(
        "level",
        "info"
    )

    message = notification.get(
        "message",
        ""
    )

    if level == "success":

        st.success(
            message
        )

    elif level == "warning":

        st.warning(
            message
        )

    elif level == "error":

        st.error(
            message
        )

    else:

        st.info(
            message
        )


# ====================================
# MODE BANNER
# ====================================

if RUNTIME_MODE == "LIVE":

    st.error(
        "🚨 LIVE TRADING MODE"
    )

elif RUNTIME_MODE == "PAPER":

    st.warning(
        "🟡 PAPER TRADING MODE"
    )

else:

    st.success(
        "✅ SIMULATION MODE"
    )


# ====================================
# TOP STATUS
# ====================================

col1, col2, col3, col4 = st.columns(4)

with col1:

    st.metric(
        "Runtime Mode",
        RUNTIME_MODE
    )

with col2:

    st.metric(
        "Data Mode",
        DATA_MODE
    )

with col3:

    if st.session_state.websocket_connected:

        st.success(
            "WebSocket Connected"
        )

    else:

        st.error(
            "WebSocket Disconnected"
        )

with col4:

    st.metric(

        "Worker Running",

        st.session_state.runtime_status.get(
            "worker_running",
            "N/A"
        )
    )


st.markdown("---")


# ====================================
# ACCOUNT / PORTFOLIO
# ====================================

st.subheader(
    "Account & Portfolio"
)

account = (

    st.session_state
    .portfolio
    .get(
        "account",
        {}
    )
)

col1, col2, col3, col4 = st.columns(4)

with col1:

    st.metric(

        "Cash",

        account.get(
            "cash",
            0
        )
    )

with col2:

    st.metric(

        "Buying Power",

        account.get(
            "buying_power",
            0
        )
    )

with col3:

    st.metric(

        "Equity",

        account.get(
            "equity",
            0
        )
    )

with col4:

    st.metric(

        "Gross Exposure",

        st.session_state.portfolio.get(
            "gross_exposure",
            0
        )
    )


col5, col6, col7 = st.columns(3)

with col5:

    st.metric(

        "Realized PnL",

        st.session_state.portfolio.get(
            "total_realized_pnl",
            0
        )
    )

with col6:

    st.metric(

        "Unrealized PnL",

        st.session_state.portfolio.get(
            "total_unrealized_pnl",
            0
        )
    )

with col7:

    st.metric(

        "Position Count",

        st.session_state.portfolio.get(
            "total_positions",
            0
        )
    )


st.markdown("---")


# ====================================
# ORDER ENTRY
# ====================================

order_entry = (
    OrderEntryPanel()
)

order_entry.render()


st.markdown("---")


# ====================================
# PARENT ORDER PROGRESS
# ====================================

st.subheader(
    "Parent Order Progress"
)

parent_orders = (
    st.session_state.parent_orders
)

if (

    isinstance(
        parent_orders,
        dict
    )

    and

    len(parent_orders) > 0
):

    parent_order_rows = []

    for order in parent_orders.values():

        total_children = order.get(
            "total_children",
            0
        )

        completed_children = order.get(
            "completed_children",
            0
        )

        completion_pct = order.get(
            "completion_pct",
            0
        )

        parent_order_rows.append(

            {

                "parent_order_id":
                order.get(
                    "parent_order_id",
                    ""
                ),

                "symbol":
                order.get(
                    "symbol",
                    ""
                ),

                "side":
                order.get(
                    "side",
                    ""
                ),

                "strategy":
                order.get(
                    "strategy",
                    ""
                ),

                "total_qty":
                order.get(
                    "total_qty",
                    0
                ),

                "children":
                f"{completed_children}/{total_children}",

                "completion_pct":
                completion_pct,

                "status":
                order.get(
                    "status",
                    ""
                ),

                "reason":
                order.get(
                    "reason",
                    ""
                )
            }
        )

    parent_order_df = pd.DataFrame(
        parent_order_rows
    )

    st.dataframe(

        parent_order_df,

        use_container_width=True
    )

    for order in parent_orders.values():

        label = (

            f"{order.get('symbol', '')} | "
            f"{order.get('side', '')} | "
            f"{order.get('strategy', '')} | "
            f"{order.get('status', '')}"
        )

        pct = int(

            min(

                max(

                    order.get(
                        "completion_pct",
                        0
                    ),

                    0
                ),

                100
            )
        )

        st.write(
            label
        )

        st.progress(
            pct
        )

else:

    st.info(
        "No parent orders yet"
    )


st.markdown("---")


# ====================================
# MARKET DATA
# ====================================

st.subheader(
    "Market Data"
)

market_snapshots = (
    st.session_state.market_snapshots
)

if (

    isinstance(
        market_snapshots,
        dict
    )

    and

    len(market_snapshots) > 0
):

    if all(

        isinstance(v, dict)

        for v in market_snapshots.values()
    ):

        market_df = pd.DataFrame(

            list(
                market_snapshots.values()
            )
        )

        st.dataframe(

            market_df,

            use_container_width=True
        )

    else:

        st.json(
            market_snapshots
        )

else:

    st.info(
        "No market data yet"
    )


st.markdown("---")


# ====================================
# POSITIONS
# ====================================

st.subheader(
    "Positions"
)

positions = (
    st.session_state.positions
)

if (

    isinstance(
        positions,
        dict
    )

    and

    len(positions) > 0
):

    position_df = pd.DataFrame(

        list(
            positions.values()
        )
    )

    st.dataframe(

        position_df,

        use_container_width=True
    )

else:

    st.info(
        "No positions yet"
    )


st.markdown("---")


# ====================================
# ACTIVE ORDERS
# ====================================

st.subheader(
    "Active Orders"
)

active_orders = (
    st.session_state.active_orders
)

if (

    isinstance(
        active_orders,
        dict
    )

    and

    len(active_orders) > 0
):

    active_orders_df = pd.DataFrame(

        list(
            active_orders.values()
        )
    )

    st.dataframe(

        active_orders_df,

        use_container_width=True
    )

elif (

    isinstance(
        active_orders,
        list
    )

    and

    len(active_orders) > 0
):

    st.dataframe(

        pd.DataFrame(
            active_orders
        ),

        use_container_width=True
    )

else:

    st.info(
        "No active orders"
    )


st.markdown("---")


# ====================================
# RECENT FILLS
# ====================================

st.subheader(
    "Recent Fills"
)

fills = (
    st.session_state.fills
)

if len(fills) == 0:

    st.info(
        "No fills yet"
    )

else:

    st.dataframe(

        pd.DataFrame(
            fills[-50:]
        ),

        use_container_width=True
    )


st.markdown("---")


# ====================================
# PNL DASHBOARD
# ====================================

pnl_dashboard = (

    PnLDashboard(
        fills
    )
)

pnl_dashboard.render()


st.markdown("---")


# ====================================
# ALERTS
# ====================================

st.subheader(
    "Alerts / Runtime Events"
)

alerts = (
    st.session_state.alerts
)

if len(alerts) == 0:

    st.success(
        "No Active Alerts"
    )

else:

    st.dataframe(

        pd.DataFrame(
            alerts[-20:]
        ),

        use_container_width=True
    )


# ====================================
# FOOTER
# ====================================

st.caption(
    f"Runtime Mode: {RUNTIME_MODE} | Data Mode: {DATA_MODE}"
)