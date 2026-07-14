# ====================================
# redis_state.py
# ====================================

import json
import redis

from utils.runtime_mode import (
    RUNTIME_MODE
)


class RedisState:


    # ====================================
    # INIT
    # ====================================

    def __init__(self):

        self.redis_client = redis.Redis(

            host="localhost",

            port=6379,

            decode_responses=True
        )


    # ====================================
    # BUILD RUNTIME KEY
    # ====================================

    def build_key(

        self,

        key
    ):

        return (
            f"{RUNTIME_MODE}:{key}"
        )


    # ====================================
    # MARKET STATE
    # ====================================

    def set_market_state(

        self,

        symbol,

        data
    ):

        self.redis_client.set(

            self.build_key(
                f"market:{symbol}"
            ),

            json.dumps(data)
        )


    def get_market_state(

        self,

        symbol
    ):

        data = self.redis_client.get(

            self.build_key(
                f"market:{symbol}"
            )
        )

        if data:

            return json.loads(data)

        return None


    # ====================================
    # SYSTEM STATE
    # ====================================

    def set_system_state(

        self,

        data
    ):

        self.redis_client.set(

            self.build_key(
                "system_state"
            ),

            json.dumps(data)
        )


    def get_system_state(self):

        data = self.redis_client.get(

            self.build_key(
                "system_state"
            )
        )

        if data:

            return json.loads(data)

        return None


    # ====================================
    # FILLS
    # ====================================

    def set_fills(

        self,

        fills
    ):

        self.redis_client.set(

            self.build_key(
                "fills"
            ),

            json.dumps(

                fills,

                default=str
            )
        )


    def get_fills(self):

        data = self.redis_client.get(

            self.build_key(
                "fills"
            )
        )

        if data:

            return json.loads(data)

        return []


    # ====================================
    # AI RISK
    # ====================================

    def set_ai_risk_result(

        self,

        data
    ):

        self.redis_client.set(

            self.build_key(
                "ai_risk_result"
            ),

            json.dumps(data)
        )


    def get_ai_risk_result(self):

        data = self.redis_client.get(

            self.build_key(
                "ai_risk_result"
            )
        )

        if data:

            return json.loads(data)

        return None


    # ====================================
    # ALERTS
    # ====================================

    def set_alerts(

        self,

        alerts
    ):

        self.redis_client.set(

            self.build_key(
                "alerts"
            ),

            json.dumps(alerts)
        )


    def get_alerts(self):

        data = self.redis_client.get(

            self.build_key(
                "alerts"
            )
        )

        if data:

            return json.loads(data)

        return []


    # ====================================
    # EXECUTION STATUS
    # ====================================

    def set_execution_status(

        self,

        status_data
    ):

        self.redis_client.set(

            self.build_key(
                "execution_status"
            ),

            json.dumps(status_data)
        )


    def get_execution_status(self):

        data = self.redis_client.get(

            self.build_key(
                "execution_status"
            )
        )

        if data:

            return json.loads(data)

        return {}


    # ====================================
    # EXECUTION SUMMARY
    # ====================================

    def set_execution_summary(

        self,

        summary
    ):

        self.redis_client.set(

            self.build_key(
                "execution_summary"
            ),

            json.dumps(

                summary,

                default=str
            )
        )


    def get_execution_summary(self):

        data = self.redis_client.get(

            self.build_key(
                "execution_summary"
            )
        )

        if data:

            return json.loads(data)

        return {}


    # ====================================
    # RUNTIME MODE
    # ====================================

    def set_runtime_mode(

        self,

        mode
    ):

        self.redis_client.set(

            self.build_key(
                "runtime_mode"
            ),

            mode
        )


    def get_runtime_mode(self):

        return self.redis_client.get(

            self.build_key(
                "runtime_mode"
            )
        )


    # ====================================
    # WORKER STATUS
    # ====================================

    def set_worker_status(

        self,

        status
    ):

        self.redis_client.set(

            self.build_key(
                "worker_status"
            ),

            json.dumps(

                status,

                default=str
            )
        )


    def get_worker_status(self):

        data = self.redis_client.get(

            self.build_key(
                "worker_status"
            )
        )

        if data:

            return json.loads(data)

        return {}


    # ====================================
    # POSITIONS
    # ====================================

    def set_positions(

        self,

        positions
    ):

        self.redis_client.set(

            self.build_key(
                "positions"
            ),

            json.dumps(

                positions,

                default=str
            )
        )


    def get_positions(self):

        data = self.redis_client.get(

            self.build_key(
                "positions"
            )
        )

        if data:

            return json.loads(data)

        return {}


    # ====================================
    # PORTFOLIO SUMMARY
    # ====================================

    def set_portfolio_summary(

        self,

        summary
    ):

        self.redis_client.set(

            self.build_key(
                "portfolio_summary"
            ),

            json.dumps(

                summary,

                default=str
            )
        )


    def get_portfolio_summary(self):

        data = self.redis_client.get(

            self.build_key(
                "portfolio_summary"
            )
        )

        if data:

            return json.loads(data)

        return {}