# ====================================
# order_queue.py
# ====================================

from collections import deque

from utils.logger import (
    SystemLogger
)

from utils.helpers import (
    get_current_time
)


class OrderQueue:


    # ====================================
    # INIT
    # ====================================

    def __init__(self):

        # ====================================
        # LOGGER
        # ====================================

        self.logger = (
            SystemLogger()
        )

        # ====================================
        # ORDER QUEUE
        # ====================================

        self.queue = deque()

        # ====================================
        # STATS
        # ====================================

        self.total_submitted = 0

        self.total_processed = 0

        self.total_removed = 0

        self.logger.info(
            "Order Queue Initialized"
        )


    # ====================================
    # SUBMIT ORDER
    # ====================================

    def submit_order(

        self,

        parent_order
    ):

        queue_item = {

            "timestamp":
            get_current_time(),

            "order":
            parent_order
        }

        self.queue.append(
            queue_item
        )

        self.total_submitted += 1

        self.logger.info(

            f"Order Added To Queue | "

            f"{parent_order.order_id} | "

            f"{parent_order.symbol}"
        )


    # ====================================
    # GET NEXT ORDER
    # ====================================

    def get_next_order(self):

        if self.is_empty():

            self.logger.warning(
                "Order Queue Empty"
            )

            return None

        queue_item = (
            self.queue.popleft()
        )

        self.total_processed += 1

        order = queue_item["order"]

        self.logger.info(

            f"Dequeued Order | "

            f"{order.order_id}"
        )

        return order


    # ====================================
    # PEEK NEXT ORDER
    # ====================================

    def peek(self):

        if self.is_empty():

            return None

        return self.queue[0]["order"]


    # ====================================
    # REMOVE ORDER
    # ====================================

    def remove_order(

        self,

        order_id
    ):

        for item in list(self.queue):

            order = item["order"]

            if order.order_id == order_id:

                self.queue.remove(item)

                self.total_removed += 1

                self.logger.warning(

                    f"Order Removed | "

                    f"{order_id}"
                )

                return True

        self.logger.warning(

            f"Order Not Found | "

            f"{order_id}"
        )

        return False


    # ====================================
    # GET ALL ORDERS
    # ====================================

    def get_all_orders(self):

        return [

            item["order"].get_snapshot()

            for item in self.queue
        ]


    # ====================================
    # QUEUE SIZE
    # ====================================

    def size(self):

        return len(self.queue)


    # ====================================
    # IS EMPTY
    # ====================================

    def is_empty(self):

        return len(self.queue) == 0


    # ====================================
    # CLEAR QUEUE
    # ====================================

    def clear(self):

        queue_size = len(self.queue)

        self.queue.clear()

        self.logger.warning(

            f"Queue Cleared | "

            f"{queue_size} Orders Removed"
        )


    # ====================================
    # GET STATS
    # ====================================

    def get_stats(self):

        return {

            "queue_size":
            self.size(),

            "total_submitted":
            self.total_submitted,

            "total_processed":
            self.total_processed,

            "total_removed":
            self.total_removed
        }


    # ====================================
    # SHOW QUEUE
    # ====================================

    def show_queue(self):

        print(

            "\n========== ORDER QUEUE ==========\n"
        )

        if self.is_empty():

            print("Queue Empty")

        else:

            for index, item in enumerate(

                self.queue,

                start=1
            ):

                order = item["order"]

                print(

                    f"{index}. "

                    f"{order.symbol} | "

                    f"{order.side} | "

                    f"Qty: {order.quantity} | "

                    f"Status: {order.status}"
                )

        print(

            "\n=================================\n"
        )


    # ====================================
    # SHOW STATS
    # ====================================

    def show_stats(self):

        stats = (
            self.get_stats()
        )

        print(

            "\n========== QUEUE STATS ==========\n"
        )

        for key, value in stats.items():

            print(f"{key}: {value}")

        print(

            "\n=================================\n"
        )