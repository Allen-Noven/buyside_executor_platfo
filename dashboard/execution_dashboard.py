# ====================================
# execution_dashboard.py
# ====================================

import streamlit as st

from core.global_state import (
    system_state
)

from utils.config import (
    DASHBOARD_TITLE
)


class ExecutionDashboard:

    def __init__(self):

        self.system_state = (
            system_state
        )


    # ====================================
    # PAGE CONFIG
    # ====================================

    def configure_page(self):

        st.set_page_config(

            page_title=
            DASHBOARD_TITLE,

            layout="wide"
        )


    # ====================================
    # HEADER
    # ====================================

    def render_header(self):

        st.title(
            DASHBOARD_TITLE
        )

        st.markdown("---")


    # ====================================
    # MARKET PANEL
    # ====================================

    def render_market_panel(self):

        market = (
            self.system_state
            .market_state
        )

        st.subheader(
            "Market State"
        )

        col1, col2, col3, col4 = (
            st.columns(4)
        )

        col1.metric(

            "Symbol",

            market.symbol
        )

        col2.metric(

            "Price",

            market.current_price
        )

        col3.metric(

            "Spread",

            market.spread
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

            "Volume",

            market.current_volume
        )


    # ====================================
    # EXECUTION PANEL
    # ====================================

    def render_execution_panel(self):

        execution = (

            self.system_state
            .execution_summary
        )

        st.subheader(
            "Execution Summary"
        )

        col1, col2, col3 = (
            st.columns(3)
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

            "Completion",

            execution["completion"]
        )

        st.json(execution)


    # ====================================
    # AI RISK PANEL
    # ====================================

    def render_ai_risk_panel(self):

        ai_risk = (

            self.system_state
            .ai_risk_result
        )

        st.subheader(
            "AI Risk Engine"
        )

        severity = (
            ai_risk["severity"]
        )

        if severity == "HIGH":

            st.error(
                severity
            )

        elif severity == "MEDIUM":

            st.warning(
                severity
            )

        else:

            st.success(
                severity
            )

        st.json(ai_risk)


    # ====================================
    # PNL PANEL
    # ====================================

    def render_pnl_panel(self):

        st.subheader(
            "PnL"
        )

        col1, col2, col3 = (
            st.columns(3)
        )

        col1.metric(

            "Realized",

            round(

                self.system_state
                .realized_pnl,

                2
            )
        )

        col2.metric(

            "Unrealized",

            round(

                self.system_state
                .unrealized_pnl,

                2
            )
        )

        col3.metric(

            "Total",

            round(

                self.system_state
                .total_pnl,

                2
            )
        )


    # ====================================
    # FILLS PANEL
    # ====================================

    def render_fills_panel(self):

        st.subheader(
            "Recent Fills"
        )

        fills = (
            self.system_state
            .fills
        )

        if len(fills) == 0:

            st.info(
                "No fills yet"
            )

        else:

            st.table(

                fills[-10:]
            )


    # ====================================
    # EXECUTION STATUS
    # ====================================

    def render_execution_status(self):

        st.subheader(
            "Execution Status"
        )

        if (

            self.system_state
            .execution_halted

        ):

            st.error(

                f"HALTED | "

                f"{self.system_state.halt_reason}"
            )

        else:

            st.success(
                "RUNNING"
            )


    # ====================================
    # ALERT PANEL
    # ====================================

    def render_alert_panel(self):

        st.subheader(
            "Alerts"
        )

        alerts = (
            self.system_state
            .alerts
        )

        if len(alerts) == 0:

            st.info(
                "No active alerts"
            )

        else:

            for alert in alerts[-10:]:

                st.warning(alert)


    # ====================================
    # FULL DASHBOARD
    # ====================================

    def render(self):

        self.configure_page()

        self.render_header()

        self.render_market_panel()

        st.markdown("---")

        self.render_execution_panel()

        st.markdown("---")

        self.render_ai_risk_panel()

        st.markdown("---")

        self.render_pnl_panel()

        st.markdown("---")

        self.render_fills_panel()

        st.markdown("---")

        self.render_execution_status()

        st.markdown("---")

        self.render_alert_panel()