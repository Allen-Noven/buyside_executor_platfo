# ====================================
# risk_manager.py
# ====================================

from utils.config import (

    MAX_ORDER_SIZE,

    MAX_POSITION_SIZE,

    MAX_NOTIONAL,

    MAX_PARTICIPATION
)

from utils.helpers import (

    calculate_notional,

    calculate_participation_rate
)

from utils.logger import (
    SystemLogger
)


class RiskManager:

    def __init__(

        self,

        market_state,

        system_state=None

    ):

        # ====================================
        # LOGGER
        # ====================================

        self.logger = (
            SystemLogger()
        )


        # ====================================
        # SHARED STATE
        # ====================================

        self.market_state = (
            market_state
        )

        self.system_state = (
            system_state
        )


        # ====================================
        # RISK LIMITS
        # ====================================

        self.max_order_size = (
            MAX_ORDER_SIZE
        )

        self.max_position_size = (
            MAX_POSITION_SIZE
        )

        self.max_notional = (
            MAX_NOTIONAL
        )

        self.max_participation = (
            MAX_PARTICIPATION
        )


        # ====================================
        # AUDIT TRAIL
        # ====================================

        self.risk_events = []


    # ====================================
    # LOG RISK EVENT
    # ====================================

    def log_risk_event(

        self,

        approved,

        reason

    ):

        event = {

            "approved":
            approved,

            "reason":
            reason
        }

        self.risk_events.append(
            event
        )


    # ====================================
    # CHECK ORDER SIZE
    # ====================================

    def check_order_size(

        self,

        qty

    ):

        dynamic_limit = (
            self.get_dynamic_order_limit()
        )


        if qty > dynamic_limit:

            return (

                False,

                "Order size exceeds limit"
            )


        return (True, None)


    # ====================================
    # CHECK POSITION LIMIT
    # ====================================

    def check_position_limit(

        self,

        qty,

        current_position

    ):

        projected_position = (

            current_position + qty
        )


        if (

            projected_position
            > self.max_position_size

        ):

            return (

                False,

                "Position limit exceeded"
            )


        return (True, None)


    # ====================================
    # CHECK NOTIONAL
    # ====================================

    def check_notional_limit(

        self,

        qty

    ):

        market_price = (
            self.market_state.current_price
        )


        if market_price is None:

            return (

                False,

                "No market price available"
            )


        notional = calculate_notional(

            qty,

            market_price
        )


        if notional > self.max_notional:

            return (

                False,

                "Notional limit exceeded"
            )


        return (True, None)


    # ====================================
    # CHECK PARTICIPATION
    # ====================================

    def check_participation_rate(

        self,

        qty

    ):

        market_volume = (
            self.market_state.current_volume
        )


        if (

            market_volume is None
            or
            market_volume == 0

        ):

            return (

                False,

                "No market volume available"
            )


        participation_rate = (

            calculate_participation_rate(

                qty,

                market_volume
            )
        )


        dynamic_limit = (
            self.get_dynamic_participation_limit()
        )


        if participation_rate > dynamic_limit:

            return (

                False,

                "Participation too high"
            )


        return (True, None)


    # ====================================
    # DYNAMIC ORDER LIMIT
    # ====================================

    def get_dynamic_order_limit(self):

        volatility = (
            self.market_state.volatility
        )


        if volatility is None:

            return self.max_order_size


        # high volatility
        if volatility > 0.05:

            return (

                self.max_order_size * 0.5
            )


        return self.max_order_size


    # ====================================
    # DYNAMIC PARTICIPATION
    # ====================================

    def get_dynamic_participation_limit(self):

        liquidity_score = (
            self.market_state.liquidity_score
        )


        if liquidity_score is None:

            return self.max_participation


        # poor liquidity
        if liquidity_score < 50:

            return (

                self.max_participation * 0.5
            )


        return self.max_participation


    # ====================================
    # AI RISK CHECK
    # ====================================

    def check_ai_risk(self):

        if self.system_state is None:

            return (True, None)


        ai_result = (
            self.system_state.ai_risk_result
        )


        if ai_result is None:

            return (True, None)


        severity = ai_result.get(
            "severity"
        )


        halt_execution = ai_result.get(
            "halt_execution"
        )


        if (

            severity == "HIGH"
            and halt_execution

        ):

            return (

                False,

                "AI risk engine halted execution"
            )


        return (True, None)


    # ====================================
    # OVERALL VALIDATION
    # ====================================

    def validate_order(

        self,

        qty,

        current_position

    ):

        checks = [

            self.check_order_size(qty),

            self.check_position_limit(

                qty,

                current_position
            ),

            self.check_notional_limit(
                qty
            ),

            self.check_participation_rate(
                qty
            ),

            self.check_ai_risk()
        ]


        for approved, reason in checks:

            if not approved:

                self.logger.warning(

                    f"Risk Rejected | "
                    f"{reason}"
                )

                self.log_risk_event(
                    False,
                    reason
                )

                return {

                    "approved":
                    False,

                    "reason":
                    reason
                }


        self.logger.info(
            "Risk Check Passed"
        )

        self.log_risk_event(
            True,
            "Approved"
        )

        return {

            "approved":
            True,

            "reason":
            None
        }


    # ====================================
    # GET RISK EVENTS
    # ====================================

    def get_risk_events(self):

        return self.risk_events