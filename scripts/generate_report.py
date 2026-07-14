# ====================================
# generate_report.py
# ====================================

from utils.logger import (
    SystemLogger
)

from analytics.pnl_tracker import (
    PnLTracker
)

from analytics.trade_blotter import (
    TradeBlotter
)

from analytics.transaction_cost_engine import (
    TransactionCostEngine
)

from analytics.execution_quality import (
    ExecutionQuality
)

from portfolio.position_manager import (
    PositionManager
)

from portfolio.portfolio_state import (
    PortfolioState
)

from portfolio.holdings_snapshot import (
    HoldingsSnapshot
)


# ====================================
# LOGGER
# ====================================

logger = SystemLogger()


# ====================================
# GENERATE REPORT
# ====================================

def generate_report():

    logger.info(

        "Generating End-of-Day Reports..."
    )


    # ====================================
    # INITIALIZE PORTFOLIO
    # ====================================

    position_manager = (
        PositionManager()
    )

    portfolio_state = (
        PortfolioState(
            position_manager
        )
    )

    holdings_snapshot = (
        HoldingsSnapshot(
            position_manager
        )
    )


    # ====================================
    # INITIALIZE ANALYTICS
    # ====================================

    pnl_tracker = (
        PnLTracker()
    )

    trade_blotter = (
        TradeBlotter()
    )

    transaction_cost_engine = (
        TransactionCostEngine()
    )

    execution_quality = (
        ExecutionQuality()
    )


    # ====================================
    # GENERATE HOLDINGS SNAPSHOT
    # ====================================

    logger.info(

        "Saving Holdings Snapshot..."
    )

    holdings_snapshot.save_snapshot()


    # ====================================
    # SHOW PORTFOLIO SUMMARY
    # ====================================

    portfolio_state.show_portfolio_summary()


    # ====================================
    # SHOW PNL
    # ====================================

    logger.info(

        "Generating PnL Summary..."
    )

    pnl_tracker.show_pnl_summary()


    # ====================================
    # SHOW TRANSACTION COSTS
    # ====================================

    logger.info(

        "Generating Transaction Cost Report..."
    )

    transaction_cost_engine.show_summary()


    # ====================================
    # SHOW EXECUTION QUALITY
    # ====================================

    logger.info(

        "Generating Execution Quality Report..."
    )

    execution_quality.show_summary()


    # ====================================
    # GENERATE TRADE BLOTTER
    # ====================================

    logger.info(

        "Generating Trade Blotter..."
    )

    trade_blotter.generate_report()


    # ====================================
    # REPORT COMPLETE
    # ====================================

    logger.info(

        "All Reports Generated Successfully"
    )


# ====================================
# MAIN
# ====================================

if __name__ == "__main__":

    generate_report()