# ====================================
# kill_switch.py
# ====================================

from utils.helpers import (
    get_current_time
)

from utils.logger import (
    SystemLogger
)

from notifications.email_service import (
    EmailService
)

from utils.constants import (

    HALTED,

    RUNNING,

    KILL_SWITCH_EVENT
)


class KillSwitch:


    # ====================================
    # INIT
    # ====================================

    def __init__(

        self,

        scheduler=None,

        oms=None,

        system_state=None,

        event_bus=None,

        execution_service=None,

        execution_worker=None,

        position_manager=None
    ):

        # ====================================
        # LOGGER
        # ====================================

        self.logger = (
            SystemLogger()
        )

        # ====================================
        # EMAIL SERVICE
        # ====================================

        self.email_service = (
            EmailService()
        )

        # ====================================
        # EVENT BUS
        # ====================================

        self.event_bus = (
            event_bus
        )

        # ====================================
        # SHARED COMPONENTS
        # ====================================

        self.scheduler = (
            scheduler
        )

        self.oms = oms

        self.system_state = (
            system_state
        )

        self.execution_service = (
            execution_service
        )

        self.execution_worker = (
            execution_worker
        )

        self.position_manager = (
            position_manager
        )

        # ====================================
        # EXECUTION STATE
        # ====================================

        self.execution_halted = False

        self.halt_reason = None

        # ====================================
        # AUDIT TRAIL
        # ====================================

        self.events = []


    # ====================================
    # HALT EXECUTION
    # ====================================

    def halt_execution(

        self,

        reason,

        trigger_source="UNKNOWN"
    ):

        self.execution_halted = True

        self.halt_reason = reason

        # ====================================
        # STOP SCHEDULER
        # ====================================

        if self.scheduler:

            self.scheduler.stop()

        # ====================================
        # UPDATE SYSTEM STATE
        # ====================================

        if self.system_state:

            self.system_state.execution_halted = (
                True
            )

            self.system_state.halt_reason = (
                reason
            )

            self.system_state.execution_status = (
                HALTED
            )

        # ====================================
        # AUDIT EVENT
        # ====================================

        event = {

            "timestamp":
            get_current_time(),

            "trigger_source":
            trigger_source,

            "reason":
            reason
        }

        self.events.append(
            event
        )

        # ====================================
        # LOG EVENT
        # ====================================

        self.logger.error(

            f"KILL SWITCH ACTIVATED | "

            f"{reason}"
        )

        # ====================================
        # EMAIL ALERT
        # ====================================

        try:

            self.email_service.send_kill_switch_alert(

                symbol="SYSTEM",

                reason=reason
            )

        except Exception as error:

            self.logger.error(

                f"Email Alert Failed | "

                f"{error}"
            )

        # ====================================
        # PUBLISH EVENT
        # ====================================

        if self.event_bus:

            self.event_bus.publish(

                KILL_SWITCH_EVENT,

                {

                    "halted":
                    True,

                    "reason":
                    reason
                }
            )


    # ====================================
    # HALT ALL EXECUTION
    # ====================================

    def halt_all_execution(self):

        self.execution_halted = True

        # ====================================
        # STOP SCHEDULER
        # ====================================

        if self.scheduler:

            self.scheduler.stop()

        # ====================================
        # STOP EXECUTION SERVICE
        # ====================================

        if self.execution_service:

            self.execution_service.stop()

        # ====================================
        # STOP EXECUTION WORKER
        # ====================================

        if self.execution_worker:

            self.execution_worker.stop()

        self.logger.warning(
            "All Execution Halted"
        )


    # ====================================
    # CANCEL ALL ORDERS
    # ====================================

    def cancel_all_orders(self):

        if self.execution_service is None:

            return

        active_orders = (

            self.execution_service
            .active_orders
        )

        for order_id in active_orders:

            try:

                if self.oms:

                    self.oms.cancel_order(
                        order_id
                    )

            except Exception as error:

                self.logger.error(

                    f"Cancel Failed | "

                    f"{error}"
                )


    # ====================================
    # FLATTEN POSITIONS
    # ====================================

    def flatten_positions(self):

        if self.position_manager is None:

            return

        positions = (

            self.position_manager
            .get_all_positions()
        )

        for symbol, position in positions.items():

            quantity = abs(

                position.get(
                    "quantity",
                    0
                )
            )

            if quantity == 0:

                continue

            side = "SELL"

            if position["quantity"] < 0:

                side = "BUY"

            try:

                if self.oms:

                    self.oms.submit_market_order(

                        symbol=symbol,

                        qty=quantity,

                        side=side
                    )

                self.logger.warning(

                    f"Flattened | "

                    f"{symbol}"
                )

            except Exception as error:

                self.logger.error(

                    f"Flatten Failed | "

                    f"{error}"
                )


    # ====================================
    # EMERGENCY SHUTDOWN
    # ====================================

    def emergency_shutdown(

        self,

        reason="UNKNOWN"
    ):

        self.logger.warning(

            f"Emergency Shutdown | "

            f"{reason}"
        )

        self.halt_all_execution()

        self.cancel_all_orders()

        self.flatten_positions()

        self.halt_reason = reason

        self.execution_halted = True

        self.logger.warning(
            "Emergency Shutdown Complete"
        )


    # ====================================
    # RESUME EXECUTION
    # ====================================

    def resume_execution(self):

        self.execution_halted = False

        self.halt_reason = None

        # ====================================
        # RESUME SCHEDULER
        # ====================================

        if self.scheduler:

            self.scheduler.resume()

        # ====================================
        # UPDATE SYSTEM STATE
        # ====================================

        if self.system_state:

            self.system_state.execution_halted = (
                False
            )

            self.system_state.halt_reason = None

            self.system_state.execution_status = (
                RUNNING
            )

        self.logger.warning(
            "Execution Resumed"
        )


    # ====================================
    # EVENT CALLBACK
    # ====================================

    def on_ai_risk(

        self,

        ai_result
    ):

        self.process_ai_risk(
            ai_result
        )


    # ====================================
    # CHECK HALT STATUS
    # ====================================

    def is_halted(self):

        return self.execution_halted


    # ====================================
    # GET HALT REASON
    # ====================================

    def get_halt_reason(self):

        return self.halt_reason


    # ====================================
    # GET AUDIT EVENTS
    # ====================================

    def get_events(self):

        return self.events


    # ====================================
    # PROCESS AI RISK
    # ====================================

    def process_ai_risk(

        self,

        ai_result
    ):

        if ai_result is None:

            return

        severity = (
            ai_result["severity"]
        )

        halt_execution = (
            ai_result.get(

                "halt_execution",

                False
            )
        )

        reason = (
            ai_result.get(

                "reason",

                "Unknown Risk"
            )
        )

        recommended_action = (

            ai_result.get(

                "recommended_action",

                "MONITOR"
            )
        )

        # ====================================
        # HARD HALT
        # ====================================

        if (

            severity == "HIGH"
            and
            halt_execution

        ):

            self.logger.error(

                f"AI Risk Triggered | "

                f"{reason}"
            )

            self.emergency_shutdown(
                reason
            )

        # ====================================
        # REDUCE AGGRESSION
        # ====================================

        elif recommended_action == (

            "REDUCE_AGGRESSION"
        ):

            self.logger.warning(

                "AI recommends reducing "
                "execution aggression."
            )

        # ====================================
        # SWITCH TO ICEBERG
        # ====================================

        elif recommended_action == (

            "SWITCH_TO_ICEBERG"
        ):

            self.logger.warning(

                "AI recommends switching "
                "to ICEBERG execution."
            )

        # ====================================
        # NORMAL STATE
        # ====================================

        else:

            self.logger.info(

                "Risk Level Acceptable | "
                "Execution Continues"
            )