# ====================================
# replay_feed.py
# ====================================

from data.feeds.base_feed import (
    BaseFeed
)

from data.replay import (
    MarketReplay
)


class ReplayFeed(BaseFeed):


    # ====================================
    # INIT
    # ====================================

    def __init__(

        self,

        replay_engine
    ):

        self.replay_engine = (
            replay_engine
        )


    # ====================================
    # START
    # ====================================

    def start(self):

        self.replay_engine.run()


    # ====================================
    # STOP
    # ====================================

    def stop(self):

        pass


    # ====================================
    # SUBSCRIBE
    # ====================================

    def subscribe(

        self,

        symbol
    ):

        pass