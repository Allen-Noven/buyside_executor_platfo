# ====================================
# reconciliation# reconciliation_engine.py

from utils.logger import (
    SystemLogger
)


class ReconciliationEngine:


    # ====================================
    # INIT
    # ====================================

    def __init__(

        self,

        oms,

        execution_service,

        position_manager
    ):

        self.oms = oms

        self.execution_service = (
            execution_service
        )

        self.position_manager = (
            position_manager
        )

        self.logger = (
            SystemLogger()
        )


    # ====================================
    # RECONCILE POSITIONS
    # ====================================

    def reconcile_positions(self):

        self.logger.info(
            "Reconciling Positions"
        )

        try:

            broker_positions = (
                self.oms.get_positions()
            )

            internal_positions = (

                self.position_manager
                .get_all_positions()
            )

            mismatches = []

            # ====================================
            # CHECK INTERNAL VS BROKER
            # ====================================

            for symbol, internal_position in (

                internal_positions.items()
            ):

                broker_qty = (

                    broker_positions
                    .get(symbol, {})
                    .get("quantity", 0)
                )

                internal_qty = (

                    internal_position
                    .get("quantity", 0)
                )

                if broker_qty != internal_qty:

                    mismatch = {

                        "symbol":
                        symbol,

                        "broker_qty":
                        broker_qty,

                        "internal_qty":
                        internal_qty
                    }

                    mismatches.append(
                        mismatch
                    )

                    self.logger.error(

                        f"Position Mismatch | "

                        f"{symbol} | "

                        f"Broker={broker_qty} | "

                        f"Internal={internal_qty}"
                    )

            # ====================================
            # CHECK BROKER ONLY POSITIONS
            # ====================================

            for symbol, broker_position in (

                broker_positions.items()
            ):

                if symbol not in internal_positions:

                    mismatch = {

                        "symbol":
                        symbol,

                        "broker_qty":
                        broker_position.get(
                            "quantity",
                            0
                        ),

                        "internal_qty":
                        0
                    }

                    mismatches.append(
                        mismatch
                    )

                    self.logger.error(

                        f"Broker Position Missing "
                        f"Internally | "

                        f"{symbol}"
                    )

            # ====================================
            # SUCCESS
            # ====================================

            if len(mismatches) == 0:

                self.logger.info(
                    "Position Reconciliation Passed"
                )

            return mismatches

        except Exception as error:

            self.logger.error(

                f"Position Reconciliation Failed | "

                f"{error}"
            )

            return []


    # ====================================
    # RECONCILE ORDERS
    # ====================================

    def reconcile_orders(self):

        self.logger.info(
            "Reconciling Orders"
        )

        try:

            broker_orders = (
                self.oms.get_open_orders()
            )

            internal_orders = (

                self.execution_service
                .active_orders
            )

            # ====================================
            # NORMALIZE BROKER IDS
            # ====================================

            broker_order_ids = set()

            for order in broker_orders:

                try:

                    order_id = str(order.id)

                except Exception:

                    order_id = str(

                        order.get(
                            "order_id"
                        )
                    )

                broker_order_ids.add(
                    order_id
                )

            # ====================================
            # INTERNAL IDS
            # ====================================

            internal_order_ids = {

                str(order_id)

                for order_id

                in internal_orders
            }

            # ====================================
            # BROKER ONLY
            # ====================================

            missing_internal = (

                broker_order_ids
                -
                internal_order_ids
            )

            # ====================================
            # INTERNAL ONLY
            # ====================================

            missing_broker = (

                internal_order_ids
                -
                broker_order_ids
            )

            # ====================================
            # LOG BROKER ONLY
            # ====================================

            for order_id in missing_internal:

                self.logger.error(

                    f"Broker Order Missing "
                    f"Internally | "

                    f"{order_id}"
                )

            # ====================================
            # LOG INTERNAL ONLY
            # ====================================

            for order_id in missing_broker:

                self.logger.error(

                    f"Internal Order Missing "
                    f"At Broker | "

                    f"{order_id}"
                )

            # ====================================
            # SUCCESS
            # ====================================

            if (

                len(missing_internal) == 0
                and
                len(missing_broker) == 0

            ):

                self.logger.info(
                    "Order Reconciliation Passed"
                )

            return {

                "missing_internal":
                list(missing_internal),

                "missing_broker":
                list(missing_broker)
            }

        except Exception as error:

            self.logger.error(

                f"Order Reconciliation Failed | "

                f"{error}"
            )

            return {

                "missing_internal":
                [],

                "missing_broker":
                []
            }


    # ====================================
    # RECONCILE ALL
    # ====================================

    def reconcile_all(self):

        self.logger.info(
            "Starting Full Reconciliation"
        )

        # ====================================
        # POSITIONS
        # ====================================

        position_mismatches = (
            self.reconcile_positions()
        )

        # ====================================
        # ORDERS
        # ====================================

        order_mismatches = (
            self.reconcile_orders()
        )

        self.logger.info(
            "Reconciliation Complete"
        )

        return {

            "position_mismatches":
            position_mismatches,

            "order_mismatches":
            order_mismatches
        }
