# ====================================
# order_book_manager.py
# ====================================

from data.market_book.order_book import (
    OrderBook
)

from utils.logger import (
    SystemLogger
)


class OrderBookManager:


    # ====================================
    # INIT
    # ====================================

    def __init__(

        self,

        market_state=None
    ):

        self.market_state = (
            market_state
        )

        self.books = {}

        self.logger = (
            SystemLogger()
        )

        self.logger.info(
            "OrderBookManager Initialized"
        )


    # ====================================
    # CREATE BOOK
    # ====================================

    def create_book(

        self,

        symbol
    ):

        if symbol not in self.books:

            self.books[symbol] = (

                OrderBook(symbol)
            )

            self.logger.info(

                f"OrderBook Created | "

                f"{symbol}"
            )

        return self.books[symbol]


    # ====================================
    # GET BOOK
    # ====================================

    def get_book(

        self,

        symbol
    ):

        if symbol not in self.books:

            return self.create_book(
                symbol
            )

        return self.books[symbol]


    # ====================================
    # UPDATE BOOK
    # ====================================

    def update_book(

        self,

        symbol,

        bids,

        asks,

        timestamp=None
    ):

        book = (
            self.get_book(symbol)
        )

        book.update_book(

            bids=bids,

            asks=asks,

            timestamp=timestamp
        )

        # ====================================
        # SYNC MARKET STATE
        # ====================================

        if self.market_state:

            self.market_state.order_book = (
                book
            )

            best_bid = (
                book.get_best_bid()
            )

            best_ask = (
                book.get_best_ask()
            )

            self.market_state.bid = (

                best_bid[0]

                if best_bid

                else None
            )

            self.market_state.ask = (

                best_ask[0]

                if best_ask

                else None
            )

            self.market_state.spread = (
                book.get_spread()
            )

            self.market_state.mid_price = (
                book.get_mid_price()
            )

            self.market_state.imbalance = (
                book.get_imbalance()
            )

        self.logger.info(

            f"Book Updated | "

            f"{symbol}"
        )


    # ====================================
    # GET SNAPSHOT
    # ====================================

    def get_snapshot(

        self,

        symbol
    ):

        book = (
            self.get_book(symbol)
        )

        return book.get_snapshot()


    # ====================================
    # GET ALL SNAPSHOTS
    # ====================================

    def get_all_snapshots(self):

        snapshots = {}

        for symbol, book in (

            self.books.items()
        ):

            snapshots[symbol] = (
                book.get_snapshot()
            )

        return snapshots


    # ====================================
    # REMOVE BOOK
    # ====================================

    def remove_book(

        self,

        symbol
    ):

        if symbol in self.books:

            del self.books[symbol]

            self.logger.warning(

                f"Book Removed | "

                f"{symbol}"
            )


    # ====================================
    # CLEAR ALL BOOKS
    # ====================================

    def clear_all_books(self):

        for book in self.books.values():

            book.clear()

        self.logger.warning(
            "All Books Cleared"
        )


    # ====================================
    # GET SYMBOLS
    # ====================================

    def get_symbols(self):

        return list(
            self.books.keys()
        )


    # ====================================
    # BOOK COUNT
    # ====================================

    def get_book_count(self):

        return len(
            self.books
        )


    # ====================================
    # SHOW SNAPSHOT
    # ====================================

    def show_snapshot(

        self,

        symbol
    ):

        snapshot = (
            self.get_snapshot(symbol)
        )

        print(

            "\n========== "
            "BOOK SNAPSHOT "
            "==========\n"
        )

        print(

            f"Symbol: "
            f"{snapshot['symbol']}"
        )

        print(

            f"Best Bid: "
            f"{snapshot['best_bid']}"
        )

        print(

            f"Best Ask: "
            f"{snapshot['best_ask']}"
        )

        print(

            f"Spread: "
            f"{snapshot['spread']}"
        )

        print(

            f"Mid Price: "
            f"{snapshot['mid_price']}"
        )

        print(

            f"Imbalance: "
            f"{snapshot['imbalance']}"
        )

        print(

            "\n=================================\n"
        )