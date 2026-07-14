# ====================================
# monitoring_panel.py
# ====================================

import streamlit as st

from core.global_state import (
    system_state
)

from utils.helpers import (
    format_timestamp
)


class MonitoringPanel:

    def __init__(self):

        self.system_state = (
            system_state
        )


    # ====================================
    # SYSTEM HEALTH
    # ====================================

    def render_system_health(self):

        st.subheader(
            "System Health"
        )

        col1, col2, col3 = (
            st.columns(3)
        )

        # ====================================
        # SYSTEM STATUS
        # ====================================

        if (

            self.system_state
            .system_online

        ):

            col1.success(
                "ONLINE"
            )

        else:

            col1.error(
                "OFFLINE"
            )

        # ====================================
        # EXECUTION STATUS
        # ====================================

        col2.info(

            self.system_state
            .execution_status
        )

        # ====================================
        # LAST UPDATE
        # ====================================

        col3.metric(

            "Last Update",

            format_timestamp(

                self.system_state
                .last_update_time
            )
        )


    # ====================================
    # MARKET MONITOR
    # ====================================

    def render_market_monitor(self):

        market = (
            self.system_state
            .market_state
        )

        st.subheader(
            "Market Monitor"
        )

        col1, col2, col3, col4 = (
            st.columns(4)
        )

        col1.metric(

            "Current Price",

            market.current_price
        )

        col2.metric(

            "Spread",

            market.spread
        )

        col3.metric(

            "Volume",

            market.current_volume
        )

        col4.metric(

            "Liquidity",

            market.liquidity_score
        )

        col5, col6, col7 = (
            st.columns(3)
        )

        col5.metric(

            "Bid",

            market.bid_price
        )

        col6.metric(

            "Ask",

            market.ask_price
        )

        col7.metric(

            "Volatility",

            market.volatility
        )


    # ====================================
    # RISK MONITOR
    # ====================================

    def render_risk_monitor(self):

        st.subheader(
            "Risk Monitor"
        )

        ai_risk = (

            self.system_state
            .ai_risk_result
        )

        severity = (
            ai_risk["severity"]
        )

        if severity == "HIGH":

            st.error(

                f"HIGH RISK | "

                f"{ai_risk['reason']}"
            )

        elif severity == "MEDIUM":

            st.warning(

                f"MEDIUM RISK | "

                f"{ai_risk['reason']}"
            )

        else:

            st.success(

                f"LOW RISK | "

                f"{ai_risk['reason']}"
            )

        st.json(ai_risk)


    # ====================================
    # EXECUTION MONITOR
    # ====================================

    def render_execution_monitor(self):

        st.subheader(
            "Execution Monitor"
        )

        execution = (

            self.system_state
            .execution_summary
        )

        col1, col2, col3, col4 = (
            st.columns(4)
        )

        col1.metric(

            "Strategy",

            execution["strategy"]
        )

        col2.metric(

            "Filled Qty",

            execution["filled_qty"]
        )

        col3.metric(

            "Remaining Qty",

            execution["remaining_qty"]
        )

        col4.metric(

            "Completion",

            execution["completion"]
        )

        st.json(execution)


    # ====================================
    # PNL MONITOR
    # ====================================

    def render_pnl_monitor(self):

        st.subheader(
            "PnL Monitor"
        )

        col1, col2, col3 = (
            st.columns(3)
        )

        col1.metric(

            "Realized PnL",

            round(

                self.system_state
                .realized_pnl,

                2
            )
        )

        col2.metric(

            "Unrealized PnL",

            round(

                self.system_state
                .unrealized_pnl,

                2
            )
        )

        col3.metric(

            "Total PnL",

            round(

                self.system_state
                .total_pnl,

                2
            )
        )


    # ====================================
    # POSITION MONITOR
    # ====================================

    def render_position_monitor(self):

        st.subheader(
            "Position Monitor"
        )

        st.metric(

            "Current Position",

            self.system_state.position
        )


    # ====================================
    # ALERT MONITOR
    # ====================================

    def render_alert_monitor(self):

        st.subheader(
            "Alerts"
        )

        alerts = (
            self.system_state
            .alerts
        )

        if len(alerts) == 0:

            st.success(
                "No Active Alerts"
            )

        else:

            for alert in alerts[-10:]:

                st.warning(alert)


    # ====================================
    # FILLS MONITOR
    # ====================================

    def render_fills_monitor(self):

        st.subheader(
            "Recent Fills"
        )

        fills = (
            self.system_state
            .fills
        )

        if len(fills) == 0:

            st.info(
                "No fills available"
            )

        else:

            st.table(

                fills[-10:]
            )


    # ====================================
    # FULL PANEL
    # ====================================

    def render(self):

        self.render_system_health()

        st.markdown("---")

        self.render_market_monitor()

        st.markdown("---")

        self.render_risk_monitor()

        st.markdown("---")

        self.render_execution_monitor()

        st.markdown("---")

        self.render_pnl_monitor()

        st.markdown("---")

        self.render_position_monitor()

        st.markdown("---")

        self.render_alert_monitor()

        st.markdown("---")

        self.render_fills_monitor()