# ====================================
# runtime_bootstrap.py
# ====================================

import threading

from utils.logger import (
    SystemLogger
)

from utils.runtime_mode import (

    RUNTIME_MODE,

    SIMULATION,

    PAPER,

    LIVE
)

from utils.constants import (

    MARKET_UPDATE_EVENT,

    ORDER_FILLED_EVENT,

    EXECUTION_STARTED,

    EXECUTION_COMPLETED,

    MARKET_DATA_CONNECTED,

    MARKET_DATA_DISCONNECTED,

    MARKET_DATA_ERROR,

    MARKET_DATA_SUBSCRIBED,

    PARENT_ORDER_SPLIT,

    PARENT_ORDER_PROGRESS,

    PARENT_ORDER_COMPLETED,

    PARENT_ORDER_HALTED
)

from runtime.runtime_context import (

    register_runtime,

    set_worker_running,

    set_market_data_running
)

from runtime.runtime_event_handlers import (
    make_websocket_handler
)

from core.market_state import (
    MarketState
)

from core.redis_state import (
    RedisState
)

from data.market_event_bus import (
    MarketEventBus
)

from data.market_data_factory import (
    create_market_data_service
)

from execution.order_queue import (
    OrderQueue
)

from execution.execution_service import (
    ExecutionService
)

from execution.execution_worker import (
    ExecutionWorker
)

from execution.oms.oms_factory import (
    create_oms
)

from portfolio.position_manager import (
    PositionManager
)

from portfolio.portfolio_state import (
    PortfolioState
)

from portfolio.simulation_account import (
    SimulationAccount
)

from portfolio.broker_position_service import (
    BrokerPositionService
)

from portfolio.position_reconciliation import (
    PositionReconciliation
)

from portfolio.reconciliation_worker import (
    ReconciliationWorker
)

from storage.order_repository import (
    OrderRepository
)

from storage.position_repository import (
    PositionRepository
)


