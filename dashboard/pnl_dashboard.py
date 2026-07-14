# ====================================
# pnl_dashboard.py
# ====================================

import streamlit as st
import pandas as pd


class PnLDashboard:


    # ====================================
    # INIT
    # ====================================

    def __init__(

        self,

        fills
    ):

        self.fills = fills


    # ====================================
    # CALCULATE PNL
    # ====================================

    def calculate_pnl(self):

        realized_pnl = 0

        total_notional = 0

        total_qty = 0

        for fill in self.fills:

            qty = fill.get(
                "qty",
                0
            )

            fill_price = fill.get(
                "fill_price",
                0
            )

            total_qty += qty

            total_notional += (
                qty * fill_price
            )

        avg_price = 0

        if total_qty > 0:

            avg_price = round(

                total_notional
                /
                total_qty,

                4
            )

        return {

            "realized_pnl":
            round(realized_pnl, 2),

            "total_qty":
            total_qty,

            "avg_fill_price":
            avg_price,

            "total_notional":
            round(total_notional, 2)
        }


    # ====================================
    # RENDER METRICS
    # ====================================

    def render_metrics(

        self,

        pnl
    ):

        col1, col2, col3, col4 = (
            st.columns(4)
        )

        col1.metric(

            "Realized PnL",

            pnl["realized_pnl"]
        )

        col2.metric(

            "Total Qty",

            pnl["total_qty"]
        )

        col3.metric(

            "Avg Fill Price",

            pnl["avg_fill_price"]
        )

        col4.metric(

            "Total Notional",

            pnl["total_notional"]
        )


    # ====================================
    # RENDER FILLS TABLE
    # ====================================

    def render_fills_table(self):

        st.subheader(
            "Execution Fills"
        )

        if len(self.fills) == 0:

            st.info(
                "No fills available"
            )

            return

        df = pd.DataFrame(
            self.fills
        )

        st.dataframe(

            df,

            use_container_width=True
        )


    # ====================================
    # RENDER CHART
    # ====================================

    def render_chart(self):

        st.subheader(
            "Fill Price Trend"
        )

        if len(self.fills) == 0:

            st.info(
                "No fill chart available"
            )

            return

        df = pd.DataFrame(
            self.fills
        )

        if "fill_price" in df.columns:

            chart_df = pd.DataFrame({

                "fill_price":
                df["fill_price"]
            })

            st.line_chart(
                chart_df
            )


    # ====================================
    # RENDER DASHBOARD
    # ====================================

    def render(self):

        st.subheader(
            "PnL Dashboard"
        )

        pnl = (
            self.calculate_pnl()
        )

        self.render_metrics(
            pnl
        )

        st.markdown("---")

        self.render_chart()

        st.markdown("---")

        self.render_fills_table()