# ====================================
# system_state.py
# ====================================

from core.market_state import (
    MarketState
)

from utils.logger import (
    SystemLogger
)

from utils.constants import (
    RUNNING
)


class SystemState:

    def __init__(self):

        # ====================================
        # LOGGER
        # ====================================

        self.logger = (
            SystemLogger()
        )

        # ====================================
        # MARKET STATE
        # ====================================

        self.market_state = (
            MarketState()
        )

        # ====================================
        # EXECUTION SUMMARY
        # ====================================

        self.execution_summary = {

            "strategy":
            "TWAP",

            "symbol":
            None,

            "filled_qty":
            0,

            "remaining_qty":
            0,

            "target_qty":
            0,

            "avg_fill_price":
            0,

            "completion":
            "0%"
        }

        # ====================================
        # EXECUTION STATUS
        # ====================================

        self.execution_status = (
            RUNNING
        )

        self.execution_halted = False

        self.halt_reason = None

        # ====================================
        # FILLS
        # ====================================

        self.fills = []

        # ====================================
        # ACTIVE ORDERS
        # ====================================

        self.active_orders = []

        # ====================================
        # AI RISK
        # ====================================

        self.ai_risk_result = {

            "severity":
            "LOW",

            "recommended_action":
            "MONITOR",

            "confidence":
            1.0,

            "reason":
            "No active risk events"
        }

        # ====================================
        # ALERTS
        # ====================================

        self.alerts = []

        # ====================================
        # RISK EVENTS
        # ====================================

        self.risk_events = []

        # ====================================
        # PNL
        # ====================================

        self.realized_pnl = 0.0

        self.unrealized_pnl = 0.0

        self.total_pnl = 0.0

        # ====================================
        # POSITION
        # ====================================

        self.position = 0

        # ====================================
        # SLIPPAGE
        # ====================================

        self.total_slippage = 0.0

        self.avg_slippage_bps = 0.0

        # ====================================
        # SYSTEM HEALTH
        # ====================================

        self.system_online = True

        self.last_update_time = None


    # ====================================
    # UPDATE EXECUTION SUMMARY
    # ====================================

    def update_execution_summary(

        self,

        strategy=None,

        symbol=None,

        filled_qty=None,

        remaining_qty=None,

        target_qty=None,

        avg_fill_price=None

    ):

        if strategy is not None:

            self.execution_summary[
                "strategy"
            ] = strategy

        if symbol is not None:

            self.execution_summary[
                "symbol"
            ] = symbol

        if filled_qty is not None:

            self.execution_summary[
                "filled_qty"
            ] = filled_qty

        if remaining_qty is not None:

            self.execution_summary[
                "remaining_qty"
            ] = remaining_qty

        if target_qty is not None:

            self.execution_summary[
                "target_qty"
            ] = target_qty

        if avg_fill_price is not None:

            self.execution_summary[
                "avg_fill_price"
            ] = avg_fill_price

        # ====================================
        # COMPLETION %
        # ====================================

        target = self.execution_summary[
            "target_qty"
        ]

        filled = self.execution_summary[
            "filled_qty"
        ]

        if target > 0:

            completion = round(

                (filled / target) * 100,

                2
            )

            self.execution_summary[
                "completion"
            ] = f"{completion}%"

        self.logger.info(

            "Execution Summary Updated"
        )


    # ====================================
    # ADD FILL
    # ====================================

    def add_fill(

        self,

        fill_data

    ):

        self.fills.append(
            fill_data
        )

        self.logger.info(

            f"Fill Added | "
            f"{fill_data}"
        )


    # ====================================
    # ADD ALERT
    # ====================================

    def add_alert(

        self,

        alert

    ):

        self.alerts.append(
            alert
        )

        self.logger.warning(

            f"Alert Added | "
            f"{alert}"
        )


    # ====================================
    # ADD RISK EVENT
    # ====================================

    def add_risk_event(

        self,

        risk_event

    ):

        self.risk_events.append(
            risk_event
        )

        self.logger.warning(

            f"Risk Event | "
            f"{risk_event}"
        )


    # ====================================
    # UPDATE AI RISK
    # ====================================

    def update_ai_risk(

        self,

        ai_result

    ):

        self.ai_risk_result = (
            ai_result
        )

        self.logger.info(

            "AI Risk Updated"
        )


    # ====================================
    # UPDATE PNL
    # ====================================

    def update_pnl(

        self,

        realized=None,

        unrealized=None

    ):

        if realized is not None:

            self.realized_pnl = (
                realized
            )

        if unrealized is not None:

            self.unrealized_pnl = (
                unrealized
            )

        self.total_pnl = (

            self.realized_pnl
            +
            self.unrealized_pnl
        )

        self.logger.info(

            f"PnL Updated | "
            f"Total: {self.total_pnl}"
        )


    # ====================================
    # SYSTEM SNAPSHOT
    # ====================================

    def get_snapshot(self):

        return {

            "market_state":

            self.market_state.get_snapshot(),

            "execution_summary":

            self.execution_summary,

            "execution_status":

            self.execution_status,

            "execution_halted":

            self.execution_halted,

            "halt_reason":

            self.halt_reason,

            "position":

            self.position,

            "realized_pnl":

            self.realized_pnl,

            "unrealized_pnl":

            self.unrealized_pnl,

            "total_pnl":

            self.total_pnl,

            "fills_count":

            len(self.fills),

            "alerts_count":

            len(self.alerts),

            "risk_events_count":

            len(self.risk_events)
        }