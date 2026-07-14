# ====================================
# execution_api.py
# ====================================

from fastapi import (
    FastAPI
)

from pydantic import (
    BaseModel
)

from utils.logger import (
    SystemLogger
)

from utils.runtime_mode import (
    RUNTIME_MODE
)

from core.parent_order import (
    ParentOrder
)

from api.websocket_api import (
    router as websocket_router,
    broadcast_event,
    manager as websocket_manager
)

import runtime.runtime_context as runtime_context


# ====================================
# LOGGER
# ====================================

logger = (
    SystemLogger()
)

logger.warning(
    f"FASTAPI Runtime Mode | {RUNTIME_MODE}"
)


# ====================================
# FASTAPI APP
# ====================================

app = (
    FastAPI()
)

app.include_router(
    websocket_router
)


# ====================================
# ORDER REQUEST MODEL
# ====================================

class OrderRequest(BaseModel):

    symbol: str

    qty: float

    side: str

    strategy: str = "VWAP"


# ====================================
# GET EXECUTION SERVICE
# ====================================

def get_execution_service():

    service = (
        runtime_context.execution_service
    )

    if service is None:

        raise RuntimeError(
            "ExecutionService Not Initialized"
        )

    return service


# ====================================
# HEALTH CHECK
# ====================================

@app.get("/health")
def health():

    return {

        "status":
        "running",

        "runtime_mode":
        RUNTIME_MODE,

        "runtime_initialized":
        runtime_context.runtime_status.get(
            "initialized",
            False
        ),

        "has_execution_service":
        runtime_context.execution_service is not None,

        "has_position_manager":
        runtime_context.position_manager is not None,

        "has_portfolio_state":
        getattr(
            runtime_context,
            "portfolio_state",
            None
        ) is not None,

        "has_market_state":
        runtime_context.market_state is not None,

        "has_market_data_service":
        getattr(
            runtime_context,
            "market_data_service",
            None
        ) is not None,

        "worker_running":
        runtime_context.runtime_status.get(
            "worker_running",
            False
        ),

        "market_data_running":
        runtime_context.runtime_status.get(
            "market_data_running",
            False
        ),

        "websocket_connections":
        websocket_manager.get_connection_count()
    }


# ====================================
# SUBMIT ORDER
# ====================================

@app.post("/orders")
async def submit_order(
    order: OrderRequest
):

    logger.info(
        f"External PM Order | "
        f"{order.symbol} | "
        f"{order.qty} | "
        f"{order.side} | "
        f"{order.strategy}"
    )

    try:

        execution_service = (
            get_execution_service()
        )

        parent_order = (
            ParentOrder(

                symbol=
                order.symbol,

                side=
                order.side,

                quantity=
                order.qty,

                strategy=
                order.strategy
            )
        )

        result = (
            execution_service.submit_order(
                parent_order
            )
        )

        await broadcast_event(

            "ORDER_UPDATE",

            {

                "symbol":
                order.symbol,

                "qty":
                order.qty,

                "side":
                order.side,

                "strategy":
                order.strategy,

                "status":
                result.get(
                    "status",
                    "UNKNOWN"
                ),

                "order_id":
                result.get(
                    "order_id"
                ),

                "reason":
                result.get(
                    "reason"
                )
            }
        )

        if result.get(
            "status"
        ) == "COMPLETED":

            await broadcast_event(

                "EXECUTION_COMPLETED",

                {

                    "symbol":
                    order.symbol,

                    "qty":
                    order.qty,

                    "side":
                    order.side,

                    "strategy":
                    order.strategy,

                    "order_id":
                    result.get(
                        "order_id"
                    )
                }
            )

        return {

            "accepted":
            True,

            "symbol":
            order.symbol,

            "qty":
            order.qty,

            "side":
            order.side,

            "strategy":
            order.strategy,

            "result":
            result,

            "order_id":
            result.get(
                "order_id"
            )
        }

    except Exception as error:

        logger.error(
            f"Execution API Failed | {error}"
        )

        await broadcast_event(

            "SYSTEM_ERROR",

            {

                "source":
                "ExecutionAPI",

                "message":
                str(error)
            }
        )

        return {

            "accepted":
            False,

            "error":
            str(error)
        }


