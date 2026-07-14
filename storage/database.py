# ====================================
# database.py
# ====================================

import os
import sqlite3


DATABASE_PATH = (
    "storage/trading_system.db"
)


# ====================================
# ENSURE STORAGE DIR
# ====================================

os.makedirs(
    os.path.dirname(DATABASE_PATH),
    exist_ok=True
)


# ====================================
# GET CONNECTION
# ====================================

def get_connection():

    connection = sqlite3.connect(
        DATABASE_PATH,
        check_same_thread=False
    )

    connection.row_factory = sqlite3.Row

    return connection


# ====================================
# INIT DATABASE
# ====================================

def init_database():

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS orders (
            order_id TEXT PRIMARY KEY,
            symbol TEXT,
            side TEXT,
            quantity REAL,
            filled_quantity REAL,
            strategy TEXT,
            status TEXT,
            arrival_price REAL,
            created_at TEXT,
            updated_at TEXT
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS fills (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id TEXT,
            broker_order_id TEXT,
            symbol TEXT,
            side TEXT,
            qty REAL,
            fill_price REAL,
            notional REAL,
            status TEXT,
            strategy TEXT,
            timestamp TEXT
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS positions (
            symbol TEXT PRIMARY KEY,
            qty REAL,
            avg_price REAL,
            market_price REAL,
            market_value REAL,
            realized_pnl REAL,
            unrealized_pnl REAL,
            total_bought REAL,
            total_sold REAL,
            updated_at TEXT
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS executions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            execution_id TEXT,
            order_id TEXT,
            symbol TEXT,
            side TEXT,
            quantity REAL,
            filled_quantity REAL,
            strategy TEXT,
            status TEXT,
            payload TEXT,
            timestamp TEXT
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS account_snapshots (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            account_type TEXT,
            cash REAL,
            buying_power REAL,
            equity REAL,
            realized_pnl REAL,
            unrealized_pnl REAL,
            total_notional_traded REAL,
            trade_count INTEGER,
            timestamp TEXT
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS market_snapshots (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            symbol TEXT,
            price REAL,
            bid_price REAL,
            ask_price REAL,
            spread REAL,
            volume REAL,
            liquidity_score REAL,
            volatility REAL,
            source TEXT,
            timestamp TEXT
        )
        """
    )

    connection.commit()

    connection.close()