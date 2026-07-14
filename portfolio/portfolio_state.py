# ====================================
# portfolio_state.py
# ====================================

from utils.logger import (
    SystemLogger
)

from utils.helpers import (
    format_price
)


class PortfolioState:


    # ====================================
    # INIT
    # ====================================

    def __init__(

        self,

        position_manager,

        account_provider=None
    ):

        self.logger = (
            SystemLogger()
        )

        self.position_manager = (
            position_manager
        )

        self.account_provider = (
            account_provider
        )


    # ====================================
    # GET TOTAL POSITIONS
    # ====================================

    def get_total_positions(self):

        positions = (
            self.position_manager
            .get_all_positions()
        )

        return len(
            positions
        )


    # ====================================
    # GET GROSS EXPOSURE
    # ====================================

    def get_gross_exposure(self):

        positions = (
            self.position_manager
            .get_all_positions()
        )

        gross_exposure = 0

        for position in positions.values():

            gross_exposure += abs(
                position[
                    "market_value"
                ]
            )

        return format_price(
            gross_exposure
        )


    # ====================================
    # GET NET EXPOSURE
    # ====================================

    def get_net_exposure(self):

        positions = (
            self.position_manager
            .get_all_positions()
        )

        net_exposure = 0

        for position in positions.values():

            net_exposure += (
                position[
                    "market_value"
                ]
            )

        return format_price(
            net_exposure
        )


    # ====================================
    # GET LONG EXPOSURE
    # ====================================

    def get_long_exposure(self):

        positions = (
            self.position_manager
            .get_all_positions()
        )

        long_exposure = 0

        for position in positions.values():

            market_value = (
                position[
                    "market_value"
                ]
            )

            if market_value > 0:

                long_exposure += market_value

        return format_price(
            long_exposure
        )


    # ====================================
    # GET SHORT EXPOSURE
    # ====================================

    def get_short_exposure(self):

        positions = (
            self.position_manager
            .get_all_positions()
        )

        short_exposure = 0

        for position in positions.values():

            market_value = (
                position[
                    "market_value"
                ]
            )

            if market_value < 0:

                short_exposure += abs(
                    market_value
                )

        return format_price(
            short_exposure
        )


    # ====================================
    # GET ACCOUNT SNAPSHOT
    # ====================================

    def get_account_snapshot(self):

        if not self.account_provider:

            return None

        try:

            if hasattr(
                self.account_provider,
                "get_snapshot"
            ):

                return (
                    self.account_provider
                    .get_snapshot()
                )

            if hasattr(
                self.account_provider,
                "get_account"
            ):

                account = (
                    self.account_provider
                    .get_account()
                )

                if account is None:

                    return None

                if isinstance(
                    account,
                    dict
                ):

                    return account

                return {

                    "account_type":
                    "BROKER",

                    "cash":
                    float(
                        getattr(
                            account,
                            "cash",
                            0
                        )
                    ),

                    "buying_power":
                    float(
                        getattr(
                            account,
                            "buying_power",
                            0
                        )
                    ),

                    "equity":
                    float(
                        getattr(
                            account,
                            "equity",
                            0
                        )
                    )
                }

        except Exception as error:

            self.logger.error(

                f"Account Snapshot Failed | "

                f"{error}"
            )

        return None


    # ====================================
    # GET PORTFOLIO SUMMARY
    # ====================================

    def get_portfolio_summary(self):

        position_summary = (
            self.position_manager
            .get_portfolio_summary()
        )

        account_snapshot = (
            self.get_account_snapshot()
        )

        return {

            "total_positions":
            self.get_total_positions(),

            "gross_exposure":
            self.get_gross_exposure(),

            "net_exposure":
            self.get_net_exposure(),

            "long_exposure":
            self.get_long_exposure(),

            "short_exposure":
            self.get_short_exposure(),

            "total_market_value":
            position_summary.get(
                "total_market_value"
            ),

            "total_realized_pnl":
            position_summary.get(
                "total_realized_pnl"
            ),

            "total_unrealized_pnl":
            position_summary.get(
                "total_unrealized_pnl"
            ),

            "account":
            account_snapshot
        }