# ====================================
# ALIAS: /order
# ====================================

@app.post("/order")
async def submit_order_alias(
    order: OrderRequest
):

    return await submit_order(
        order
    )


# ====================================
# GET POSITIONS
# ====================================

@app.get("/positions")
def get_positions():

    if runtime_context.position_manager is None:

        return {}

    return (
        runtime_context
        .position_manager
        .get_all_positions()
    )


# ====================================
# GET ACTIVE ORDERS
# ====================================

@app.get("/orders/active")
def get_active_orders():

    execution_service = (
        get_execution_service()
    )

    return (
        execution_service
        .get_active_orders()
    )


# ====================================
# BACKWARD COMPATIBILITY
# ====================================

@app.get("/active-orders")
def get_active_orders_legacy():

    return get_active_orders()


# ====================================
# GET PORTFOLIO
# ====================================

@app.get("/portfolio")
def get_portfolio():

    if getattr(
        runtime_context,
        "portfolio_state",
        None
    ) is not None:

        return (
            runtime_context
            .portfolio_state
            .get_portfolio_summary()
        )

    if runtime_context.position_manager is None:

        return {

            "total_realized_pnl":
            0,

            "total_unrealized_pnl":
            0,

            "total_exposure":
            0,

            "position_count":
            0
        }

    return (
        runtime_context
        .position_manager
        .get_portfolio_summary()
    )


# ====================================
# GET MARKET SNAPSHOTS
# ====================================

@app.get("/market")
def get_market():

    if runtime_context.market_state is None:

        return {}

    if hasattr(
        runtime_context.market_state,
        "get_all_snapshots"
    ):

        return (
            runtime_context
            .market_state
            .get_all_snapshots()
        )

    if hasattr(
        runtime_context.market_state,
        "get_snapshot"
    ):

        return (
            runtime_context
            .market_state
            .get_snapshot()
        )

    return {}


# ====================================
# GET FILLS
# ====================================

@app.get("/fills")
def get_fills():

    if runtime_context.execution_service is None:

        return []

    fill_tracker = (
        runtime_context
        .execution_service
        .fill_tracker
    )

    if hasattr(
        fill_tracker,
        "get_recent_fills"
    ):

        return (
            fill_tracker
            .get_recent_fills(
                limit=50
            )
        )

    if hasattr(
        fill_tracker,
        "get_fills"
    ):

        return (
            fill_tracker
            .get_fills()
        )

    return []


# ====================================
# GET RUNTIME STATUS
# ====================================

@app.get("/runtime")
def get_runtime_status():

    return (
        runtime_context
        .get_runtime_status()
    )


# ====================================
# GET ACCOUNT
# ====================================

@app.get("/account")
def get_account():

    if getattr(
        runtime_context,
        "portfolio_state",
        None
    ) is not None:

        portfolio = (
            runtime_context
            .portfolio_state
            .get_portfolio_summary()
        )

        return portfolio.get(
            "account",
            {}
        )

    if getattr(
        runtime_context,
        "simulation_account",
        None
    ) is not None:

        return (
            runtime_context
            .simulation_account
            .get_snapshot()
        )

    if getattr(
        runtime_context,
        "oms",
        None
    ) is not None:

        return (
            runtime_context
            .oms
            .get_account()
        )

    return {}


# ====================================
# GET ORDERS SNAPSHOT
# ====================================

@app.get("/orders")
def get_orders():

    if runtime_context.execution_service is None:

        return {}

    return (
        runtime_context
        .execution_service
        .get_active_orders()
    )