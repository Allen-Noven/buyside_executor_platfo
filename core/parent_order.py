# ====================================
# parent_order.py
# ====================================

from uuid import uuid4

from core.order_state_machine import (
    OrderStateMachine
)

from utils.logger import (
    SystemLogger
)

from utils.helpers import (

    get_current_time,

    calculate_notional
)

from utils.constants import (

    BUY,

    SELL,

    PENDING,

    RUNNING,

    PARTIALLY_FILLED,

    COMPLETED,

    CANCELLED,

    HALTED,

    FAILED
)


class ParentOrder:


    # ====================================
    # INIT
    # ====================================

    def __init__(

        self,

        symbol,

        side,

        quantity,

        strategy,

        arrival_price=None
    ):

        # ====================================
        # LOGGER
        # ====================================

        self.logger = (
            SystemLogger()
        )

        # ====================================
        # STATE MACHINE
        # ====================================

        self.state_machine = (
            OrderStateMachine()
        )

        # ====================================
        # ORDER ID
        # ====================================

        self.order_id = str(
            uuid4()
        )

        # ====================================
        # BASIC INFO
        # ====================================

        self.symbol = symbol

        self.side = side

        self.quantity = quantity

        self.total_qty = quantity

        self.strategy = strategy

        self.arrival_price = (
            arrival_price
        )

        # ====================================
        # EXECUTION STATE
        # ====================================

        self.filled_quantity = 0

        self.remaining_quantity = (
            quantity
        )

        self.avg_fill_price = 0.0

        # ====================================
        # ORDER STATUS
        # ====================================

        self.status = PENDING

        # ====================================
        # TIMESTAMPS
        # ====================================

        self.created_at = (
            get_current_time()
        )

        self.started_at = None

        self.completed_at = None

        self.halted_at = None

        self.cancelled_at = None

        self.failed_at = None

        # ====================================
        # STATE REASONS
        # ====================================

        self.halt_reason = None

        self.cancel_reason = None

        self.failure_reason = None

        # ====================================
        # EXECUTION METRICS
        # ====================================

        self.notional = 0.0

        self.realized_slippage = 0.0

        self.realized_bps = 0.0

        # ====================================
        # CHILD ORDERS
        # ====================================

        self.child_orders = []

        # ====================================
        # FILLS
        # ====================================

        self.fills = []

        # ====================================
        # VALIDATE ORDER
        # ====================================

        self.validate_order()

        # ====================================
        # LOG
        # ====================================

        self.logger.info(

            f"Parent Order Created | "

            f"{self.symbol} | "

            f"{self.side} | "

            f"Qty: {self.quantity}"
        )


    # ====================================
    # VALIDATE ORDER
    # ====================================

    def validate_order(self):

        if self.side not in [

            BUY,

            SELL
        ]:

            raise ValueError(
                "Invalid Order Side"
            )

        if self.quantity <= 0:

            raise ValueError(
                "Quantity Must Be Positive"
            )


    # ====================================
    # TRANSITION STATE
    # ====================================

    def transition_state(

        self,

        next_state,

        reason=None
    ):

        # ====================================
        # AVOID DUPLICATE TRANSITION
        # ====================================

        if self.status == next_state:

            return

        self.state_machine.transition(

            order=self,

            next_state=next_state,

            reason=reason
        )


    # ====================================
    # START ORDER
    # ====================================

    def start_order(self):

        self.transition_state(
            RUNNING
        )


    # ====================================
    # COMPLETE ORDER
    # ====================================

    def complete_order(self):

        # ====================================
        # PREVENT RECURSION
        # ====================================

        if self.status == COMPLETED:

            return

        self.transition_state(
            COMPLETED
        )


    # ====================================
    # HALT ORDER
    # ====================================

    def halt_order(

        self,

        reason
    ):

        # ====================================
        # PREVENT RECURSION
        # ====================================

        if self.status == HALTED:

            return

        self.transition_state(

            HALTED,

            reason=reason
        )


    # ====================================
    # CANCEL ORDER
    # ====================================

    def cancel_order(

        self,

        reason=None
    ):

        # ====================================
        # PREVENT RECURSION
        # ====================================

        if self.status == CANCELLED:

            return

        self.transition_state(

            CANCELLED,

            reason=reason
        )


    # ====================================
    # FAIL ORDER
    # ====================================

    def fail_order(

        self,

        reason=None
    ):

        # ====================================
        # PREVENT RECURSION
        # ====================================

        if self.status == FAILED:

            return

        self.transition_state(

            FAILED,

            reason=reason
        )


    # ====================================
    # ADD CHILD ORDER
    # ====================================

    def add_child_order(

        self,

        child_order
    ):

        self.child_orders.append(
            child_order
        )

        self.logger.info(

            f"Child Order Added | "

            f"{child_order}"
        )


    # ====================================
    # ADD FILL
    # ====================================

    def add_fill(

        self,

        fill_qty,

        fill_price
    ):

        # ====================================
        # CREATE FILL RECORD
        # ====================================

        fill_data = {

            "timestamp":
            get_current_time(),

            "fill_qty":
            fill_qty,

            "fill_price":
            fill_price
        }

        # ====================================
        # STORE FILL
        # ====================================

        self.fills.append(
            fill_data
        )

        # ====================================
        # UPDATE FILLED QTY
        # ====================================

        self.filled_quantity += (
            fill_qty
        )

        # ====================================
        # UPDATE REMAINING QTY
        # ====================================

        self.remaining_quantity = max(

            0,

            self.quantity
            -
            self.filled_quantity
        )

        # ====================================
        # UPDATE AVG FILL PRICE
        # ====================================

        total_notional = sum(

            fill["fill_qty"]
            *
            fill["fill_price"]

            for fill in self.fills
        )

        total_qty = sum(

            fill["fill_qty"]

            for fill in self.fills
        )

        if total_qty > 0:

            self.avg_fill_price = round(

                total_notional
                /
                total_qty,

                4
            )

        # ====================================
        # UPDATE NOTIONAL
        # ====================================

        self.notional = (

            calculate_notional(

                self.filled_quantity,

                self.avg_fill_price
            )
        )

        # ====================================
        # UPDATE ORDER STATE
        # ====================================

        if self.remaining_quantity <= 0:

            self.transition_state(
                COMPLETED
            )

        else:

            if self.status not in [

                PARTIALLY_FILLED,

                COMPLETED
            ]:

                self.transition_state(
                    PARTIALLY_FILLED
                )

        # ====================================
        # LOG
        # ====================================

        self.logger.info(

            f"Fill Added | "

            f"{self.symbol} | "

            f"Filled: "

            f"{self.filled_quantity}/"

            f"{self.quantity}"
        )


    # ====================================
    # GET COMPLETION RATE
    # ====================================

    def get_completion_rate(self):

        if self.quantity == 0:

            return 0

        return round(

            (

                self.filled_quantity
                /
                self.quantity

            ) * 100,

            2
        )


    # ====================================
    # IS ACTIVE
    # ====================================

    def is_active(self):

        return self.status in [

            RUNNING,

            PARTIALLY_FILLED
        ]


    # ====================================
    # IS COMPLETED
    # ====================================

    def is_completed(self):

        return self.status == COMPLETED


    # ====================================
    # GET SNAPSHOT
    # ====================================

    def get_snapshot(self):

        return {

            "order_id":
            self.order_id,

            "symbol":
            self.symbol,

            "side":
            self.side,

            "strategy":
            self.strategy,

            "quantity":
            self.quantity,

            "filled_quantity":
            self.filled_quantity,

            "remaining_quantity":
            self.remaining_quantity,

            "completion_rate":
            self.get_completion_rate(),

            "avg_fill_price":
            self.avg_fill_price,

            "arrival_price":
            self.arrival_price,

            "status":
            self.status,

            "notional":
            self.notional,

            "created_at":
            str(self.created_at),

            "started_at":
            str(self.started_at)
            if self.started_at
            else None,

            "completed_at":
            str(self.completed_at)
            if self.completed_at
            else None,

            "halted_at":
            str(self.halted_at)
            if self.halted_at
            else None,

            "cancelled_at":
            str(self.cancelled_at)
            if self.cancelled_at
            else None,

            "failed_at":
            str(self.failed_at)
            if self.failed_at
            else None,

            "halt_reason":
            self.halt_reason,

            "cancel_reason":
            self.cancel_reason,

            "failure_reason":
            self.failure_reason
        }


    # ====================================
    # SHOW ORDER
    # ====================================

    def show(self):

        snapshot = (
            self.get_snapshot()
        )

        print(

            "\n========== PARENT ORDER ==========\n"
        )

        for key, value in snapshot.items():

            print(f"{key}: {value}")

        print(

            "\n==================================\n"
        )
