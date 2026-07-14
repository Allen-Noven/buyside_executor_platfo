# ====================================
# benchmark_engine.py
# ====================================

from utils.helpers import (
    format_price
)


class BenchmarkEngine:

    def __init__(self):

        # ====================================
        # STORE BENCHMARK RESULTS
        # ====================================

        self.results = []


    # ====================================
    # RECORD STRATEGY PERFORMANCE
    # ====================================

    def record_strategy(

        self,

        strategy_name,

        slippage_analyzer,

        pnl_tracker

    ):

        records = (
            slippage_analyzer.records
        )


        # ====================================
        # NO RECORDS
        # ====================================

        if len(records) == 0:

            return


        # ====================================
        # CALCULATE METRICS
        # ====================================

        total_qty = sum(

            record["qty"]

            for record in records
        )


        total_slippage = sum(

            record["slippage"]

            for record in records
        )


        total_bps = sum(

            record["slippage_bps"]

            for record in records
        )


        total_execution_cost = sum(

            record["execution_cost"]

            for record in records
        )


        avg_slippage = (

            total_slippage
            / len(records)
        )


        avg_bps = (

            total_bps
            / len(records)
        )


        # ====================================
        # BUILD RESULT
        # ====================================

        result = {

            "strategy":
            strategy_name,

            "total_qty":
            total_qty,

            "average_slippage":
            round(
                avg_slippage,
                4
            ),

            "average_bps":
            round(
                avg_bps,
                2
            ),

            "execution_cost":
            round(
                total_execution_cost,
                2
            ),

            "realized_pnl":
            round(
                pnl_tracker.realized_pnl,
                2
            ),

            "unrealized_pnl":
            round(
                pnl_tracker.unrealized_pnl,
                2
            )
        }


        # ====================================
        # STORE RESULT
        # ====================================

        self.results.append(
            result
        )


        # ====================================
        # SHOW RESULT
        # ====================================

        print(

            "\n========== STRATEGY BENCHMARK ==========\n"
        )

        print(

            f"Strategy: "
            f"{strategy_name}"
        )

        print(

            f"Total Qty: "
            f"{total_qty}"
        )

        print(

            f"Average Slippage: "
            f"{round(avg_slippage, 4)}"
        )

        print(

            f"Average BPS: "
            f"{round(avg_bps, 2)}"
        )

        print(

            f"Execution Cost: "
            f"{round(total_execution_cost, 2)}"
        )

        print(

            f"Realized PnL: "
            f"{round(pnl_tracker.realized_pnl, 2)}"
        )

        print(

            f"Unrealized PnL: "
            f"{round(pnl_tracker.unrealized_pnl, 2)}"
        )

        print(

            "\n========================================\n"
        )


    # ====================================
    # SHOW ALL RESULTS
    # ====================================

    def show_results(self):

        print(

            "\n========== BENCHMARK REPORT ==========\n"
        )

        for result in self.results:

            print(result)

            print()

        print(

            "\n======================================\n"
        )


    # ====================================
    # SHOW BEST STRATEGY
    # ====================================

    def show_best_strategy(self):

        if len(self.results) == 0:

            print(

                "\nNo benchmark results.\n"
            )

            return


        best_result = min(

            self.results,

            key=lambda x:
            x["average_bps"]
        )


        print(

            "\n========== BEST STRATEGY ==========\n"
        )

        print(

            f"Strategy: "
            f"{best_result['strategy']}"
        )

        print(

            f"Average BPS: "
            f"{best_result['average_bps']}"
        )

        print(

            f"Execution Cost: "
            f"{best_result['execution_cost']}"
        )

        print(

            "\n===================================\n"
        )
