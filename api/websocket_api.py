# ====================================
# websocket_api.py
# ====================================

import asyncio

from fastapi import (
    APIRouter,
    WebSocket,
    WebSocketDisconnect
)

from fastapi.encoders import (
    jsonable_encoder
)

from utils.logger import (
    SystemLogger
)

from utils.helpers import (
    get_current_timestamp
)


# ====================================
# LOGGER
# ====================================

logger = (
    SystemLogger()
)


# ====================================
# ROUTER
# ====================================

router = (
    APIRouter()
)


# ====================================
# CONNECTION MANAGER
# ====================================

class ConnectionManager:


    # ====================================
    # INIT
    # ====================================

    def __init__(self):

        self.active_connections = []

        self.loop = None

        logger.info(
            "WebSocket Manager Initialized"
        )


    # ====================================
    # CONNECT
    # ====================================

    async def connect(

        self,

        websocket: WebSocket
    ):

        await websocket.accept()

        self.loop = asyncio.get_running_loop()

        self.active_connections.append(
            websocket
        )

        logger.info(

            f"WebSocket Connected | "

            f"Clients={len(self.active_connections)}"
        )


    # ====================================
    # DISCONNECT
    # ====================================

    def disconnect(

        self,

        websocket: WebSocket
    ):

        if websocket in self.active_connections:

            self.active_connections.remove(
                websocket
            )

        logger.warning(

            f"WebSocket Disconnected | "

            f"Clients={len(self.active_connections)}"
        )


    # ====================================
    # BROADCAST EVENT ASYNC
    # ====================================

    async def broadcast_event(

        self,

        event_type,

        payload
    ):

        raw_message = {

            "event":
            event_type,

            "timestamp":
            get_current_timestamp(),

            "payload":
            payload
        }

        message = jsonable_encoder(
            raw_message
        )

        disconnected_clients = []

        for connection in list(
            self.active_connections
        ):

            try:

                await connection.send_json(
                    message
                )

            except Exception as error:

                logger.error(

                    f"WebSocket Send Failed | "

                    f"{error}"
                )

                disconnected_clients.append(
                    connection
                )

        for client in disconnected_clients:

            self.disconnect(
                client
            )


    # ====================================
    # BROADCAST EVENT THREADSAFE
    # ====================================

    def broadcast_event_threadsafe(

        self,

        event_type,

        payload
    ):

        if self.loop is None:

            return

        try:

            asyncio.run_coroutine_threadsafe(

                self.broadcast_event(

                    event_type,

                    payload
                ),

                self.loop
            )

        except Exception as error:

            logger.error(

                f"Threadsafe Broadcast Failed | "

                f"{event_type} | "

                f"{error}"
            )


    # ====================================
    # CONNECTION COUNT
    # ====================================

    def get_connection_count(self):

        return len(
            self.active_connections
        )


# ====================================
# MANAGER
# ====================================

manager = (
    ConnectionManager()
)


# ====================================
# WEBSOCKET ENDPOINT
# ====================================

@router.websocket("/ws")
async def websocket_endpoint(

    websocket: WebSocket
):

    await manager.connect(
        websocket
    )

    try:

        while True:

            await websocket.receive_text()

    except WebSocketDisconnect:

        manager.disconnect(
            websocket
        )

    except Exception as error:

        logger.error(

            f"WebSocket Error | "

            f"{error}"
        )

        manager.disconnect(
            websocket
        )


# ====================================
# HEALTH CHECK
# ====================================

@router.get("/ws-health")
def websocket_health():

    return {

        "status":
        "RUNNING",

        "active_connections":
        manager.get_connection_count()
    }


# ====================================
# PUBLIC BROADCAST FUNCTIONS
# ====================================

async def broadcast_event(

    event_type,

    payload
):

    await manager.broadcast_event(

        event_type,

        payload
    )


def broadcast_event_threadsafe(

    event_type,

    payload
):

    manager.broadcast_event_threadsafe(

        event_type,

        payload
    )