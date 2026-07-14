# ====================================
# oms_factory.py
# ====================================

from utils.runtime_mode import (

    RUNTIME_MODE,

    SIMULATION,

    PAPER,

    LIVE
)

from utils.logger import (
    SystemLogger
)

from execution.oms.fake_oms import (
    SimulationOMS
)

from execution.oms.live_oms import (
    LiveOMS
)


logger = (
    SystemLogger()
)


# ====================================
# CREATE OMS
# ====================================

def create_oms(

    simulation_account=None,

    market_state=None
):

    logger.warning(

        f"Creating OMS | "

        f"Mode={RUNTIME_MODE}"
    )

    # ====================================
    # SIMULATION MODE
    # ====================================

    if RUNTIME_MODE == SIMULATION:

        logger.warning(

            "#################################\n"

            "####### SIMULATION MODE ########\n"

            "#################################"
        )

        return SimulationOMS(

            simulation_account=
            simulation_account,

            market_state=
            market_state
        )

    # ====================================
    # PAPER MODE
    # ====================================

    if RUNTIME_MODE == PAPER:

        logger.warning(

            "#################################\n"

            "########## PAPER MODE ##########\n"

            "#################################"
        )

        # For now, use LiveOMS with Alpaca paper=True
        # PAPER_TRADING in config controls Alpaca paper account.
        return LiveOMS()

    # ====================================
    # LIVE MODE
    # ====================================

    if RUNTIME_MODE == LIVE:

        logger.warning(

            "#################################\n"

            "########### LIVE MODE ##########\n"

            "#################################"
        )

        return LiveOMS()

    # ====================================
    # INVALID MODE
    # ====================================

    raise RuntimeError(

        f"Unsupported Runtime Mode | "

        f"{RUNTIME_MODE}"
    )