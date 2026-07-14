# ====================================
# runtime_event_handlers.py
# ====================================

from api.websocket_api import (
    broadcast_event_threadsafe
)


# ====================================
# MAKE WEBSOCKET HANDLER
# ====================================

def make_websocket_handler(

    event_type
):

    def handler(

        payload
    ):

        broadcast_event_threadsafe(

            event_type,

            payload
        )

    return handler


# ====================================
# DEFAULT SYSTEM ERROR HANDLER
# ====================================

websocket_broadcast_handler = (
    make_websocket_handler(
        "SYSTEM_ERROR"
    )
)