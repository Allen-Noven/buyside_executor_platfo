# ====================================
# market_event_bus.py
# ====================================

import threading

from collections import defaultdict

from utils.logger import (
    SystemLogger
)


class MarketEventBus:


    # ====================================
    # INIT
    # ====================================

    def __init__(self):

        self.logger = (
            SystemLogger()
        )

        self.subscribers = (
            defaultdict(list)
        )

        self.bus_lock = (
            threading.Lock()
        )


    # ====================================
    # SUBSCRIBE
    # ====================================

    def subscribe(

        self,

        event_type,

        callback
    ):

        with self.bus_lock:

            self.subscribers[
                event_type
            ].append(callback)

        self.logger.info(

            f"Subscribed | "
            f"{event_type}"
        )


    # ====================================
    # UNSUBSCRIBE
    # ====================================

    def unsubscribe(

        self,

        event_type,

        callback
    ):

        with self.bus_lock:

            if event_type in self.subscribers:

                if callback in self.subscribers[
                    event_type
                ]:

                    self.subscribers[
                        event_type
                    ].remove(callback)

                    self.logger.info(

                        f"Unsubscribed | "
                        f"{event_type}"
                    )


    # ====================================
    # PUBLISH EVENT
    # ====================================

    def publish(

        self,

        event_type,

        data
    ):

        # ====================================
        # COPY CALLBACKS
        # ====================================

        with self.bus_lock:

            callbacks = list(

                self.subscribers.get(
                    event_type,
                    []
                )
            )

        self.logger.info(

            f"Publishing Event | "
            f"{event_type}"
        )

        # ====================================
        # EXECUTE CALLBACKS
        # ====================================

        for callback in callbacks:

            try:

                callback(data)

            except Exception as error:

                self.logger.error(

                    f"Event Error | "
                    f"{event_type} | "
                    f"{error}"
                )