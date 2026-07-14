# ====================================
# order_repository.py
# ====================================

from storage.database import (
    get_connection,
    init_database
)

from utils.helpers import (
    get_current_timestamp
)


class OrderRepository:


    def __init__(self):

        init_database()

        self.connection = (
            get_connection()
        )


    def save_order(

        self,

        order
    ):

        cursor = self.connection.cursor()

        cursor.execute(
            """
            INSERT OR REPLACE INTO orders (
                order_id,
                symbol,
                side,
                quantity,
                filled_quantity,
                strategy,
                status,
                arrival_price,
                created_at,
                updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                order.order_id,
                order.symbol,
                order.side,
                order.quantity,
                order.filled_quantity,
                order.strategy,
                order.status,
                getattr(order, "arrival_price", None),
                str(getattr(order, "created_at", "")),
                get_current_timestamp()
            )
        )

        self.connection.commit()


    def load_active_orders(self):

        cursor = self.connection.cursor()

        cursor.execute(
            """
            SELECT *
            FROM orders
            WHERE status NOT IN ('COMPLETED', 'CANCELLED', 'REJECTED', 'FAILED', 'HALTED')
            ORDER BY updated_at DESC
            """
        )

        rows = cursor.fetchall()

        return [
            dict(row)
            for row in rows
        ]


    def get_order(

        self,

        order_id
    ):

        cursor = self.connection.cursor()

        cursor.execute(
            """
            SELECT *
            FROM orders
            WHERE order_id = ?
            """,
            (
                order_id,
            )
        )

        row = cursor.fetchone()

        return dict(row) if row else None


    def list_orders(

        self,

        limit=100
    ):

        cursor = self.connection.cursor()

        cursor.execute(
            """
            SELECT *
            FROM orders
            ORDER BY updated_at DESC
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


    def close(self):

        self.connection.close()