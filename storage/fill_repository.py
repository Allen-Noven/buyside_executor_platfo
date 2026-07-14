# ====================================
# fill_repository.py
# ====================================

from storage.database import (
    get_connection,
    init_database
)

from utils.helpers import (
    get_current_timestamp
)


class FillRepository:


    def __init__(self):

        init_database()

        self.connection = (
            get_connection()
        )


    def save_fill(

        self,

        fill
    ):

        cursor = self.connection.cursor()

        qty = float(
            fill.get("qty", 0)
        )

        fill_price = float(
            fill.get("fill_price", 0)
        )

        notional = (
            qty
            *
            fill_price
        )

        cursor.execute(
            """
            INSERT INTO fills (
                order_id,
                broker_order_id,
                symbol,
                side,
                qty,
                fill_price,
                notional,
                status,
                strategy,
                timestamp
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                fill.get("order_id"),
                fill.get("broker_order_id"),
                fill.get("symbol"),
                fill.get("side"),
                qty,
                fill_price,
                notional,
                fill.get("status"),
                fill.get("strategy"),
                fill.get("timestamp", get_current_timestamp())
            )
        )

        self.connection.commit()


    def list_fills(

        self,

        limit=100
    ):

        cursor = self.connection.cursor()

        cursor.execute(
            """
            SELECT *
            FROM fills
            ORDER BY id DESC
            LIMIT ?
            """,
            (
                limit,
            )
        )

        rows = cursor.fetchall()

        return [
            dict(row)
            for row in rows
        ]


    def get_fills_by_symbol(

        self,

        symbol
    ):

        cursor = self.connection.cursor()

        cursor.execute(
            """
            SELECT *
            FROM fills
            WHERE symbol = ?
            ORDER BY id DESC
            """,
            (
                symbol.upper(),
            )
        )

        rows = cursor.fetchall()

        return [
            dict(row)
            for row in rows
        ]


    def close(self):

        self.connection.close()