class RuntimeBootstrap:


    # ====================================
    # INIT
    # ====================================

    def __init__(self):

        self.logger = (
            SystemLogger()
        )

        self.order_repository = (
            OrderRepository()
        )

        self.position_repository = (
            PositionRepository()
        )

        self.market_data_service = None

        self.market_state = None

        self.redis_state = None

        self.event_bus = None

        self.oms = None

        self.simulation_account = None

        self.position_manager = None

        self.portfolio_state = None

        self.broker_position_service = None

        self.position_reconciliation = None

        self.reconciliation_worker = None

        self.execution_service = None

        self.order_queue = None

        self.execution_worker = None

        self.execution_worker_thread = None


    # ====================================
    # REGISTER WEBSOCKET EVENT HANDLERS
    # ====================================

    def register_websocket_event_handlers(self):

        if self.event_bus is None:

            raise RuntimeError(
                "Event Bus Not Initialized"
            )

        # ====================================
        # SYSTEM EVENTS
        # ====================================

        self.event_bus.subscribe(

            "SYSTEM_ERROR",

            make_websocket_handler(
                "SYSTEM_ERROR"
            )
        )

        # ====================================
        # MARKET DATA EVENTS
        # ====================================

        self.event_bus.subscribe(

            MARKET_UPDATE_EVENT,

            make_websocket_handler(
                "MARKET_UPDATE"
            )
        )

        self.event_bus.subscribe(

            MARKET_DATA_CONNECTED,

            make_websocket_handler(
                "MARKET_DATA_CONNECTED"
            )
        )

        self.event_bus.subscribe(

            MARKET_DATA_DISCONNECTED,

            make_websocket_handler(
                "MARKET_DATA_DISCONNECTED"
            )
        )

        self.event_bus.subscribe(

            MARKET_DATA_ERROR,

            make_websocket_handler(
                "MARKET_DATA_ERROR"
            )
        )

        self.event_bus.subscribe(

            MARKET_DATA_SUBSCRIBED,

            make_websocket_handler(
                "MARKET_DATA_SUBSCRIBED"
            )
        )

        # ====================================
        # EXECUTION EVENTS
        # ====================================

        self.event_bus.subscribe(

            ORDER_FILLED_EVENT,

            make_websocket_handler(
                "FILL_UPDATE"
            )
        )

        self.event_bus.subscribe(

            EXECUTION_STARTED,

            make_websocket_handler(
                "EXECUTION_STARTED"
            )
        )

        self.event_bus.subscribe(

            EXECUTION_COMPLETED,

            make_websocket_handler(
                "EXECUTION_COMPLETED"
            )
        )

        # ====================================
        # PARENT ORDER EVENTS
        # ====================================

        self.event_bus.subscribe(

            PARENT_ORDER_SPLIT,

            make_websocket_handler(
                "PARENT_ORDER_SPLIT"
            )
        )

        self.event_bus.subscribe(

            PARENT_ORDER_PROGRESS,

            make_websocket_handler(
                "PARENT_ORDER_PROGRESS"
            )
        )

        self.event_bus.subscribe(

            PARENT_ORDER_COMPLETED,

            make_websocket_handler(
                "PARENT_ORDER_COMPLETED"
            )
        )

        self.event_bus.subscribe(

            PARENT_ORDER_HALTED,

            make_websocket_handler(
                "PARENT_ORDER_HALTED"
            )
        )

        self.logger.info(
            "WebSocket Event Handlers Registered"
        )


    # ====================================
    # BOOTSTRAP
    # ====================================

    def bootstrap(self):

        self.logger.warning(

            f"Bootstrapping Runtime | "
            f"Mode={RUNTIME_MODE}"
        )

        try:

            # ====================================
            # CORE RUNTIME
            # ====================================

            self.market_state = (
                MarketState()
            )

            self.redis_state = (
                RedisState()
            )

            self.event_bus = (
                MarketEventBus()
            )

            # ====================================
            # WEBSOCKET EVENT HANDLERS
            # ====================================

            self.register_websocket_event_handlers()

            # ====================================
            # SIMULATION ACCOUNT
            # ====================================

            self.simulation_account = None

            if RUNTIME_MODE == SIMULATION:

                self.simulation_account = (

                    SimulationAccount(

                        initial_cash=
                        100000
                    )
                )

                self.logger.info(
                    "Simulation Account Created"
                )

            # ====================================
            # POSITION MANAGER
            # ====================================

            self.position_manager = (

                PositionManager(

                    event_bus=
                    self.event_bus,

                    simulation_account=
                    self.simulation_account
                )
            )

            # ====================================
            # OMS
            # ====================================

            self.oms = create_oms(

                simulation_account=
                self.simulation_account,

                market_state=
                self.market_state
            )

            # ====================================
            # ENSURE SIMULATION ACCOUNT CONNECTED
            # ====================================

            if (

                RUNTIME_MODE == SIMULATION
                and
                hasattr(
                    self.oms,
                    "broker_adapter"
                )
                and
                hasattr(
                    self.oms.broker_adapter,
                    "simulation_account"
                )
            ):

                self.oms.broker_adapter.simulation_account = (
                    self.simulation_account
                )

                self.logger.info(
                    "Simulation Account Attached To OMS Broker Adapter"
                )

            # ====================================
            # PORTFOLIO STATE
            # ====================================

            account_provider = (

                self.simulation_account

                if self.simulation_account

                else self.oms
            )

            self.portfolio_state = (

                PortfolioState(

                    position_manager=
                    self.position_manager,

                    account_provider=
                    account_provider
                )
            )

            # ====================================
            # MARKET DATA SERVICE
            # ====================================

            self.market_data_service = (

                create_market_data_service(

                    market_state=
                    self.market_state,

                    event_bus=
                    self.event_bus
                )
            )

            self.logger.info(
                "Market Data Service Created"
            )

            # ====================================
            # BROKER POSITION / RECONCILIATION
            # ====================================

            if RUNTIME_MODE in [

                PAPER,

                LIVE
            ]:

                self.broker_position_service = (

                    BrokerPositionService(

                        event_bus=
                        self.event_bus
                    )
                )

                self.position_reconciliation = (

                    PositionReconciliation(

                        internal_position_manager=
                        self.position_manager,

                        broker_positions=
                        self.broker_position_service,

                        event_bus=
                        self.event_bus
                    )
                )

                self.reconciliation_worker = (

                    ReconciliationWorker(

                        broker_position_service=
                        self.broker_position_service,

                        reconciliation_engine=
                        self.position_reconciliation,

                        interval=
                        30
                    )
                )

                self.logger.info(
                    "Broker Position Reconciliation Created"
                )

            else:

                self.logger.warning(

                    "Broker Reconciliation Disabled "
                    "For Simulation Runtime"
                )

            # ====================================
            # EXECUTION SERVICE
            # ====================================

            self.execution_service = (

                ExecutionService(

                    market_state=
                    self.market_state,

                    event_bus=
                    self.event_bus,

                    oms=
                    self.oms,

                    position_manager=
                    self.position_manager,

                    market_data_service=
                    self.market_data_service
                )
            )

            # ====================================
            # ORDER QUEUE
            # ====================================

            self.order_queue = (
                OrderQueue()
            )

            # ====================================
            # EXECUTION WORKER
            # ====================================

            self.execution_worker = (

                ExecutionWorker(

                    order_queue=
                    self.order_queue,

                    execution_service=
                    self.execution_service
                )
            )

            # ====================================
            # REGISTER RUNTIME CONTEXT
            # ====================================

            register_runtime(

                runtime_market_state=
                self.market_state,

                runtime_redis_state=
                self.redis_state,

                runtime_event_bus=
                self.event_bus,

                runtime_oms=
                self.oms,

                runtime_position_manager=
                self.position_manager,

                runtime_portfolio_state=
                self.portfolio_state,

                runtime_simulation_account=
                self.simulation_account,

                runtime_execution_service=
                self.execution_service,

                runtime_order_queue=
                self.order_queue,

                runtime_execution_worker=
                self.execution_worker,

                runtime_market_data_service=
                self.market_data_service
            )

            # ====================================
            # RECOVER STATE
            # ====================================

            self.recover_runtime_state()

            # ====================================
            # START EXECUTION WORKER
            # ====================================

            self.start_execution_worker()

            # ====================================
            # START MARKET DATA SERVICE
            # ====================================

            if self.market_data_service:

                self.market_data_service.start_async()

                set_market_data_running(
                    True
                )

                self.logger.info(
                    "Market Data Service Started"
                )

            # ====================================
            # START RECONCILIATION WORKER
            # ====================================

            if self.reconciliation_worker:

                self.reconciliation_worker.start()

                self.logger.info(
                    "Reconciliation Worker Started"
                )

            self.logger.info(
                "Runtime Bootstrap Complete"
            )

        except Exception as error:

            self.logger.error(

                f"Runtime Bootstrap Failed | "
                f"{error}"
            )

            raise


    # ====================================
    # START EXECUTION WORKER
    # ====================================

    def start_execution_worker(self):

        try:

            if self.execution_worker is None:

                raise RuntimeError(
                    "Execution Worker Not Initialized"
                )

            self.execution_worker_thread = threading.Thread(

                target=
                self.execution_worker.start,

                daemon=True
            )

            self.execution_worker_thread.start()

            set_worker_running(
                True
            )

            self.logger.info(
                "Execution Worker Thread Started"
            )

        except Exception as error:

            self.logger.error(

                f"Execution Worker Failed | "
                f"{error}"
            )

            raise


    # ====================================
    # RECOVER RUNTIME STATE
    # ====================================

    def recover_runtime_state(self):

        try:

            self.logger.info(
                "Recovering Runtime State"
            )

            positions = (

                self.position_repository
                .load_positions()
            )

            active_orders = (

                self.order_repository
                .load_active_orders()
            )

            self.logger.info(

                f"Recovered Positions | "
                f"{len(positions)}"
            )

            self.logger.info(

                f"Recovered Active Orders | "
                f"{len(active_orders)}"
            )

        except Exception as error:

            self.logger.error(

                f"Recovery Failed | "
                f"{error}"
            )


    # ====================================
    # SHUTDOWN
    # ====================================

    def shutdown(self):

        self.logger.warning(
            "Runtime Shutdown Started"
        )

        try:

            if self.execution_worker:

                self.execution_worker.stop()

            if self.market_data_service:

                self.market_data_service.stop()

                set_market_data_running(
                    False
                )

            if self.reconciliation_worker:

                self.reconciliation_worker.stop()

            set_worker_running(
                False
            )

        except Exception as error:

            self.logger.error(

                f"Shutdown Failed | "
                f"{error}"
            )

        self.logger.warning(
            "Runtime Shutdown Complete"
        )