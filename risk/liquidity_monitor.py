# ====================================
# liquidity_monitor.py
# ====================================

from utils.logger import (
    SystemLogger
)

from utils.config import (

    SPREAD_THRESHOLD,

    MIN_VOLUME
)


class LiquidityMonitor:

    def __init__(

        self,

        market_state

    ):

        self.logger = (
            SystemLogger()
        )

        self.market_state = (
            market_state
        )

        self.spread_threshold = (
            SPREAD_THRESHOLD
        )

        self.min_volume = (
            MIN_VOLUME
        )


    # ====================================
    # EVENT CALLBACK
    # ====================================

    def on_market_update(

        self,

        market_state

    ):

        result = (
            self.evaluate_market()
        )

        self.logger.info(

            f"Liquidity Score | "

            f"{result['liquidity_score']}"
        )


    # ====================================
    # EVALUATE MARKET
    # ====================================

    def evaluate_market(self):

        spread = (
            self.market_state.spread
        )

        volume = (
            self.market_state.current_volume
        )

        volatility = (
            self.market_state.volatility
        )

        score = 100

        if (

            spread is not None
            and
            spread > self.spread_threshold

        ):

            score -= 40

        if (

            volume is not None
            and
            volume < self.min_volume

        ):

            score -= 40

        if (

            volatility is not None
            and
            volatility > 0.05

        ):

            score -= 20

        score = max(score, 0)

        self.market_state.liquidity_score = (
            score
        )

        return {

            "liquidity_score":
            score,

            "market_quality":

            "GOOD"
            if score >= 80
            else "POOR"
        }