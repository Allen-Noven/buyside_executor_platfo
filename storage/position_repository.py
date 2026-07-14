# ====================================
# position_repository.py
# ====================================

from storage.database import (
    get_connection,
    init_database
)

from utils.helpers import (
    get_current_timestamp
)


class PositionRepository:


    def __init__(self):

        init_database()

        self.connection = (
            get_connection()
        )


    def save_position(

        self,

        position
    ):

        cursor = self.connection.cursor()

        cursor.execute(
            """
            INSERT OR REPLACE INTO positions (
                symbol,
                qty,
                avg_price,
                market_price,
                market_value,
                realized_pnl,
                unrealized_pnl,
                total_bought,
                total_sold,
                updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                position.get("symbol"),
                position.get("qty", position.get("quantity", 0)),
                position.get("avg_price", position.get("average_price", 0)),
                position.get("market_price", 0),
                position.get("market_value", 0),
                position.get("realized_pnl", 0),
                position.get("unrealized_pnl", 0),
                position.get("total_bought", 0),
                position.get("total_sold", 0),
                get_current_timestamp()
            )
        )

        self.connection.commit()


    def save_positions(

        self,

        positions
    ):

        for position in positions.values():

            self.save_position(
                position
            )


    def load_positions(self):

        cursor = self.connection.cursor()

        cursor.execute(
            """
            SELECT *
            FROM positions
            """
        )

        rows = cursor.fetchall()

        return {
            row["symbol"]: dict(row)
            for row in rows
        }


    def get_position(

        self,

        symbol
    ):

        cursor = self.connection.cursor()

        cursor.execute(
            """
            SELECT *
            FROM positions
            WHERE symbol = ?
            """,
            (
                symbol.upper(),
            )
        )

        row = cursor.fetchone()

        return dict(row) if row else None


    def clear_positions(self):

        cursor = self.connection.cursor()

        cursor.execute(
            """
            DELETE FROM positions
            """
        )

        self.connection.commit()


    def close(self):

        self.connection.close()