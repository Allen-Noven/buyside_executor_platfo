# ====================================
# live_feed.py
# ====================================

from data.feeds.base_feed import (
    BaseFeed
)


class LiveFeed(BaseFeed):


    # ====================================
    # INIT
    # ====================================

    def __init__(

        self,

        loader
    ):

        self.loader = (
            loader
        )


    # ====================================
    # START
    # ====================================

    def start(self):

        if hasattr(

            self.loader,

            "start"
        ):

            self.loader.start()

        else:

            self.loader.run()


    # ====================================
    # START ASYNC
    # ====================================

    def start_async(self):

        if hasattr(

            self.loader,

            "start_async"
        ):

            self.loader.start_async()

        else:

            self.start()


    # ====================================
    # STOP
    # ====================================

    def stop(self):

        if hasattr(

            self.loader,

            "stop"
        ):

            self.loader.stop()


    # ====================================
    # SUBSCRIBE
    # ====================================

    def subscribe(

        self,

        symbol
    ):

        if hasattr(

            self.loader,

            "subscribe"
        ):

            self.loader.subscribe(
                symbol
            )


    # ====================================
    # GET SNAPSHOT
    # ====================================

    def get_latest_snapshot(

        self,

        symbol
    ):

        if hasattr(

            self.loader,

            "get_latest_snapshot"
        ):

            return self.loader.get_latest_snapshot(
                symbol
            )

        return None