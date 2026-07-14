# ====================================
# order_state_machine.py
# ====================================

from utils.logger import (
    SystemLogger
)

from utils.constants import (

    PENDING,

    RUNNING,

    PARTIALLY_FILLED,

    COMPLETED,

    CANCELLED,

    HALTED,

    FAILED
)

from utils.helpers import (
    get_current_time
)


class OrderStateMachine:


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
        # VALID TRANSITIONS
        # ====================================

        self.valid_transitions = {

            # ====================================
            # PENDING
            # ====================================

            PENDING: [

                RUNNING,

                CANCELLED,

                FAILED
            ],

            # ====================================
            # RUNNING
            # ====================================

            RUNNING: [

                PARTIALLY_FILLED,

                COMPLETED,

                HALTED,

                CANCELLED,

                FAILED
            ],

            # ====================================
            # PARTIALLY FILLED
            # ====================================

            PARTIALLY_FILLED: [

                RUNNING,

                COMPLETED,

                HALTED,

                CANCELLED,

                FAILED
            ],

            # ====================================
            # HALTED
            # ====================================

            HALTED: [

                RUNNING,

                CANCELLED,

                FAILED
            ],

            # ====================================
            # COMPLETED
            # ====================================

            COMPLETED: [],

            # ====================================
            # CANCELLED
            # ====================================

            CANCELLED: [],

            # ====================================
            # FAILED
            # ====================================

            FAILED: []
        }

        self.logger.info(
            "Order State Machine Initialized"
        )


    # ====================================
    # VALIDATE TRANSITION
    # ====================================

    def can_transition(

        self,

        current_state,

        next_state
    ):

        allowed_states = (

            self.valid_transitions.get(

                current_state,

                []
            )
        )

        return next_state in allowed_states


    # ====================================
    # TRANSITION
    # ====================================

    def transition(

        self,

        order,

        next_state,

        reason=None
    ):

        current_state = (
            order.status
        )

        # ====================================
        # VALIDATE
        # ====================================

        if not self.can_transition(

            current_state,

            next_state
        ):

            self.logger.error(

                f"Invalid Transition | "

                f"{current_state} -> "

                f"{next_state}"
            )

            raise ValueError(

                f"Cannot transition "

                f"from {current_state} "

                f"to {next_state}"
            )

        # ====================================
        # UPDATE STATUS
        # ====================================

        order.status = next_state

        # ====================================
        # UPDATE STATE TIMESTAMPS
        # ====================================

        self.update_state_metadata(

            order,

            next_state,

            reason
        )

        # ====================================
        # LOG
        # ====================================

        self.logger.info(

            f"Order Transition | "

            f"{order.order_id} | "

            f"{current_state} -> "

            f"{next_state}"
        )

        return next_state


    # ====================================
    # UPDATE METADATA
    # ====================================

    def update_state_metadata(

        self,

        order,

        state,

        reason=None
    ):

        # ====================================
        # STARTED
        # ====================================

        if state == RUNNING:

            order.started_at = (
                get_current_time()
            )

        # ====================================
        # COMPLETED
        # ====================================

        elif state == COMPLETED:

            order.completed_at = (
                get_current_time()
            )

        # ====================================
        # HALTED
        # ====================================

        elif state == HALTED:

            order.halted_at = (
                get_current_time()
            )

            order.halt_reason = (
                reason
            )

        # ====================================
        # CANCELLED
        # ====================================

        elif state == CANCELLED:

            order.cancelled_at = (
                get_current_time()
            )

            order.cancel_reason = (
                reason
            )

        # ====================================
        # FAILED
        # ====================================

        elif state == FAILED:

            order.failed_at = (
                get_current_time()
            )

            order.failure_reason = (
                reason
            )


    # ====================================
    # TERMINAL STATE
    # ====================================

    def is_terminal_state(

        self,

        state
    ):

        return state in [

            COMPLETED,

            CANCELLED,

            FAILED
        ]


    # ====================================
    # GET VALID TRANSITIONS
    # ====================================

    def get_valid_transitions(

        self,

        state
    ):

        return self.valid_transitions.get(

            state,

            []
        )


    # ====================================
    # RESET ORDER
    # ====================================

    def reset_order(

        self,

        order
    ):

        order.status = PENDING

        order.started_at = None

        order.completed_at = None

        order.halted_at = None

        order.cancelled_at = None

        order.failed_at = None

        order.halt_reason = None

        order.cancel_reason = None

        order.failure_reason = None

        self.logger.warning(

            f"Order Reset | "

            f"{order.order_id}"
        )


    # ====================================
    # SHOW TRANSITIONS
    # ====================================

    def show_transitions(self):

        print(

            "\n========== ORDER STATE MACHINE ==========\n"
        )

        for state, transitions in (

            self.valid_transitions.items()
        ):

            print(

                f"{state} -> {transitions}"
            )

        print(

            "\n=========================================\n"
        )