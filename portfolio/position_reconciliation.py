# ====================================
# position_reconciliation.py
# ====================================

from utils.logger import (
    SystemLogger
)

from utils.helpers import (
    get_current_timestamp
)

from utils.constants import (

    POSITION_MISMATCH_EVENT,

    RECONCILIATION_COMPLETED_EVENT
)


class PositionReconciliation:


    # ====================================
    # INIT
    # ====================================

    def __init__(

        self,

        internal_position_manager,

        broker_positions,

        event_bus=None,

        tolerance=0.0001
    ):

        self.logger = (
            SystemLogger()
        )

        self.internal_position_manager = (
            internal_position_manager
        )

        self.broker_positions = (
            broker_positions
        )

        self.event_bus = (
            event_bus
        )

        self.tolerance = (
            tolerance
        )

        self.last_results = []


    # ====================================
    # RECONCILE POSITIONS
    # ====================================

    def reconcile_positions(self):

        internal_positions = (

            self.internal_position_manager
            .snapshot_positions()
        )

        broker_positions = (

            self.broker_positions
            .snapshot_positions()
        )

        reconciliation_results = []

        # ====================================
        # GET ALL SYMBOLS
        # ====================================

        all_symbols = set(

            list(
                internal_positions.keys()
            )

            +

            list(
                broker_positions.keys()
            )
        )

        # ====================================
        # COMPARE POSITIONS
        # ====================================

        for symbol in all_symbols:

            internal_qty = (

                internal_positions
                .get(symbol, {})
                .get("qty", 0)
            )

            broker_qty = (

                broker_positions
                .get(symbol, {})
                .get("qty", 0)
            )

            difference = (

                internal_qty
                -
                broker_qty
            )

            matched = (

                abs(difference)
                <=
                self.tolerance
            )

            result = {

                "timestamp":
                get_current_timestamp(),

                "symbol":
                symbol,

                "internal_qty":
                internal_qty,

                "broker_qty":
                broker_qty,

                "difference":
                difference,

                "matched":
                matched
            }

            reconciliation_results.append(
                result
            )

            # ====================================
            # LOG / EVENT
            # ====================================

            if matched:

                self.logger.info(

                    f"[RECONCILIATION] "

                    f"{symbol} matched"
                )

            else:

                self.logger.warning(

                    f"[RECONCILIATION] "

                    f"{symbol} mismatch | "

                    f"Internal={internal_qty} | "

                    f"Broker={broker_qty} | "

                    f"Diff={difference}"
                )

                if self.event_bus:

                    self.event_bus.publish(

                        POSITION_MISMATCH_EVENT,

                        result
                    )

        self.last_results = (
            reconciliation_results
        )

        # ====================================
        # COMPLETED EVENT
        # ====================================

        if self.event_bus:

            self.event_bus.publish(

                RECONCILIATION_COMPLETED_EVENT,

                self.get_summary()
            )

        return reconciliation_results


    # ====================================
    # GET MISMATCHES
    # ====================================

    def get_mismatches(self):

        return [

            result

            for result in self.last_results

            if not result[
                "matched"
            ]
        ]


    # ====================================
    # HAS MISMATCH
    # ====================================

    def has_mismatch(self):

        return (

            len(
                self.get_mismatches()
            )
            >
            0
        )


    # ====================================
    # GET SUMMARY
    # ====================================

    def get_summary(self):

        total = (
            len(
                self.last_results
            )
        )

        mismatches = (
            len(
                self.get_mismatches()
            )
        )

        matched = (
            total
            -
            mismatches
        )

        return {

            "total":
            total,

            "matched":
            matched,

            "mismatches":
            mismatches,

            "has_mismatch":
            mismatches > 0
        }


    # ====================================
    # SHOW RECONCILIATION REPORT
    # ====================================

    def show_reconciliation_report(self):

        if not self.last_results:

            self.reconcile_positions()

        self.logger.warning(

            "========== "
            "POSITION RECONCILIATION "
            "=========="
        )

        for result in self.last_results:

            self.logger.info(

                f"{result['symbol']} | "

                f"Internal={result['internal_qty']} | "

                f"Broker={result['broker_qty']} | "

                f"Difference={result['difference']} | "

                f"Matched={result['matched']}"
            )

        self.logger.warning(

            "========== "
            "RECONCILIATION SUMMARY "
            "=========="
        )

        summary = (
            self.get_summary()
        )

        for key, value in summary.items():

            self.logger.info(

                f"{key} = {value}"
            )