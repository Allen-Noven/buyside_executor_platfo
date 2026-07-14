# ====================================
# execution_log.py
# ====================================

from utils.helpers import (

    get_current_time,

    format_order_log
)

from utils.logger import (
    SystemLogger
)


class ExecutionAuditLogger:

    def __init__(self):

        # ====================================
        # SYSTEM LOGGER
        # ====================================

        self.logger = (
            SystemLogger()
        )


        # ====================================
        # EXECUTION LOG STORAGE
        # ====================================

        self.logs = []


    # ====================================
    # LOG EXECUTION EVENT
    # ====================================

    def log_execution(

        self,

        symbol,

        qty,

        strategy,

        order_response,

        side=None,

        fill_price=None

    ):

        execution_record = {

            "timestamp":
            get_current_time(),

            "symbol":
            symbol,

            "side":
            side,

            "qty":
            qty,

            "strategy":
            strategy,

            "order_id":
            str(order_response.id),

            "status":
            str(order_response.status),

            "fill_price":
            fill_price
        }


        # ====================================
        # STORE LOG
        # ====================================

        self.logs.append(
            execution_record
        )


        self.logger.info(

            f"Execution Logged | "

            f"{symbol} | "

            f"{qty} shares | "

            f"{order_response.status}"
        )


    # ====================================
    # GET ALL LOGS
    # ====================================

    def get_logs(self):

        return self.logs


    # ====================================
    # GET RECENT LOGS
    # ====================================

    def get_recent_logs(

        self,

        limit=10

    ):

        return self.logs[-limit:]


    # ====================================
    # FILTER BY SYMBOL
    # ====================================

    def filter_by_symbol(

        self,

        symbol

    ):

        return [

            log

            for log in self.logs

            if log["symbol"] == symbol
        ]


    # ====================================
    # FILTER BY STATUS
    # ====================================

    def filter_by_status(

        self,

        status

    ):

        return [

            log

            for log in self.logs

            if log["status"] == status
        ]


    # ====================================
    # EXECUTION SUMMARY
    # ====================================

    def get_summary(self):

        total_executions = (
            len(self.logs)
        )


        total_qty = sum(

            log["qty"]

            for log in self.logs
        )


        return {

            "total_executions":
            total_executions,

            "total_qty":
            total_qty
        }


    # ====================================
    # SHOW LOGS
    # ====================================

    def show_logs(self):

        print(

            "\n========== EXECUTION LOGS ==========\n"
        )

        for log in self.logs:

            print(

                format_order_log(

                    log["symbol"],

                    log["qty"],

                    log["status"]
                )
            )

            print(log)

            print()

        print(

            "\n====================================\n"
        )


    # ====================================
    # SHOW SUMMARY
    # ====================================

    def show_summary(self):

        summary = (
            self.get_summary()
        )

        print(

            "\n========== EXECUTION SUMMARY ==========\n"
        )

        print(

            f"Total Execution Events: "

            f"{summary['total_executions']}"
        )

        print(

            f"Total Quantity Executed: "

            f"{summary['total_qty']}"
        )

        print(

            "\n=======================================\n"
        )