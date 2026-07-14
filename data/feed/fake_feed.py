# ====================================
# fake_feed.py
# ====================================

from base_feed import (
    BaseFeed
)

from data.fake_market_generator import (
    FakeMarketGenerator
)


class FakeFeed(BaseFeed):


    # ====================================
    # INIT
    # ====================================

    def __init__(

        self,

        generator
    ):

        self.generator = (
            generator
        )


    # ====================================
    # START
    # ====================================

    def start(self):

        self.generator.start()


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