# ====================================
# redis_cache.py
# ====================================

import json

import redis

from utils.logger import (
    SystemLogger
)

from utils.helpers import (
    get_current_timestamp
)

from utils.config import (

    REDIS_HOST,

    REDIS_PORT,

    REDIS_DB
)


class RedisCache:


    # ====================================
    # INIT
    # ====================================

    def __init__(self):

        self.logger = (
            SystemLogger()
        )

        try:

            self.redis_client = redis.Redis(

                host=REDIS_HOST,

                port=REDIS_PORT,

                db=REDIS_DB,

                decode_responses=True
            )

            self.redis_client.ping()

            self.logger.info(

                "Redis Cache Connected"
            )

        except Exception as error:

            self.logger.error(

                f"Redis Connection Failed | "

                f"{error}"
            )

            self.redis_client = None


    # ====================================
    # SET VALUE
    # ====================================

    def set_value(

        self,

        key,

        value
    ):

        if self.redis_client is None:

            return

        try:

            payload = {

                "timestamp":
                get_current_timestamp(),

                "value":
                value
            }

            self.redis_client.set(

                key,

                json.dumps(payload)
            )

        except Exception as error:

            self.logger.error(

                f"Redis SET Failed | "

                f"{error}"
            )


    # ====================================
    # GET VALUE
    # ====================================

    def get_value(

        self,

        key
    ):

        if self.redis_client is None:

            return None

        try:

            data = self.redis_client.get(
                key
            )

            if data is None:

                return None

            return json.loads(data)

        except Exception as error:

            self.logger.error(

                f"Redis GET Failed | "

                f"{error}"
            )

            return None


    # ====================================
    # DELETE VALUE
    # ====================================

    def delete_value(

        self,

        key
    ):

        if self.redis_client is None:

            return

        try:

            self.redis_client.delete(key)

            self.logger.info(

                f"Redis Key Deleted | "

                f"{key}"
            )

        except Exception as error:

            self.logger.error(

                f"Redis DELETE Failed | "

                f"{error}"
            )


    # ====================================
    # CACHE MARKET STATE
    # ====================================

    def cache_market_state(

        self,

        symbol,

        market_state
    ):

        key = (

            f"market_state:{symbol}"
        )

        self.set_value(

            key,

            market_state
        )


    # ====================================
    # GET MARKET STATE
    # ====================================

    def get_market_state(

        self,

        symbol
    ):

        key = (

            f"market_state:{symbol}"
        )

        return self.get_value(key)


    # ====================================
    # CACHE POSITION
    # ====================================

    def cache_position(

        self,

        symbol,

        position
    ):

        key = (

            f"position:{symbol}"
        )

        self.set_value(

            key,

            position
        )


    # ====================================
    # GET POSITION
    # ====================================

    def get_position(

        self,

        symbol
    ):

        key = (

            f"position:{symbol}"
        )

        return self.get_value(key)


    # ====================================
    # CACHE ACTIVE ORDER
    # ====================================

    def cache_active_order(

        self,

        order_id,

        order_data
    ):

        key = (

            f"active_order:{order_id}"
        )

        self.set_value(

            key,

            order_data
        )


    # ====================================
    # GET ACTIVE ORDER
    # ====================================

    def get_active_order(

        self,

        order_id
    ):

        key = (

            f"active_order:{order_id}"
        )

        return self.get_value(key)


    # ====================================
    # CLEAR CACHE
    # ====================================

    def clear_cache(self):

        if self.redis_client is None:

            return

        try:

            self.redis_client.flushdb()

            self.logger.warning(

                "Redis Cache Cleared"
            )

        except Exception as error:

            self.logger.error(

                f"Redis Clear Failed | "

                f"{error}"
            )