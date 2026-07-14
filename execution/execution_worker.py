# ====================================
# execution_worker.py
# ====================================

import time

from utils.logger import (
    SystemLogger
)

from utils.constants import (

    RUNNING,

    HALTED,

    COMPLETED
)


class ExecutionWorker:


    # ====================================
    # INIT
    # ====================================

    def __init__(

        self,

        order_queue,

        execution_service,

        poll_interval=1
    ):

        self.logger = (
            SystemLogger()
        )

        self.order_queue = (
            order_queue
        )

        self.execution_service = (
            execution_service
        )

        self.poll_interval = (
            poll_interval
        )

        self.status = HALTED

        self.processed_orders = 0

        self.failed_orders = 0

        self.current_order = None

        self.logger.info(
            "Execution Worker Initialized"
        )


    # ====================================
    # START WORKER
    # ====================================

    def start(self):

        self.status = RUNNING

        self.logger.info(
            "Execution Worker Started"
        )

        print(
            "\n========== EXECUTION WORKER ==========\n"
        )

        while self.status == RUNNING:

            if self.order_queue.is_empty():

                time.sleep(
                    self.poll_interval
                )

                continue

            parent_order = (
                self.order_queue
                .get_next_order()
            )

            if parent_order is None:

                continue

            self.current_order = (
                parent_order
            )

            self.logger.info(

                f"Processing Order | "

                f"{parent_order.order_id}"
            )

            try:

                result = (

                    self.execution_service
                    .submit_order(
                        parent_order
                    )
                )

                if (

                    result[
                        "status"
                    ]
                    ==
                    COMPLETED
                ):

                    self.processed_orders += 1

                    self.logger.info(

                        f"Order Completed | "

                        f"{parent_order.order_id}"
                    )

                else:

                    self.failed_orders += 1

                    self.logger.warning(

                        f"Order Failed | "

                        f"{parent_order.order_id} | "

                        f"{result}"
                    )

            except Exception as error:

                self.failed_orders += 1

                try:

                    parent_order.fail_order(
                        str(error)
                    )

                except Exception:

                    pass

                self.logger.error(

                    f"Worker Error | "

                    f"{error}"
                )

            finally:

                self.current_order = None

            time.sleep(
                self.poll_interval
            )

        self.logger.warning(
            "Execution Worker Stopped"
        )


    # ====================================
    # STOP WORKER
    # ====================================

    def stop(self):

        self.status = HALTED

        self.logger.warning(
            "Execution Worker Halted"
        )


    # ====================================
    # GET STATUS
    # ====================================

    def get_status(self):

        return {

            "status":
            self.status,

            "queue_size":
            self.order_queue.size(),

            "processed_orders":
            self.processed_orders,

            "failed_orders":
            self.failed_orders,

            "current_order":
            (

                self.current_order.order_id

                if self.current_order

                else None
            )
        }


    # ====================================
    # IS RUNNING
    # ====================================

    def is_running(self):

        return (
            self.status
            ==
            RUNNING
        )


    # ====================================
    # SHOW STATUS
    # ====================================

    def show_status(self):

        status = (
            self.get_status()
        )

        print(
            "\n========== EXECUTION WORKER ==========\n"
        )

        for key, value in status.items():

            print(f"{key}: {value}")

        print(
            "\n======================================\n"
        )