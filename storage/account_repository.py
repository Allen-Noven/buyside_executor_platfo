# ====================================
# account_repository.py
# ====================================

from storage.database import (
    get_connection,
    init_database
)

from utils.helpers import (
    get_current_timestamp
)


class AccountRepository:


    def __init__(self):

        init_database()

        self.connection = (
            get_connection()
        )


    def save_account_snapshot(

        self,

        account
    ):

        if account is None:

            return

        cursor = self.connection.cursor()

        cursor.execute(
            """
            INSERT INTO account_snapshots (
                account_type,
                cash,
                buying_power,
                equity,
                realized_pnl,
                unrealized_pnl,
                total_notional_traded,
                trade_count,
                timestamp
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                account.get("account_type", "UNKNOWN"),
                account.get("cash", 0),
                account.get("buying_power", 0),
                account.get("equity", 0),
                account.get("realized_pnl", 0),
                account.get("unrealized_pnl", 0),
                account.get("total_notional_traded", 0),
                account.get("trade_count", 0),
                get_current_timestamp()
            )
        )

        self.connection.commit()


    def get_latest_account_snapshot(self):

        cursor = self.connection.cursor()

        cursor.execute(
            """
            SELECT *
            FROM account_snapshots
            ORDER BY id DESC
            LIMIT 1
            """
        )

        row = cursor.fetchone()

        return dict(row) if row else None


    def close(self):

        self.connection.close()