# ====================================
# order_api.py
# ====================================

from fastapi import (

    FastAPI,

    HTTPException
)

from pydantic import (
    BaseModel
)

from utils.logger import (
    SystemLogger
)

from utils.validators import (

    validate_symbol,

    validate_quantity,

    validate_side,

    validate_strategy
)

from core.parent_order import (
    ParentOrder
)

from runtime.runtime_context import (

    execution_service,

    order_queue,

    execution_worker,

    start_worker,

    stop_worker
)


# ====================================
# LOGGER
# ====================================

logger = (
    SystemLogger()
)


# ====================================
# FASTAPI APP
# ====================================

app = FastAPI(

    title="Execution Platform API"
)


# ====================================
# ORDER REQUEST MODEL
# ====================================

class OrderRequest(BaseModel):

    symbol: str

    qty: float

    side: str

    strategy: str


# ====================================
# HEALTH CHECK
# ====================================

@app.get("/health")

def health_check():

    return {

        "status":
        "RUNNING",

        "queue_size":
        order_queue.size(),

        "worker_status":
        execution_worker.status
    }


# ====================================
# START WORKER
# ====================================

@app.post("/worker/start")

def api_start_worker():

    try:

        if execution_worker.is_running():

            return {

                "status":
                "ALREADY_RUNNING"
            }

        start_worker()

        logger.info(
            "Execution Worker Started"
        )

        return {

            "status":
            "WORKER_STARTED"
        }

    except Exception as error:

        logger.error(

            f"Worker Start Failed | "

            f"{error}"
        )

        raise HTTPException(

            status_code=500,

            detail=str(error)
        )


# ====================================
# STOP WORKER
# ====================================

@app.post("/worker/stop")

def api_stop_worker():

    try:

        stop_worker()

        logger.warning(
            "Execution Worker Stopped"
        )

        return {

            "status":
            "WORKER_STOPPED"
        }

    except Exception as error:

        logger.error(

            f"Worker Stop Failed | "

            f"{error}"
        )

        raise HTTPException(

            status_code=500,

            detail=str(error)
        )


# ====================================
# SUBMIT ORDER
# ====================================

@app.post("/order")

def submit_order(

    order_request: OrderRequest
):

    try:

        # ====================================
        # VALIDATION
        # ====================================

        validate_symbol(
            order_request.symbol
        )

        validate_quantity(
            order_request.qty
        )

        validate_side(
            order_request.side
        )

        validate_strategy(
            order_request.strategy
        )

        # ====================================
        # CREATE PARENT ORDER
        # ====================================

        parent_order = (

            ParentOrder(

                symbol=
                order_request.symbol,

                quantity=
                order_request.qty,

                side=
                order_request.side,

                strategy=
                order_request.strategy
            )
        )

        # ====================================
        # SUBMIT TO QUEUE
        # ====================================

        order_queue.submit_order(
            parent_order
        )

        logger.info(

            f"Order Queued | "

            f"{order_request.side} "

            f"{order_request.qty} "

            f"{order_request.symbol}"
        )

        # ====================================
        # RESPONSE
        # ====================================

        return {

            "status":
            "QUEUED",

            "order_id":
            parent_order.order_id,

            "symbol":
            order_request.symbol,

            "qty":
            order_request.qty,

            "side":
            order_request.side,

            "strategy":
            order_request.strategy,

            "queue_size":
            order_queue.size()
        }

    except Exception as error:

        logger.error(

            f"Order Queue Failed | "

            f"{error}"
        )

        raise HTTPException(

            status_code=400,

            detail=str(error)
        )


# ====================================
# GET QUEUE
# ====================================

@app.get("/queue")

def get_queue():

    return {

        "queue_size":
        order_queue.size(),

        "orders":
        order_queue.get_all_orders()
    }


# ====================================
# GET ACTIVE ORDERS
# ====================================

@app.get("/orders")

def get_active_orders():

    active_orders = (

        execution_service
        .get_active_orders()
    )

    return active_orders


# ====================================
# GET WORKER STATUS
# ====================================

@app.get("/worker/status")

def get_worker_status():

    return (
        execution_worker.get_status()
    )