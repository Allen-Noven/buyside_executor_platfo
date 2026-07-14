# ====================================
# order_entry.py
# ====================================

import os

import requests
import streamlit as st


# ====================================
# API CONFIG
# ====================================

API_URL = (
    "http://127.0.0.1:8000"
)


# ====================================
# DISABLE LOCAL PROXY
# ====================================

os.environ["NO_PROXY"] = (
    "127.0.0.1,localhost"
)

os.environ["no_proxy"] = (
    "127.0.0.1,localhost"
)


# ====================================
# API SESSION
# ====================================

api_session = (
    requests.Session()
)

api_session.trust_env = False


class OrderEntryPanel:


    # ====================================
    # RENDER
    # ====================================

    def render(self):

        st.subheader(
            "Order Entry"
        )

        symbol = st.text_input(

            "Symbol",

            value="NVDA"
        )

        side = st.selectbox(

            "Side",

            [

                "BUY",

                "SELL"
            ]
        )

        qty = st.number_input(

            "Quantity",

            min_value=1,

            value=100
        )

        strategy = st.selectbox(

            "Strategy",

            [

                "TWAP",

                "VWAP",

                "POV"
            ]
        )

        if st.button(

            "Submit Order",

            use_container_width=True
        ):

            self.submit_order(

                symbol=
                symbol,

                qty=
                qty,

                side=
                side,

                strategy=
                strategy
            )


    # ====================================
    # SUBMIT ORDER
    # ====================================

    def submit_order(

        self,

        symbol,

        qty,

        side,

        strategy
    ):

        try:

            payload = {

                "symbol":
                symbol.upper(),

                "qty":
                float(qty),

                "side":
                side,

                "strategy":
                strategy
            }

            response = api_session.post(

                f"{API_URL}/order",

                json=
                payload,

                timeout=
                5
            )

            if response.status_code == 200:

                result = (
                    response.json()
                )

                if result.get(
                    "accepted",
                    False
                ):

                    order_id = (

                        result.get(
                            "order_id"
                        )

                        or

                        result.get(
                            "result",
                            {}
                        ).get(
                            "order_id"
                        )

                        or

                        "UNKNOWN"
                    )

                    st.success(

                        f"Order Submitted | "

                        f"{order_id}"
                    )

                    st.json(
                        result
                    )

                else:

                    st.error(

                        f"Order Rejected | "

                        f"{result.get('error', 'Unknown Error')}"
                    )

                    st.json(
                        result
                    )

            else:

                st.error(

                    f"Order Failed | "

                    f"HTTP {response.status_code} | "

                    f"{response.text}"
                )

        except Exception as error:

            st.error(

                f"Connection Failed | "

                f"{error}"
            )