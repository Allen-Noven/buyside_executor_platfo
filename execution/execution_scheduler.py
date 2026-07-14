# ====================================
# execution_scheduler.py
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


class ExecutionScheduler:


    def __init__(

        self,

        execution_interval=1,

        market_state=None
    ):

        self.logger = (
            SystemLogger()
        )

        self.execution_interval = (
            execution_interval
        )

        self.market_state = (
            market_state
        )

        self.status = RUNNING

        self.current_slice = 0

        self.total_slices = 0

        self.completed_slices = 0


    # ====================================
    # DYNAMIC EXECUTION INTERVAL
    # ====================================

    def get_dynamic_interval(self):

        if self.market_state is None:

            return self.execution_interval

        volatility = getattr(

            self.market_state,

            "volatility",

            None
        )

        if volatility is None:

            return self.execution_interval

        if volatility > 0.05:

            return (
                self.execution_interval * 2
            )

        elif volatility < 0.01:

            return (
                self.execution_interval * 0.5
            )

        return self.execution_interval


    # ====================================
    # RUN EXECUTION SCHEDULE
    # ====================================

    def run_schedule(

        self,

        schedule,

        execution_callback,

        progress_callback=None
    ):

        self.total_slices = (
            len(schedule)
        )

        self.completed_slices = 0

        self.logger.info(

            f"Starting Execution Schedule | "

            f"{self.total_slices} slices"
        )

        if self.total_slices == 0:

            self.status = COMPLETED

            if progress_callback:

                progress_callback(

                    {

                        "status":
                        COMPLETED,

                        "current_slice":
                        0,

                        "total_slices":
                        0,

                        "completed_slices":
                        0,

                        "completion_pct":
                        100
                    }
                )

            return self.get_status()

        for child_order in schedule:

            if self.status == HALTED:

                self.logger.warning(
                    "Execution Halted"
                )

                break

            self.current_slice += 1

            self.logger.info(

                f"Executing Slice "

                f"{self.current_slice}/"

                f"{self.total_slices}"
            )

            self.logger.info(

                f"Qty: "

                f"{child_order['qty']}"
            )

            execution_ok = execution_callback(
                child_order
            )

            if execution_ok is False:

                self.status = HALTED

                self.logger.warning(

                    f"Execution Slice Failed | "

                    f"{self.current_slice}/"

                    f"{self.total_slices}"
                )

                if progress_callback:

                    progress_callback(

                        {

                            "status":
                            HALTED,

                            "current_slice":
                            self.current_slice,

                            "total_slices":
                            self.total_slices,

                            "completed_slices":
                            self.completed_slices,

                            "completion_pct":
                            round(

                                self.completed_slices
                                /
                                self.total_slices
                                *
                                100,

                                2
                            ),

                            "reason":
                            "Child order execution failed or risk rejected"
                        }
                    )

                break

            self.completed_slices += 1

            completion_pct = round(

                self.completed_slices
                /
                self.total_slices
                *
                100,

                2
            )

            if progress_callback:

                progress_callback(

                    {

                        "status":
                        RUNNING,

                        "current_slice":
                        self.current_slice,

                        "total_slices":
                        self.total_slices,

                        "completed_slices":
                        self.completed_slices,

                        "completion_pct":
                        completion_pct
                    }
                )

            interval = (
                self.get_dynamic_interval()
            )

            self.logger.info(

                f"Waiting "

                f"{interval} seconds"
            )

            time.sleep(
                interval
            )

        if self.status != HALTED:

            self.status = COMPLETED

            if progress_callback:

                progress_callback(

                    {

                        "status":
                        COMPLETED,

                        "current_slice":
                        self.current_slice,

                        "total_slices":
                        self.total_slices,

                        "completed_slices":
                        self.completed_slices,

                        "completion_pct":
                        100
                    }
                )

            self.logger.info(
                "Execution Schedule Completed"
            )

        return self.get_status()


    # ====================================
    # STOP EXECUTION
    # ====================================

    def stop(self):

        self.status = HALTED

        self.logger.warning(
            "Scheduler Stopped"
        )


    # ====================================
    # RESUME EXECUTION
    # ====================================

    def resume(self):

        self.status = RUNNING

        self.logger.info(
            "Scheduler Resumed"
        )


    # ====================================
    # GET STATUS
    # ====================================

    def get_status(self):

        return {

            "status":
            self.status,

            "current_slice":
            self.current_slice,

            "total_slices":
            self.total_slices,

            "completed_slices":
            self.completed_slices
        }


    # ====================================
    # SHOW SCHEDULE
    # ====================================

    def show_schedule(

        self,

        schedule
    ):

        print(
            "\n========== EXECUTION SCHEDULE ==========\n"
        )

        for child_order in schedule:

            print(
                child_order
            )

        print(
            "\n========================================\n"
        )