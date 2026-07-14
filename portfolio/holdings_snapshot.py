# ====================================
# holdings_snapshot.py
# ====================================

import os

import pandas as pd

from utils.logger import (
    SystemLogger
)

from utils.helpers import (
    get_current_timestamp
)

from utils.config import (
    HOLDINGS_REPORT_DIR
)


class HoldingsSnapshot:


    # ====================================
    # INIT
    # ====================================

    def __init__(

        self,

        position_manager
    ):

        self.logger = (
            SystemLogger()
        )

        self.position_manager = (
            position_manager
        )

        os.makedirs(

            HOLDINGS_REPORT_DIR,

            exist_ok=True
        )


    # ====================================
    # CREATE SNAPSHOT DATAFRAME
    # ====================================

    def create_snapshot(self):

        positions = (

            self.position_manager
            .get_all_positions()
        )

        snapshot_rows = []

        for symbol, position in (

            positions.items()
        ):

            snapshot_rows.append({

                "timestamp":
                get_current_timestamp(),

                "symbol":
                symbol,

                "qty":
                position["qty"],

                "avg_price":
                position["avg_price"],

                "market_value":
                position["market_value"]
            })

        return pd.DataFrame(
            snapshot_rows
        )


    # ====================================
    # SAVE SNAPSHOT
    # ====================================

    def save_snapshot(self):

        snapshot_df = (
            self.create_snapshot()
        )

        timestamp = (

            get_current_timestamp()

            .replace(":", "-")

            .replace(" ", "_")
        )

        file_name = (

            f"{HOLDINGS_REPORT_DIR}"

            f"holdings_snapshot_"

            f"{timestamp}.csv"
        )

        snapshot_df.to_csv(

            file_name,

            index=False
        )

        self.logger.info(

            f"Holdings Snapshot Saved | "

            f"{file_name}"
        )

        return file_name


    # ====================================
    # SHOW SNAPSHOT
    # ====================================

    def show_snapshot(self):

        snapshot_df = (
            self.create_snapshot()
        )

        print(

            "\n========== "
            "HOLDINGS SNAPSHOT "
            "==========\n"
        )

        print(snapshot_df)

        print(

            "\n==============================="
            "===================\n"
        )